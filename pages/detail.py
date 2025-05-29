import streamlit as st
import os
import json
from datetime import datetime, timedelta, timezone
from llm import generate_advice

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
        margin-top:6px;
    '>{emoji} {status}</div>
    """

st.set_page_config(page_title="블랙리스트 관리", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# 세션에서 선택된 파일 정보 가져오기
file_name = st.session_state.get("detail_file")
author_folder = st.session_state.get("detail_folder")
if not file_name or not author_folder:
    st.error("상세보기 항목이 선택되지 않았습니다.")
    st.stop()

# 파일 로드 이후, 세션 기반 조언 초기화 여부 확인
advice_key = f"advice_{author_folder}_{file_name}"

# 목록에서 진입한 경우에만 초기화
if st.session_state.get("from_blacklist", False):
    if advice_key in st.session_state:
        del st.session_state[advice_key]
    st.session_state["from_blacklist"] = False  # 초기화 후 플래그 리셋

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

editable = (
    "user_name" in st.session_state and
    data.get("author") == st.session_state["user_name"]
)

if st.button("🔙 목록으로 돌아가기"):
    st.switch_page("blacklist.py")
st.markdown("----")

status = data.get("status", "진행 중")  # 기본값: 진행 중

# 작성자 본인은 상태 전환 가능
if editable :
    new_status = "처리 완료" if status == "진행 중" else "진행 중"
    if st.button(f"🔁 '{new_status}' 상태로 변경"):
        data["status"] = new_status
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success(f"진행 현황이 '{new_status}'로 변경되었습니다.")
        st.rerun()
        
st.markdown(render_status_badge(status), unsafe_allow_html=True)

info_html = f"""
    <div style="background-color:#f0f8ff; padding:15px; border:1px solid #ddd; border-radius:8px; margin-top: 10px; margin-bottom:20px; line-height:2.0;">
        <h5>📄 고객 정보</h5>
        <ul>
            <li><b>고객명:</b> {data.get('customer_name', '')}</li>
            <li><b>전화번호:</b> {data.get('customer_phone', '')}</li>
            <li><b>상담일자:</b> {data.get('consult_date', '')}</li>
            <li><b>상담원:</b> {data.get('author', '')}</li>
            <li><b>태그:</b> {', '.join(data.get('tags', []))}</li>
        </ul>
        <h5>📌 내용</h5>
        <ul>
            <li>{data.get("consult_content", "")}</li>
        </ul>
    </div>
"""
st.markdown(info_html, unsafe_allow_html=True)

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
        st.session_state[advice_key] = advice

if advice_key in st.session_state:
    st.markdown(st.session_state[advice_key])

st.markdown("----")

# 댓글 기능
comment_path = file_path.replace(".json", "_comments.json")

def load_comments(comment_path):
    if os.path.exists(comment_path):
        with open(comment_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

comments = load_comments(comment_path)

# 댓글 입력
if "user_name" in st.session_state:
    new_comment = st.text_area("댓글 작성", key="comment_input", placeholder="댓글을 남겨보세요.")

    if st.button("✏️ 댓글 저장"):
        if new_comment.strip() == "":
            st.warning("댓글 내용을 입력해주세요.")
        else:
            KST = timezone(timedelta(hours=9))
            comments.append({
                "작성자": st.session_state["user_name"],
                "내용": new_comment.strip(),
                "일자": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
            })
            with open(comment_path, "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)

            st.success("댓글이 저장되었습니다.")
            st.rerun()

else:
    st.text_area("댓글 작성", key="comment_input_disabled", placeholder="로그인 후 이용해주세요.", disabled=True)

# 댓글 표시 및 삭제 기능
if comments:
    st.markdown("")
    for i, c in enumerate(reversed(comments)):
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f"**{c['작성자']}** ({c['일자']})  \n{c['내용']}")
        with col2:
            if "user_name" in st.session_state and c["작성자"] == st.session_state["user_name"]:
                if st.button("🗑 삭제", key=f"delete_comment_{i}"):
                    original_index = len(comments) - 1 - i
                    del comments[original_index]
                    with open(comment_path, "w", encoding="utf-8") as f:
                        json.dump(comments, f, ensure_ascii=False, indent=2)
                    st.success("댓글이 삭제되었습니다.")
                    st.rerun()
