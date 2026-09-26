import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
import datetime

API_KEYS = st.secrets.get("API_KEYS", [])

def generate_ai_response(prompt_content):
    """Tự động thử lần lượt các Key trong secrets, nếu Key lỗi sẽ chuyển Key tiếp theo"""
    if not API_KEYS:
        st.error("⚠️ Chưa cấu hình API_KEYS trong Streamlit Secrets!")
        return None

    for key in API_KEYS:
        if not key.strip(): 
            continue
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_content
            )
            return response.text
        except Exception:
            continue
            
    return None

st.set_page_config(page_title="Trợ lý học tập", page_icon="🤖", layout="wide")

if not firebase_admin._apps:
    cred = credentials.Certificate("data/key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

if "user" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập từ trang chủ trước!")
    st.stop()

user_uid = st.session_state["user"]

st.title("Trợ Lý Học Tập AI")
st.subheader("Hỗ trợ tóm tắt tài liệu, giải đáp thắc mắc và tạo đề ôn luyện")

tab1, tab2, tab3 = st.tabs(["💬 Chatbot", "📝 Luyện Đề Trắc Nghiệm", "📚 Tóm Tắt & Hỏi Đáp"])

#TAB 1:CHATBOT
with tab1:
    st.markdown("### 💬 Trò chuyện cùng AI")
    if "chat_counter" not in st.session_state:
        st.session_state["chat_counter"] = 1
    if "all_chats" not in st.session_state:
        st.session_state["all_chats"] = {"Đoạn chat 1": [{"role": "assistant", "content": "Chào bạn! Mình có thể giúp gì cho bạn hôm nay?"}]}
        st.session_state["current_chat"] = "Đoạn chat 1"

    col_menu, col_chat = st.columns([1, 3])
    with col_menu:
        st.markdown("**📚 Lịch sử chat**")
        
        if st.button("➕ Đoạn chat mới", use_container_width=True, type="primary"):
            st.session_state["chat_counter"] += 1
            new_chat_name = f"Đoạn chat {st.session_state['chat_counter']}"
            st.session_state["all_chats"][new_chat_name] = [{"role": "assistant", "content": "Chào bạn! Mình có thể giúp gì cho bạn hôm nay?"}]
            st.session_state["current_chat"] = new_chat_name
            st.rerun()
        st.markdown("---")
        for chat_name in list(st.session_state["all_chats"].keys()):
            col_name, col_del = st.columns([4, 1])

            with col_name:
                btn_type = "primary" if st.session_state.get("current_chat") == chat_name else "secondary"
                if st.button(chat_name, use_container_width=True, type=btn_type, key=f"btn_{chat_name}"):
                    st.session_state["current_chat"] = chat_name
                    st.rerun()
            
            with col_del:
                if st.button("🗑️", key=f"del_{chat_name}", help="Xóa đoạn chat này"):
                    del st.session_state["all_chats"][chat_name]
                    if not st.session_state["all_chats"]:
                        st.session_state["current_chat"] = None
                    elif st.session_state["current_chat"] == chat_name:
                        st.session_state["current_chat"] = list(st.session_state["all_chats"].keys())[0]
                    st.rerun()

    with col_chat:
        if st.session_state.get("current_chat") and st.session_state["current_chat"] in st.session_state["all_chats"]:
            current_history = st.session_state["all_chats"][st.session_state["current_chat"]]
            chat_container = st.container(height=450)
            for msg in current_history:
                chat_container.chat_message(msg["role"]).write(msg["content"])
            if prompt := st.chat_input("Nhập câu hỏi của bạn vào đây..."):
                current_history.append({"role": "user", "content": prompt})
                chat_container.chat_message("user").write(prompt)
                with chat_container.chat_message("assistant"):
                    with st.spinner("AI đang suy nghĩ..."):
                        history_context = "\n".join([f"{m['role']}: {m['content']}" for m in current_history])
                        answer = generate_ai_response(history_context)
                        
                        if answer:
                            st.write(answer)
                            current_history.append({"role": "assistant", "content": answer})
                        else:
                            st.error("⚠️ Hệ thống AI đang bận hoặc hết lượt dùng. Vui lòng thử lại sau!")

#TAB 2 TAOJ DDEEF THI
with tab2:
    st.markdown("### 🎯 Tự động tạo bài tập trắc nghiệm")
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        quiz_topic = st.text_area("Nhập chủ đề hoặc dán đoạn văn bản cần tạo đề:", height=120, placeholder="Ví dụ: Lịch sử Việt Nam giai đoạn 1945 - 1954...")
    with col_b:
        num_questions = st.number_input("Số câu hỏi:", min_value=1, max_value=30, value=3)
        do_kho = st.selectbox("Độ khó:", ["Cơ bản", "Trung bình", "Nâng cao"])

    if st.button("🎲 Tạo đề thi ngay", type="primary"):
        if not quiz_topic.strip():
            st.warning("Vui lòng nhập chủ đề hoặc nội dung cần tạo đề!")
        else:
            with st.spinner("AI đang soạn đề thi trắc nghiệm..."):
                prompt = f"""
                Bạn là giáo viên chuyên ra đề thi trắc nghiệm. Dựa vào nội dung dưới đây, hãy tạo đúng {num_questions} câu hỏi trắc nghiệm mức độ {do_kho}.
                
                NỘI DUNG:
                {quiz_topic}
                
                YÊU CẦU BẮT BUỘC:
                1. CHỈ trả về một mảng JSON hợp lệ. KHÔNG dùng ```json hay văn bản thừa.
                2. Mỗi phần tử là 1 câu hỏi có đúng 4 key:
                   - "question": Nội dung câu hỏi. (TUYỆT ĐỐI KHÔNG dùng mã LaTeX như \\frac, hãy viết phân số dạng (A)/(B) hoặc dùng ký tự thông thường).
                   - "options": Mảng gồm 4 phương án lựa chọn.
                   - "answer": Đáp án đúng.
                   - "explanation": Lời giải thích chi tiết.
                """
                res_text = generate_ai_response(prompt)
                
                if res_text:
                    try:
                        clean_text = res_text.replace("```json", "").replace("```", "").strip()
                        quiz_data = json.loads(clean_text)
                        
                        st.session_state["quiz_data"] = quiz_data
                        st.session_state["user_answers"] = {}
                        
                        title_quiz = quiz_topic[:40] + "..." if len(quiz_topic) > 40 else quiz_topic
                        db.collection("users").document(user_uid).collection("saved_quizzes").add({
                            "title": title_quiz,
                            "data": quiz_data,
                            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.toast("Đề thi đã được tự động lưu vào Kho dữ liệu!", icon="💾")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi xử lý đề thi từ AI: {e}")
                else:
                    st.error("⚠️ Hệ thống AI đang bận hoặc hết lượt dùng. Vui lòng thử lại sau!")

    if "quiz_data" in st.session_state and st.session_state["quiz_data"]:
        st.markdown("---")
        st.markdown("### 📋 Bài Làm Trắc Nghiệm")
        
        quiz_list = st.session_state["quiz_data"]
        user_answers = {}
        
        with st.form("quiz_form"):
            for i in range(len(quiz_list)):
                j = quiz_list[i]
                st.markdown(f"**Câu {i + 1}: {j['question']}**")
                user_answers[i] = st.radio(
                    f"Chọn đáp án cho câu {i + 1}:",
                    options=j["options"],
                    index=None,
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                st.write("")
            
            submit_quiz = st.form_submit_button("💯 Nộp bài & Chấm điểm", type="primary")
            
        if submit_quiz:
            score = 0
            st.markdown("---")
            st.markdown("### 📊 Kết Quả Bài Làm")
            
            for i in range(len(quiz_list)):
                j = quiz_list[i]
                selected = user_answers[i]
                correct = j["answer"]
                
                if selected == correct:
                    score += 1
                    st.success(f"✅ **Câu {i + 1}: Đúng!** (Bạn chọn: {selected})")
                else:
                    st.error(f"❌ **Câu {i + 1}: Sai!** (Bạn chọn: {selected} | Đáp án đúng: **{correct}**)")
                
                with st.expander(f"💡 Xem giải thích câu {i + 1}"):
                    st.write(j["explanation"])
            
            phantram = int((score / len(quiz_list)) * 100)
            st.markdown(f"**Tổng điểm của bạn:** {score}/{len(quiz_list)} câu ({phantram}%)")            
            if phantram >= 90:
                st.balloons()

#TAB 3 TOM TAWSWT VÀ HỎI ĐÁP
with tab3:
    st.header("📚 Tóm Tắt Tài Liệu & Hỏi Đáp Kiến Thức")
    st.caption("Tải lên bài học hoặc dán nội dung để AI giúp bạn tóm tắt và giải đáp mọi thắc mắc!")

    col_sum, col_qa = st.columns([1, 1], gap="large")
    
    # Cột 1: Tóm tắt
    with col_sum:
        st.subheader("📄 1. Tóm tắt tài liệu")
        
        input_type = st.radio("Nguồn tài liệu:", ["Dán văn bản", "Tải file"], horizontal=True)
        content_to_summarize = ""

        if input_type == "Dán văn bản":
            content_to_summarize = st.text_area("Nhập/Dán nội dung bài học:", height=150, placeholder="Dán đoạn văn bản...")
        else:
            uploaded_file = st.file_uploader("Tải file tài liệu:", type=["txt", "docx", "pdf", "xlsx"])
            if uploaded_file is not None:
                try:
                    content_to_summarize = uploaded_file.read().decode("utf-8")
                    st.success("✅ Đọc file thành công!")
                except Exception as e:
                    st.error("❌ Lỗi đọc file!")

        summary_style = st.multiselect(
            "Kiểu tóm tắt mong muốn:",
            options=[
                "📌 Các ý chính quan trọng (Bullet points)",
                "🧠 Sơ đồ tư duy dạng chữ (Mindmap Text)",
                "💡 Tóm tắt ngắn gọn + Từ khóa cốt lõi",
                "❓ Tóm tắt kèm 3 câu hỏi ôn tập",
                "✏️ Yêu cầu khác"
            ],
            default=["📌 Các ý chính quan trọng (Bullet points)"]
        )
        custom_request = ""
        if "✏️ Yêu cầu khác" in summary_style:
            custom_request = st.text_input(
                "Nhập yêu cầu riêng của bạn:",
                placeholder="Ví dụ: Tóm tắt dưới 200 từ, giải thích các từ khó, viết bằng tiếng Anh..."
            )
        if st.button("🚀 Tiến hành tóm tắt", type="primary", use_container_width=True):
            if not content_to_summarize.strip():
                st.warning("⚠️ Vui lòng dán văn bản hoặc tải file trước!")
            else:
                with st.spinner("🤖 AI đang đọc và tóm tắt tài liệu..."):
                    prompt = f"""
                    Bạn là một trợ lý học tập EduHub thông minh và chuyên nghiệp.
                    Nhiệm vụ của bạn là phân tích và tóm tắt nội dung tài liệu bên dưới theo ĐẦY ĐỦ các yêu cầu được chọn sau đây:
                    📌 Danh sách các kiểu tóm tắt được chọn:
                    {", ".join(summary_style)}
                    ✏️ Yêu cầu bổ sung riêng (nếu có):
                    {custom_request if custom_request else "Không có"}
                    YÊU CẦU TRÌNH BÀY KẾT QUẢ:
                    1. Phân chia rõ ràng từng kiểu tóm tắt đã chọn thành các mục riêng biệt bằng tiêu đề Markdown (`###`).
                    2. Trình bày súc tích, dễ hiểu, dùng gạch đầu dòng hoặc in đậm từ khóa quan trọng.
                    3. Đảm bảo thực hiện đầy đủ tất cả các kiểu tóm tắt được chọn, không bỏ sót mục nào.

                    NỘI DUNG TÀI LIỆU:
                    ---
                    {content_to_summarize}
                    ---
                    """
                    res_text = generate_ai_response(prompt)
                    
                    if res_text:
                        st.session_state["summary_result"] = res_text
                        st.session_state["doc_context"] = content_to_summarize
                        
                        title_sum = content_to_summarize[:30] + "..." if len(content_to_summarize) > 30 else "Bản tóm tắt"
                        db.collection("users").document(user_uid).collection("saved_summaries").add({
                            "title": title_sum,
                            "content": res_text,
                            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.toast("Bài tóm tắt đã được tự động lưu!", icon="💾")
                    else:
                        st.error("⚠️ Hệ thống AI đang bận hoặc hết lượt dùng. Vui lòng thử lại sau!")

        if "summary_result" in st.session_state:
            st.markdown("---")
            st.markdown("### 📝 Kết quả tóm tắt:")
            st.info(st.session_state["summary_result"])

    # Cột 2: Chatbot Hỏi đáp
    with col_qa:
        st.subheader("💬 2. Hỏi đáp bài học")
        
        if "qa_messages" not in st.session_state:
            st.session_state["qa_messages"] = []

        if st.session_state.get("doc_context"):
            st.success("💡 **Đã kết nối tài liệu:** AI sẽ ưu tiên trả lời dựa trên bài học bạn vừa tải ở cột bên trái.")
            if st.button("🧹 Xóa ngữ cảnh tài liệu"):
                st.session_state["doc_context"] = ""
                st.rerun()

        col_title, col_clear = st.columns([3, 1])
        with col_clear:
            if st.button("🗑️ Xóa chat"):
                st.session_state["qa_messages"] = []
                st.rerun()

        chat_container = st.container(height=350)
        with chat_container:
            if not st.session_state["qa_messages"]:
                st.write("👋 *Hãy đặt câu hỏi về bài học trên hoặc bất kỳ kiến thức nào bạn chưa hiểu!*")
            
            for msg in st.session_state["qa_messages"]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        if user_question := st.chat_input("Hỏi AI về bài học..."):
            st.session_state["qa_messages"].append({"role": "user", "content": user_question})
            
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_question)

                with st.chat_message("assistant"):
                    with st.spinner("🤖 AI đang suy nghĩ..."):
                        doc_ctx = st.session_state.get("doc_context", "")
                        
                        prompt = f"""
                        Bạn là trợ lý học tập EduHub AI.
                        Ngữ cảnh tài liệu: {doc_ctx if doc_ctx else 'Không có'}
                        Câu hỏi: {user_question}
                        """
                        answer = generate_ai_response(prompt)
                        
                        if answer:
                            st.write(answer)
                            st.session_state["qa_messages"].append({"role": "assistant", "content": answer})
                        else:
                            st.error("⚠️ Hệ thống AI đang bận hoặc hết lượt dùng. Vui lòng thử lại sau!")