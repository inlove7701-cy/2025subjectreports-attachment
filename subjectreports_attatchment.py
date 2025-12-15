import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# Pypdf 라이브러리 (파일 읽기용 - 없어도 앱이 죽지 않게 처리)
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

# --- 2. [디자인] 숲속 테마 CSS (기존 유지) ---
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

# --- 4. 헤더 영역 ---
st.title("📚 2025 과목세특 메이트")
st.markdown("##### 1학기 요약 + 2학기 심화(기고문/북리뷰/AI) 통합 생성")
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <b>💡 작성 가이드</b><br>
    1. <b>1학기</b>: 기존 내용은 핵심만 요약하여 반영합니다.<br>
    2. <b>2학기</b>: <b>신문기사 기고문, 원서 북리뷰, AI 도구 활용</b> 내용을 중심으로 작성됩니다.<br>
    3. <b>증빙자료</b>: 활동지나 기사를 PDF/사진으로 첨부하면 내용이 구체적으로 반영됩니다.
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (분리됨) ---

# [1학기]
st.markdown("### 1. 1학기 기존 세특 (요약용)")
sem1_input = st.text_area(
    "1학기 입력창", height=120,
    placeholder="이미 작성된 1학기 내용을 붙여넣으세요. (분량이 많으면 AI가 요약합니다)",
    label_visibility="collapsed"
)

# [2학기]
st.markdown("### 2. 2학기 활동 내용 (심화용)")
sem2_input = st.text_area(
    "2학기 입력창", height=150,
    placeholder="예: AI 의료 기술의 명암을 다룬 기사를 읽고 기고문 작성. 'Deep Medicine' 원서를 읽고 비평문 작성. 챗GPT와 토론하며 사고 확장.",
    label_visibility="collapsed"
)

# [파일 첨부]
uploaded_files = st.file_uploader(
    "📎 활동 증빙 자료 (이미지/PDF)", 
    type=["png", "jpg", "jpeg", "pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)}개의 파일이 첨부되었습니다.")

# --- 6. 옵션 설정 ---
st.markdown("### 3. 작성 옵션")

# [카드 1] 모드 선택
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("작성 모드", ["✨ 풍성하게 (의미 부여)", "🛡️ 엄격하게 (팩트 중심)"], horizontal=True)
    with col2:
        target_length = st.slider("목표 글자 수", 300, 1000, 500, 50)

# [카드 2] 모델 선택 (사용자 요청대로 1.5 유지)
with st.expander("⚙️ AI 모델 선택 (기본값: 1.5-flash)"):
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

                # [모델 설정] 사용자가 원했던 '작동하는' 1.5 모델 유지
                if "pro" in manual_model:
                    target_model = "gemini-1.5-pro"
                else:
                    target_model = "gemini-1.5-flash"

                # 모드별 온도 설정
                temp = 0.2 if "엄격하게" in mode else 0.75

                model = genai.GenerativeModel(target_model, generation_config=genai.types.GenerationConfig(temperature=temp))

                # [파일 처리 로직]
                files_content = []
                pdf_text_extracted = ""

                if uploaded_files:
                    for f in uploaded_files:
                        bytes_data = f.getvalue()
                        if f.type == "application/pdf":
                            if PdfReader:
                                try:
                                    pdf_reader = PdfReader(io.BytesIO(bytes_data))
                                    for page in pdf_reader.pages:
                                        t = page.extract_text()
                                        if t: pdf_text_extracted += t + "\n"
                                except: pass
                        elif f.type.startswith("image/"):
                            image = Image.open(io.BytesIO(bytes_data))
                            files_content.append(image)

                # [핵심] 프롬프트: 2학기 활동 명령 & 사용자 문체 스타일 반영
                prompt_text = f"""
                당신은 입학사정관이 주목하는 고등학교 교사입니다. 학생의 [1학기 기존 세특]과 [2학기 신규 활동]을 통합하여, 전체 분량 약 {target_length}자의 '과목 세특'을 작성하세요.

                [입력 데이터]
                1. 1학기 내용: {sem1_input}
                2. 2학기 활동 개요: {sem2_input}
                3. 증빙 자료(PDF): {pdf_text_extracted[:5000]}
                4. 모드: {mode}

                [★ 필수 반영: 2학기 활동 내용]
                다음 3가지 활동이 반드시 포함되어야 하며, 전체 글의 70% 비중을 차지해야 합니다.
                1. **신문기사 기고문 작성**: 관련 분야 기사를 읽고 심층 분석하여 자신의 견해를 논리적으로 기고문으로 작성함.
                2. **원서 북리뷰**: 원서(책)를 읽고 핵심 내용을 비평하거나 주제를 확장하여 보고서를 작성함.
                3. **AI 도구 활용**: 인공지능 도구(ChatGPT 등)를 활용하여 사고를 확장하고, 그 과정에서 느낀점이나 한계를 서술함.

                [★ 필수 반영: 문체 및 스타일]
                - **고급 어휘 사용**: 해당 교과목의 전문 용어와 고급 어휘를 맥락에 맞게 구사할 것.
                - **논리적 서술**: "구체적 사례를 들어 ~의 위험성을 제시하고, ~의 필요성을 설득력 있게 전달함"과 같은 구조 사용.
                - **문장 구조**: 단순 나열이 아닌, [동기 -> 심화탐구(분석) -> 결과 및 확장]의 흐름 유지.
                - 종결 어미: '~함', '~임', '~보임', '~드러냄'.

                [작성 지침]
                Step 1: 1학기 내용은 핵심 역량 위주로 요약하여 앞부분에 배치 (30% 이내).
                Step 2: 위 2학기 3대 활동(기고문, 북리뷰, AI)을 구체적으로 서술하여 뒷부분에 배치 (70% 이상).
                Step 3: 두 학기 내용이 하나의 스토리처럼 자연스럽게 연결되도록 작성.

                [출력 양식]
                1. 활동 분석 (1학기 요약 / 2학기 활동 포인트)
                ---SPLIT---
                2. 최종 과목 세특 (제출용 줄글)
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
                
                with st.expander("🔍 활동 분석 및 전략 보기", expanded=True):
                    st.markdown(analysis_text)
                
                st.markdown("---")
                st.markdown(f"""
                <div class="count-box">
                    📊 목표: {target_length}자 | <b>실제: {char_count}자</b> (공백제외 {char_count_no_space}자)<br>
                    💾 <b>용량: {byte_count} Bytes</b> (UTF-8 기준)
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"※ {mode.split()[1]} 모드 동작 중 ({target_model})")
                st.text_area("최종 결과 (생활기록부 입력용)", value=final_text, height=400)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                if "404" in str(e):
                    st.error("🚨 모델 오류: requirements.txt 파일 확인 및 앱 재부팅(Reboot)이 필요합니다.")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. All rights reserved.<br>
</div>
""", unsafe_allow_html=True)
