import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader # PDF 읽기용
from PIL import Image       # 이미지 처리용
import io

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 영어 세특 메이트 (AI Vision)",
    page_icon="📘",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS ---
st.markdown("""
    <style>
    /* 폰트 설정 */
    html, body, [class*="css"] { 
        font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif; 
    }
    
    /* 입력창 디자인 */
    .stTextArea textarea { 
        border-radius: 12px; 
        border: 1px solid rgba(85, 124, 100, 0.2); 
        background-color: #FAFCFA; 
    }
    
    /* 제목 스타일 */
    h1 { font-weight: 700; letter-spacing: -1px; color: #2F4F3A; } 
    .subtitle { font-size: 16px; color: #666; margin-top: -15px; margin-bottom: 30px; }
    
    /* 버튼 스타일 */
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
    
    /* 파일 업로더 스타일 커스텀 */
    div[data-testid="stFileUploader"] {
        border: 1px dashed #557C64;
        border-radius: 10px;
        padding: 10px;
        background-color: #F7F9F8;
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
except FileNotFoundError:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("📘 2025 영어 과목세특 메이트")
st.markdown("<p class='subtitle'>Gift for English Teachers (Text + PDF/Image)</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 영어 세특용 작성 팁
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 고퀄리티 영어 세특을 위한 가이드</span>
    입력창에 내용을 적거나, <b>학생의 수행평가 자료(PDF/이미지)</b>를 업로드하세요.<br><br>
    1. <b>(What)</b> 수업 내용, 지문 주제, 수행평가 활동<br>
    2. <b>(How)</b> 심화 자료(TED, 원서) 탐구 과정 및 파일 첨부<br>
    3. <b>(Why)</b> 향상된 영어 실력 및 진로 연계
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 (텍스트 + 파일) ---
st.markdown("### 1. 학생 관찰 내용 및 자료")

# 텍스트 입력
student_input = st.text_area(
    "입력창",
    height=150,
    placeholder="예시: '환경' 단원을 배우고 첨부된 파일과 같이 에세이를 작성함. 수업 시간에 배운 표현을 활용하여...", 
    label_visibility="collapsed"
)

# [NEW] 파일 업로더 추가
uploaded_file = st.file_uploader("📂 증빙 자료 업로드 (PDF, 이미지)", type=['pdf', 'png', 'jpg', 'jpeg'])

# 파일 정보 표시
file_content = ""
upload_image = None # 이미지 객체 저장용

if uploaded_file is not None:
    # 1. PDF 파일인 경우: 텍스트 추출
    if uploaded_file.type == "application/pdf":
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                file_content += page.extract_text() + "\n"
            st.info(f"📄 PDF 파일 '{uploaded_file.name}'의 내용을 읽어들였습니다.")
        except Exception as e:
            st.error("PDF를 읽는 중 오류가 발생했습니다.")
    
    # 2. 이미지 파일인 경우: 이미지 객체 저장
    else:
        try:
            upload_image = Image.open(uploaded_file)
            st.image(upload_image, caption="업로드된 이미지", width=200)
            st.info("📷 이미지를 인식했습니다. AI가 내용을 분석합니다.")
        except:
            st.error("이미지를 처리할 수 없습니다.")

if not student_input and not uploaded_file:
    st.markdown("<p class='warning-text'>⚠️ 텍스트를 입력하거나 파일을 업로드해주세요.</p>", unsafe_allow_html=True)

# --- 6. 3단계 작성 옵션 ---
st.markdown("### 2. 작성 옵션 설정")

# [카드 1] 모드 선택
with st.container(border=True):
    st.markdown('<p class="card-title">① 작성 모드 선택</p>', unsafe_allow_html=True)
    mode = st.radio(
        "모드",
        ["✨ 풍성하게 (내용 보강)", "🛡️ 엄격하게 (팩트 중심)"],
        captions=["살을 붙여 자연스럽게 만듭니다.", "자료에 있는 내용만 서술합니다."],
        horizontal=True, 
        label_visibility="collapsed"
    )

# [카드 2] 희망 분량
with st.container(border=True):
    st.markdown('<p class="card-title">② 희망 분량 (공백 포함)</p>', unsafe_allow_html=True)
    target_length = st.slider("글자 수", 100, 1000, 500, 10, label_visibility="collapsed")

# [카드 3] 키워드 선택
with st.container(border=True):
    st.markdown('<p class="card-title">③ 강조할 핵심 역량 (다중 선택)</p>', unsafe_allow_html=True)
    filter_options = ["👑 AI 자동 판단", "📖 심화 독해력", "✍️ 논리적 영작문", "🗣️ 유창한 발표", "📚 어휘/문법 활용", "🔎 비판적 사고", "🌏 글로벌 감각", "🚀 진로 연계"]
    try:
        selected_tags = st.pills("키워드 버튼", options=filter_options, selection_mode="multi", label_visibility="collapsed")
    except:
        selected_tags = st.multiselect("키워드 선택", filter_options, label_visibility="collapsed")

# [고급 설정] 모델 선택
st.markdown("")
with st.expander("⚙️ AI 모델 직접 선택하기 (고급 설정)"):
    manual_model = st.selectbox("사용할 모델", ["⚡ gemini-1.5-flash (기본값)", "🤖 gemini-1.5-pro (고성능)"], index=0)

# --- 7. 실행 및 결과 영역 ---
st.markdown("")
if st.button("✨ 영어 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not student_input and not uploaded_file:
        st.warning("⚠️ 입력 내용이나 파일 중 하나는 필수입니다!")
    else:
        with st.spinner(f'AI가 자료를 분석하여 세특을 작성 중입니다...'):
            try:
                genai.configure(api_key=api_key)

                # 모델 선택
                target_model = "gemini-1.5-pro" if "pro" in manual_model else "gemini-1.5-flash"

                # 모드별 프롬프트
                if "엄격하게" in mode:
                    temp = 0.2
                    prompt_instruction = "입력된 텍스트와 파일 내용에 근거하지 않은 사실은 절대 쓰지 마십시오."
                else:
                    temp = 0.75
                    prompt_instruction = "입력된 내용이 다소 부족하더라도 문맥에 맞는 교육적 표현을 활용하여 풍성하게 작성하십시오."

                generation_config = genai.types.GenerationConfig(temperature=temp)
                model = genai.GenerativeModel(target_model, generation_config=generation_config)

                # 키워드
                tags_str = f"핵심 키워드: {', '.join(selected_tags)}" if selected_tags else "별도 지정 없음. AI가 자율적으로 판단."

                # PDF 텍스트가 있다면 입력 정보에 합침
                final_input_text = student_input
                if file_content:
                    final_input_text += f"\n\n[첨부된 PDF 파일 내용]:\n{file_content}"

                # 시스템 프롬프트
                system_prompt = f"""
                당신은 고등학교 영어 교사입니다. 학생의 활동 기록(텍스트 및 첨부파일)을 바탕으로 '과목 세부능력 및 특기사항'을 작성합니다.
                
                [입력 정보]: {final_input_text}
                [강조 역량]: {tags_str}
                
                # 작성 지침
                1. 다음 두 가지 파트로 나누어 출력하세요. 구분선: "---SPLIT---"
                2. [Part 1] 역량별 분석: 활동 내용을 [수업참여/심화탐구/영어능력] 등으로 분류 요약.
                3. [Part 2] 영어 세특 (종합): 공백 포함 약 {target_length}자 내외.
                4. 첨부된 파일(이미지/PDF)이 있다면 그 내용을 구체적으로 인용하여 학생의 우수성을 드러내십시오.
                {prompt_instruction}
                """

                # --- AI에게 요청 보내기 ---
                # 이미지가 있으면 [프롬프트, 이미지] 리스트로 보냄
                if upload_image:
                    response = model.generate_content([system_prompt, upload_image])
                else:
                    response = model.generate_content(system_prompt)
                
                full_text = response.text
                
                # 결과 분리
                if "---SPLIT---" in full_text:
                    parts = full_text.split("---SPLIT---")
                    analysis_text = parts[0].strip()
                    final_text = parts[1].strip()
                else:
                    analysis_text = "분석 내용을 생성하지 못했습니다."
                    final_text = full_text

                # 글자 수 계산
                char_count = len(final_text)
                char_count_no_space = len(final_text.replace(" ", "").replace("\n", ""))
                byte_count = 0
                for char in final_text:
                    byte_count += 3 if ord(char) > 127 else 1
                
                st.success("작성 완료!")
                
                with st.expander("🔍 역량별 분석 내용 확인하기 (클릭)", expanded=True):
                    st.markdown(analysis_text)
                
                st.markdown("---")
                st.markdown("### 📋 최종 제출용 종합본")

                st.markdown(f"""
                <div class="count-box">
                    목표: {target_length}자 | <b>실제: {char_count}자</b> (공백제외 {char_count_no_space}자)<br>
                    💾 <b>예상 바이트: {byte_count} Bytes</b> (NEIS 기준)
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"※ {mode.split()[1]} 모드 | 사용 모델: {target_model}")
                st.text_area("결과 (복사해서 나이스에 붙여넣으세요)", value=final_text, height=350)

            except Exception as e:
                if "429" in str(e):
                    st.error("🚨 하루 무료 사용량을 초과했습니다. 내일 다시 시도해주세요.")
                else:
                    st.error(f"오류 발생: {e}")
                    st.info("GitHub의 requirements.txt에 'pypdf'와 'Pillow'가 추가되었는지 확인해주세요.")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. All rights reserved.<br>
    문의: <a href="mailto:inlove11@naver.com" style="color: #888; text-decoration: none;">inlove11@naver.com</a>
</div>
""", unsafe_allow_html=True)