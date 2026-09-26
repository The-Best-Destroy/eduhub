import streamlit as st
import pandas as pd
import time
import json
import datetime
from docx import Document
from google import genai
import firebase_admin
from firebase_admin import credentials, firestore

@st.cache_resource
def get_firestore_db():
    if not firebase_admin._apps:
        key_dict = dict(st.secrets["firebase"])
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = get_firestore_db()
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
THU_TU_COT = ["Môn Học", "Điểm Thi", "Mục Tiêu", "Thời Gian Học", "Mức Độ Hiểu Bài", "Ghi Chú"]
st.set_page_config(
    page_title="Quản lý học tập", 
    page_icon="🧑‍🎓", 
    layout="wide"
)

if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("⚠️ Vui lòng đăng nhập từ trang chủ trước!")
    st.stop()

user_uid = st.session_state["user"]

st.title("📊 Quản Lý Học Tập")
st.subheader("📝 Bảng theo dõi môn học")
doc = db.collection("quanlyhoctap").document(user_uid).get()
if doc.exists:
    df = pd.DataFrame(doc.to_dict().get("subjects", []))
    df = df.reindex(columns=THU_TU_COT) 
else:
    df = pd.DataFrame(columns=THU_TU_COT)
mon_hoc = ["Toán", "Ngữ văn", "Tiếng Anh", "Vật lí", "Hóa học", "Sinh học", "Lịch sử & Địa lí", "Tin học", "GDCD","Lập trình", "Môn học khác..."]
quanly = {
    "Môn Học": st.column_config.SelectboxColumn(
        "Môn Học", 
        options=mon_hoc,
        required=True
    ),
    "Điểm Thi": st.column_config.NumberColumn(
        "Điểm Thi", 
        min_value=0.0, 
        max_value=10.0, 
        step=0.1
    ),
    "Mục Tiêu": st.column_config.NumberColumn(
        "Mục Tiêu", 
        min_value=0.0, 
        max_value=10.0, 
        step=0.1
    ),
    "Thời Gian Học": st.column_config.NumberColumn(
        "Thời Gian Học (giờ/ngày)", 
        min_value=0.0, 
        max_value=24.0, 
        step=0.5,
        required=True
    ),
    "Mức Độ Hiểu Bài": st.column_config.SelectboxColumn(
        "Mức Độ Hiểu Bài", 
        options=["👑 Chuyên gia","🟢Thành thạo", "🔵 Biết vận dụng", "🟡 Hiểu cơ bản", "🟠 Đang làm quen", "🔴 Mất gốc"]
    ),
    "Ghi Chú": st.column_config.TextColumn(
        "Ghi Chú"
    )
}
with st.popover("📝 Nhập thông tin bổ sung"):
    lop = st.selectbox("Bạn đang học lớp:", ["Lớp 6","Lớp 7","Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    muc_tieu = st.text_area("Mục tiêu của bạn: ")

editdf = st.data_editor(
    df,
    column_config=quanly, 
    num_rows="dynamic", 
    use_container_width=True
)

btnsave, btnsubmit= st.columns(2)
with btnsave:
    if st.button("💾 Lưu thay đổi"):
        with st.spinner():
            thu_tu_cot = ["Môn Học", "Điểm Thi", "Mục Tiêu", "Thời Gian Học", "Mức Độ Hiểu Bài", "Ghi Chú"]
            du_lieu = editdf[thu_tu_cot].to_dict(orient="records")
            db.collection("quanlyhoctap").document(user_uid).set({
                "subjects": du_lieu
            })
            time.sleep(1)
        # st.toast("Đã lưu dữ liệu thành công!", icon="✅")
        st.badge("Đã lưu dữ liệu thành công!", icon=":material/check:", color="green")
        time.sleep(0.8)
        st.rerun()
with btnsubmit:
    if st.button("🗓️Submit"):
        if editdf.dropna().empty:
            st.warning("Hãy nhập ít nhất 1 môn học")
        else:
            with st.spinner("Đang tạo thời gian biểu cho bạn..."):
                du_lieu_hoc_tap=editdf.to_markdown()
                prompt = f"""
Bạn là một cố vấn học tập AI chuyên xây dựng thời gian biểu cá nhân cho học sinh.

THÔNG TIN HỌC SINH:
- Lớp: {lop}
  → Điều chỉnh độ khó và khối lượng kiến thức phù hợp với học sinh {lop}.
- Mục tiêu: {muc_tieu}
  → Ưu tiên phân bổ nhiều thời gian hơn cho các môn liên quan đến mục tiêu này.

DỮ LIỆU HỌC TẬP:
{du_lieu_hoc_tap}

Nhiệm vụ:
Hãy phân tích toàn bộ dữ liệu học tập và tạo một thời gian biểu học tập trong tuần.

Khi lập kế hoạch phải dựa trên:
- Lớp học
- Mục tiêu của học sinh
- Điểm hiện tại
- Điểm mục tiêu
- Thời gian học hiện tại
- Mức độ hiểu bài
- Ghi chú của từng môn

Nguyên tắc:
- Không chia đều thời gian cho tất cả các môn.
- Môn yếu hoặc còn cách xa mục tiêu phải được ưu tiên nhiều hơn.
- Môn đã thành thạo vẫn cần ôn nhưng thời lượng ít hơn.
- Điều chỉnh thời lượng nếu học sinh đang học chưa hợp lý.
- Mỗi ngày học từ 2–4 môn.
- Một môn có thể xuất hiện nhiều ngày nếu cần ưu tiên.
- Không học một môn quá nhiều lần trong cùng một ngày.
- Tổng thời gian học mỗi ngày nên hợp lý (khoảng 5–9 giờ).
- Nếu ghi chú có nội dung cần cải thiện thì đưa vào "Nhiệm Vụ".
- Nếu ghi chú trống, hãy tự đề xuất nội dung học phù hợp với môn học, trình độ lớp {lop} và mục tiêu của học sinh.

YÊU CẦU BẮT BUỘC:
1. CHỈ trả về một mảng JSON hợp lệ.
2. KHÔNG giải thích.
3. KHÔNG dùng Markdown.
4. KHÔNG thêm bất kỳ văn bản nào ngoài JSON.
5. Mỗi object PHẢI có đúng 4 key sau:
   - "Thứ"
   - "Môn Học"
   - "Thời Gian Học"
   - "Nhiệm Vụ"
6. Giá trị "Thời Gian Học" là thời lượng của môn học (ví dụ: "1 giờ 30 phút", "45 phút", "2 giờ"), KHÔNG phải khung giờ.
7. Mảng JSON phải bao gồm đầy đủ lịch học cho cả tuần nếu cần.

Ví dụ:

[
  {{
    "Thứ": "Thứ 2",
    "Môn Học": "Toán",
    "Thời Gian Học": "2 giờ",
    "Nhiệm Vụ": "Ôn đại số và luyện bài tập phương trình"
  }},
  {{
    "Thứ": "Thứ 2",
    "Môn Học": "Tiếng Anh",
    "Thời Gian Học": "1 giờ 15 phút",
    "Nhiệm Vụ": "Luyện Reading và ôn từ vựng"
  }}
]
Kết quả phải là JSON có thể parse trực tiếp bằng json.loads(), không chứa ```json hoặc bất kỳ ký tự nào ngoài JSON.
"""
                res_text = generate_ai_response(prompt) # Gọi hàm tự thử từng Key ở đầu file

                if res_text:
                    clean_text = res_text.replace("```json", "").replace("```", "").strip()
                    try:
                        tkb_list = json.loads(clean_text)
                        st.session_state["ketqua_ai"] = tkb_list
                        st.rerun()
                    except Exception:
                        st.error("Lỗi xử lý dữ liệu từ AI, vui lòng thử lại!")
                else:
                    st.error("⚠️ Hệ thống AI đang bận hoặc hết lượt dùng. Vui lòng thử lại sau!")

st.markdown("---")
st.subheader("🗓️ Thời gian biểu")
TGB_COLS = ["Thứ", "Môn Học", "Thời Gian Học", "Nhiệm Vụ", "Hoàn thành"]
tgb_data = None
if "ketqua_ai" in st.session_state:
    tgb_data = st.session_state["ketqua_ai"]
else:
    tgb_doc = db.collection("thoigianbieu").document(user_uid).get()
    if tgb_doc.exists:
        tgb_data = tgb_doc.to_dict().get("tasks", [])

if tgb_data:
    tgb = pd.DataFrame(tgb_data)
    tgb = tgb.reindex(columns=TGB_COLS)
    tgb["Hoàn thành"] = tgb["Hoàn thành"].fillna(False)
        
    edit_tgb = st.data_editor(
        tgb,
        hide_index=True,
        column_config={
            "Hoàn thành": st.column_config.CheckboxColumn("Hoàn thành", default=False),
            "Thời Gian Học": st.column_config.TextColumn("Thời Gian Học"),
            "Môn Học": st.column_config.TextColumn("Môn Học"),
            "Nhiệm Vụ": st.column_config.TextColumn("Nhiệm Vụ")
        },
        use_container_width=True
    )
    
    if st.button("💾 Lưu thời gian biểu"):
        data_to_save = edit_tgb[TGB_COLS].to_dict(orient="records")
        db.collection("thoigianbieu").document(user_uid).set({
            "tasks": data_to_save
        })
        now_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        db.collection("users").document(user_uid).collection("lich_su_tkb").add({
            "tasks": data_to_save,
            "created_at": now_str
        })
        
        st.success("Đã lưu thời gian biểu thành công!")
    #tải về
    csv = edit_tgb.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Tải thời gian biểu",
        data=csv,
        file_name="thoi_gian_bieu.csv",
        mime="text/csv",
        icon=":material/download:"
    )
