import streamlit as st
import requests
import re
import textwrap
from collections import Counter

# --- 페이지 설정 ---
st.set_page_config(page_title="디지털 유령", layout="wide")
st.title("🌌 디지털 유령: 나의 AI 분신 챗봇과 대화하기")

# 간단한 소개
st.markdown("AI 분신 챗봇과 자연스럽게 대화해보세요. ")

# --- 기본값 함수 ---
def default_user_data():
    return {
        'my_name': '기본이',
        'partner_name': '상대방',
        'tone_str': "",
        'tone_summary': ""
    }

# --- 카톡 말투 추출 ---
def extract_user_lines(uploaded_file, speaker_name):
    text = uploaded_file.read().decode('utf-8')
    lines = []
    pattern = rf"\[{re.escape(speaker_name)}\] \[[^\]]+\] (.+)"
    for match in re.finditer(pattern, text):
        lines.append(match.group(1))
    return "\n".join(lines)

# --- REST 호출용 함수 ---
def generate_content(prompt: str):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("❗ ‘GOOGLE_API_KEY’가 설정되지 않았습니다. Secrets를 확인하세요.")
        return ""

    # API 키를 ?key= 로 붙입니다.
    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1beta2/models/chat-bison-001:generateMessage?key={api_key}"
    )
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
    }
    body = {
        "prompt": {"text": prompt},
        "temperature": 0.7,
        "candidateCount": 1,
    }

    try:
        res = requests.post(url, headers=headers, json=body, timeout=30)
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        st.error(f"❗ API 호출 오류 {res.status_code}\n{res.text}")
        return ""
    except requests.exceptions.RequestException as e:
        st.error(f"❗ 네트워크 오류: {e}")
        return ""

    return res.json()["candidates"][0]["message"]["content"]


# --- 세션 초기화 ---
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = default_user_data()
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'menu' not in st.session_state:
    st.session_state['menu'] = '홈'

# --- 사이드바 메뉴 스타일링 ---
st.markdown("""
    <style>
      [data-testid="stSidebar"] .stButton > button {
        background: none; border: none; padding: 0;
        color: #1f77b4; font-size: 1rem; text-align: left;
      }
      [data-testid="stSidebar"] .stButton > button:hover {
        text-decoration: underline;
      }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 메뉴")
    if st.button("🏠 홈"):
        st.session_state['menu'] = '홈'
    if st.button("✍ 입력"):
        st.session_state['menu'] = '입력'
    if st.button("💬 대화하기"):
        st.session_state['menu'] = '대화'

menu = st.session_state['menu']

# --- 홈 화면 ---
if menu == '홈':
    st.markdown("""
이 앱은 여러분이 준비한 카카오톡 대화 파일을 기반으로,  
AI 분신 챗봇과 자연스럽게 대화하도록 돕습니다.

**사용법**  
1. **카카오톡 대화 저장**  
   - 채팅방 우측 상단 **메뉴(≡)** → **대화내용** → **대화 내보내기** → **txt 파일** 저장  
   - 저장된 `.txt` 파일을 준비하세요.  

2. **프로그램 사용**  
   - ✍ ‘입력’ 메뉴에서 내 이름과 `.txt` 파일 업로드 후 저장  
   - 💬 ‘대화하기’ 메뉴에서 상대방 역할로 질문 입력 → 대화 시작  
   - AI 분신이 분석된 말투를 반영해 자연스럽게 응답합니다.
""")

# --- 데이터 입력 화면 ---
elif menu == '입력':
    data = st.session_state['user_data']
    with st.form("input_form"):
        my_name      = st.text_input("내 이름",      value=data['my_name'])
        partner_name = st.text_input("상대방 이름", value=data['partner_name'])
        kakao_file   = st.file_uploader("카톡 대화 파일 (.txt)", type="txt")
        submitted    = st.form_submit_button("저장")

    if submitted:
        tone_str     = ""
        tone_summary = ""
        if kakao_file and my_name:
            tone_str = extract_user_lines(kakao_file, my_name)
            prompt = f"""
다음은 '{my_name}' 사용자가 카카오톡에서 실제 쓴 짧은 대화입니다.
말투의 스타일적 특징(이모티콘 사용, 문장 마무리, 말끝 표현, 어투 등)을 요약해 주세요.

[대화 예시]
{textwrap.shorten(tone_str, width=2000)}

[요약]
"""
            tone_summary = generate_content(prompt)

        st.session_state['user_data'] = {
            'my_name': my_name,
            'partner_name': partner_name,
            'tone_str': tone_str,
            'tone_summary': tone_summary
        }
        st.success("✅ 데이터가 저장되었습니다. ‘대화하기’로 이동하세요.")

# --- 대화하기 화면 ---
elif menu == '대화':
    data         = st.session_state['user_data']
    my_name      = data['my_name']
    partner_name = data['partner_name']
    tone_summary = data.get('tone_summary', "")

    st.header(f"💬 {my_name}의 AI 분신과 {partner_name} 대화 중")
    partner_input = st.text_input(f"{partner_name}:")

    if partner_input:
        # 최근 대화 내역
        history = ""
        for spk, msg in st.session_state['chat_history'][-6:]:
            history += f"{spk}: {msg}\n"

        prompt = f"""
당신은 '{my_name}'입니다.
말투 분석: {tone_summary}

대화 히스토리:
{history}{partner_name}: {partner_input}

— 지시 사항 —
1) 친구에게 편하게 대화하듯 자연스럽고 구체적으로 답변하세요.
2) 말투 스타일은 분석 요약을 살짝 반영하되 과도하게 재현하지 마세요.
3) 질문 요지에 집중하고 필요 정보만 간결히 제공하세요.
4) 이모티콘은 사용하지 마세요.

{my_name}:"""

        reply = generate_content(prompt)
        # 혹시 남은 이모티콘 제거
        reply = re.sub(r'[^\w\s가-힣\.,\?!]', '', reply)

        st.session_state['chat_history'].append((partner_name, partner_input))
        st.session_state['chat_history'].append((my_name, reply))

    for spk, msg in st.session_state['chat_history']:
        st.markdown(f"**{spk}:** {msg}")
