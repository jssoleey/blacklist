# main.py
import streamlit as st
import os
st.set_page_config(page_title="블랙리스트 관리", layout="wide", initial_sidebar_state="collapsed")
st.write("현재 작업 디렉토리:", os.getcwd())
st.switch_page("blacklist.py")
