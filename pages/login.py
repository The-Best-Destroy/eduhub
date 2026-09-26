import streamlit as st
from firebase_auth import auth

st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

if "success_msg" in st.session_state:
    st.toast(st.session_state["success_msg"], icon="✅")
    del st.session_state["success_msg"]

col1, login, col3 = st.columns([1, 2, 1])
with login:
    st.title("🔐 Đăng nhập")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)

    if submit_btn:
        if not email or not password:
            st.warning("⚠️ Vui lòng nhập đầy đủ email và mật khẩu!")
        else:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state["user"] = user["localId"]
                st.query_params["user_uid"] = user["localId"]
                st.session_state["success_msg"] = "Đăng nhập thành công"
                st.rerun()
            except Exception as e:
                st.error("❌ Sai email hoặc mật khẩu! Vui lòng thử lại.")

    st.markdown("---")
    
    col_forgot, col_reg = st.columns(2)
    
    with col_forgot:
        with st.popover("🔑 Quên mật khẩu?", use_container_width=True):
            st.write("### 🔑 Khôi phục mật khẩu")
            reset_email = st.text_input("Nhập Email tài khoản:", value=email)
            if st.button("Khôi phục mật khấu", type="primary", use_container_width=True):
                if not reset_email:
                    st.warning("Vui lòng nhập Email!")
                else:
                    try:
                        auth.send_password_reset_email(reset_email)
                        st.success(f"Đã gửi liên kết khôi phục tới **{reset_email}**. Hãy kiểm tra hộp thư!")
                    except Exception as e:
                        st.error("❌ Email không tồn tại trên hệ thống hoặc có lỗi xảy ra!")

    with col_reg:
        if st.button("📝 Đăng ký ngay", use_container_width=True):
            st.switch_page("pages/register.py")
