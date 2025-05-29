import streamlit as st
import os
import json
from datetime import date
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from login import login

# 상수: 데이터 저장 경로
DATA_DIR = "/data/blacklist_data"

# 블랙리스트 데이터 로드 함수
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
                            "title": item.get("title", "제목 없음"),
                            "customer_name": item.get("customer_name", ""),
                            "tags": item.get("tags", []),
                            "tags_str": "#"+", #".join(item.get("tags", [])),
                            "consult_date": item.get("consult_date", ""),
                            "author": item.get("author", ""),
                            "file_name": file,
                            "folder": folder,
                            "status": item.get("status", "진행 중")
                        })
                        index += 1
                except:
                    pass
    return sorted(data, key=lambda x: x["consult_date"], reverse=True)

# 페이지 설정
st.set_page_config(page_title="블랙리스트 관리", layout="wide")

##### 디버깅
import os

# 현재 작업 디렉토리 확인
cwd = os.getcwd()
st.write("📂 현재 작업 디렉토리:", cwd)

# pages 디렉토리 내 파일 구조 확인
pages_dir = os.path.join(cwd, "pages")
if os.path.exists(pages_dir):
    st.write("📄 pages 폴더 내 파일 목록:")
    for root, dirs, files in os.walk(pages_dir):
        for file in files:
            st.write(" -", os.path.relpath(os.path.join(root, file), pages_dir))
else:
    st.error("❌ pages 디렉토리를 찾을 수 없습니다.")
#####

keys_to_clear = [k for k in st.session_state.keys() if k.startswith("confirm_delete_")]
for k in keys_to_clear:
    del st.session_state[k]

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        background-color: #dfe5ed;  /* 원하는 색상 코드 */
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 📋 블랙리스트 목록")
st.markdown("---")

# 블랙리스트 전체 로드
data = load_blacklist()

# ---------------------- 사이드바 구성 ----------------------
today = date.today().strftime("%Y년 %m월 %d일")
st.sidebar.markdown("")
st.sidebar.markdown(
    f"<span style='font-size:18px;'>📅 <b>{today}</b></span>",
    unsafe_allow_html=True
)

if "user_name" not in st.session_state:
    # 로그인 UI
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 로그인")
    input_name = st.sidebar.text_input("이름", key="login_name")
    input_pw = st.sidebar.text_input("비밀번호", type="password", key="login_pw")
    if st.sidebar.button("로그인", use_container_width=True):
        if not input_name or not input_pw:
            st.sidebar.warning("이름과 비밀번호를 입력해주세요.")
        else:
            user_dir = login(input_name, input_pw)
            st.session_state["user_name"] = input_name
            st.session_state["user_folder"] = user_dir
            st.success("✅ 로그인 성공!")
            st.rerun()

    st.sidebar.markdown("---")

    # 🔍 검색 / 필터 옵션
    st.sidebar.markdown("### 🔍 검색")
    name_options = list({item["customer_name"] for item in data})
    author_options = list({item["author"] for item in data})
    tag_options = sorted({tag for item in data for tag in item["tags"]})

    search_name = st.sidebar.text_input("고객명 검색")
    search_author = st.sidebar.text_input("작성자 검색")
    search_tags = st.sidebar.multiselect("태그 선택", options=tag_options)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("➕ 블랙리스트 추가하기", use_container_width=True):
        st.sidebar.warning("로그인 후 이용해주세요.")

else:
    # 로그인 된 상태
    st.sidebar.title(f"😊 {st.session_state['user_name']}님, 반갑습니다!")
    st.sidebar.markdown("---")

    # 🔍 검색 / 필터 옵션
    st.sidebar.markdown("### 🔍 검색")
    name_options = list({item["customer_name"] for item in data})
    author_options = list({item["author"] for item in data})
    tag_options = sorted({tag for item in data for tag in item["tags"]})

    search_name = st.sidebar.text_input("고객명 검색")
    search_author = st.sidebar.text_input("작성자 검색")
    search_tags = st.sidebar.multiselect("태그 선택", options=tag_options)

    st.sidebar.markdown("---")
    if st.sidebar.button("➕ 블랙리스트 추가하기", use_container_width=True):
        st.switch_page("add")

    if st.sidebar.button("📂 마이페이지", use_container_width=True):
        st.session_state["my_author"] = st.session_state["user_name"]
        st.switch_page("mypage")

    if st.sidebar.button("🔓 로그아웃", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ---------------------- 필터링 처리 ----------------------
filtered_blacklist = [item for item in data if
    (search_name.lower() in item["customer_name"].lower()) and
    (search_author.lower() in item["author"].lower()) and
    (all(tag in item["tags"] for tag in search_tags))
]

if search_name and all(search_name.lower() not in name.lower() for name in name_options):
    st.sidebar.warning("해당 고객명을 찾을 수 없습니다.")
if search_author and all(search_author.lower() not in author.lower() for author in author_options):
    st.sidebar.warning("해당 작성자를 찾을 수 없습니다.")

# ---------------------- 목록 출력 ----------------------
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
    
if "visible_count" not in st.session_state:
    st.session_state.visible_count = 10

visible_blacklist = filtered_blacklist[:st.session_state.visible_count]

for item in visible_blacklist: 
    label = f"**{item['customer_name']}** | **{item['title']}**" 
    with st.expander(label, expanded=True):
        col1, col2, col3 = st.columns([6, 1, 1.5])
        with col1 :
            st.markdown(
                f"<p style='font-size: 12px; color: #666; margin-top: 0px'>{item['tags_str']}</p>",
                unsafe_allow_html=True
            )
        with col2 :
            st.markdown(
                f"<p style='font-size: 12px; color: #666; margin-top: -30px'>{item['consult_date']}</p>",
                unsafe_allow_html=True
            )
        with col3 :
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
                st.switch_page("detail")

        confirm_key = f"confirm_delete_{item['index']}"  # 밖에서 정의

        with col4:
            if "user_name" in st.session_state and item["author"] == st.session_state["user_name"]:
                col3a, col3b = st.columns(2)
                with col3a:
                    if not st.session_state.get(confirm_key, False):
                        if st.button("삭제하기", key=f"delete_{item['index']}", use_container_width=True):
                            st.session_state[confirm_key] = True
                with col3b:
                    if st.button("수정하기", key=f"edit_{item['index']}", use_container_width=True):
                        st.session_state["edit_file"] = item["file_name"]
                        st.session_state["edit_folder"] = item["folder"]
                        st.switch_page("edit")

        # ✅ 삭제 확인 영역은 열 외부 (columns 영향 받지 않음)
        if st.session_state.get(confirm_key, False):
            st.markdown("<br>", unsafe_allow_html=True)  # 간격 조절용
            st.markdown("---")
            st.warning(f"🗑️ **{item['customer_name']}** 항목을 정말 삭제하시겠습니까?")
            col_confirm1, col_confirm2 = st.columns([1, 1])
            with col_confirm1:
                if st.button("✅ 예", key=f"confirm_yes_{item['index']}", use_container_width=True):
                    file_path = os.path.join(DATA_DIR, item["folder"], item["file_name"])
                    try:
                        os.remove(file_path)
                        st.success(f"{item['customer_name']} 항목이 삭제되었습니다.")
                        del st.session_state[confirm_key]
                        st.rerun()
                    except Exception as e:
                        st.error("삭제 중 오류 발생: " + str(e))
            with col_confirm2:
                if st.button("❌ 아니오", key=f"confirm_no_{item['index']}", use_container_width=True):
                    st.session_state[confirm_key] = False
                    st.rerun()

if st.session_state.visible_count < len(filtered_blacklist):
    if st.button("더보기"):
        st.session_state.visible_count += 10
