import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# Pypdf가 없어도 앱이 죽지 않도록 예외 처리
try:
    from pypdf import PdfReader
except ImportError:
    st.error("시스템 설정 오류: requirements.txt에 'pypdf'가 누락되었습니다.")
    PdfReader = None

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 과목세특 메이트 (최종)",
    page_icon="📚",
    layout="centered"
)

# --- 2. CSS 스타일 ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; background-color: #FAFCFA; }
    .stButton button { 
        background-color: #557C64 !important; color: white !important; 
        border-radius: 10px; padding: 0.8rem; font-size: 16px; font-weight: bold; border: none;
    }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    .guide-box { background-color: #F0F4F1; padding: 15px; border-radius: 10px; margin-bottom: 20px; color: #333; }
    .count-box { background-color: #E3EBE6; padding: 10px; border-radius: 8px; text-align: right; font-weight: bold; color: #2F4F3A; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

st.title("📚 2025 과목세특 메이트")
st.caption("1학기 요약 + 2학기 심화 활동(파일첨부) 통합 생성기")
st.divider()

if not api_key:
    with st.expander("🔐 API Key 설정"):
        api_key = st.text_input("Google API Key", type="password")

# --- 4. 입력 영역 ---
st.markdown("### 1. 1학기 내용 (요약용)")
sem1_input = st.text_area("1학기 내용", height=100, placeholder="기존 생기부 내용을 입력하세요. (AI가 핵심만 요약합니다)", label_visibility="collapsed")

st.markdown("### 2. 2학기 활동 (심화용)")
sem2_input = st.text_area("2학기 활동", height=150, placeholder="예: 'AI 윤리' 기고문 작성, 독서 활동 등", label_visibility="collapsed")

uploaded_files = st.file_uploader("📎 증빙 자료 (PDF/이미지)", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)

# --- 5. 옵션 ---
st.markdown("### 3. 설정")
col1, col2 = st.columns(2)
with col1:
    mode = st.radio("모드", ["✨ 풍성하게", "🛡️ 엄격하게"], horizontal=True)
with col2:
    # 모델 선택 (가장 안전한 이름 사용)
    model_choice = st.selectbox("모델", ["gemini-1.5-flash", "gemini-1.5-pro"])

target_len = st.slider("목표 글자 수", 300, 1000, 500, 50)

# --- 6. 실행 로직 ---
if st.button("✨ 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("API Key를 입력해주세요.")
    elif not sem1_input and not sem2_input:
        st.warning("내용을 입력해주세요.")
    else:
        with st.spinner("자료 분석 중... (시간이 조금 걸릴 수 있습니다)"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_choice)

                # 파일 처리
                files_data = []
                pdf_text = ""
                
                if uploaded_files:
                    for f in uploaded_files:
                        if f.type == "application/pdf":
                            if PdfReader:
                                try:
                                    reader = PdfReader(f)
                                    for page in reader.pages:
                                        pdf_text += page.extract_text() + "\n"
                                except:
                                    st.warning(f"PDF {f.name}을 읽는데 실패했습니다.")
                        elif f.type.startswith("image/"):
                            # 이미지는 PIL Image 객체로 변환하여 리스트에 추가
                            img = Image.open(f)
                            files_data.append(img)

                # 프롬프트 구성
                prompt = f"""
                당신은 고등학교 교사입니다. 다음 지침에 따라 학교생활기록부 '세부능력 및 특기사항'을 작성하세요.
                
                [입력 데이터]
                1. 1학기 내용(요약 대상): {sem1_input}
                2. 2학기 활동(심화 대상): {sem2_input}
                3. 증빙 자료(PDF 텍스트): {pdf_text[:10000]} (너무 길면 잘림)
                4. 모드: {mode}
                
                [작성 가이드]
                - 전체 분량: 공백 포함 약 {target_len}자
                - 1학기 내용은 핵심만 요약하여 전체의 30% 이내로 구성.
                - 2학기 내용은 구체적 활동과 변화를 중심으로 70% 이상 구성.
                - 첨부된 이미지나 PDF 내용이 있다면 적극 반영할 것.
                - 문체: '~함', '~임' 등의 개조식 문체와 줄글의 조화.
                
                [출력 양식]
                1. 구성 전략 (간단 요약)
                ---SPLIT---
                2. 세특 본문
                """
                
                # 콘텐츠 조합 (텍스트 + 이미지들)
                content_payload = [prompt]
                if files_data:
                    content_payload.extend(files_data)

                # AI 호출
                response = model.generate_content(content_payload)
                text = response.text

                # 결과 분리
                if "---SPLIT---" in text:
                    parts = text.split("---SPLIT---")
                    analysis = parts[0]
                    result_body = parts[1]
                else:
                    analysis = "전략 요약 없음"
                    result_body = text

                # 결과 표시
                st.success("작성 완료!")
                with st.expander("🔍 작성 전략 보기"):
                    st.write(analysis)
                
                st.markdown("---")
                st.text_area("최종 결과", value=result_body.strip(), height=400)
                
                # 글자수 정보
                char_cnt = len(result_body.strip())
                st.caption(f"글자 수: {char_cnt}자 (공백 포함)")

            except Exception as e:
                # 에러 메시지 분석
                err_msg = str(e)
                if "404" in err_msg:
                    st.error("🚨 중요: 라이브러리 버전 문제입니다. 1단계의 'requirements.txt' 수정을 하고 'Reboot App'을 꼭 해주세요!")
                    st.code("google-generativeai>=0.8.3", language="text")
                elif "429" in err_msg:
                    st.error("🚨 사용량이 많아 잠시 제한되었습니다. 잠시 후 다시 시도하거나 모델을 변경하세요.")
                else:
                    st.error(f"오류 발생: {err_msg}")
