import streamlit as st
from firebase_auth import auth
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

st.set_page_config(page_title="Đăng ký")
st.title("Đăng ký")
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)
if not firebase_admin._apps:
    cred = credentials.Certificate("data/key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

with st.form("register_form"):
    name = st.text_input("Họ tên *")
    email = st.text_input("Email *")
    password = st.text_input("Mật khẩu *", type="password", help="Mật khẩu phải có ít nhất 6 ký tự")
    password2 = st.text_input("Nhập lại mật khẩu *", type="password")

    st.markdown("---")
    gender = st.selectbox("Giới tính (không bắt buộc)", ["Không chọn", "Nam", "Nữ", "Khác"])

    dob = st.date_input(
        "Ngày sinh (không bắt buộc)",
        min_value=datetime.date(1990, 1, 1),
        max_value=datetime.date.today()
    )
    submit_btn = st.form_submit_button("Đăng ký", type="primary")
if submit_btn:
    if not name or not email or not password or not password2:
        st.warning("⚠️ Vui lòng nhập đầy đủ thông tin bắt buộc")
    elif "@" not in email:
        st.warning("⚠️ Email không hợp lệ!")
    elif password != password2:
        st.warning("⚠️ Mật khẩu nhập lại không khớp!")
    else:
        with st.spinner("Đang tạo tài khoản..."):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                uid = user["localId"]
                db.collection("users").document(uid).set({
                    "name": name,
                    "email": email,
                    "gender": gender if gender != "Không chọn" else None,
                    "dob": dob.isoformat(),
                    "lop": "Chưa cập nhật",
                    "truong": "Chưa cập nhật",
                    "dia_chi": "Chưa cập nhật"
                })
                st.session_state["user"] = uid
                st.session_state["success_msg"] = "Đăng ký thành công! Chào mừng bạn đến với EduHub 🎉"
                st.rerun()

            except Exception as e:
                error_msg = str(e).upper()
                if "EMAIL_EXISTS" in error_msg:
                    st.error("❌ Email này đã được đăng ký! Vui lòng dùng email khác hoặc chuyển sang Đăng nhập.")
                elif "WEAK_PASSWORD" in error_msg:
                    st.error("❌ Mật khẩu quá yếu! Mật khẩu phải có ít nhất 6 ký tự.")
                elif "INVALID_EMAIL" in error_msg:
                    st.error("❌ Định dạng email không hợp lệ!")
                else:
                    st.error("❌ Đã xảy ra lỗi, vui lòng thử lại sau!")

st.markdown("---")
st.write("Bạn đã có tài khoản?")
if st.button("🚪 Đăng nhập ngay", use_container_width=True):
    st.switch_page("pages/login.py")