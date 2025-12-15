import streamlit as st
import google.generativeai as genai

# --- 1. 기본 설정 ---
st.set_page_config(page_title="2025 과목세특 메이트", page_icon="📝")

# --- 2. 스타일 CSS ---
st.markdown("""
    <style>
    .stTextArea textarea { background-color: #FAFCFA; border-radius: 10px; }
    .stButton button { background-color: #557C64 !important; color: white !important; font-weight: bold; border-radius: 10px; }
    .guide-box { background-color: #F7F9F8; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("🚨 API 키를 찾을 수 없습니다. Streamlit [Settings] -> [Secrets]에 GOOGLE_API_KEY를 등록해주세요.")
    st.stop() # 키 없으면 여기서 멈춤

# --- 4. 제목 및 가이드 ---
st.title("📚 2025 과목세특 메이트")
st.markdown("##### 1학기 요약 + 2학기 심화(기고문/북리뷰/AI) 통합")
st.divider()

st.markdown("""
<div class="guide-box">
    <b>💡 작성 방식</b><br>
    1. <b>1학기</b>: 입력 내용을 핵심 위주로 요약합니다.<br>
    2. <b>2학기</b>: 입력 키워드를 바탕으로 <b>[신문기사 기고문 + 원서 북리뷰 + AI 활용]</b> 내용으로 확장합니다.<br>
    3. <b>결과</b>: 두 학기 내용이 자연스럽게 이어지는 <b>500자 내외</b>의 글을 만듭니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력창 (텍스트 전용) ---
st.subheader("1. 1학기 내용 (요약 대상)")
sem1_input = st.text_area("1학기 내용을 입력하세요", height=100, placeholder="기존 생기부 내용을 붙여넣으세요.", label_visibility="collapsed")

st.subheader("2. 2학기 활동 키워드 (심화 대상)")
st.caption("※ 입력한 주제를 바탕으로 기고문, 북리뷰, AI 활용 활동이 자동 생성됩니다.")
sem2_input = st.text_area("2학기 주제를 입력하세요", height=100, placeholder="예: AI 의료 윤리, 'Deep Medicine' 독서, 챗GPT 토론 등", label_visibility="collapsed")

# --- 6. 옵션 ---
col1, col2 = st.columns(2)
with col1:
    mode = st.radio("작성 모드", ["✨ 풍성하게", "🛡️ 엄격하게"], horizontal=True)
with col2:
    target_length = st.slider("목표 글자 수", 300, 1000, 500, 50)

# --- 7. 실행 로직 ---
if st.button("✨ 세특 생성하기", use_container_width=True):
    if not sem1_input or not sem2_input:
        st.warning("⚠️ 1학기 내용과 2학기 키워드를 모두 입력해주세요.")
    else:
        with st.spinner("AI가 내용을 작성 중입니다..."):
            try:
                # API 설정
                genai.configure(api_key=api_key)
                
                # 모델 설정 (가장 안정적인 1.5 Flash 강제 고정)
                model = genai.GenerativeModel("gemini-1.5-flash")

                # 프롬프트 작성
                prompt = f"""
                당신은 고등학교 교사입니다. 학생의 [1학기 기존 세특]과 [2학기 신규 활동]을 통합하여, 전체 분량 약 {target_length}자의 '과목 세특'을 작성하세요.

                [입력 데이터]
                - 1학기 내용: {sem1_input}
                - 2학기 주제: {sem2_input}
                - 모드: {mode}

                [★ 필수 작성 지침]
                1. **1학기 (30%)**: 입력된 1학기 내용을 핵심만 요약하여 서두에 배치하세요.
                2. **2학기 (70%)**: 입력된 2학기 주제를 바탕으로 아래 3가지 활동을 구체적으로 창작하여 서술하세요.
                   - ① **신문기사 기고문**: 관련 기사를 읽고 자신의 견해를 논리적으로 기고함.
                   - ② **원서 북리뷰**: 관련 원서를 읽고 내용을 비평하거나 심화 탐구함.
                   - ③ **AI 도구 활용**: AI를 활용해 탐구를 확장하고 한계를 분석함.
                3. **스타일**: '~함', '~임' 등의 생기부 문체 사용. 문장은 [동기-과정-결과-성장] 흐름 유지.

                [출력 양식]
                1. 활동 요약 (1학기/2학기 포인트)
                ---SPLIT---
                2. 최종 세특 본문
                """

                # 생성 요청
                response = model.generate_content(prompt)
                text = response.text

                # 결과 분리
                if "---SPLIT---" in text:
                    parts = text.split("---SPLIT---")
                    analysis = parts[0].strip()
                    result = parts[1].strip()
                else:
                    analysis = "요약 없음"
                    result = text

                # 결과 표시
                st.success("작성 완료!")
                with st.expander("🔍 활동 요약 보기"):
                    st.write(analysis)
                
                st.markdown("---")
                st.text_area("최종 결과", value=result, height=400)
                st.caption(f"글자 수: {len(result)}자 (공백 포함)")

            except Exception as e:
                # 에러 발생 시 정확한 이유 출력
                st.error(f"오류가 발생했습니다: {str(e)}")
                if "404" in str(e):
                    st.warning("👉 해결책: 'requirements.txt' 파일을 확인하고 앱을 재부팅(Reboot) 해주세요.")
