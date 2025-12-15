import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 과목세특 메이트",
    page_icon="📚",
    layout="centered"
)

# --- 2. CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; letter-spacing: -1px; color: #2F4F3A; } 
    .stButton button { 
        background-color: #557C64 !important; color: white !important;
        border-radius: 10px; font-weight: bold; border: none; 
        transition: all 0.2s ease; padding: 0.8rem 1rem; font-size: 16px !important; width: 100%; 
    }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); color: white !important; }
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 10px; text-align: right; border: 1px solid #C4D7CD; }
    .footer { margin-top: 50px; text-align: center; font-size: 14px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 4. 헤더 ---
st.title("📚 2025 과목세특 메이트")
st.markdown("##### 1학기 요약 + 2학기 심화(기고문/북리뷰/AI) 통합 [텍스트 전용]")
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

st.markdown("""
<div class="guide-box">
    <b>💡 작성 가이드</b><br>
    1. <b>1학기</b>: 기존 내용을 입력하면 AI가 핵심만 요약합니다.<br>
    2. <b>2학기</b>: 입력된 키워드를 바탕으로 <b>신문기사 기고문, 원서 북리뷰, AI 도구 활용</b> 내용으로 확장합니다.<br>
    3. <b>결과</b>: 두 학기가 자연스럽게 연결된 500자 내외의 글이 완성됩니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 ---
st.markdown("### 1. 1학기 기존 세특 (요약용)")
sem1_input = st.text_area(
    "1학기 입력창", height=150,
    placeholder="이미 작성된 1학기 내용을 붙여넣으세요. (분량이 많으면 AI가 요약합니다)",
    label_visibility="collapsed"
)

st.markdown("### 2. 2학기 활동 내용 (심화용)")
sem2_input = st.text_area(
    "2학기 입력창", height=150,
    placeholder="예: AI 의료 기사 분석, 'Deep Medicine' 원서 독서, 챗GPT 활용 토론 등 (키워드 위주로 입력해도 됩니다)",
    label_visibility="collapsed"
)

# --- 6. 옵션 설정 ---
st.markdown("### 3. 작성 옵션")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("작성 모드", ["✨ 풍성하게", "🛡️ 엄격하게"], horizontal=True)
    with col2:
        target_length = st.slider("목표 글자 수", 300, 1000, 500, 50)

# 모델 목록 로딩(실제 사용 가능한 모델만) - 핵심 수정
available_models = []
model_display_names = []
model_name_map = {}

if api_key:
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        for m in models:
            # generateContent 가능한 모델만
            if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                # m.name 예: "models/gemini-2.0-flash"
                name = m.name
                display = name.replace("models/", "")
                available_models.append(name)
                model_display_names.append(display)
                model_name_map[display] = name
    except Exception as e:
        st.warning(f"모델 목록을 불러오지 못했습니다: {e}")

with st.expander("⚙️ AI 모델 선택 (서버에서 실제 사용 가능한 모델만 표시)"):
    if not api_key:
        st.info("먼저 API Key를 입력하세요.")
        manual_model_display = None
    elif not model_display_names:
        st.error("이 API Key로 사용할 수 있는 모델이 없습니다. (listModels 결과가 비어있음)")
        manual_model_display = None
    else:
        # 기본 추천 우선순위: 1.5-flash → 2.0-flash → 첫 번째
        default_idx = 0
        for preferred in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-2.0-pro"]:
            if preferred in model_display_names:
                default_idx = model_display_names.index(preferred)
                break

        manual_model_display = st.selectbox(
            "사용할 모델",
            model_display_names,
            index=default_idx
        )

# --- 7. 실행 ---
st.markdown("")
if st.button("✨ 과목 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not sem1_input and not sem2_input:
        st.warning("⚠️ 1학기 내용 또는 2학기 내용을 입력해주세요!")
    elif manual_model_display is None:
        st.error("⚠️ 호출할 모델을 선택할 수 없습니다. (모델 목록 확인 필요)")
    else:
        with st.spinner('1학기 요약 및 2학기 심화 활동(기고문/북리뷰/AI) 작성 중...'):
            try:
                genai.configure(api_key=api_key)

                target_model = model_name_map[manual_model_display]  # "models/..." 형태
                temp = 0.2 if "엄격하게" in mode else 0.75

                model = genai.GenerativeModel(
                    model_name=target_model,
                    generation_config={"temperature": temp}
                )

                prompt_text = f"""
당신은 입학사정관이 주목하는 고등학교 교사입니다. 학생의 [1학기 기존 세특]과 [2학기 신규 활동]을 통합하여, 전체 분량 약 {target_length}자의 '과목 세특'을 작성하세요.

[입력 데이터]
1. 1학기 내용: {sem1_input}
2. 2학기 활동 키워드: {sem2_input}
3. 모드: {mode}

[★ 필수 반영: 2학기 활동 내용]
입력된 2학기 키워드를 바탕으로 다음 3가지 활동을 구체적으로 서술하세요 (전체 분량의 70% 비중).
1. **신문기사 기고문 작성**: 관련 분야 기사를 읽고 심층 분석하여 자신의 견해를 논리적으로 기고문으로 작성함.
2. **원서 북리뷰**: 원서(책)를 읽고 핵심 내용을 비평하거나 주제를 확장하여 보고서를 작성함.
3. **AI 도구 활용**: 인공지능 도구(ChatGPT 등)를 활용하여 사고를 확장하고, 그 과정에서 느낀점이나 한계를 서술함.

[★ 필수 반영: 문체 및 스타일]
- **고급 어휘 사용**: 해당 교과목의 전문 용어와 고급 어휘를 맥락에 맞게 구사할 것.
- **논리적 서술**: "구체적 사례를 들어 ~의 위험성을 제시하고, ~의 필요성을 설득력 있게 전달함"과 같은 구조 사용.
- **문장 구조**: 단순 나열이 아닌, [동기 -> 심화탐구(분석) -> 결과 및 확장]의 흐름 유지.
- 종결 어미: '~함', '~임', '~보임', '~드러냄' (명사형 종결).

[작성 지침]
Step 1: 1학기 내용은 핵심 역량 위주로 요약하여 앞부분에 배치 (30% 이내).
Step 2: 2학기 3대 활동(기고문, 북리뷰, AI)을 구체적으로 창작/서술하여 뒷부분에 배치 (70% 이상).
Step 3: 두 학기 내용이 하나의 스토리처럼 자연스럽게 연결되도록 작성.

[출력 양식]
1. 활동 분석 (1학기 요약 포인트 / 2학기 반영 포인트)
---SPLIT---
2. 최종 과목 세특 (제출용 줄글)
"""

                response = model.generate_content(prompt_text)

                # 응답 텍스트 추출(버전 방어)
                if hasattr(response, "text") and response.text:
                    full_text = response.text
                else:
                    try:
                        full_text = response.candidates[0].content.parts[0].text
                    except Exception:
                        raise RuntimeError("AI 응답에서 텍스트를 가져오지 못했습니다.")

                if "---SPLIT---" in full_text:
                    parts = full_text.split("---SPLIT---")
                    analysis_text = parts[0].strip()
                    final_text = parts[1].strip()
                else:
                    analysis_text = "분석 내용 없음"
                    final_text = full_text

                char_count = len(final_text)
                char_count_no_space = len(final_text.replace(" ", "").replace("\n", ""))
                byte_count = sum(3 if ord(c) > 127 else 1 for c in final_text)

                st.success("작성 완료!")

                with st.expander("🔍 활동 분석 및 전략 보기", expanded=True):
                    st.markdown(analysis_text)

                st.markdown("---")
                st.markdown(f"""
                <div class="count-box">
                    📊 목표: {target_length}자 | <b>실제: {char_count}자</b> (공백제외 {char_count_no_space}자)<br>
                    💾 <b>용량: {byte_count} Bytes</b> (NEIS 기준)
                </div>
                """, unsafe_allow_html=True)

                st.caption(f"※ {mode} 모드 동작 중 ({manual_model_display})")
                st.text_area("최종 결과 (생활기록부 입력용)", value=final_text, height=400)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

                # 자주 나는 케이스 안내
                msg = str(e)
                if "404" in msg or "not found" in msg:
                    st.error("🚨 모델 404: 이 키/환경에서 해당 모델이 제공되지 않습니다. (모델 목록에서 다른 모델을 선택해보세요)")
                if "429" in msg or "ResourceExhausted" in msg:
                    st.error("🚨 429(쿼터/요청 한도) 초과: Google AI Studio/콘솔에서 Rate limit/결제/쿼터를 확인하세요.")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. All rights reserved.<br>
</div>
""", unsafe_allow_html=True)
