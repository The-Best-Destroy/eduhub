import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_auth import auth
import datetime

if not firebase_admin._apps:
    cred = credentials.Certificate("data/key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title="Tài khoản", page_icon="👤")

if "user" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập!")
    st.stop()

user_uid = st.session_state["user"]
doc_ref = db.collection("users").document(user_uid)
doc = doc_ref.get()

if doc.exists:
    info = doc.to_dict()
    user_email = info.get("email", "")
    
    st.title("👤 Thông tin tài khoản")
    
    avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={user_uid}"
    
    col_avt, col_info = st.columns([1, 3])
    with col_avt:
        st.image(avatar_url, width=120)
    with col_info:
        st.subheader(info.get("name", "Người dùng"))
        st.write(f"📧 {user_email}")

    st.markdown("---")
    
    fields = [
        ("Họ tên", "name", info.get("name", "")),
        ("Giới tính", "gender", info.get("gender", "Không chọn")),
        ("Ngày sinh", "dob", info.get("dob", "")),
        ("Lớp", "lop", info.get("lop", "")),
        ("Trường", "truong", info.get("truong", "")),
        ("Địa chỉ", "dia_chi", info.get("dia_chi", ""))
    ]

    for label, key, current_val in fields:
        row = st.columns([2, 3, 1])
        row[0].write(f"**{label}:**")
        row[1].write(current_val if current_val else "Chưa cập nhật")
        
        with row[2].popover("✏️ Sửa"):
            with st.form(f"form_{key}"):
                st.write(f"Chỉnh sửa {label}")
                if key == "gender":
                    new_val = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"], 
                                           index=["Nam", "Nữ", "Khác"].index(current_val) if current_val in ["Nam", "Nữ", "Khác"] else 0)
                elif key == "dob":
                    try:
                        date_val = datetime.datetime.strptime(current_val, "%Y-%m-%d").date()
                    except:
                        date_val = datetime.date.today()
                    new_val = str(st.date_input("Ngày sinh", value=date_val))
                else:
                    new_val = st.text_input(f"Nhập {label}", value=current_val)
                
                if st.form_submit_button("Lưu"):
                    doc_ref.update({key: new_val})
                    st.success("Đã cập nhật!")
                    st.rerun()

    st.markdown("---")
    with st.expander("🔐 Đổi mật khẩu"):
        with st.form("change_password_form"):
            old_pass = st.text_input("Mật khẩu hiện tại", type="password")
            new_pass = st.text_input("Mật khẩu mới", type="password", help="Mật khẩu phải có ít nhất 6 ký tự")
            confirm_pass = st.text_input("Xác nhận mật khẩu mới", type="password")
            
            submit_change = st.form_submit_button("Đổi mật khẩu", type="primary", use_container_width=True)

        if submit_change:
            if not old_pass or not new_pass or not confirm_pass:
                st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")
            elif new_pass != confirm_pass:
                st.error("❌ Mật khẩu mới và xác nhận mật khẩu không trùng khớp!")
            elif len(new_pass) < 6:
                st.error("❌ Mật khẩu mới phải có ít nhất 6 ký tự!")
            else:
                try:
                    user_session = auth.sign_in_with_email_and_password(user_email, old_pass)
                    
                    if hasattr(auth, "update_password"):
                        auth.update_password(user_session["idToken"], new_pass)
                    elif hasattr(auth, "change_password"):
                        auth.change_password(user_session["idToken"], new_pass)
                        
                    st.success("🎉 Đổi mật khẩu thành công!")
                except Exception as e:
                    st.error("❌ Mật khẩu hiện tại không đúng. Vui lòng kiểm tra lại!")

else:
    st.error("Không tìm thấy thông tin tài khoản!")