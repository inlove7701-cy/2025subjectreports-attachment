import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 영어 세특 메이트 (1/2학기 통합)",
    page_icon="🅰️",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS (기존 유지) ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; color: #2F4F3A; } 
    .subtitle { font-size: 16px; color: #666; margin-top: -15px; margin-bottom: 30px; }
    .stButton button { background-color: #557C64 !important; color: white !important; border-radius: 10px; font-weight: bold; padding: 0.8rem 1rem; width: 100%; }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; text-align: right; border: 1px solid #C4D7CD; }
    .semester-header { color: #2F4F3A; font-weight: bold; margin-bottom: 5px; border-bottom: 2px solid #557C64; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("🇬🇧 2025 영어과목 세특 메이트")
st.markdown("<p class='subtitle'>English Subject: 1학기 요약 & 2학기 심화 생성</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <b>💡 영어 세특 작성 가이드</b><br>
    <b>1학기 (요약):</b> 수행평가, 지문 분석 등 활동 팩트 위주로 압축합니다.<br>
    <b>2학기 (생성):</b> 영어 원서 독해, 에세이 작성, TED 분석 등 <b>언어적 역량</b>을 구체화합니다.<br>
    ※ 1, 2학기 합계 <b>500자(1500바이트) 미만</b>으로 자동 조절됩니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (1학기/2학기 분리) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="semester-header">📝 1학기 (내용 줄이기)</p>', unsafe_allow_html=True)
    input_sem1 = st.text_area(
        "1학기",
        height=250,
        placeholder="예: '환경 보호' 영문 기사 읽기 수행평가에서 플라스틱 문제의 심각성을 다룬 기사를 요약하고 발표함. 관계대명사를 활용하여...",
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<p class="semester-header">✨ 2학기 (새로 만들기)</p>', unsafe_allow_html=True)
    input_sem2 = st.text_area(
        "2학기",
        height=250,
        placeholder="예: 관심 진로인 'AI' 관련 TED 강연을 시청함. 기술 발전의 양면성에 대해 영어로 에세이를 작성하고, 학급 친구들과 토론함.", 
        label_visibility="collapsed"
    )

# --- 6. 옵션 설정 ---
st.markdown("### 작성 옵션 설정")

# [카드] 영어 교과 전용 키워드
with st.container(border=True):
    st.markdown('<p class="card-title">🎯 2학기 강조 역량 (영어과 핵심 역량)</p>', unsafe_allow_html=True)
    filter_options = [
        "🗣️ 유창한 의사소통(Speaking)", "📖 비판적 독해(Reading)", "✍️ 논리적 영작(Writing)", 
        "👂 직청직해(Listening)", "🌍 문화적 소양/다양성", "📚 심화 어휘 활용", 
        "🛠️ 문법/구문 응용력", "🤝 협력적 문제해결", "🔗 진로 연계 심화탐구"
    ]
    try:
        selected_tags = st.pills("키워드 버튼", options=filter_options, selection_mode="multi", label_visibility="collapsed")
    except Exception:
        selected_tags = st.multiselect("키워드 선택", filter_options, label_visibility="collapsed")

# [고급 설정]
with st.expander("⚙️ 고급 설정 (모델 & 글자 수)"):
    manual_model = st.selectbox("AI 모델", ["🤖 자동 (Flash)", "⚡ 고성능 (Pro)"], index=0)
    target_total_length = st.slider("총 글자 수 목표 (공백 포함)", 300, 1000, 480, step=10)

# --- 7. 실행 및 결과 영역 ---
st.markdown("")
if st.button("✨ 영어 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 필요합니다.")
    elif not input_sem1 and not input_sem2:
        st.warning("⚠️ 최소한 하나의 학기 내용은 입력해주세요.")
    else:
        with st.spinner('English Teacher 모드로 분석 중입니다...'):
            try:
                genai.configure(api_key=api_key)
                model_name = "gemini-1.5-pro" if "pro" in manual_model else "gemini-1.5-flash"
                tags_str = f"강조 키워드: {', '.join(selected_tags)}" if selected_tags else "강조 키워드: 영어 독해 및 표현 능력"

                # [영어과 특화 프롬프트]
                prompt = f"""
                당신은 고등학교 **'영어' 교과 담당 교사**입니다. 
                학생의 1년간의 활동을 바탕으로 생기부 세특(세부능력 및 특기사항)을 작성해야 합니다.

                # 입력 데이터
                [1학기 기존 내용]: {input_sem1 if input_sem1 else "(내용 없음)"}
                [2학기 관찰 내용]: {input_sem2 if input_sem2 else "(내용 없음)"}
                [2학기 강조점]: {tags_str}

                # ★★★ 핵심 미션 ★★★
                **1학기와 2학기 결과물의 합계가 공백 포함 {target_total_length}자 내외(최대 500자 미만)**가 되도록 작성하세요.

                # 영어과 작성 지침 (English Subject Guidelines)
                1. **[1학기 - 요약]**: 입력된 내용에서 핵심 활동(주제)과 어법성/태도만 남기고 문장을 간결하게 줄이십시오.
                2. **[2학기 - 심화 생성]**: 
                   - 단순 활동 나열 금지. **'어떤 영어 자료(원서, 기사, TED)를 접하고 -> 어떤 어휘/구문을 활용하여 -> 자신의 생각을 어떻게 표현(에세이, 발표)했는지'** 구체적으로 서술하세요.
                   - 학생의 진로와 연계된 주제를 영어로 탐구한 과정을 부각하세요.
                3. **[표현 어휘]**: '영문 기사를 분석함', '논리적으로 서술함', '유창하게 발표함', '문맥을 정확히 파악함', '자신의 견해를 영어로 피력함' 등 교과 특화 용어를 사용하세요.

                # 출력 형식 (Strict format)
                ---1학기---
                (1학기 내용)
                ---2학기---
                (2학기 내용)
                """

                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                full_text = response.text

                # 파싱 및 출력
                try:
                    parts = full_text.split("---2학기---")
                    sem1_result = parts[0].replace("---1학기---", "").strip()
                    sem2_result = parts[1].strip() if len(parts) > 1 else ""
                except:
                    sem1_result = full_text
                    sem2_result = "생성 오류 발생"

                total_len = len(sem1_result + sem2_result)
                total_bytes = sum(3 if ord(c) > 127 else 1 for c in (sem1_result + sem2_result))

                st.success("작성 완료!")
                st.markdown(f"""
                <div class="count-box">
                    📊 총 글자 수: <b>{total_len}자</b> (목표: {target_total_length}자) / 예상 {total_bytes} Bytes
                </div>
                """, unsafe_allow_html=True)

                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.info("📉 1학기 (Summary)")
                    st.text_area("1학기", value=sem1_result, height=350)
                with r_col2:
                    st.success("📈 2학기 (Deep Learning)")
                    st.text_area("2학기", value=sem2_result, height=350)

            except Exception as e:
                st.error(f"Error: {e}")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. English Dept Edition.<br>
</div>
""", unsafe_allow_html=True)
