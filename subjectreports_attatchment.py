import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 영어 세특 메이트 (커리큘럼 ver)",
    page_icon="🏫",
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
    
    /* 라디오 버튼 스타일 */
    div[data-testid="stRadio"] { background-color: transparent; }
    div[data-testid="stRadio"] > div[role="radiogroup"] { display: flex; gap: 10px; }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex-grow: 1; background-color: #FFFFFF; border: 1px solid #E0E5E2; border-radius: 8px; padding: 10px; justify-content: center;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color: #557C64; background-color: #F7F9F8; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. [핵심] 모델 자동 감지 함수 ---
def get_best_available_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority_list = [
            "models/gemini-1.5-flash", "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro", "models/gemini-1.5-pro-latest", "models/gemini-pro"
        ]
        for model_name in priority_list:
            if model_name in available_models: return model_name
        return available_models[0] if available_models else "gemini-pro"
    except:
        return "gemini-pro"

# --- 4. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 5. 헤더 영역 ---
st.title("🏫 2025 영어 세특 메이트")
st.markdown("<p class='subtitle'>1학기 요약 & 2학기 수행평가(뉴스/AI/문제제작) 반영</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

st.markdown("""
<div class="guide-box">
    <b>💡 2학기 커리큘럼 자동 반영</b><br>
    2학기 입력창에 소재만 적으면, AI가 아래 수행평가 활동으로 연결하여 작성합니다.<br>
    1. 📰 <b>뉴스 기고문(Op-Ed)</b> 작성<br>
    2. 🤖 <b>미래사회 소설 & AI 툴 창작</b> 프로젝트<br>
    3. ❓ <b>지문 분석 및 문제 만들기</b> (Question Creation)
</div>
""", unsafe_allow_html=True)

# --- 6. 입력 영역 ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="semester-header">📝 1학기 (요약)</p>', unsafe_allow_html=True)
    input_sem1 = st.text_area("1학기", height=220, placeholder="기존 내용을 입력하면 중복을 피해서 요약합니다.", label_visibility="collapsed")

with col2:
    st.markdown('<p class="semester-header">✨ 2학기 (수행평가 연계)</p>', unsafe_allow_html=True)
    input_sem2 = st.text_area("2학기", height=220, placeholder="예: 환경 뉴스 읽음 / 'The Giver' 읽고 AI 이미지 생성 / 친구들 멘토링함", label_visibility="collapsed")

# --- 7. 옵션 설정 ---
st.markdown("### 🎨 작성 모드 & 키워드")
mode = st.radio(
    "작성 모드",
    ["✨ 풍성하게 (과정/성장 중심)", "🛡️ 엄격하게 (팩트/결과 중심)"],
    horizontal=True, label_visibility="collapsed"
)

filter_options = ["🗣️ 유창한 말하기", "📖 심화 독해", "✍️ 논리적 글쓰기", "👂 직청직해", "🌍 문화적 이해", "📚 어휘 응용력", "🔗 진로 심화"]
try:
    selected_tags = st.pills("강조 키워드", filter_options, selection_mode="multi", label_visibility="collapsed")
except:
    selected_tags = st.multiselect("강조 키워드", filter_options, label_visibility="collapsed")

# --- 8. 실행 로직 ---
st.markdown("")
if st.button("✨ 커리큘럼 기반 세특 생성", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 없습니다.")
    elif not input_sem1 and not input_sem2:
        st.warning("⚠️ 내용을 입력해주세요.")
    else:
        with st.spinner(f"2학기 수행평가 기준에 맞춰 '{mode.split()[1]}' 모드로 작성 중..."):
            try:
                genai.configure(api_key=api_key)
                target_model_name = get_best_available_model()
                
                # 모드별 설정
                if "풍성하게" in mode:
                    temp = 0.8
                    style_instruction = "활동의 동기, 구체적인 탐구 과정, 이를 통해 확장된 사고를 유기적으로 연결하여 교육적 성장이 돋보이게 서술."
                else:
                    temp = 0.3
                    style_instruction = "미사여구를 배제하고 '무엇을 읽고, 무엇을 작성하여, 어떤 결과를 냄'과 같이 객관적 사실 위주로 건조하게 서술."

                tags_str = f"2학기 핵심역량: {', '.join(selected_tags)}" if selected_tags else ""

                # [핵심] 프롬프트 엔지니어링
                prompt = f"""
                당신은 고등학교 영어 교사입니다. 학생의 1학기 내용을 고려하여 2학기 세특을 작성해야 합니다.

                # [2학기 필수 커리큘럼 및 평가 기준]
                사용자가 입력한 내용이 아래 활동 중 어디에 해당하는지 파악하여 전문적으로 서술하세요.
                1. **[Op-Ed Writing]**: 관심 분야 영어 뉴스 기사를 읽고, 학교 신문에 자신의 견해를 담은 기고문(Op-Ed) 작성.
                2. **[AI & Book Review]**: 미래 사회를 다룬 영미 소설을 읽고, 인공지능 윤리에 대한 서평(Book Review)을 쓴 뒤, AI 툴을 활용해 관련 창작물(이미지/영상/포스터 등) 제작.
                3. **[Question Making]**: 지문의 핵심 내용을 파악하여 동료 학습자를 위한 문항(Question)을 직접 제작.
                4. **[Attitude]**: 수업 참여도, 경청하는 태도, 협력적 자세.

                # [입력 데이터]
                - 1학기 내용: {input_sem1}
                - 2학기 관찰: {input_sem2}
                - {tags_str}

                # [작성 미션]
                1. **중복 회피(Anti-Overlap)**: 1학기에 언급된 소재나 활동 방식이 2학기에 반복되지 않게 하세요. 
                   (예: 1학기에 '환경' 주제가 있었다면 2학기엔 'AI 기술'이나 '문화'로 초점을 바꾸거나, 활동의 깊이를 심화시키세요.)
                2. **분량 통제**: 1학기(요약) + 2학기(생성) = **총 450~490자 (공백 포함)**.
                3. **스타일**: {style_instruction}
                4. **문체**: '~함', '~임', '~보임', '~분석함' (생기부 표준).

                # [출력 형식]
                ---1학기---
                (1학기 요약 내용)
                ---2학기---
                (2학기 생성 내용)
                """

                model = genai.GenerativeModel(target_model_name, generation_config=genai.types.GenerationConfig(temperature=temp))
                response = model.generate_content(prompt)
                full_text = response.text

                if "---2학기---" in full_text:
                    parts = full_text.split("---2학기---")
                    sem1_res = parts[0].replace("---1학기---", "").strip()
                    sem2_res = parts[1].strip()
                else:
                    sem1_res = full_text.replace("---1학기---", "").strip()
                    sem2_res = ""

                total_len = len(sem1_res + sem2_res)
                
                st.success("작성 완료!")
                st.markdown(f"<div class='count-box'>📊 총 {total_len}자 (목표: 500자 미만)</div>", unsafe_allow_html=True)

                r1, r2 = st.columns(2)
                with r1:
                    st.info("📉 1학기 (중복제거/요약)")
                    st.text_area("1학기 결과", value=sem1_res, height=350)
                with r2:
                    st.success(f"📈 2학기 ({mode.split()[1]})")
                    st.text_area("2학기 결과", value=sem2_res, height=350)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
