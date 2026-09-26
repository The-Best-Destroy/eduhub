import streamlit as st
import pandas as pd
import json
from google import genai
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("data/key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

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
st.set_page_config(page_title="Dự báo phong độ", page_icon="📈", layout="wide")

if "user" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập từ trang chủ trước!")
    st.stop()
user_uid = st.session_state["user"]

st.title("📈 Dự Báo Phong Độ Học Tập")
st.subheader("Dùng AI phân tích tiềm năng và đề xuất nhiệm vụ")

# 2. Lấy dữ liệu học tập từ Firestore
doc = db.collection("quanlyhoctap").document(user_uid).get()
if not doc.exists:
    st.info("Chưa có dữ liệu học tập. Hãy nhập thông tin ở trang 'Quản Lý Học Tập' trước nhé!")
    st.stop()

df = pd.DataFrame(doc.to_dict().get("subjects", []))

with st.expander("📊 Xem dữ liệu học tập hiện tại của bạn"):
    st.dataframe(df, use_container_width=True)

# 3. Nút phân tích
if st.button("🚀 Dự báo phong độ & Lên kế hoạch", type="primary"):
    if df.empty:
        st.warning("Bảng dữ liệu của bạn đang trống, không thể phân tích!")
    else:
        with st.spinner("AI đang phân tích dữ liệu và tạo nhiệm vụ..."):
            prompt = f"""
                Bạn là chuyên gia phân tích dữ liệu giáo dục. Hãy dựa trên dữ liệu điểm số, thời gian học và mục tiêu của học sinh dưới đây để đưa ra dự báo và nhiệm vụ cụ thể.
                
                Dữ liệu:
                {df.to_markdown()}
                
                YÊU CẦU BẮT BUỘC:
                1. CHỈ trả về một mảng JSON hợp lệ. KHÔNG có bất kỳ văn bản nào khác, KHÔNG dùng markdown ```json.
                2. Mỗi phần tử là 1 object có đúng 3 key: "Môn Học", "Điểm Dự Báo", "Nhiệm Vụ Cải Thiện".
                3. "Nhiệm Vụ Cải Thiện" phải là hành động cực kỳ cụ thể (ví dụ: "Luyện 3 đề trắc nghiệm", "Ôn lại công thức tính diện tích").
                
                Ví dụ kết quả mong muốn:
                [
                  {{"Môn Học": "Toán", "Điểm Dự Báo": "8.5", "Nhiệm Vụ Cải Thiện": "Làm thêm 5 bài tập hình học chứng minh tam giác đồng dạng"}},
                  {{"Môn Học": "Tiếng Anh", "Điểm Dự Báo": "7.0", "Nhiệm Vụ Cải Thiện": "Học thuộc 20 từ vựng chủ đề môi trường và làm 2 bài đọc hiểu"}}
                ]
                """
                
            res_text = generate_ai_response(prompt)
            
            if res_text:
                try:
                    clean_text = res_text.replace("```json", "").replace("```", "").strip()
                    result_json = json.loads(clean_text)
                    
                    db.collection("dudoandiem").document(user_uid).set({
                        "tasks": result_json
                    })
                    
                    st.session_state["ketqua_dubao"] = result_json
                    st.rerun()
                except Exception:
                    st.error("Lỗi xử lý dữ liệu từ AI, vui lòng thử lại!")
            else:
                st.error("⚠️ Hệ thống AI đang bận hoặc hết lượt dùng. Vui lòng thử lại sau!")
st.markdown("---")
st.subheader("🎯 Bảng nhiệm vụ & Dự báo")

dubao_data = None
if "ketqua_dubao" in st.session_state:
    dubao_data = st.session_state["ketqua_dubao"]
else:
    doc_dubao = db.collection("dudoandiem").document(user_uid).get()
    if doc_dubao.exists:
        dubao_data = doc_dubao.to_dict().get("tasks", [])

if dubao_data:
    df_dubao = pd.DataFrame(dubao_data)
    
    COLS = ["Môn Học", "Điểm Dự Báo", "Nhiệm Vụ Cải Thiện"]
    df_dubao = df_dubao.reindex(columns=COLS)
    
    edit_df = st.data_editor(
        df_dubao,
        hide_index=True,
        column_config={
            "Môn Học": st.column_config.TextColumn("Môn Học", disabled=True),
            "Điểm Dự Báo": st.column_config.TextColumn("Điểm Dự Báo (Dự kiến)", disabled=True),
            "Nhiệm Vụ Cải Thiện": st.column_config.TextColumn("Nhiệm Vụ Cải Thiện")
        },
        use_container_width=True
    )
    
    if st.button("💾 Lưu bảng dự báo"):
        with st.spinner("Đang lưu..."):
            data_to_save = edit_df.to_dict(orient="records")
            db.collection("dudoandiem").document(user_uid).set({
                "tasks": data_to_save
            })  
        st.success("Đã lưu bảng dự báo thành công!")
else:
    st.info("Chưa có dự báo nào. Bấm nút phía trên để AI bắt đầu phân tích nhé!")