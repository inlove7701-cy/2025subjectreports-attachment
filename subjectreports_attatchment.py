import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 영어 세특 메이트 (파일 첨부 버전)",
    page_icon="📸",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; color: #2F4F3A; } 
    .stButton button { background-color: #557C64 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; text-align: right; border: 1px solid #C4D7CD; }
    .semester-header { color: #2F4F3A; font-weight: bold; margin-bottom: 5px; border-bottom: 2px solid #557C64; display: inline-block; }
    /* 파일 업로더 스타일링 */
    div[data-testid="stFileUploader"] section { background-color: #f0f2f6; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 함수 정의 (파일 처리) ---
def extract_text_from_pdf(file):
    """PDF에서 텍스트 추출"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"PDF 읽기 오류: {e}"

# --- 4. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 5. 헤더 영역 ---
st.title("📸 2025 영어 세특 메이트 (Pro)")
st.markdown("이미지/PDF 수행평가 자료를 분석하여 세특을 생성합니다.", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드
st.markdown("""
<div class="guide-box">
    <b>💡 파일 업로드 기능 추가됨!</b><br>
    학생이 제출한 <b>영어 에세이 사진, 활동지 PDF, 필기 노트</b> 등을 직접 올리세요.<br>
    AI가 이미지 속 글자나 PDF 내용을 읽어서 세특을 작성해줍니다.
</div>
""", unsafe_allow_html=True)

# --- 6. 입력 영역 ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="semester-header">📝 1학기 (요약)</p>', unsafe_allow_html=True)
    input_sem1 = st.text_area(
        "1학기 내용",
        height=300,
        placeholder="기존 1학기 세특 내용을 붙여넣으세요 (자동 요약됨)",
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<p class="semester-header">✨ 2학기 (파일/텍스트)</p>', unsafe_allow_html=True)
    
    # 탭으로 입력 방식 구분
    tab_text, tab_file = st.tabs(["✍️ 직접 입력", "📂 파일 업로드"])
    
    with tab_text:
        input_sem2_text = st.text_area(
            "2학기 텍스트",
            height=230,
            placeholder="수행평가 내용, 관찰 기록 등을 입력하세요.",
            label_visibility="collapsed"
        )
    
    with tab_file:
        uploaded_file = st.file_uploader("이미지/PDF 업로드", type=["png", "jpg", "jpeg", "pdf"], label_visibility="collapsed")
        
        # 파일 미리보기 및 처리 로직
        processed_content = None # AI에게 보낼 최종 컨텐츠 (텍스트 or 이미지객체)
        file_text_preview = ""   # PDF일 경우 텍스트 미리보기용

        if uploaded_file is not None:
            file_type = uploaded_file.type
            
            # [CASE 1] 이미지 파일
            if "image" in file_type:
                image_data = Image.open(uploaded_file)
                st.image(image_data, caption="업로드된 이미지", use_container_width=True)
                processed_content = image_data # 이미지 객체 자체를 저장
            
            # [CASE 2] PDF 파일
            elif "pdf" in file_type:
                text = extract_text_from_pdf(uploaded_file)
                if len(text) > 10:
                    st.success("PDF 텍스트 추출 성공!")
                    st.caption(f"내용 미리보기: {text[:100]}...")
                    processed_content = text # 추출된 텍스트 저장
                    file_text_preview = text
                else:
                    st.error("⚠️ 텍스트를 추출할 수 없는 PDF입니다 (스캔본 등).")

# --- 7. 옵션 및 실행 ---
st.markdown("---")
# 키워드 선택
filter_options = [
    "🗣️ 유창한 의사소통", "📖 비판적 독해", "✍️ 논리적 영작", 
    "🌍 문화적 다양성 이해", "📚 심화 어휘 활용", "🛠️ 문법 응용력"
]
selected_tags = st.multiselect("📌 2학기 강조 키워드 (선택)", filter_options)

# 실행 버튼
if st.button("✨ 분석 및 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 필요합니다.")
        st.stop()
        
    # 2학기 입력 소스 확인 (텍스트 vs 파일)
    final_sem2_input = ""
    image_input = None
    
    # 우선순위: 파일 > 텍스트창
    if processed_content:
        if isinstance(processed_content, str): # PDF 텍스트
            final_sem2_input = f"PDF 내용: {processed_content}"
        else: # 이미지 객체
            image_input = processed_content
            final_sem2_input = "이미지 자료(첨부됨)"
    elif input_sem2_text:
        final_sem2_input = input_sem2_text
    
    if not input_sem1 and not final_sem2_input:
        st.warning("⚠️ 1학기 내용이나 2학기 자료를 입력해주세요.")
    else:
        with st.spinner('자료를 분석하여 세특을 작성 중입니다...'):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash") # 멀티모달 지원 모델
                
                tags_str = f"강조점: {', '.join(selected_tags)}" if selected_tags else ""
                
                # 프롬프트 구성
                base_prompt = f"""
                당신은 고등학교 영어 교사입니다. 학생 자료를 분석해 생기부 세특을 작성하세요.
                
                # 목표
                1. [1학기]: "{input_sem1}" 내용을 요약.
                2. [2학기]: 제공된 2학기 자료(텍스트 또는 이미지)를 바탕으로, 학생의 영어 역량(독해, 작문, 어휘 등)이 드러나게 구체적으로 서술.
                3. [분량]: 1,2학기 합계 공백포함 500자 미만.
                4. [기타]: {tags_str}
                
                # 출력 형식
                ---1학기---
                (요약 내용)
                ---2학기---
                (생성 내용)
                """
                
                # AI에게 보낼 콘텐츠 리스트 구성
                content_to_send = [base_prompt]
                if image_input:
                    content_to_send.append(image_input) # 이미지 객체 추가
                elif isinstance(processed_content, str):
                    # PDF 내용은 이미 base_prompt 안에 텍스트로 녹여낼 수도 있지만,
                    # 내용이 길 경우를 대비해 리스트에 추가 문자열로 붙임
                    content_to_send.append(f"\n[2학기 PDF 자료 내용]:\n{processed_content}")

                # 생성 요청
                response = model.generate_content(content_to_send)
                full_text = response.text
                
                # 결과 파싱 (기존 로직 동일)
                try:
                    parts = full_text.split("---2학기---")
                    sem1_result = parts[0].replace("---1학기---", "").strip()
                    sem2_result = parts[1].strip() if len(parts) > 1 else ""
                except:
                    sem1_result = full_text
                    sem2_result = "생성 오류"
                
                # 결과 출력
                st.success("작성 완료!")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.info("📉 1학기")
                    st.text_area("result1", sem1_result, height=300)
                with col_r2:
                    st.success("📈 2학기 (자료 분석됨)")
                    st.text_area("result2", sem2_result, height=300)
                    
            except Exception as e:
                st.error(f"오류 발생: {e}")
