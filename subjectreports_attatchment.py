import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 영어 세특 메이트 (Lite)",
    page_icon="🅰️",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; color: #2F4F3A; } 
    .subtitle { font-size: 16px; color: #666; margin-top: -15px; margin-bottom: 30px; }
    .stButton button { background-color: #557C64 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; padding: 0.8rem; }
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
st.title("🇬🇧 영어 세특 메이트 (Lite)")
st.markdown("<p class='subtitle'>English Subject: 1학기 요약 + 2학기 생성 (Total 500자)</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <b>💡 사용 가이드</b><br>
    <b>1. 1학기 (Diet):</b> 기존에 작성된 긴 내용을 넣으면 핵심만 남겨서 <b>요약</b>합니다.<br>
    <b>2. 2학기 (Bulk-up):</b> 키워드나 활동(독서, TED, 영작)을 넣으면 <b>구체적으로 작성</b>합니다.<br>
    👉 결과물은 두 학기를 합쳐 <b>500자(약 1500byte) 미만</b>으로 자동 조절됩니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (좌우 분할) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="semester-header">📝 1학기 (요약하기)</p>', unsafe_allow_html=True)
    input_sem1 = st.text_area(
        "1학기",
        height=250,
        placeholder="이미 써둔 1학기 세특을 붙여넣으세요.\n(AI가 핵심 내용만 남기고 줄여줍니다.)",
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<p class="semester-header">✨ 2학기 (새로쓰기)</p>', unsafe_allow_html=True)
    input_sem2 = st.text_area(
        "2학기",
        height=250,
        placeholder="2학기 활동 소재를 입력하세요.\n예: AI 윤리 관련 영문 기사 읽고 에세이 작성, 진로 관련 TED 시청 후 발표.", 
        label_visibility="collapsed"
    )

# --- 6. 옵션 설정 ---
st.markdown("### 🎯 2학기 강조 키워드")
filter_options = [
    "🗣️ 유창한 말하기(Speaking)", "📖 심화 독해(Reading)", "✍️ 논리적 글쓰기(Writing)", 
    "👂 직청직해(Listening)", "🌍 문화적 이해", "📚 고급 어휘 활용", 
    "🛠️ 문법 응용력", "🔗 진로 연계 탐구"
]
try:
    selected_tags = st.pills("키워드 버튼", options=filter_options, selection_mode="multi", label_visibility="collapsed")
except:
    selected_tags = st.multiselect("키워드 선택", filter_options, label_visibility="collapsed")

# --- 7. 실행 로직 ---
st.markdown("")
if st.button("✨ 영어 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not input_sem1 and not input_sem2:
        st.warning("⚠️ 입력창에 내용을 적어주세요.")
    else:
        with st.spinner('AI 영어 선생님이 세특을 작성 중입니다...'):
            try:
                genai.configure(api_key=api_key)
                
                # 프롬프트 설정
                tags_str = f"2학기 강조점: {', '.join(selected_tags)}" if selected_tags else "2학기 강조점: 영어 종합 역량"
                
                prompt = f"""
                당신은 고등학교 영어 교사입니다. 학생의 생기부 세특을 작성해주세요.

                # 입력 데이터
                [1학기 원본]: {input_sem1 if input_sem1 else "없음"}
                [2학기 소재]: {input_sem2 if input_sem2 else "없음"}
                [2학기 키워드]: {tags_str}

                # ★★★ 핵심 목표 ★★★
                **1학기 결과물과 2학기 결과물을 합쳤을 때, 공백 포함 450~490자(최대 500자 미만)**가 되도록 분량을 조절하세요.

                # 작성 전략
                1. **[1학기 처리 - 요약]**: 입력된 내용이 있다면, 문법적 오류를 수정하고 중복된 표현을 제거하여 **간결하게 요약**하세요. (팩트 위주)
                2. **[2학기 처리 - 생성]**: 입력된 소재와 키워드를 바탕으로, **'동기-탐구(원서/기사)-과정(표현)-결과(성장)'** 흐름으로 구체적이고 풍성하게 작성하세요.
                3. **[문체]**: '~함', '~임', '~보임', '~분석함' (개조식 줄글)

                # 출력 형식 (반드시 지킬 것)
                ---1학기---
                (1학기 결과 텍스트)
                ---2학기---
                (2학기 결과 텍스트)
                """

                # 모델 호출 (Gemini 1.5 Flash 사용)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                full_text = response.text

                # 결과 파싱
                if "---2학기---" in full_text:
                    parts = full_text.split("---2학기---")
                    sem1_res = parts[0].replace("---1학기---", "").strip()
                    sem2_res = parts[1].strip()
                else:
                    sem1_res = full_text.replace("---1학기---", "").strip()
                    sem2_res = ""

                # 글자수/바이트 계산
                total_text = sem1_res + sem2_res
                char_len = len(total_text)
                byte_len = sum(3 if ord(c) > 127 else 1 for c in total_text)

                # 결과 화면
                st.success("작성 완료!")
                st.markdown(f"""
                <div class="count-box">
                    📊 총 글자 수: <b>{char_len}자</b> / 예상 바이트: <b>{byte_len} Bytes</b> (500자 목표)
                </div>
                """, unsafe_allow_html=True)

                r1, r2 = st.columns(2)
                with r1:
                    st.info("📉 1학기 (요약됨)")
                    st.text_area("1학기 결과", value=sem1_res, height=300)
                with r2:
                    st.success("📈 2학기 (생성됨)")
                    st.text_area("2학기 결과", value=sem2_res, height=300)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
