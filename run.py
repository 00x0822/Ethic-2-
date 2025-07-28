import streamlit as st

# 유튜브 영상 URL
url = 'https://www.youtube.com/watch?v=aZJHR0hvQyE'

# 페이지 설정
st.set_page_config(layout='wide', page_title='EthicApp')

# 타이틀
st.title('Ethic is good for us')

# 사이드바 메뉴
st.sidebar.subheader('Menu...')

# (사이드바 버튼 추가): "학생 데이터 가져오기" 버튼 추가
show_data = st.sidebar.button("📂 학생 데이터 가져오기")
col1, col2 = st.columns([10, 4])
# 왼쪽 영역: 콘텐츠 (YouTube 영상)
with col1:
    st.header("📺 디지털 유령: 나의 AI 분신")
    st.video(url)

    st.markdown("""
    **이 영상은 '디지털 유령' 개념을 소개하며, 기술이 인간의 기억과 말투를 어떻게 모방할 수 있는지 설명합니다.**
    
    - AI는 죽은 사람처럼 말할 수 있을까?
    - 나와 닮은 AI가 존재한다면, 그것은 진짜 '나'일까?
    """)

    # 학생의 생각 입력
    st.subheader("📝 당신의 생각을 남겨보세요")
    user_input = st.text_area("이 영상을 보고 어떤 생각이 들었나요?", height=150, key="reflection")

    if st.button("제출하기"):
        if user_input.strip() != "":
            try:
                with open("data.txt", "a", encoding="utf-8") as f:
                    f.write(user_input.strip() + "\n---\n")
                st.success("제출이 완료되었습니다. 감사합니다!")
            except Exception as e:
                st.error(f"파일 저장 중 오류가 발생했습니다: {e}")
        else:
            st.warning("내용을 입력한 후 제출해주세요.")

    # (학생 데이터 가져오기 버튼이 눌렸을 경우에만 아래에 출력)
    if show_data:
        st.markdown("---")
        st.subheader("📄 제출된 학생 생각 모음")
        try:
            with open("data.txt", "r", encoding="utf-8") as f:
                data = f.read()
                st.text_area("제출 내용 (읽기 전용)", value=data, height=300, disabled=True)
        except FileNotFoundError:
            st.warning("data.txt 파일이 존재하지 않습니다.")
    
    

# 오른쪽 영역: Tips 제공
with col2:
    st.subheader("💡 Tips...")
    st.markdown("""
    - **디지털 유령이란?**  
      고인의 말투, 기억, 성격 등을 모방한 AI 형태의 디지털 존재입니다.

    - **이 수업에서 다루는 주제:**  
      1. AI 분신의 기술적 기반  
      2. 기억과 윤리의 경계  
      3. 디지털 정체성과 죽음 이후의 '나'

    - **생각해 볼 질문:**  
      - 나를 닮은 AI가 존재한다면 그것은 나인가?  
      - 고인을 기억하는 기술은 위로가 될까, 고통일까?
    """)
