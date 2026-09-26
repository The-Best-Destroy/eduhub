import streamlit as st

st.set_page_config(
    page_title="EduHub AI Assitant", 
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 EduHub - Hệ Thống Trợ Lý Học Tập Toàn Diện")
st.markdown("---")

st.markdown("""
Chào mừng bạn đến với **EduHub AI Assitant**! Đây là ứng dụng thông minh được thiết kế để giúp bạn quản lý điểm số, dự báo phong độ thi cử và ôn luyện kiến thức hiệu quả bằng cách kết hợp **Dữ liệu (Pandas)**, **Machine Learning** và **Trí tuệ nhân tạo**.

### 🧭 Các phân hệ chức năng:
* **📊 Quản lý Học tập:** Nơi bạn nhập điểm số giữa kỳ, số giờ tự học và số bài tập đã làm để tạo cơ sở dữ liệu.
* **📈 Dự báo Phong độ:** Sử dụng mô hình Machine Learning để đoán trước điểm số cuối kỳ.
* **🤖 Trợ lý Học tập:** Nơi bạn nạp tài liệu ôn tập để Gemini AI tóm tắt hoặc tự động tạo đề thi trắc nghiệm.
* **🎮 Trò chơi:** Góc giải trí rèn luyện tư duy gồm đấu Nối từ Tiếng Việt với AI và Cờ Caro 3x3 đối kháng 2 người.
""")

st.info("💡 Mẹo nhỏ: Hãy bấm vào các mục ở thanh menu bên trái để khám phá từng chức năng nhé!")

with st.expander("📖 Bấm vào đây để xem Hướng Dẫn Sử Dụng", expanded=True):
    st.image("HDSD/hdsd.png", caption="Cách sử dụng hệ thống EduHub", use_container_width=True)