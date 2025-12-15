import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
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
st.caption("1학기 내용을 요약하고 2학기 활동을 더해 완벽한 세특을 완성합니다.")
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 1+2학기 통합 작성 가이드</span><br>
    1. <b>1학기 내용</b>: 기존에 작성된 내용이 길다면 AI가 핵심만 남기고 요약합니다.<br>
    2. <b>2학기 활동</b>: 기고문, 독서, AI 활용 활동을 입력하면 자연스럽게 이어 씁니다.<br>
    3. <b>결과물</b>: 두 학기 내용이 유기적으로 연결된 하나의 완결된 글이 생성됩니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (분리됨) ---

# [섹션 1] 1학기 내용
st.markdown('<div class="section-header">1️⃣ 1학기 세특 내용 (기존 작성분)</div>', unsafe_allow_html=True)
sem1_input = st.text_area(
    "1학기 내용 입력", height=120,
    placeholder="이미 작성된 1학기 세특 내용을 붙여넣으세요. (내용이 길 경우 자동으로 요약됩니다)",
    label_visibility="collapsed"
)

# [섹션 2] 2학기 활동
st.markdown('<div class="section-header">2️⃣ 2학기 활동 내용 (신규 추가)</div>', unsafe_allow_html=True)
sem2_input = st.text_area(
    "2학기 활동 입력", height=120,
    placeholder="예: 'AI 윤리' 주제로 신문 기고문 작성, '호모 데우스' 독서 후 비평문 작성, 챗GPT를 활용한 영어 토론 활동 등",
    label_visibility="collapsed"
)

# 파일 업로더 (2학기 증빙용)
uploaded_files = st.file_uploader(
    "📎 2학기 활동 증빙 자료 (이미지/PDF)", 
    type=["png", "jpg", "jpeg", "pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)}개의 2학기 활동 자료가 첨부되었습니다.")

# --- 6. 옵션 설정 ---
st.markdown("### 📝 작성 옵션")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("작성 모드", ["✨ 풍성하게 (의미 부여)", "🛡️ 엄격하게 (팩트 중심)"], horizontal=True)
    with col2:
        # 모델 선택 로직 개선
        manual_model = st.selectbox("사용할 모델", ["🤖 자동 (Auto)", "⚡ gemini-1.5-flash", "🤖 gemini-1.5-pro"])

with st.container(border=True):
    target_length = st.slider("전체 목표 글자 수 (1학기+2학기 합산)", 400, 1500, 500, 50)

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
                
                # [모델 설정] models/ 접두사 추가하여 안정성 확보
                target_model = "models/gemini-1.5-flash" 
                
# --- [수정된 모델 선택 로직] ---
                # 1.5 모델의 최신 별칭(alias)을 사용하여 호환성을 높입니다.
                if "pro" in manual_model:
                    target_model = "gemini-1.5-pro-latest"
                elif "flash" in manual_model:
                    target_model = "gemini-1.5-flash-latest"
                elif "자동" in manual_model:
                    target_model = "gemini-1.5-pro-latest" if uploaded_files else "gemini-1.5-flash-latest"
                
                # 모델 설정 (이름 그대로 사용)
                model = genai.GenerativeModel(target_model)

                # [스타일 가이드] 사용자가 제공한 이미지의 문체 분석 반영
                style_guide = """
                [문체 및 스타일 가이드]
                - 어조: 구체적이고 전문적인 어휘를 사용하며, 교사가 학생을 평가하는 객관적이면서도 긍정적인 어조.
                - 종결 어미: '~함', '~임', '~보임' 등 개조식 문체와 줄글의 조화.
                - 문장 구조: '활동 명(주제) -> 구체적 행동(분석, 적용) -> 결과 및 변화(성장)'의 구조를 가짐.
                - 예시 문구: "고급 어휘를 맥락에 맞게 사용하였으며... 설득력 있게 전달함.", "현상에 대한 호기심을 보이며..."
                """

                # [프롬프트 구성]
                base_prompt = f"""
                당신은 고등학교 교사입니다. 학생의 [1학기 기존 세특]과 [2학기 신규 활동]을 결합하여, 전체 분량 {target_length}자 내외의 '통합 과목 세특'을 작성하세요.

                {style_guide}

                [입력 데이터]
                1. 1학기 기존 내용: {sem1_input if sem1_input else "없음"}
                2. 2학기 신규 활동: {sem2_input} (주요 활동: 신문 기고문, 독서 북리뷰, AI 도구 활용)
                3. 작성 모드: {mode}

                [작성 지침 - 매우 중요]
                Step 1 (1학기 요약/조정):
                - 입력된 1학기 내용이 전체 목표 분량의 40%를 넘거나 내용이 장황하다면, 핵심 키워드(동기, 주요 탐구) 위주로 압축 요약하세요.
                - 문맥이 끊기지 않게 다듬으세요.

                Step 2 (2학기 내용 생성):
                - 입력된 [2학기 신규 활동]과 [첨부 파일 내용]을 바탕으로 내용을 창작하세요.
                - 활동 예시: 신문 기고문(주제 구체화), 북리뷰(비판적 사고), AI 도구 활용(디지털 역량).
                - 1학기 내용 뒤에 자연스럽게 이어지도록 작성하세요.

                Step 3 (통합 출력):
                - [1학기 요약분] + [2학기 생성분]을 합쳐 하나의 완성된 글을 만드세요.
                - 전체 글자 수는 공백 포함 약 {target_length}자를 목표로 하세요.

                [출력 양식]
                1. 구성 분석 (1학기 요약 내용 / 2학기 반영 내용 간단 정리)
                ---SPLIT---
                2. 최종 과목 세특 (바로 생활기록부에 입력 가능한 줄글 형태)
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

                # 글자 수 계산 (변수명 수정 완료)
                char_len = len(body)
                byte_len = sum(3 if ord(c) > 127 else 1 for c in body) # 한글 3바이트 기준

                st.success("작성 완료!")
                
                with st.expander("🔍 구성 분석 보기", expanded=True):
                    st.markdown(analysis)
                
                st.markdown("---")
                # 수정된 변수 사용 (byte_len)
                st.markdown(f'<div class="count-box">📊 글자 수: {char_len}자 | 💾 {byte_len} Bytes</div>', unsafe_allow_html=True)
                st.text_area("최종 결과 (수정 및 복사해서 사용하세요)", value=body, height=400)
                st.caption(f"Used Model: {target_model}")

            except Exception as e:
                st.error(f"오류 발생: {e}")
                if "404" in str(e):
                    st.error("🚨 모델을 찾을 수 없습니다. (gemini-1.5-flash가 활성화된 API 키인지 확인하세요.)")

