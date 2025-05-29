import streamlit as st
import os
import json
from datetime import datetime
from llm import generate_title

st.set_page_config(page_title="블랙리스트 관리", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("🔙 목록으로 돌아가기"):
    st.switch_page("main.py")
st.markdown("----")

st.markdown("### ➕ 블랙리스트 고객 등록")

# 고정 태그 목록
preset_tags = ["폭언", "욕설", "반복해지", "계약방해", "협박", "허위정보제공", "기타"]

# 입력 폼
with st.form("blacklist_form"):
    consult_date = st.date_input("상담일자", value=datetime.today())
    customer_name = st.text_input("고객 이름")
    customer_phone = st.text_input("고객 전화번호", placeholder="숫자만 입력")

    selected_tags = st.multiselect("블랙리스트 사유 태그", options=preset_tags)
    # 진행 현황 선택
    status = st.radio("진행 현황", ["진행 중", "처리 완료"], horizontal=True)
    consult_content = st.text_area("상담 내용", height=200)
    
    col1, col2, col3 = st.columns(3)
    with col2 :
        submitted = st.form_submit_button("📌 등록하기", use_container_width=True)

# 저장 처리
if submitted:
    if not customer_name or not customer_phone or not consult_content:
        st.warning("고객 이름, 전화번호, 상담 내용을 모두 입력해주세요.")
    else:
        # 제목 생성
        title = generate_title(
            customer_name=customer_name,
            tags=selected_tags,
            consult_content=consult_content
        )
        record = {
            "title": title,
            "consult_date": consult_date.strftime("%Y-%m-%d"),
            "author": st.session_state["user_name"],
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "tags": selected_tags,
            "consult_content": consult_content,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status
        }

        user_dir = st.session_state["user_folder"]
        os.makedirs(user_dir, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_name}.json"
        filepath = os.path.join(user_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        st.success("✅ 블랙리스트가 성공적으로 등록되었습니다.")
        st.switch_page("main.py")
