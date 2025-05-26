import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="블랙리스트 관리", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("🔙 목록으로 돌아가기"):
    st.switch_page("pages/blacklist.py")
    
st.markdown("")
st.markdown("")
st.markdown("### 👤내가 작성한 블랙리스트")

if "user_name" not in st.session_state or "user_folder" not in st.session_state:
    st.warning("로그인 정보가 없습니다. 메인 페이지로 돌아가 로그인해 주세요.")
    if st.button("🔐 로그인 페이지로 이동"):
        st.switch_page("main.py")
    st.stop()

DATA_DIR = "/data/blacklist_data"

# 블랙리스트 불러오기 함수
def load_my_blacklist():
    my_data = []
    index = 1
    for folder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for file in os.listdir(folder_path):
            if file.endswith(".json") and not file.endswith("_comments.json"):
                try:
                    with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                        item = json.load(f)
                        if item.get("author") == st.session_state["user_name"]:
                            my_data.append({
                                "index": index,
                                "customer_name": item.get("customer_name", ""),
                                "tags": ", ".join(item.get("tags", [])),
                                "consult_date": item.get("consult_date", ""),
                                "author": item.get("author", ""),
                                "file_name": file,
                                "folder": folder
                            })
                            index += 1
                except:
                    pass
    return sorted(my_data, key=lambda x: x["consult_date"], reverse=True)

my_blacklist = load_my_blacklist()

if not my_blacklist:
    st.info("작성한 블랙리스트가 없습니다.")
    st.stop()

for item in my_blacklist:
    with st.expander(f"{item['index']}. {item['customer_name']} | {item['tags']} | {item['consult_date']}"):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write("👉 상세 내용을 보시려면 아래 버튼을 클릭하세요.")
        with col2:
            if st.button("상세 보기", key=f"view_{item['index']}"):
                st.session_state["detail_file"] = item["file_name"]
                st.session_state["detail_folder"] = item["folder"]
                st.switch_page("pages/detail.py")
        # 삭제는 작성자 본인이므로 항상 가능
        if st.button("삭제", key=f"delete_{item['index']}"):
            file_path = os.path.join(DATA_DIR, item["folder"], item["file_name"])
            try:
                os.remove(file_path)
                st.success(f"{item['customer_name']} 항목이 삭제되었습니다.")
                st.rerun()
            except Exception as e:
                st.error("삭제 중 오류 발생: " + str(e))
