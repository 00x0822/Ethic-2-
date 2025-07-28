import streamlit as st
import google.generativeai as genai
import re
import textwrap
from collections import Counter

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

# --- 카톡 말투 추출 ---
def extract_user_lines(uploaded_file, speaker_name):
    text = uploaded_file.read().decode('utf-8')
    lines = []
    pattern = rf"\[{re.escape(speaker_name)}\] \[[^\]]+\] (.+)"
    for match in re.finditer(pattern, text):
        lines.append(match.group(1))
    return "\n".join(lines)

# --- 세션 초기화 ---
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = default_user_data()
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'menu' not in st.session_state:
    st.session_state['menu'] = '홈'

# --- Gemini API 설정 (2.5 Flash 사용) ---
model = None
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        raise KeyError("GOOGLE_API_KEY not found in secrets.toml")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
except Exception as e:
    st.error(f"❗ API/모델 설정 오류: {e}")

# --- 사이드바 메뉴 스타일링 (텍스트 링크처럼) ---
st.markdown("""
    <style>
      [data-testid="stSidebar"] .stButton > button {
        background: none;
        border: none;
        padding: 0;
        color: #1f77b4;
        font-size: 1rem;
        text-align: left;
      }
      [data-testid="stSidebar"] .stButton > button:hover {
        text-decoration: underline;
      }
    </style>
""", unsafe_allow_html=True)

# --- 사이드바 메뉴 버튼 (세로 배치) ---
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
AI 분신 챗봇과 자연스럽게 대화하며 디지털 유산과 윤리적 주제를 탐구하도록 돕습니다.

**사용법**
1. **카카오톡 대화 파일 저장 방법**  
   - 대화 상대와의 채팅방 **우측 상단 메뉴(≡)** → **대화내용** → **대화 내보내기** → **txt 파일 형태로 저장**  
   - 저장된 `.txt` 파일을 준비하세요.

2. **프로그램 사용 방법**  
   - ✍ `입력` 메뉴 클릭 후 내 이름과 준비한 대화 `.txt` 파일을 업로드하여 **저장**  
   - 💬 `대화하기` 메뉴 클릭 후 상대방 역할로 질문을 입력하여 **대화 시작**  
   - AI 분신이 여러분의 말투를 반영해 응답합니다.
""")

# --- 데이터 입력 화면 ---
elif menu == '입력':
    data = st.session_state['user_data']
    with st.form("input_form"):
        my_name = st.text_input("내 이름", value=data['my_name'])
        partner_name = st.text_input("상대방 이름", value=data['partner_name'])
        kakao_file = st.file_uploader("카톡 대화 파일 (.txt)", type="txt")
        submitted = st.form_submit_button("저장")

    if submitted:
        tone_str = ""
        tone_summary = ""
        if kakao_file and my_name and model:
            tone_str = extract_user_lines(kakao_file, my_name)
            tone_analysis_prompt = f"""
아래는 '{my_name}' 사용자의 카카오톡 대화 일부입니다. 이 사용자의 **말투 스타일 특징**을 요약해 주세요.
- 이모티콘 사용여부
- 문장 마무리 스타일
- 자주 사용하는 말끝 표현
- 어투(친근함, 장난기 등)
- 반복적 단어가 있다면 함께 알려주세요

[말투 예시]
{textwrap.shorten(tone_str, width=2000)}

[요약]
"""
            analysis = model.generate_content(tone_analysis_prompt)
            tone_summary = analysis.text.strip()

        st.session_state['user_data'] = {
            'my_name': my_name,
            'partner_name': partner_name,
            'tone_str': tone_str,
            'tone_summary': tone_summary
        }
        st.success("✅ 데이터 저장 완료! 이제 ‘대화하기’로 이동하세요.")

# --- 대화하기 화면 ---
elif menu == '대화':
    data = st.session_state['user_data']
    my_name = data['my_name']
    partner_name = data['partner_name']
    tone_summary = data.get('tone_summary', "")

    st.header(f"💬 {my_name}의 AI 분신과 {partner_name} 대화 중")
    partner_input = st.text_input(f"{partner_name}:")

    if partner_input and model:
        history = ""
        for spk, msg in st.session_state['chat_history'][-6:]:
            history += f"{spk}: {msg}\n"

        prompt = f"""
당신은 '{my_name}'입니다.
다음은 '{my_name}'의 말투 분석 요약입니다:
{tone_summary}

[대화 흐름]
{history}{partner_name}: {partner_input}

— 지시 사항 —
1) 친구에게 편하게 말하듯, **자연스럽고 구체적인** 답변을 작성하세요.
2) 말투 스타일은 위 분석을 **살짝 반영**하되, **과장 금지**.
3) 질문 요지에 맞춰 **필요 정보만** 간결히 제공하세요.
4) 불필요한 장황 설명이나 과도한 감탄사는 자제하세요.
5) **이모티콘 사용 금지**

{my_name}:
"""
        try:
            response = model.generate_content(prompt)
            reply = response.text.strip()
            reply = re.sub(r'[^\w\s가-힣\.,\?!]', '', reply)
            st.session_state['chat_history'].append((partner_name, partner_input))
            st.session_state['chat_history'].append((my_name, reply))
        except Exception as e:
            st.error(f"대화 생성 오류: {e}")

    for speaker, msg in st.session_state['chat_history']:
        st.markdown(f"**{speaker}:** {msg}")
