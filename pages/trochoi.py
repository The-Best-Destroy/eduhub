import streamlit as st
from google import genai
import random
st.set_page_config(page_title="Góc Giải Trí", page_icon="🎮", layout="centered")
API_KEYS = st.secrets.get("API_KEYS", [])
def generate_ai_response(prompt_content):
    if not API_KEYS:
        st.error("⚠️ Chưa cấu hình API_KEYS!")
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
st.title("🎮 Góc Giải Trí & Xả Stress")
st.caption("Thư giãn một chút sau những giờ làm bài tập căng thẳng.")

tab_noitu, tab_caro = st.tabs(["🔤 Nối từ Tiếng Việt", "⭕❌ Cờ Caro (XO)"])

# TAB 1:NOI TUWF
with tab_noitu:
    st.subheader("Đấu trí Nối từ với AI")
    st.markdown("**Luật chơi:** Từ tiếp theo bắt đầu bằng tiếng cuối cùng của từ trước. (VD: **Thức thời** ➔ **Thời gian** ➔ **Gian nan**)")
    def reset_noitu_game():
        if random.random() < 0.51:
            st.session_state["chat_noitu"] = [
                {"role": "assistant", "content": "Hãy nhập một từ ghép có 2 âm tiết"}
            ]
        else:
            starter_words = ["Thức thời", "Thời gian", "Học tập", "Tương lai", "Thành công", 
                "Rực rỡ", "Mặt trời", "Bầu trời", "Bình minh", "Cố gắng",
                "Công nghệ", "Phát triển", "Sáng tạo", "Năng lượng", "Động lực",
                "Tâm trí", "Ý thức", "Năng lực", "Hành động", "Phong phú",
                "Tươi đẹp", "Triển vọng", "Cơ hội", "Kinh nghiệm", "Kiến thức",
                "Lực lượng", "Bình an", "Minh mẫn", "Tập trung", "Phương pháp","Cái Bàn"]
            first_word = random.choice(starter_words)
            last_syllable = first_word.split()[-1]
            st.session_state["chat_noitu"] = [
                {"role": "assistant", "content": f"Từ của mình là: **{first_word}**.\n\n👉 Đến lượt bạn! Hãy nhập từ bắt đầu bằng tiếng **'{last_syllable}'**."}
            ]

    if st.button("🔄 Chơi lại từ đầu", key="reset_noitu", type="primary"):
        reset_noitu_game()
        st.rerun()

    if "chat_noitu" not in st.session_state:
        reset_noitu_game()
        
    chat_container = st.container(height=400)
    
    with chat_container:
        for msg in st.session_state["chat_noitu"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    if prompt := st.chat_input("Nhập từ của bạn..."):
        st.session_state["chat_noitu"].append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("AI đang tìm từ..."):
                    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state["chat_noitu"]])
                    
                    sys_prompt = f"""
                    Bạn là một chuyên gia ngôn ngữ tiếng Việt và là cao thủ chơi Nối từ.
                    Lịch sử hội thoại hiện tại:
                    {history_text}

                    Luật chơi BẮT BUỘC:
                    1. Trả lời bằng MỘT từ ghép có đúng 2 âm tiết, CÓ NGHĨA THỰC TẾ trong từ điển tiếng Việt.
                    2. Từ của bạn phải bắt đầu bằng âm tiết cuối cùng của từ người chơi vừa nhập.
                    3. XỬ LÝ LỖI NGƯỜI DÙNG: Nếu người chơi gõ không dấu, sai chính tả (ví dụ: 'cai ban', 'ban tay'), bạn phải TỰ ĐỘNG HIỂU ra từ đúng ('cái bàn', 'bàn tay') và lấy âm tiết cuối của từ chuẩn đó để nối tiếp.
                    4. Nếu từ của người dùng hoàn toàn vô nghĩa, hãy trả lời: "Từ này lạ quá, bạn đổi từ khác đi!"
                    5. TRƯỜNG HỢP BÍ TỪ: Nếu bạn KHÔNG THỂ tìm ra bất kỳ từ nào có nghĩa trong từ điển tiếng Việt để nối tiếp, BẠN BẮT BUỘC PHẢI NHẬN THUA bằng cách trả lời ĐÚNG CÂU SAU: "Mình chịu thua! Bạn giỏi quá, chúc mừng bạn đã chiến thắng! 🎉"
                    6. CHỈ IN RA TỪ CỦA BẠN (hoặc câu báo lỗi/nhận thua). Không giải thích thêm.
                    
                    Từ người chơi vừa nhập: {prompt}
                    """
                    
                    response_text = generate_ai_response(sys_prompt)
                    
                    if response_text:
                        response_text = response_text.replace(".", "").replace('"', '').strip()
                        st.write(response_text)
                        st.session_state["chat_noitu"].append({"role": "assistant", "content": response_text})
                        
                        if "chịu thua" in response_text.lower() or "chiến thắng" in response_text.lower():
                            st.balloons()
                            st.success("🏆 XUẤT SẮC! BẠN ĐÃ ĐÁNH BẠI TRÍ TUỆ NHÂN TẠO!")
                    else:
                        st.error("Lỗi kết nối AI. Bạn thử lại nhé!")

        st.rerun()
#TAB2 XO
with tab_caro:
    st.subheader("Cờ Caro 3x3 (Đấu 2 người)")
    st.markdown("""
        <style>
        div.stButton > button {
            height: 100px;
            font-size: 40px !important;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if "board" not in st.session_state:
        st.session_state.board = [["" for _ in range(3)] for _ in range(3)]
        st.session_state.turn = "❌"
        st.session_state.winner = None

    def check_winner(board):
        for i in range(3):
            #ngangdoc
            if board[i][0] == board[i][1] == board[i][2] != "": return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != "": return board[0][i]
        #chéo
        if board[0][0] == board[1][1] == board[2][2] != "": return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != "": return board[0][2]
        # Hòa
        if all(board[r][c] != "" for r in range(3) for c in range(3)): return "Hòa"
        return None

    # Hàm xử lý khi bấm vào ô cờ
    def handle_click(r, c):
        if st.session_state.board[r][c] == "" and st.session_state.winner is None:
            st.session_state.board[r][c] = st.session_state.turn
            st.session_state.winner = check_winner(st.session_state.board)
            if st.session_state.winner is None:
                st.session_state.turn = "⭕" if st.session_state.turn == "❌" else "❌"

    if st.session_state.winner:
        if st.session_state.winner == "Hòa":
            st.info("🤝 Trận đấu kết thúc với kết quả Hòa!")
        else:
            st.success(f"🎉 Chiến thắng thuộc về: **{st.session_state.winner}**")
    else:
        st.write(f"👉 Đến lượt: **{st.session_state.turn}**")

    for r in range(3):
        cols = st.columns([1, 1, 1, 3])
        for c in range(3):
            with cols[c]:
                label = st.session_state.board[r][c] if st.session_state.board[r][c] != "" else "‎ "
                if st.button(label, key=f"btn_{r}_{c}", use_container_width=True):
                    handle_click(r, c)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Chơi ván mới", key="reset_caro", type="primary"):
        st.session_state.board = [["" for _ in range(3)] for _ in range(3)]
        st.session_state.turn = "❌"
        st.session_state.winner = None
        st.rerun()