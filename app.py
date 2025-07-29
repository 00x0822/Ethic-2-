import streamlit as st
import requests
import re
import textwrap

# --- 페이지 설정 ---
st.set_page_config(page_title="디지털 유령", layout="wide")
st.title("🌌 디지털 유령: 나의 AI 분신 챗봇과 대화하기")

# --- 간단 소개 ---
st.markdown("Streamlit에 업로드한 카톡 대화 파일로 AI 분신과 말투 그대로 대화해 보세요.")

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
def generate_content(prompt: str):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("❗ GOOGLE_API_KEY가 설정되지 않았습니다. Secrets에서 키를 추가하세요.")
        return ""
    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1beta2/models/text-bison-001:generateText?key={api_key}"
    )
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    body = {
        "prompt": {"text": prompt},
        "temperature": 0.7,
        "candidateCount": 1,
    }
    try:
        res = requests.post(url, headers=headers, json=body, timeout=30)
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        st.error(f"❗ API 호출 오류 {res.status_code}\n{res.text}")
        return ""
    except requests.exceptions.RequestException as e:
        st.error(f"❗ 네트워크 오류: {e}")
        return ""
    return res.json()["candidates"][0]["output"]

# --- Streamlit 세션 초기화 ---
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

# --- 사이드바 메뉴 버튼 ---
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
AI 분신 챗봇과 자연스럽게 대화하도록 돕습니다。

**사용법**  
1. **카카오톡 대화 저장**  
   - 채팅방 우측 상단 **메뉴(≡)** → **대화내용** → **대화 내보내기** → **txt 파일** 형태로 저장  
   - 저장된 `.txt` 파일을 준비하세요。

2. **앱 사용**  
   - ✍ ‘입력’ 메뉴에서 내 이름과 `.txt` 파일 업로드 후 **저장**  
   - 💬 ‘대화하기’ 메뉴에서 상대방 역할로 질문을 입력해 **대화 시작**  
   - AI 분신이 분석된 말투를 그대로 반영해 응답합니다。
""")

# --- 데이터 입력 화면 ---
elif menu == '입력':
    data = st.session_state['user_data']
    with st.form("input_form"):
        my_name = st.text_input("내 이름", value=data['my_name'])
        partner_name = st.text_input("상대방 이름", value=data['partner_name'])
        kakao_file = st.file_uploader("카톡 대화 파일 (.txt)", type="txt")
        submitted = st.form_submit_button("저장")

    if submitted and kakao_file and my_name:
        tone_str = extract_user_lines(kakao_file, my_name)
        prompt = f"""
아래는 '{my_name}' 사용자의 카카오톡 대화 일부입니다。  
말투 스타일(이모티콘 사용, 말끝 어미, 어투 성향 등)을 간단히 요약해 주세요。

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
        st.success("✅ 데이터가 저장되었습니다。 ‘대화하기’로 이동하세요。")

# --- 대화하기 화면 ---
elif menu == '대화':
    data = st.session_state['user_data']
    st.header(f"💬 {data['my_name']}의 AI 분신과 {data['partner_name']} 대화 중")
    partner_input = st.text_input(f"{data['partner_name']}:")

    if partner_input:
        history = "\n".join(f"{s}: {m}" for s, m in st.session_state['chat_history'][-6:])
        prompt = f"""
당신은 '{data['my_name']}'입니다。  
말투 요약: {data['tone_summary']}

대화 기록：
{history}
{data['partner_name']}: {partner_input}

— 지시 사항 —  
1) 친구처럼 편안하고 구체적으로 답변하세요。  
2) 말투는 분석 요약을 살짝 반영하되 과장 금지。  
3) 이모티콘은 사용 금지。  
4) 필요 정보만 간결히 제공합니다。

{data['my_name']}: 
"""
        reply = generate_content(prompt)
        reply = re.sub(r'[^\w\s가-힣\.,\?!]', '', reply)
        st.session_state['chat_history'] += [
            (data['partner_name'], partner_input),
            (data['my_name'], reply)
        ]

    for s, m in st.session_state['chat_history']:
        st.markdown(f"**{s}:** {m}")
