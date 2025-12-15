import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 과목세특 메이트 (1+2학기 통합)",
    page_icon="📚",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; letter-spacing: -1px; color: #2F4F3A; } 
    .stButton button { 
        background-color: #557C64 !important; color: white !important;
        border-radius: 10px; font-weight: bold; border: none; 
        padding: 0.8rem 1rem; width: 100%; 
    }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    div[data-testid="stFileUploader"] { border: 1px dashed #557C64; border-radius: 10px; background-color: #F7F9F8; }
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; }
    .guide-title { font-weight: bold; color: #557C64; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; text-align: right; }
    .section-header { color: #2F4F3A; font-weight: bold; margin-top: 20px; margin-bottom: 10px; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("📚 2025 과목세특 메이트")
st.caption("1학기 내용을 요약하고 2학기 활동(기고문, 독서, AI활용)을 더해 완벽한 세특을 완성합니다.")
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 1+2학기 통합 작성 가이드</span><br>
    1. <b>1학기 내용</b>: 기존 내용이 길면 AI가 핵심만 남기고 압축 요약합니다.<br>
    2. <b>2학기 활동</b>: 신문 기고문, 독서 활동, AI 활용 탐구를 반영합니다.<br>
    3. <b>결과물</b>: 1학기와 2학기가 자연스럽게 연결된 <b>500자 내외</b>의 글이 완성됩니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (분리됨) ---

# [섹션 1] 1학기 내용
st.markdown('<div class="section-header">1️⃣ 1학기 세특 내용 (기존 작성분)</div>', unsafe_allow_html=True)
sem1_input = st.text_area(
    "1학기 내용 입력", height=150,
    placeholder="이미 작성된 1학기 세특 내용을 붙여넣으세요. (분량이 많을 경우 2학기 내용과 합쳐 500자가 되도록 자동으로 조절됩니다.)",
    label_visibility="collapsed"
)

# [섹션 2] 2학기 활동
st.markdown('<div class="section-header">2️⃣ 2학기 활동 내용 (신규 추가)</div>', unsafe_allow_html=True)
sem2_input = st.text_area(
    "2학기 활동 입력", height=150,
    placeholder="예: 'AI 윤리' 주제로 신문 기고문 작성, '호모 데우스' 독서 후 비평문 작성, 챗GPT를 활용한 영어 토론 활동 등",
    label_visibility="collapsed"
)

# 파일 업로더 (2학기 증빙용 - PDF/이미지)
uploaded_files = st.file_uploader(
    "📎 2학기 활동 증빙 자료 (이미지/PDF)", 
    type=["png", "jpg", "jpeg", "pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)}개의 파일이 첨부되었습니다.")

# --- 6. 옵션 설정 ---
st.markdown("### 📝 작성 옵션")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("작성 모드", ["✨ 풍성하게 (의미 부여)", "🛡️ 엄격하게 (팩트 중심)"], horizontal=True)
    with col2:
        # 모델 선택
        manual_model = st.selectbox("사용할 모델", ["⚡ gemini-1.5-flash (빠름)", "🤖 gemini-1.5-pro (고성능)"])

with st.container(border=True):
    target_length = st.slider("전체 목표 글자 수 (1학기+2학기)", 300, 1000, 500, 50)

# --- 7. 실행 로직 ---
if st.button("✨ 통합 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("API Key가 필요합니다.")
    elif not sem1_input and not sem2_input:
        st.warning("1학기 내용 또는 2학기 활동 내용을 입력해주세요.")
    else:
        with st.spinner("1학기 내용을 분석하고 2학기 내용을 작성 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                
                # [모델 설정]
                if "pro" in manual_model:
                    target_model = "gemini-1.5-pro"
                else:
                    target_model = "gemini-1.5-flash"
                
                model = genai.GenerativeModel(target_model)

                # [스타일 가이드]
                style_guide = """
                [필수 문체 및 스타일 가이드]
                1. 어조: 교사가 학생을 관찰하여 평가하는 객관적이고 전문적인 어조 (해요체 절대 금지).
                2. 종결 어미: 문장의 끝은 '~함', '~임', '~보임', '~드러냄' 등으로 간결하게 끝맺음.
                3. 문장 구조: '활동 동기 -> 구체적 탐구 활동(분석, 적용) -> 심화 학습/결과 -> 배우고 느낀 점(성장)'의 흐름.
                4. 표현: "탁월함", "돋보임", "논리적으로 서술함" 등 학생의 역량을 긍정적으로 평가하는 어휘 사용.
                """

                # [프롬프트 구성]
                base_prompt = f"""
                당신은 고등학교 교사입니다. 학생의 [1학기 기존 세특]과 [2학기 신규 활동]을 결합하여, 전체 분량 공백 포함 약 {target_length}자 내외의 '통합 과목 세특'을 작성하세요.

                {style_guide}

                [입력 데이터]
                1. 1학기 기존 내용: {sem1_input if sem1_input else "없음"}
                2. 2학기 신규 활동: {sem2_input} 
                   (주요 활동 예시: 신문 기고문 작성, 독서 북리뷰, AI 도구 활용 개별 활동 등)
                3. 작성 모드: {mode}

                [작성 지침]
                Step 1: 1학기 내용은 핵심만 요약하여 앞부분에 배치 (약 30~40% 비중).
                Step 2: 2학기 활동(기고문, 독서, AI)을 구체적으로 서술하여 뒷부분에 배치.
                Step 3: 두 내용이 자연스럽게 이어지도록 하고, 전체 {target_length}자 내외로 작성.

                [출력 양식]
                1. 작성 전략 (간단 요약)
                ---SPLIT---
                2. 최종 과목 세특 (생활기록부 입력용)
                """

                # 멀티모달 콘텐츠 구성
                contents = [base_prompt]

                if uploaded_files:
                    for f in uploaded_files:
                        bytes_data = f.getvalue()
                        if f.type == "application/pdf":
                            contents.append({"mime_type": "application/pdf", "data": bytes_data})
                        elif f.type.startswith("image/"):
                            contents.append({"mime_type": f.type, "data": bytes_data})

                # AI 호출
                response = model.generate_content(contents)
                full_text = response.text

                # 결과 분리
                if "---SPLIT---" in full_text:
                    parts = full_text.split("---SPLIT---")
                    analysis = parts[0].strip()
                    body = parts[1].strip()
                else:
                    analysis = "분석 내용 생성 실패"
                    body = full_text

                # 글자 수 및 바이트 계산 (안전한 방식으로 수정됨)
                char_len = len(body)
                byte_len = len(body.encode('utf-8')) # UTF-8 바이트 계산

                st.success("작성 완료!")
                
                with st.expander("🔍 작성 전략 보기 (AI 분석)", expanded=True):
                    st.markdown(analysis)
                
                st.markdown("---")
                # 결과 출력
                st.markdown(f'<div class="count-box">📊 글자 수: {char_len}자 | 💾 {byte_len} Bytes</div>', unsafe_allow_html=True)
                st.text_area("최종 결과 (생활기록부 입력용)", value=body, height=400)
                st.caption(f"Used Model: {target_model}")

            except Exception as e:
                st.error(f"오류 발생: {e}")
                # 사용자 친화적 에러 메시지
                if "404" in str(e):
                    st.error("🚨 중요: Streamlit Cloud에서 'requirements.txt' 파일이 없거나 내용이 잘못되었습니다. 위 가이드를 다시 확인해주세요.")
