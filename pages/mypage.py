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
    for k in list(st.session_state.keys()):
        if k.startswith('confirm_delete_'):
            del st.session_state[k]
    st.switch_page("main.py")
st.markdown("----")

st.markdown("### 👤내가 작성한 블랙리스트")

DATA_DIR = "/data/blacklist_data"

# 내 블랙리스트 불러오기
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
                                "title": item.get("title", "제목 없음"),
                                "customer_name": item.get("customer_name", ""),
                                "tags": item.get("tags", []),
                                "tags_str": "#" + ", #".join(item.get("tags", [])),
                                "consult_date": item.get("consult_date", ""),
                                "author": item.get("author", ""),
                                "file_name": file,
                                "folder": folder,
                                "status": item.get("status", "진행 중")
                            })
                            index += 1
                except:
                    pass
    return sorted(my_data, key=lambda x: x["consult_date"], reverse=True)

# 상태 배지
def render_status_badge(status):
    if status == "처리 완료":
        color = "#d4edda"
        border = "#28a745"
        emoji = "🟢"
    else:
        color = "#fff3cd"
        border = "#ffc107"
        emoji = "🟡"
    return f"""
    <div style='
        display:inline-block;
        background-color:{color};
        border:1px solid {border};
        color:#333;
        padding:5px 12px;
        border-radius:16px;
        font-size:14px;
        font-weight:bold;
        margin: 0 0 8px 0;
    '>{emoji} {status}</div>
    """

# 데이터 불러오기
my_blacklist = load_my_blacklist()

if not my_blacklist:
    st.info("작성한 블랙리스트가 없습니다.")
    st.stop()

for item in my_blacklist:
    label = f"**{item['customer_name']}** | **{item['title']}**"
    with st.expander(label, expanded=True):
        col1, col2, col3 = st.columns([6, 1, 1.5])
        with col1:
            st.markdown(
                f"<p style='font-size: 12px; color: #666; margin-top: 0px'>{item['tags_str']}</p>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<p style='font-size: 12px; color: #666; margin-top: -30px'>{item['consult_date']}</p>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<p style='font-size: 12px; color: #666; margin-top: -30px'>작성자: {item['author']}</p>",
                unsafe_allow_html=True
            )
        col1, col2, col3, col4 = st.columns([1, 2, 1, 2])
        with col1:
            st.markdown(render_status_badge(item.get("status", "진행 중")), unsafe_allow_html=True)
        with col2:
            st.markdown(
                "<p style='font-size: 12px; color: #666; margin-top: 10px'>👉 상세 내용을 보시려면 버튼을 클릭하세요.</p>",
                unsafe_allow_html=True
            )
        with col3:
            if st.button("상세 보기", key=f"view_{item['index']}", use_container_width=True):
                st.session_state["detail_file"] = item["file_name"]
                st.session_state["detail_folder"] = item["folder"]
                st.session_state["from_blacklist"] = True
                st.switch_page("pages/detail.py")
        with col4:
            col3a, col3b = st.columns(2)
            confirm_key = f"confirm_delete_{item['index']}"

            with col3a:
                if not st.session_state.get(confirm_key, False):
                    if st.button("삭제하기", key=f"delete_{item['index']}", use_container_width=True):
                        st.session_state[confirm_key] = True

            if st.session_state.get(confirm_key, False):
                st.markdown("---")
                st.warning(f"🗑️ **{item['customer_name']}** 항목을 정말 삭제하시겠습니까?")
                col_confirm1, col_confirm2 = st.columns([1, 1])
                with col_confirm1:
                    if st.button("✅ 예", key=f"confirm_yes_{item['index']}", use_container_width=True):
                        raw_path  = os.path.join(DATA_DIR, item["folder"], item["file_name"])
                        norm_path = os.path.normpath(raw_path)
                        file_path = os.path.abspath(norm_path)

                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                                del st.session_state[confirm_key]
                                st.success(f"{item['customer_name']} 항목이 삭제되었습니다.")
                                st.rerun()
                            except Exception as e:
                                st.error("❌ 삭제 중 오류 발생: " + str(e))
                        else:
                            st.error("❌ 해당 파일이 존재하지 않아 삭제할 수 없습니다.")
                with col_confirm2:
                    if st.button("❌ 아니요", key=f"confirm_no_{item['index']}", use_container_width=True):
                        del st.session_state[confirm_key]
                        st.rerun()

            with col3b:
                if st.button("수정하기", key=f"edit_{item['index']}", use_container_width=True):
                    st.session_state["edit_file"] = item["file_name"]
                    st.session_state["edit_folder"] = item["folder"]
                    st.switch_page("pages/edit.py")
