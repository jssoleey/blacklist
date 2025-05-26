import streamlit as st
import os
import json
from datetime import datetime
from llm import generate_advice

st.set_page_config(page_title="블랙리스트 관리", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# 로그인 확인
if "user_name" not in st.session_state or "user_folder" not in st.session_state:
    st.warning("로그인 정보가 없습니다. 메인 페이지에서 로그인해 주세요.")
    st.stop()

# 세션에서 선택된 파일 정보 가져오기
file_name = st.session_state.get("detail_file")
author_folder = st.session_state.get("detail_folder")

if not file_name or not author_folder:
    st.error("상세보기 항목이 선택되지 않았습니다.")
    st.stop()

# 파일 경로
DATA_DIR = "/data/blacklist_data"
file_path = os.path.join(DATA_DIR, author_folder, file_name)

if not os.path.exists(file_path):
    st.error("해당 블랙리스트 파일을 찾을 수 없습니다.")
    st.stop()

# 데이터 로드
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 수정 모드 여부
editable = (data.get("author") == st.session_state["user_name"])

if st.button("🔙 목록으로 돌아가기"):
    st.switch_page("pages/blacklist.py")

st.markdown("")
st.markdown("")
    
info_html = f"""
    <div style="background-color:#f0f8ff; padding:15px; border:1px solid #ddd; border-radius:8px; margin-bottom:20px; line-height:2.0;">
        <h5>📄 고객 정보</h5>
        <ul>
            <li><b>고객명:</b> {data.get('customer_name', '')}</li>
            <li><b>전화번호:</b> {data.get('customer_phone', '')}</li>
            <li><b>상담일자:</b> {data.get('consult_date', '')}</li>
            <li><b>상담원:</b> {data.get('author', '')}</li>
            <li><b>태그:</b> {', '.join(data.get('tags', []))}</li>
"""
st.markdown(info_html, unsafe_allow_html=True)

# 상세 내용 출력 또는 수정

st.markdown("")
st.markdown("###### 📌 내용")

if editable:
    updated_content = st.text_area("상담 내용 수정", value=data.get("consult_content", ""), height=200)
    if st.button("💾 수정 내용 저장"):
        data["consult_content"] = updated_content
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success("상담 내용이 수정되었습니다.")
else:
    st.write(data.get("consult_content", ""))

st.markdown("----")
st.markdown("##### 🤖 AI 조언 생성하기")

if st.button("AI 조언 생성하기"):
    with st.spinner("AI가 상황을 분석하고 조언을 생성 중입니다..."):
        advice = generate_advice(
            customer_name=data.get("customer_name", ""),
            tags=data.get("tags", []),
            consult_content=data.get("consult_content", ""),
            author=data.get("author", "")
        )
        st.session_state["generated_advice"] = advice  # 조언을 세션에 저장
    st.success("✅ AI 조언이 생성되었습니다.")
    
if "generated_advice" in st.session_state:
    st.markdown(st.session_state["generated_advice"])

# 댓글 기능
st.markdown("----")

# 댓글 파일 경로
comment_path = file_path.replace(".json", "_comments.json")

if os.path.exists(comment_path):
    with open(comment_path, "r", encoding="utf-8") as f:
        comments = json.load(f)
else:
    comments = []

# 댓글 입력
new_comment = st.text_area("댓글 작성", key="comment_input", placeholder="댓글을 남겨보세요.")

if st.button("✏️ 댓글 저장"):
    comments.append({
        "작성자": st.session_state["user_name"],
        "내용": new_comment,
        "일자": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(comment_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    st.success("댓글이 저장되었습니다.")
    st.rerun()

# 댓글 표시 및 삭제 기능
if comments:
    st.markdown("")
    updated_comments = []
    for i, c in enumerate(reversed(comments)):
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f"**{c['작성자']}** ({c['일자']})  \n{c['내용']}")
        with col2:
            if c["작성자"] == st.session_state["user_name"]:
                if st.button("🗑 삭제", key=f"delete_comment_{i}"):
                    original_index = len(comments) - 1 - i  # 역순으로 표시되었기 때문에 실제 인덱스 보정
                    del comments[original_index]
                    with open(comment_path, "w", encoding="utf-8") as f:
                        json.dump(comments, f, ensure_ascii=False, indent=2)
                    st.success("댓글이 삭제되었습니다.")
                    st.rerun()

