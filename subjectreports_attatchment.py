import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 과목세특 메이트",
    page_icon="📚",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS (기존 디자인 유지) ---
st.markdown("""
    <style>
    /* 폰트 설정 */
    html, body, [class*="css"] { 
        font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif; 
    }
    
    /* 입력창: 부드러운 테두리 */
    .stTextArea textarea { 
        border-radius: 12px; 
        border: 1px solid rgba(85, 124, 100, 0.2); 
        background-color: #FAFCFA; 
    }
    
    /* 제목 스타일 */
    h1 { font-weight: 700; letter-spacing: -1px; color: #2F4F3A; } 
    .subtitle { font-size: 16px; color: #666; margin-top: -15px; margin-bottom: 30px; }
    
    /* 버튼 스타일: 세이지 그린 */
    .stButton button { 
        background-color: #557C64 !important; 
        color: white !important;
        border-radius: 10px; 
        font-weight: bold; 
        border: none; 
        transition: all 0.2s ease; 
        padding: 0.8rem 1rem; 
        font-size: 16px !important;
        width: 100%; 
    }
    .stButton button:hover { 
        background-color: #3E5F4A !important; 
        transform: scale(1.01); 
        color: white !important;
    }
    
    /* 슬라이더 스타일 */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div {
        background-color: #E0E0E0 !important; border-radius: 10px; height: 6px !important; 
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
        background-color: #D4AC0D !important; height: 6px !important; 
    }
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: transparent !important; box-shadow: none !important; border: none !important; height: 24px; width: 24px; 
    }
    div[data-testid="stSlider"] div[role="slider"]::after {
        content: "★"; font-size: 32px; color: #D4AC0D !important; position: absolute; top: -18px; left: -5px; text-shadow: 0px 1px 2px rgba(0,0,0,0.2);
    }
    div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p { color: #557C64 !important; }

    /* 라디오 버튼 스타일 */
    div[data-testid="stRadio"] { background-color: transparent; }
    div[data-testid="stRadio"] > div[role="radiogroup"] { display: flex; justify-content: space-between; width: 100%; gap: 10px; }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex-grow: 1; background-color: #FFFFFF; border: 1px solid #E0E5E2; border-radius: 8px; padding: 12px; justify-content: center;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color: #557C64; background-color: #F7F9F8; }
    
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; line-height: 1.6; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .guide-title { font-weight: bold; margin-bottom: 8px; display: block; font-size: 15px; color: #557C64;}
    .warning-text { color: #8D6E63; font-size: 14px; margin-top: 5px; font-weight: 500; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 10px; text-align: right; border: 1px solid #C4D7CD; }
    .analysis-box { background-color: #FCFDFD; border-left: 4px solid #557C64; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-size: 14px; color: #333; }
    .footer { margin-top: 50px; text-align: center; font-size: 14px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }
    .card-title { font-size: 15px; font-weight: 700; color: #557C64; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
# (예외 타입을 넓게 잡아서 secrets 없을 때도 죽지 않게)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("📚 2025 과목세특 메이트")
st.markdown("<p class='subtitle'>Subject Specific Records Generator</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# [수정됨] 과목세특용 작성 팁
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 완벽한 세특을 위한 3-Step 작성법</span>
    단순한 활동 나열은 NO! 아래 3가지 흐름이 들어가게 적어주세요.<br><br>
    1. <b>(동기/수업내용)</b> 교과서 단원, 배운 개념, 혹은 호기심을 갖게 된 계기<br>
    2. <b>(심화탐구)</b> 수행평가, 보고서 작성, 독서 등 구체적인 탐구 과정<br>
    3. <b>(성장/결과)</b> 이를 통해 확장된 지식, 변화된 생각, 진로와의 연결점
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 ---
st.markdown("### 1. 수업 활동 및 관찰 내용")
student_input = st.text_area(
    "입력창",
    height=200,
    placeholder="예시: '유전' 단원 학습 중 유전자 가위 기술에 흥미를 느껴 관련 논문을 찾아봄. CRISPR 기술의 원리를 분석하고, 생명윤리적 관점에서 자신의 견해를 담은 보고서를 제출함.", 
    label_visibility="collapsed"
)

if student_input and len(student_input) < 30:
    st.markdown("<p class='warning-text'>⚠️ 내용이 조금 짧습니다. 어떤 활동을 어떻게 했는지 구체적으로 적어주세요.</p>", unsafe_allow_html=True)

# --- 6. 3단계 작성 옵션 ---
st.markdown("### 2. 작성 옵션 설정")

# [카드 1] 모드 선택
with st.container(border=True):
    st.markdown('<p class="card-title">① 작성 모드 선택</p>', unsafe_allow_html=True)
    mode = st.radio(
        "모드",
        ["✨ 풍성하게 (교육적 평가 추가)", "🛡️ 엄격하게 (팩트 중심)"],
        captions=["탐구의 의미와 학업적 성장을 구체화하여 작성합니다.", "입력된 활동 사실 위주로 건조하게 작성합니다."],
        horizontal=True, 
        label_visibility="collapsed"
    )

# [카드 2] 희망 분량
with st.container(border=True):
    st.markdown('<p class="card-title">② 희망 분량 (공백 포함)</p>', unsafe_allow_html=True)
    target_length = st.slider(
        "글자 수",
        min_value=100, max_value=1000, value=500, step=10,
        label_visibility="collapsed"
    )

# [카드 3] [수정됨] 과목세특 전용 키워드
with st.container(border=True):
    st.markdown('<p class="card-title">③ 강조할 학업 역량 (다중 선택)</p>', unsafe_allow_html=True)
    filter_options = [
        "👑 AI 자동 판단", 
        "🔎 비판적 사고력", "📊 데이터 분석/활용", "💡 창의적 문제해결", 
        "📚 심화 지식 탐구", "🗣️ 논리적 의사소통", "🤝 협업 및 리더십", 
        "🔗 진로/전공 연계", "📖 자기주도적 학습"
    ]
    try:
        selected_tags = st.pills("키워드 버튼", options=filter_options, selection_mode="multi", label_visibility="collapsed")
    except Exception:
        selected_tags = st.multiselect("키워드 선택", filter_options, label_visibility="collapsed")

# [고급 설정] 모델 선택
st.markdown("")
with st.expander("⚙️ AI 모델 직접 선택하기 (고급 설정)"):
    manual_model = st.selectbox(
        "사용할 모델을 선택하세요",
        ["🤖 자동 (Auto)", "⚡ gemini-1.5-flash (빠름/무료)", "🤖 gemini-1.5-pro (고성능)"],
        index=0
    )

# --- 7. 실행 및 결과 영역 ---
st.markdown("")
if st.button("✨ 과목 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not student_input:
        st.warning("⚠️ 학생 관찰 내용을 입력해주세요!")
    else:
        with st.spinner('AI가 교과 세특 전문가 모드로 분석 중입니다...'):
            try:
                # API 키 설정
                genai.configure(api_key=api_key)

                # --- 모델 선택 로직 (2025 기준, 2.5 라인 사용 예시) ---
                target_model = "gemini-2.5-flash"  # 기본값

                if "pro" in manual_model:
                    target_model = "gemini-2.5-pro"
                elif "flash" in manual_model:
                    target_model = "gemini-2.5-flash"
                elif "자동" in manual_model:
                    target_model = "gemini-2.5-flash"

                # 모드별 프롬프트 설정
                if "엄격하게" in mode:
                    temp = 0.2
                    prompt_instruction = """
                    # ★★★ 엄격 작성 원칙 (Strict Mode) ★★★
                    1. **사실 기반 서술**: 학생이 수행하지 않은 심화 활동이나 읽지 않은 책은 절대 창작하지 마십시오.
                    2. **객관적 평가**: 미사여구(탁월함, 매우 우수함 등)를 남발하기보다, '어떤 근거로 결론을 도출함'과 같이 구체적 사실 위주로 서술하십시오.
                    """
                else:
                    temp = 0.75
                    prompt_instruction = """
                    # ★★★ 풍성 작성 원칙 (Rich Mode) ★★★
                    1. **의미 부여 (Elaboration)**: 단순한 활동 나열을 넘어, 해당 탐구가 학생의 지적 호기심을 어떻게 충족시켰는지 교육적으로 서술하십시오.
                    2. **유기적 연결**: '동기-과정-결과-후속활동'이 물 흐르듯 연결되도록 문장을 구성하십시오.
                    3. 학업적 성장과 잠재력을 긍정적이고 구체적인 언어로 표현하십시오.
                    """

                generation_config = genai.types.GenerationConfig(temperature=temp)
                model = genai.GenerativeModel(target_model, generation_config=generation_config)

                # 키워드 처리
                if not selected_tags:
                    tags_str = "별도 지정 없음. [교과지식습득] -> [심화탐구활동] -> [문제해결/응용] -> [학업역량성장] 순서로 작성."
                else:
                    tags_str = f"핵심 키워드: {', '.join(selected_tags)}"

                # [핵심] 과목세특 전용 프롬프트
                system_prompt = f"""
                당신은 입학사정관의 평가 기준을 완벽히 이해하고 있는 고등학교 교과 담당 교사입니다.
                입력된 [수업 활동 관찰 내용]을 바탕으로, 학생의 학업 역량이 돋보이는 '과목별 세부능력 및 특기사항(세특)'을 작성해야 합니다.

                # 입력 정보
                1. 학생 활동 내용: {student_input}
                2. 강조할 핵심 역량: [{tags_str}]

                # 작성 전략 (Writing Strategy)
                1. **구체성(Specificity)**: "열심히 함"보다는 "**어떤 자료를 분석하여 어떤 결론을 도출함**"과 같이 구체적으로 서술하십시오.
                2. **심화 확장(Deepening)**: 교과서 개념에서 시작하여 개인적인 호기심으로 심화 학습(독서, 논문, 실험 등)을 진행한 과정을 부각하십시오.
                3. **학업 역량(Competency)**: 활동을 통해 드러난 비판적 사고력, 논리적 분석력, 창의적 문제해결력을 명시적으로 드러내십시오.
                4. **목표 분량**: 공백 포함 약 {target_length}자 (오차범위 ±10%)

                다음 두 가지 파트로 나누어 출력하세요. 구분선: "---SPLIT---"

                [Part 1] 역량별 분석 (개조식)
                - [수업태도 / 탐구주제 / 학업성취 / 발전가능성] 등으로 분류하여 요약
                
                ---SPLIT---

                [Part 2] 과목 세특 (서술형 종합본)
                - 실제 생기부 입력용 줄글
                - 문체: '~함', '~임', '~보임', '~분석함' (생기부 표준 문체)
                
                {prompt_instruction}
                """

                response = model.generate_content(system_prompt)
                full_text = response.text
                
                if "---SPLIT---" in full_text:
                    parts = full_text.split("---SPLIT---")
                    analysis_text = parts[0].strip()
                    final_text = parts[1].strip()
                else:
                    analysis_text = "영역별 분석을 생성하지 못했습니다."
                    final_text = full_text

                char_count = len(final_text)
                char_count_no_space = len(final_text.replace(" ", "").replace("\n", ""))
                
                # 바이트 계산 (한글 3byte)
                byte_count = 0
                for char in final_text:
                    if ord(char) > 127:
                        byte_count += 3
                    else:
                        byte_count += 1
                
                st.success("작성 완료!")
                
                with st.expander("🔍 역량별 분석 내용 확인하기 (클릭)", expanded=True):
                    st.markdown(analysis_text)
                
                st.markdown("---")
                st.markdown("### 📋 최종 제출용 종합본")

                st.markdown(f"""
                <div class="count-box">
                    📊 목표: {target_length}자 | <b>실제: {char_count}자</b> (공백제외 {char_count_no_space}자)<br>
                    💾 <b>예상 바이트: {byte_count} Bytes</b> (NEIS 기준)
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"※ {mode.split()[1]} 모드 동작 중 ({target_model})")
                st.text_area("결과 (복사해서 나이스에 붙여넣으세요)", value=final_text, height=350)

            except Exception as e:
                # 에러 처리
                if "429" in str(e):
                    st.error("🚨 오늘 사용 가능한 무료 AI 횟수를 모두 쓰셨습니다!")
                elif "404" in str(e):
                    st.error("🚨 모델을 찾을 수 없습니다. (requirements.txt 버전을 확인하거나 Reboot 해주세요.)")
                else:
                    st.error(f"오류가 발생했습니다: {e}")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. All rights reserved.<br>
    문의: <a href="mailto:inlove11@naver.com" style="color: #888; text-decoration: none;">inlove11@naver.com</a>
</div>
""", unsafe_allow_html=True)
