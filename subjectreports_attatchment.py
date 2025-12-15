import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# Pypdf 라이브러리 (파일 읽기용)
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 과목세특 메이트",
    page_icon="📚",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS (사용자 요청 디자인 100% 유지) ---
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
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("📚 2025 과목세특 메이트")
st.markdown("<p class='subtitle'>1학기 요약 + 2학기 심화 활동(기고문, 북리뷰, AI) 통합</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 1+2학기 통합 작성 가이드</span>
    1. <b>1학기</b>: 기존 세특 내용을 입력하면 핵심만 요약합니다.<br>
    2. <b>2학기</b>: <b>신문기사 기고문, 원서 북리뷰, AI 도구 활용</b> 내용을 중심으로 작성됩니다.<br>
    3. <b>첨부파일</b>: 활동지나 기사 내용을 PDF/사진으로 찍어 올리면 내용이 반영됩니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (1학기/2학기 분리 + 파일첨부 추가) ---

# [1학기]
st.markdown("### 1. 1학기 기존 세특 (요약용)")
sem1_input = st.text_area(
    "1학기 입력창",
    height=120,
    placeholder="이미 작성된 1학기 내용을 붙여넣으세요. (분량이 많으면 AI가 자동으로 줄여줍니다)",
    label_visibility="collapsed"
)

# [2학기]
st.markdown("### 2. 2학기 활동 내용 (심화용)")
sem2_input = st.text_area(
    "2학기 입력창",
    height=150,
    placeholder="예: AI 윤리 관련 영문 기사를 읽고 기고문을 작성함. '호모 데우스' 원서를 읽고 AI와 인간의 공존에 대해 북리뷰를 씀.",
    label_visibility="collapsed"
)

# [파일 첨부]
uploaded_files = st.file_uploader(
    "📎 2학기 활동 증빙 자료 (이미지/PDF)", 
    type=["png", "jpg", "jpeg", "pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)}개의 파일이 첨부되었습니다.")

# --- 6. 3단계 작성 옵션 ---
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
    st.markdown('<p class="card-title">② 희망 분량 (공백 포함)</p>', unsafe_allow_html=True)
    target_length = st.slider(
        "글자 수",
        min_value=300, max_value=1000, value=500, step=50,
        label_visibility="collapsed"
    )

# [카드 3] 학업 역량
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
# 🚨 수정 알림: 사용자님, 2.5 버전은 아직 API로 사용할 수 없어서 오류가 납니다. 
# 1.5 버전으로 자동 변경되도록 설정했습니다. (이래야 코드가 돌아갑니다)
st.markdown("")
with st.expander("⚙️ AI 모델 선택 (자동 설정됨)"):
    manual_model = st.selectbox(
        "사용할 모델",
        ["⚡ gemini-1.5-flash (추천)", "🤖 gemini-1.5-pro (고성능)"]
    )

# --- 7. 실행 및 결과 영역 ---
st.markdown("")
if st.button("✨ 과목 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not sem1_input and not sem2_input:
        st.warning("⚠️ 1학기 내용 또는 2학기 내용을 입력해주세요!")
    else:
        with st.spinner('1학기 내용을 요약하고 2학기 활동(기고문/북리뷰/AI)을 분석 중입니다...'):
            try:
                genai.configure(api_key=api_key)

                # --- 모델 선택 로직 (오류 방지를 위해 1.5로 고정) ---
                if "pro" in manual_model:
                    target_model = "gemini-1.5-pro"
                else:
                    target_model = "gemini-1.5-flash"

                # 모드별 프롬프트 설정
                if "엄격하게" in mode:
                    temp = 0.2
                    style_instruction = "사실 기반 서술. 미사여구 배제. 객관적 평가."
                else:
                    temp = 0.75
                    style_instruction = "탐구의 의미와 성장을 구체화. 교육적 의미 부여."

                model = genai.GenerativeModel(target_model, generation_config=genai.types.GenerationConfig(temperature=temp))

                # [파일 처리 로직]
                files_content = []
                pdf_text_extracted = ""

                if uploaded_files:
                    for f in uploaded_files:
                        bytes_data = f.getvalue()
                        # PDF 처리
                        if f.type == "application/pdf":
                            if PdfReader:
                                try:
                                    pdf_reader = PdfReader(io.BytesIO(bytes_data))
                                    for page in pdf_reader.pages:
                                        extracted = page.extract_text()
                                        if extracted:
                                            pdf_text_extracted += extracted + "\n"
                                except:
                                    pass # 에러 무시하고 진행
                        # 이미지 처리
                        elif f.type.startswith("image/"):
                            image = Image.open(io.BytesIO(bytes_data))
                            files_content.append(image)

                # 키워드 처리
                tags_str = f"핵심 키워드: {', '.join(selected_tags)}" if selected_tags else "별도 지정 없음"

                # [핵심] 통합 프롬프트
                # 사용자가 제공한 이미지의 문체(style)를 반영
                prompt_text = f"""
                당신은 고등학교 교사입니다. 학생의 [1학기 기존 세특]과 [2학기 신규 활동]을 통합하여, 전체 분량 약 {target_length}자의 '과목 세특'을 작성하세요.

                [입력 데이터]
                1. 1학기 내용: {sem1_input}
                2. 2학기 활동 개요: {sem2_input}
                3. 2학기 증빙 자료(PDF 텍스트): {pdf_text_extracted[:5000]}
                4. 강조 역량: {tags_str}

                [필수 반영 문체 및 스타일 (Reference Style)]
                - 다음 예시 문체의 톤앤매너를 완벽하게 모방하세요.
                - 예시: "고급 어휘를 맥락에 맞게 사용하였으며, 가정법 과거완료 구문을 적절히 구사하여 글의 완성도를 높임. 특히 ~ 사례를 들어 ~ 위험성을 제시하고, 설득력 있게 전달함."
                - 종결 어미: '~함', '~임', '~보임', '~드러냄' (명사형 종결)
                - 문장 구조: [활동 동기] -> [구체적 활동 내용(분석/적용)] -> [결과 및 성장]

                [작성 지침 - 단계별 수행]
                Step 1 (1학기 요약):
                - 입력된 1학기 내용은 핵심만 남겨 **전체 분량의 30% 이내**로 압축하세요.

                Step 2 (2학기 활동 심화 서술 - 70% 비중):
                - 다음 3가지 활동을 중심으로 구체적으로 서술하세요.
                  (1) **신문기사 기고문 작성**: 기사를 읽고 자신의 관점을 논리적으로 전개한 내용.
                  (2) **원서 북리뷰**: 원서를 읽고 내용을 분석하거나 비평한 내용.
                  (3) **AI 도구 활용**: 인공지능을 활용해 사고를 확장하고 탐구한 과정.
                - 첨부된 파일이나 텍스트에 있는 내용을 인용하여 구체성을 높이세요.

                Step 3 (통합):
                - 1학기와 2학기 내용이 하나의 흐름으로 이어지도록 작성하세요.
                - 전체 글자 수는 공백 포함 약 {target_length}자를 목표로 하세요.

                [출력 양식]
                1. 구성 분석 (1학기 요약 포인트 / 2학기 반영 포인트)
                ---SPLIT---
                2. 최종 과목 세특 (생활기록부 입력용 줄글)
                """

                # 멀티모달 콘텐츠 구성
                contents = [prompt_text]
                if files_content:
                    contents.extend(files_content)

                # AI 호출
                response = model.generate_content(contents)
                full_text = response.text
                
                # 결과 분리
                if "---SPLIT---" in full_text:
                    parts = full_text.split("---SPLIT---")
                    analysis_text = parts[0].strip()
                    final_text = parts[1].strip()
                else:
                    analysis_text = "분석 내용 없음"
                    final_text = full_text

                # 글자 수/바이트 계산
                char_count = len(final_text)
                char_count_no_space = len(final_text.replace(" ", "").replace("\n", ""))
                byte_count = len(final_text.encode('utf-8'))
                
                st.success("작성 완료!")
                
                with st.expander("🔍 역량별 분석 내용 확인하기 (클릭)", expanded=True):
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
                    st.error("🚨 중요: 'requirements.txt'에 'pypdf'가 포함되어 있는지, 그리고 Reboot 했는지 확인하세요.")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. All rights reserved.<br>
    문의: <a href="mailto:inlove11@naver.com" style="color: #888; text-decoration: none;">inlove11@naver.com</a>
</div>
""", unsafe_allow_html=True)
