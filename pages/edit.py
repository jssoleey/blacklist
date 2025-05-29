import streamlit as st
import os
import json
from datetime import date

DATA_DIR = "/data/blacklist_data"

st.set_page_config(page_title="블랙리스트 관리", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("🔙 목록으로 돌아가기"):
    st.switch_page("blacklist.py")
st.markdown("----")

st.markdown("### ✏️ 블랙리스트 정보 수정")

# 파일 정보 확인
if "edit_file" not in st.session_state or "edit_folder" not in st.session_state:
    st.error("수정할 항목이 선택되지 않았습니다.")
    st.stop()

file_path = os.path.join(DATA_DIR, st.session_state["edit_folder"], st.session_state["edit_file"])
if not os.path.exists(file_path):
    st.error("해당 항목을 찾을 수 없습니다.")
    st.stop()

# 기존 데이터 로드
with open(file_path, "r", encoding="utf-8") as f:
    original = json.load(f)

# 전체 태그 모음 (기존 데이터에서 추출)
def get_all_tags():
    tags_set = set()
    for folder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for file in os.listdir(folder_path):
            if file.endswith(".json") and not file.endswith("_comments.json"):
                try:
                    with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                        item = json.load(f)
                        tags_set.update(item.get("tags", []))
                except:
                    continue
    return sorted(list(tags_set))

preset_tags = ["폭언", "욕설", "반복해지", "계약방해", "협박", "허위정보제공", "기타"]

# 입력 폼
with st.form("edit_form"):
    title = st.text_input("제목", value=original.get("title", ""))
    customer_name = st.text_input("고객명", value=original.get("customer_name", ""))
    consult_date = st.date_input("상담일자", value=date.fromisoformat(original.get("consult_date", str(date.today()))))
    customer_phone = st.text_input("고객 전화번호", value=original.get("customer_phone", ""))
    tags = st.multiselect("태그 선택", options=preset_tags, default=original.get("tags", []))
    consult_content = st.text_area("상세 내용", value=original.get("consult_content", "") or "", height=300)
    status = st.selectbox("진행 현황", ["진행 중", "처리 완료"], index=0 if original.get("status", "진행 중") == "진행 중" else 1)

    col1, col2, col3 = st.columns(3)
    
    with col2 :
        submitted = st.form_submit_button("저장하기", use_container_width=True)

if submitted:
    updated = {
        "title": title,
        "customer_name": customer_name,
        "consult_date": consult_date.isoformat(),
        "customer_phone": customer_phone,
        "tags": tags,
        "consult_content": consult_content,
        "status": status,
        "author": original.get("author", "")  # 작성자 정보는 그대로 유지
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    st.success("수정이 완료되었습니다!")
    st.session_state["refresh_blacklist"] = True  # ✅ 이 줄 추가
    st.switch_page("blacklist.py")
