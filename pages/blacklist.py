import streamlit as st
import os
import json
from datetime import date

st.set_page_config(page_title="블랙리스트 관리", layout="wide")
st.markdown("### 📋 블랙리스트 목록")

# 사이드바 네비게이션 메뉴 숨기기
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

if "user_name" not in st.session_state or "user_folder" not in st.session_state:
    st.warning("로그인 정보가 없습니다. 메인 페이지로 돌아가 로그인해 주세요.")
    st.stop()

DATA_DIR = "blacklist_data"

# 블랙리스트 불러오기 함수
def load_blacklist():
    data = []
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
                        data.append({
                            "index": index,
                            "customer_name": item.get("customer_name", ""),
                            "tags": item.get("tags", []),
                            "tags_str": ", ".join(item.get("tags", [])),
                            "consult_date": item.get("consult_date", ""),
                            "author": item.get("author", ""),
                            "file_name": file,
                            "folder": folder
                        })
                        index += 1
                except:
                    pass
    return sorted(data, key=lambda x: x["consult_date"], reverse=True)

blacklist = load_blacklist()

if not blacklist:
    st.info("등록된 블랙리스트가 없습니다.")
    st.stop()
    
# 사이드바 상단 인사 및 날짜
today = date.today().strftime("%Y년 %m월 %d일")
st.sidebar.markdown("")
st.sidebar.markdown(
    f"<span style='font-size:18px;'>📅 <b>{today}</b></span>",
    unsafe_allow_html=True
)
st.sidebar.title(f"😊 {st.session_state['user_name']}님, 반갑습니다!")
st.sidebar.markdown("---")

# 🔎 검색 / 필터 옵션
st.sidebar.header("🔍 필터")

name_options = list({item["customer_name"] for item in blacklist})
author_options = list({item["author"] for item in blacklist})
tag_options = sorted({tag for item in blacklist for tag in item["tags"]})

search_name = st.sidebar.text_input("고객명 검색")
search_author = st.sidebar.text_input("작성자 검색")
search_tags = st.sidebar.multiselect("태그 선택", options=tag_options)

# 필터링
filtered_blacklist = [item for item in blacklist if
    (search_name.lower() in item["customer_name"].lower()) and
    (search_author.lower() in item["author"].lower()) and
    (all(tag in item["tags"] for tag in search_tags))
]

# 예외 처리
if search_name and all(search_name.lower() not in name.lower() for name in name_options):
    st.sidebar.warning("해당 고객명을 찾을 수 없습니다.")
if search_author and all(search_author.lower() not in author.lower() for author in author_options):
    st.sidebar.warning("해당 작성자를 찾을 수 없습니다.")

st.sidebar.markdown("---")

# 마이페이지 버튼
if st.sidebar.button("📂 마이페이지", use_container_width=True):
    st.session_state["my_author"] = st.session_state["user_name"]
    st.switch_page("pages/mypage.py")

# 블랙리스트 추가 버튼 → 사이드바로 이동
if st.sidebar.button("➕ 블랙리스트 추가하기", use_container_width=True):
    st.switch_page("pages/add.py")

# 보여줄 개수 설정
if "visible_count" not in st.session_state:
    st.session_state.visible_count = 10

visible_blacklist = filtered_blacklist[:st.session_state.visible_count]

for item in visible_blacklist:
    with st.expander(f"{item['index']}. {item['customer_name']} | {item['tags_str']} | {item['consult_date']} | 작성자: {item['author']}"):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(
                "<p style='font-size: 13px; color: #666;'>👉 상세 내용을 보시려면 아래 버튼을 클릭하세요.</p>",
                unsafe_allow_html=True
            )
        with col2:
            if st.button("상세 보기", key=f"view_{item['index']}"):
                st.session_state["detail_file"] = item["file_name"]
                st.session_state["detail_folder"] = item["folder"]
                st.switch_page("pages/detail.py")
        with col3:
            if item["author"] == st.session_state["user_name"]:
                if st.button("삭제", key=f"delete_{item['index']}"):
                    file_path = os.path.join(DATA_DIR, item["folder"], item["file_name"])
                    try:
                        os.remove(file_path)
                        st.success(f"{item['customer_name']} 항목이 삭제되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error("삭제 중 오류 발생: " + str(e))

# 더보기 버튼
if st.session_state.visible_count < len(filtered_blacklist):
    if st.button("더보기"):
        st.session_state.visible_count += 10
