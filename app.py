import streamlit as st
import requests
import re
import textwrap

# --- 페이지 설정 ---
st.set_page_config(page_title="디지털 유령", layout="wide")
st.title("🌌 디지털 유령: 나의 AI 분신 챗봇과 대화하기")

# --- 기본값 함수 ---
def default_user_data():
    return {
        'my_name': '기본이',
        'partner_name': '상대방',
        'tone_str': "",
        'tone_summary': ""
    }

# --- 카톡 말투 추출 함수 ---
def extract_user_lines(uploaded_file, speaker_name):
    text = uploaded_file.read().decode('utf-8')
    pattern = rf"\[{re.escape(speaker_name)}\] \[[^\]]+\] (.+)"
    return "\n".join(m.group(1) for m in re.finditer(pattern, text))

# --- Gemini REST 호출 함수 ---
def generate_content(prompt: str) -> str:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("❗ GOOGLE_API_KEY가 설정되지 않았습니다. Secrets에서 키를 추가하세요.")
        return ""

    model_id = "gemini-2.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1/models/{model_id}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    body = {
        "prompt": {"text": prompt},
        "temperature": 0.7,
        "candidateCount": 1
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=60)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        st.error("❗ 요청이 너무 오래 걸립니다. 잠시 후 다시 시도해 주세요.")
        return ""
    except requests.exceptions.HTTPError as http_err:
        status = http_err.response.status_code if http_err.response else 'Unknown'
        error_msg = http_err.response.text if http_err.response and http_err.response.text else str(http_err)
        st.error("❗ API 호출 오류 {}
{}".format(status, error_msg))
