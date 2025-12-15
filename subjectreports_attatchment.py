import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from pypdf import PdfReader  # PDF 처리를 위한 라이브러리 추가

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 과목세특 메이트 (1+2학기 통합)",
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
    
    /* 가이드 박스 등 기타 스타일 */
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; line-height: 1.6; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .guide-title { font-weight: bold; margin-bottom: 8px; display: block; font-size: 15px; color: #557C64;}
    .warning-text { color: #8D6E63; font-size: 14px; margin-top: 5px; font-weight: 500; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 10px; text-align: right; border: 1px solid #C4D7CD; }
    .footer { margin-top: 50px; text-align: center; font-size: 14px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }
    .card-title { font-size: 15px; font-weight: 700; color: #557C64; margin-bottom: 10px; }
    
    /* 파일 업로더 스타일 */
    div[data-testid="stFileUploader"] { border: 1px dashed #557C64; border-radius: 10px; background-color: #F7F9F8; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("📚 2025 과목세특 메이트")
st.markdown("<p class='subtitle'>1학기 요약 + 2학기 심화 활동 통합 생성기</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 1+2학기 통합 작성 가이드</span>
    1. <b>1학기</b>: 기존 내용이 길면 AI가 핵심만 남기고 <b>30% 비중으로 요약</b>합니다.<br>
    2. <b>2학기</b>: <b>첨부 자료(PDF/이미지)</b>와 텍스트를 분석해 구체적으로 확장합니다.<br>
    3. <b>결과</b>: 두 내용이 자연스럽게 이어지는 하나의 완결된 글(약 500자)을 만듭니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (분리됨) ---

# [섹션 1] 1학기 내용
st.markdown("### 1. 1학기 기존 세특 (요약용)")
sem1_input = st.text_area(
    "1학기 입력창", height=120,
    placeholder="이미 작성된 1학기 세특 내용을 붙여넣으세요. (내용이 길 경우 자동으로 핵심만 요약됩니다)",
    label_visibility="collapsed"
)

# [섹션 2] 2학기 활동
st.markdown("### 2. 2학기 신규 활동 (심화/확장용)")
sem2_input = st.text_area(
    "2학기 입력창", height=150,
    placeholder="예: 'AI 윤리' 주제로 신문 기고문 작성, 독서 비평문 등 구체적인 활동 개요를 적어주세요.",
    label_visibility="collapsed"
)

# [파일 업로더] 2학기 증빙용
uploaded_files = st.file_uploader(
    "📎 2학기 활동 증빙 자료 (이미지/PDF)", 
    type=["png", "jpg", "jpeg", "pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)}개의 파일이 첨부되었습니다.")

# --- 6. 옵션 설정 ---
st.markdown("### 3. 작성 옵션 설정")

# [카드 1] 모드 선택
with st.container(border=True):
    st.markdown('<p class="card-title">① 작성 모드 선택</p>', unsafe_allow_html=True)
    mode = st.radio(
        "모드",
        ["✨ 풍성하게 (교육적 평가 추가)", "🛡️ 엄격하게 (팩트 중심)"],
        horizontal=True, 
        label_visibility="collapsed"
    )

# [카드 2] 희망 분량
with st.container(border=True):
    st.markdown('<p class="card-title">② 전체 목표 분량 (1학기+2학기 합산)</p>', unsafe_allow_html=True)
    target_length = st.slider(
        "글자 수",
        min_value=300, max_value=1000, value=500, step=50,
        label_visibility="collapsed"
    )

# [카드 3] 강조 키워드
with st.container(border=True):
    st.markdown('<p class="card-title">③ 강조할 학업 역량</p>', unsafe_allow_html=True)
    filter_options = [
        "👑 AI 자동 판단", 
        "🔎 비판적 사고력", "📊 데이터 분석", "💡 창의적 문제해결", 
        "📚 심화 탐구", "🗣️ 논리적 소통", "🤝 협업/리더십", 
        "🔗 진로 연계", "📖 자기주도성"
    ]
    try:
        selected_tags = st.pills("키워드", options=filter_options, selection_mode="multi", label_visibility="collapsed")
    except Exception:
        selected_tags = st.multiselect("키워드", filter_options, label_visibility="collapsed")

# [고급 설정] 모델 선택
st.markdown("")
with st.expander("⚙️ AI 모델 선택 (고급 설정)"):
    manual_model = st.selectbox(
        "사용할 모델",
        ["🤖 자동 (Auto)", "⚡ gemini-1.5-flash", "🤖 gemini-1.5-pro"]
    )

# --- 7. 실행 및 결과 영역 ---
st.markdown("")
if st.button("✨ 통합 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not sem1_input and not sem2_input:
        st.warning("⚠️ 1학기 내용 또는 2학기 활동 내용을 입력해주세요.")
    else:
        with st.spinner('1학기 내용을 요약하고 자료를 분석하여 세특을 작성 중입니다...'):
            try:
                genai.configure(api_key=api_key)

                # --- 모델 선택 로직 (최신 모델명 반영) ---
                # 주의: gemini-2.5는 아직 정식 출시 전일 수 있어 1.5로 고정합니다.
                target_model = "gemini-1.5-flash" 

                if "pro" in manual_model:
                    target_model = "gemini-1.5-pro"
                elif "flash" in manual_model:
                    target_model = "gemini-1.5-flash"
                elif "자동" in manual_model:
                    # 파일이 있으면 성능 좋은 Pro, 없으면 빠른 Flash
                    target_model = "gemini-1.5-pro" if uploaded_files else "gemini-1.5-flash"

                # [파일 처리 로직]
                files_content = []  # 이미지 저장용
                pdf_text_extracted = ""  # PDF 텍스트 저장용

                if uploaded_files:
                    for f in uploaded_files:
                        bytes_data = f.getvalue()
                        # PDF 처리
                        if f.type == "application/pdf":
                            try:
                                pdf_reader = PdfReader(io.BytesIO(bytes_data))
                                for page in pdf_reader.pages:
                                    extracted = page.extract_text()
                                    if extracted:
                                        pdf_text_extracted += extracted + "\n"
                            except Exception as e:
                                st.warning(f"PDF 읽기 실패 ({f.name}): {e}")
                        # 이미지 처리 (Gemini에게 직접 전송)
                        elif f.type.startswith("image/"):
                            image = Image.open(io.BytesIO(bytes_data))
                            files_content.append(image)

                # 키워드 처리
                if not selected_tags:
                    tags_str = "별도 지정 없음. 자연스러운 흐름 중시."
                else:
                    tags_str = f"강조 키워드: {', '.join(selected_tags)}"

                # [핵심] 프롬프트 구성
                prompt_instruction = f"""
                당신은 고등학교 교사입니다. 학생의 [1학기 기존 세특]과 [2학기 신규 활동]을 통합하여, 전체 분량 공백 포함 약 {target_length}자(±10%)의 '과목 세특'을 작성하세요.

                [입력 데이터]
                1. 1학기 내용: {sem1_input if sem1_input else "없음"}
                2. 2학기 활동 개요: {sem2_input}
                3. 2학기 증빙 자료(PDF 내용): {pdf_text_extracted if pdf_text_extracted else "없음"}
                4. 강조 역량: {tags_str}
                5. 작성 모드: {mode}

                [작성 전략 - 매우 중요]
                Step 1 (1학기 요약):
                - 입력된 1학기 내용이 길다면, 핵심 활동과 역량 위주로 요약하여 **전체 글의 30% 이내**로 줄이세요.
                - 단, 문맥이 끊기지 않게 자연스럽게 서술하세요.

                Step 2 (2학기 심화 서술):
                - 2학기 활동(기고문, 독서, AI 활용 등)과 첨부된 자료 내용을 바탕으로 구체적으로 서술하세요.
                - **전체 글의 70% 이상**을 2학기 내용으로 풍성하게 채우세요.
                - 전문 용어, 구체적 수치, 활동의 결과(성장)를 반드시 포함하세요.

                Step 3 (통합 및 문체):
                - 1학기와 2학기 내용이 하나의 글처럼 매끄럽게 연결되도록 하세요.
                - 문체: '~함', '~임', '~보임', '~분석함' 등 개조식과 줄글의 조화 (생기부 표준).

                [출력 양식]
                1. 구성 분석 (1학기 요약 포인트 / 2학기 확장 포인트 간단 정리)
                ---SPLIT---
                2. 최종 과목 세특 (바로 생활기록부에 입력 가능한 줄글)
                """

                # 멀티모달 입력 리스트 생성
                request_content = [prompt_instruction]
                if files_content:
                    request_content.extend(files_content)  # 이미지가 있으면 추가

                # AI 호출
                model = genai.GenerativeModel(target_model)
                response = model.generate_content(request_content)
                full_text = response.text
                
                # 결과 분리
                if "---SPLIT---" in full_text:
                    parts = full_text.split("---SPLIT---")
                    analysis_text = parts[0].strip()
                    final_text = parts[1].strip()
                else:
                    analysis_text = "분석 내용 없음"
                    final_text = full_text

                # 글자 수 및 바이트 계산 (안전한 방식 사용)
                char_count = len(final_text)
                char_count_no_space = len(final_text.replace(" ", "").replace("\n", ""))
                byte_count = len(final_text.encode('utf-8')) # UTF-8 바이트 계산 (가장 정확)
                
                st.success("작성 완료!")
                
                with st.expander("🔍 작성 전략(요약 및 확장) 확인하기", expanded=True):
                    st.markdown(analysis_text)
                
                st.markdown("---")
                st.markdown("### 📋 최종 제출용 종합본")

                st.markdown(f"""
                <div class="count-box">
                    📊 목표: {target_length}자 | <b>실제: {char_count}자</b> (공백제외 {char_count_no_space}자)<br>
                    💾 <b>용량: {byte_count} Bytes</b> (UTF-8 기준)
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"※ {mode.split()[1]} 모드 동작 중 ({target_model})")
                st.text_area("결과 (복사해서 나이스에 붙여넣으세요)", value=final_text, height=350)

            except Exception as e:
                # 에러 처리
                st.error(f"오류가 발생했습니다: {e}")
                if "404" in str(e):
                    st.error("🚨 중요: requirements.txt 파일에 'pypdf'와 'google-generativeai>=0.8.0'이 있는지 확인하고 앱을 Reboot 해주세요.")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. All rights reserved.<br>
    문의: <a href="mailto:inlove11@naver.com" style="color: #888; text-decoration: none;">inlove11@naver.com</a>
</div>
""", unsafe_allow_html=True)

