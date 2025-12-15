import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 영어 세특 메이트 (Final)",
    page_icon="🎓",
    layout="centered"
)

# --- 2. [디자인] 스타일 설정 ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; color: #2F4F3A; } 
    .stButton button { background-color: #557C64 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; padding: 0.8rem; }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; text-align: right; border: 1px solid #C4D7CD; }
    .semester-header { color: #2F4F3A; font-weight: bold; margin-bottom: 5px; border-bottom: 2px solid #557C64; display: inline-block; }
    
    /* 라디오 버튼 카드 스타일 */
    div[data-testid="stRadio"] { background-color: transparent; }
    div[data-testid="stRadio"] > div[role="radiogroup"] { display: flex; gap: 10px; }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex-grow: 1; background-color: #FFFFFF; border: 1px solid #E0E5E2; border-radius: 8px; padding: 10px; justify-content: center;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color: #557C64; background-color: #F7F9F8; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. [핵심] 사용 가능한 모델 자동 찾기 ---
def get_best_available_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority_list = [
            "models/gemini-1.5-flash", "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro", "models/gemini-1.5-pro-latest",
            "models/gemini-pro"
        ]
        for model_name in priority_list:
            if model_name in available_models:
                return model_name
        return available_models[0] if available_models else "gemini-pro"
    except:
        return "gemini-pro"

# --- 4. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 5. 헤더 영역 ---
st.title("🎓 2025 영어 세특 메이트")
st.markdown("<p class='subtitle'>1학기 요약 + 2학기 생성 (총 500자 관리)</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

st.markdown("""
<div class="guide-box">
    <b>💡 작성 모드 선택 가능</b><br>
    이제 <b>'풍성하게'</b>와 <b>'엄격하게'</b> 모드를 선택할 수 있습니다.<br>
    AI가 선택한 스타일에 맞춰 2학기 내용을 작성하고 전체 분량을 조절합니다.
</div>
""", unsafe_allow_html=True)

# --- 6. 입력 영역 ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="semester-header">📝 1학기 (요약)</p>', unsafe_allow_html=True)
    input_sem1 = st.text_area("1학기 내용", height=200, placeholder="기존 내용을 입력하면 핵심만 요약합니다.", label_visibility="collapsed")

with col2:
    st.markdown('<p class="semester-header">✨ 2학기 (생성)</p>', unsafe_allow_html=True)
    input_sem2 = st.text_area("2학기 내용", height=200, placeholder="관찰한 활동, 독서, 수행평가 내용을 입력하세요.", label_visibility="collapsed")

# --- 7. 옵션 설정 (스타일 & 키워드) ---
st.markdown("### 🎨 작성 스타일 및 키워드")

# [스타일 선택 라디오 버튼]
mode = st.radio(
    "작성 모드 선택",
    ["✨ 풍성하게 (교육적 의미 부여)", "🛡️ 엄격하게 (팩트 중심 서술)"],
    captions=["탐구 동기와 성장 과정을 구체적으로 풀어서 씁니다.", "미사여구를 배제하고 객관적 사실 위주로 씁니다."],
    horizontal=True,
    label_visibility="collapsed"
)

# [키워드 선택]
filter_options = ["🗣️ 유창한 말하기", "📖 심화 독해", "✍️ 논리적 글쓰기", "👂 직청직해", "🌍 문화적 이해", "📚 고급 어휘 활용", "🔗 진로 연계"]
try:
    selected_tags = st.pills("강조 키워드", filter_options, selection_mode="multi", label_visibility="collapsed")
except:
    selected_tags = st.multiselect("강조 키워드", filter_options, label_visibility="collapsed")

# --- 8. 실행 로직 ---
st.markdown("")
if st.button("✨ 맞춤형 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 없습니다.")
    elif not input_sem1 and not input_sem2:
        st.warning("⚠️ 내용을 입력해주세요.")
    else:
        with st.spinner(f"AI가 '{mode.split()[1]}' 모드로 분석 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                
                # 1. 모델 자동 감지
                target_model_name = get_best_available_model()
                
                # 2. 모드에 따른 프롬프트 및 온도 설정
                if "풍성하게" in mode:
                    temp = 0.8  # 창의성 높임
                    style_prompt = """
                    - **풍성 모드(Rich Mode)**: 
                    입력된 활동이 학생에게 어떤 '지적 호기심'을 주었는지, 구체적으로 어떤 '과정'을 거쳤는지 살를 붙여 작성하세요. 
                    단순 나열이 아니라 '동기-심화탐구-성장'의 스토리텔링이 느껴지도록 교육적 의미를 부여하세요.
                    """
                else:
                    temp = 0.3  # 사실성 높임
                    style_prompt = """
                    - **엄격 모드(Strict Mode)**: 
                    입력되지 않은 내용은 절대 창작하지 마세요. 형용사와 부사(매우, 탁월한 등)를 최대한 배제하고, 
                    '무엇을 읽고', '무엇을 분석하여', '어떤 산출물을 냈다'는 **객관적 사실(Fact)** 위주로 건조하게 작성하세요.
                    """

                tags_str = f"2학기 키워드: {', '.join(selected_tags)}" if selected_tags else "키워드: 영어 종합 역량"
                
                # 3. 통합 프롬프트 구성
                prompt = f"""
                당신은 고등학교 영어 교사입니다. 아래 지침에 따라 세특을 작성하세요.
                
                [입력 데이터]
                - 1학기: {input_sem1}
                - 2학기: {input_sem2}
                - 키워드: {tags_str}

                [작성 지침]
                1. **분량 조절**: 1학기와 2학기 결과물을 합쳐서 **공백 포함 450~490자(500자 미만)**가 되도록 맞추세요.
                2. **1학기 (Diet)**: 문법 오류 수정 및 핵심 내용 요약.
                3. **2학기 (Bulk-up)**: 아래 스타일 지침을 따를 것.
                {style_prompt}
                
                [출력 형식]
                ---1학기---
                (내용)
                ---2학기---
                (내용)
                """

                # 4. 생성 요청
                model = genai.GenerativeModel(target_model_name, generation_config=genai.types.GenerationConfig(temperature=temp))
                response = model.generate_content(prompt)
                full_text = response.text

                # 5. 결과 처리
                if "---2학기---" in full_text:
                    parts = full_text.split("---2학기---")
                    sem1_res = parts[0].replace("---1학기---", "").strip()
                    sem2_res = parts[1].strip()
                else:
                    sem1_res = full_text.replace("---1학기---", "").strip()
                    sem2_res = ""

                # 6. 화면 출력
                total_len = len(sem1_res + sem2_res)
                st.success(f"작성 완료! ({mode.split()[1]} 모드)")
                
                st.markdown(f"""
                <div class="count-box">
                    📊 총 글자 수: <b>{total_len}자</b> (목표: 500자 미만)
                </div>
                """, unsafe_allow_html=True)

                r1, r2 = st.columns(2)
                with r1:
                    st.info("📉 1학기 (요약)")
                    st.text_area("1학기 결과", value=sem1_res, height=300)
                with r2:
                    st.success(f"📈 2학기 ({mode.split()[1]})")
                    st.text_area("2학기 결과", value=sem2_res, height=300)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
