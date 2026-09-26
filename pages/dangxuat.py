import streamlit as st
@st.dialog("🚪 Xác nhận đăng xuất", width="small")
def logout():
    st.write("Bạn có chắc chắn muốn đăng xuất khỏi hệ thống **EduHub** không?")
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Hủy", use_container_width=True):
            st.switch_page("trangchu.py")
            
    with col2:
        if st.button("🚪 Đăng xuất", type="primary", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

logout()

st.caption("Hộp thoại xác nhận đang được hiển thị...")
if st.button("⬅️ Quay lại Trang Chủ"):
    st.switch_page("trangchu.py")