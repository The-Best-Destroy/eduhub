import streamlit as st

if "user" not in st.session_state and "user_uid" in st.query_params:
    st.session_state["user"] = st.query_params["user_uid"]

if "user" in st.session_state:
    if st.query_params.get("user_uid") != st.session_state["user"]:
        st.query_params["user_uid"] = st.session_state["user"]

if "user" not in st.session_state:
    login_pg = st.Page("pages/login.py", title="Đăng nhập")
    register_pg = st.Page("pages/register.py", title="Đăng ký", icon="📝")
    
    pg = st.navigation([login_pg, register_pg])
    pg.run()
else:
    trang_chu = st.Page("trangchu.py", title="Trang Chủ", icon="🎓", default=True)
    quan_ly = st.Page("pages/quanlyhoctap.py", title="Quản Lý Học Tập", icon="📊")
    du_bao = st.Page("pages/dudoandiem.py", title="Dự Báo Phong Độ", icon="📈") 
    tro_choi = st.Page("pages/trochoi.py", title="Trò Chơi", icon="🎮")
    tro_ly = st.Page("pages/trolyhoctap.py", title="Trợ Lý Học Tập", icon="🤖")
    du_lieu = st.Page("pages/dulieu.py", title="Dữ Liệu", icon="📁")
    cai_dat = st.Page("pages/taikhoan.py", title="Tài khoản", icon="⚙️")
    dang_xuat = st.Page("pages/dangxuat.py", title="Đăng xuất", icon="🚪")
    pages = {
        "Tài khoản của bạn": [cai_dat, dang_xuat],
        "Hệ Thống EduHub": [trang_chu, quan_ly, du_bao, tro_ly, tro_choi, du_lieu]
    }
    pg = st.navigation(pages)

    st.markdown("""
        <style>
            div[data-testid="stSidebarNavItems"] ul:nth-of-type(2) li:last-child {
                display: none !important;
            }
            
            div[data-testid="stSidebarUserContent"] {
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            div[data-testid="stSidebarNav"] {
                flex-grow: 1;
            }
            
            .chatgpt-upgrade-box {
                padding: 14px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                margin-bottom: 6px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            }
            .upgrade-title { font-weight: bold; color: #343a40; font-size: 0.9rem; display: block; margin-bottom: 4px; }
            .upgrade-desc { margin: 0; font-size: 0.78rem; color: #6c757d; line-height: 1.3; }
        </style>
    """, unsafe_allow_html=True)
    


    pg.run()