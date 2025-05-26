import streamlit as st
import os
import json
import hashlib

# 상수: 데이터 저장 경로
BASE_DIR = "/data/blacklist_data"
os.makedirs(BASE_DIR, exist_ok=True)

# Streamlit 페이지 설정
st.set_page_config(page_title="블랙리스트 관리", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 블랙리스트 통합관리")
st.markdown("#### 🔐 Login")

# 1. 로그인 입력
name = st.text_input("이름", key="name_input")
password = st.text_input("비밀번호", type="password", key="password_input")

# 2. 해시 함수 (단순 해싱으로 비밀번호 보관)
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# 3. 로그인 함수
def login(name, password):
    user_dir = os.path.join(BASE_DIR, f"{name}_{hash_password(password)}")
    os.makedirs(user_dir, exist_ok=True)

    # 사용자 인덱스 파일에 저장
    index_file = os.path.join(BASE_DIR, "index.json")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {}

    # 사용자 등록 (이미 등록돼 있으면 생략)
    key = f"{name}_{password[-4:]}"  # 비밀번호 뒷자리로 구분
    if key not in index:
        index[key] = os.path.basename(user_dir)
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    return user_dir

# 4. 로그인 처리
col1, col2, col3 = st.columns(3)

with col2 :
    st.markdown("")
    if st.button("로그인", use_container_width=True):
        if not name or not password:
            st.warning("이름과 비밀번호를 모두 입력해주세요.")
        else:
            user_dir = login(name, password)
            st.session_state["user_name"] = name
            st.session_state["user_folder"] = user_dir
            st.success("✅ 로그인 성공! 잠시만 기다려주세요...")
            st.switch_page("pages/blacklist.py")
