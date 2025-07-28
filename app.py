import streamlit as st
import google.generativeai as genai
import re
import textwrap
from collections import Counter

# --- 페이지 설정 ---
st.set_page_config(page_title="디지털 유령", layout="wide")
st.title("🌌 디지털 유령: 나의 AI 분신 챗봇과 대화하기")

# --- 간단 소개 ---
st.markdown("Streamlit에 업로드한 카톡 대화 파일로 AI 분신과 말투 그대로 대화해 보세요.")

# --- Gemini API 초기화 ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("❗ 환경 변수 ‘GOOGLE_API_KEY’가 설정되지 않았습니다. Settings → Secrets 에 추가해주세요.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

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

# --- Streamlit 세션 초기화 ---
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = default_user_data()
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'menu' not in st.session_state:
    st.session_state['menu'] = '홈'

# --- 사이드바 메뉴 스타일링 (텍스트 링크처럼) ---
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
   - 채팅방 우측 상단 **메뉴(≡)** → **대화내용** → **대화 내보내기** → **txt 파일** 형태로 저장  
   - 저장된 `.txt` 파일을 준비하세요.  

2. **앱 사용**  
   - ✍ ‘입력’ 메뉴에서 내 이름과 `.txt` 파일 업로드 후 **저장**  
   - 💬 ‘대화하기’ 메뉴에서 상대방 역할로 질문을 입력해 **대화 시작**  
   - AI 분신이 분석된 말투를 그대로 반영해 응답합니다.
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
        if kakao_file and model:
            tone_str = extract_user_lines(kakao_file, data['my_name'])
            # 말투 요약 프롬프트
            analysis_prompt = f"""
아래는 '{data['my_name']}' 사용자가 실제 카카오톡에서 쓴 대화 일부입니다.
이 대화에서 나타나는 말투 스타일(이모티콘 사용, 말끝 어미, 어투 성향 등)을 간단히 요약해 주세요.

[대화 예시]
{textwrap.shorten(tone_str, width=2000)}

[말투 요약]
"""
            resp = model.generate_content(analysis_prompt)
            tone_summary = resp.text.strip()

        st.session_state['user_data'] = {
            'my_name':      my_name,
            'partner_name': partner_name,
            'tone_str':     tone_str,
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

    if partner_input and model:
        # 최신 3쌍(6줄) 히스토리
        hist = ""
        for spk, msg in st.session_state['chat_history'][-6:]:
            hist += f"{spk}: {msg}\n"

        # 대화 생성 프롬프트
        chat_prompt = f"""
당신은 '{my_name}'입니다.
말투 요약: {tone_summary}

대화 기록:
{hist}{partner_name}: {partner_input}

— 지시 사항 —  
1) 친구처럼 편안하고 구체적으로 답변하세요.  
2) 말투는 분석 요약을 살짝 반영하되 과장 금지.  
3) 이모티콘은 사용 금지.  

{my_name}:
"""
        chat_resp = model.generate_content(chat_prompt)
        reply = chat_resp.text.strip()
        # 이모티콘 제거
        reply = re.sub(r'[^\w\s가-힣\.,\?!]', '', reply)

        st.session_state['chat_history'].append((partner_name, partner_input))
        st.session_state['chat_history'].append((my_name, reply))

    for spk, msg in st.session_state['chat_history']:
        st.markdown(f"**{spk}:** {msg}")
