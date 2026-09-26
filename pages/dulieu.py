import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

st.set_page_config(page_title="Kho dữ liệu", page_icon="📁", layout="wide")

if not firebase_admin._apps:
    cred = credentials.Certificate("data/key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

if "user" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập từ trang chủ trước!")
    st.stop()

user_uid = st.session_state["user"]

st.title("📁 Kho Dữ Liệu & Lịch Sử Học Tập")
st.caption("Nơi quản lý tập trung toàn bộ đề thi, bản tóm tắt, thời gian biểu và dự báo phong độ.")

tab_quiz, tab_summary, tab_tgb= st.tabs([
    "📝 Đề Thi Trắc Nghiệm", 
    "📚 Bài Tóm Tắt", 
    "🗓️ Thời Gian Biểu"
])

#TAB1: LUU DE THI
with tab_quiz:
    st.subheader("📝 Lịch sử đề thi trắc nghiệm đã lưu")
    
    quizzes_ref = db.collection("users").document(user_uid).collection("saved_quizzes").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    quiz_docs = [(doc.id, doc.to_dict()) for doc in quizzes_ref]

    if not quiz_docs:
        st.info("Chưa có đề thi nào được tạo và lưu.")
    else:
        for doc_id, q_data in quiz_docs:
            with st.expander(f"📌 {q_data.get('title', 'Đề thi')} — 🕒 {q_data.get('created_at', '')}"):
                col_info, col_btn = st.columns([5, 1])
                with col_btn:
                    if st.button("🗑️ Xóa đề", key=f"del_q_{doc_id}"):
                        db.collection("users").document(user_uid).collection("saved_quizzes").document(doc_id).delete()
                        st.success("Đã xóa đề thi!")
                        st.rerun()

                st.markdown("---")
                for idx, item in enumerate(q_data.get("data", [])):
                    st.write(f"**Câu {idx + 1}: {item['question']}**")
                    for opt in item["options"]:
                        st.write(f"- {opt}")
                    st.success(f"👉 **Đáp án đúng:** {item['answer']}")
                    st.caption(f"💡 Giải thích: {item['explanation']}")
                    st.markdown("---")

#TAB 2:TOM TAT TAI LEIU
with tab_summary:
    st.subheader("📚 Lịch sử bài tóm tắt tài liệu")
    
    sums_ref = db.collection("users").document(user_uid).collection("saved_summaries").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    sum_docs = [(doc.id, doc.to_dict()) for doc in sums_ref]

    if not sum_docs:
        st.info("Chưa có bản tóm tắt nào được tạo.")
    else:
        for doc_id, s_data in sum_docs:
            with st.expander(f"📌 {s_data.get('title', 'Bài tóm tắt')} — 🕒 {s_data.get('created_at', '')}"):
                col_info, col_btn = st.columns([5, 1])
                with col_btn:
                    if st.button("🗑️ Xóa bài", key=f"del_s_{doc_id}"):
                        db.collection("users").document(user_uid).collection("saved_summaries").document(doc_id).delete()
                        st.success("Đã xóa bản tóm tắt!")
                        st.rerun()

                st.markdown("---")
                st.markdown(s_data.get("content", ""))

#TAB 3:TGB
with tab_tgb:
    st.subheader("🗓️ Lịch sử Thời gian biểu")
    
    tkb_ref = db.collection("users").document(user_uid).collection("lich_su_tkb").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    tkb_docs = [(doc.id, doc.to_dict()) for doc in tkb_ref]

    if not tkb_docs:
        st.info("💡 Chưa có thời gian biểu nào được lưu.")
    else:
        for doc_id, t_data in tkb_docs:
            with st.expander(f"📌 Thời gian biểu lưu lúc — 🕒 {t_data.get('created_at', 'Không rõ')}"):
                col1, col2 = st.columns([5, 1])
                with col2:
                    if st.button("🗑️ Xóa thời gian biểu", key=f"del_tkb_{doc_id}"):
                        db.collection("users").document(user_uid).collection("lich_su_tkb").document(doc_id).delete()
                        st.success("Đã xóa!")
                        st.rerun()
                
                df_tgb = pd.DataFrame(t_data.get("tasks", []))
                if not df_tgb.empty:
                    st.dataframe(df_tgb, hide_index=True, use_container_width=True)
