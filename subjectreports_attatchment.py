import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
import io

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 과목세특 메이트",
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
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("📚 2025 과목세특 메이트")
st.caption("AI Assistant for Subject Specific Records (Text + PDF/Image)")
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드 박스
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 세특 작성 3-Step 가이드</span><br>
    1. <b>(동기)</b> 수업 중 호기심을 갖게 된 계기나 단원<br>
    2. <b>(과정)</b> 탐구 보고서, 독서, 수행평가 활동 (파일 첨부 가능)<br>
    3. <b>(결과)</b> 확장된 지식과 학업적 성장, 진로 연계
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 ---
st.markdown("### 1. 학생 활동 내용 및 자료")
student_input = st.text_area(
    "입력창", height=150,
    placeholder="예시: '유전' 단원에서 CRISPR 기술에 흥미를 느껴 관련 논문을 분석하고 윤리적 쟁점 보고서를 작성함.",
    label_visibility="collapsed"
)

# 파일 업로더
uploaded_files = st.file_uploader(
    "📎 증빙 자료 업로드 (이미지/PDF)", 
    type=["png", "jpg", "jpeg", "pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)}개의 파일이 첨부되었습니다.")

# --- 6. 옵션 설정 ---
st.markdown("### 2. 작성 옵션")
with st.container(border=True):
    mode = st.radio("작성 모드", ["✨ 풍성하게 (의미 부여)", "🛡️ 엄격하게 (팩트 중심)"], horizontal=True)

with st.container(border=True):
    target_length = st.slider("목표 글자 수", 300, 1000, 500, 50)

with st.container(border=True):
    filter_options = [
        "👑 AI 자동 판단", "🔎 비판적 사고력", "📊 데이터 분석", 
        "💡 창의적 문제해결", "📚 심화 탐구", "🗣️ 논리적 소통", 
        "🤝 협업/리더십", "🔗 진로 연계", "📖 자기주도성"
    ]
    try:
        selected_tags = st.pills("핵심 역량", filter_options, selection_mode="multi")
    except:
        selected_tags = st.multiselect("핵심 역량", filter_options)

# 모델 선택 (1.5 버전으로 고정)
with st.expander("⚙️ 고급 설정 (모델 선택)"):
    manual_model = st.selectbox("사용할 모델", ["🤖 자동 (Auto)", "⚡ gemini-1.5-flash", "🤖 gemini-1.5-pro"])

# --- 7. 실행 ---
if st.button("✨ 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("API Key가 필요합니다.")
    elif not student_input and not uploaded_files:
        st.warning("내용을 입력하거나 파일을 업로드해주세요.")
    else:
        with st.spinner("자료를 분석하여 세특을 작성 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                
                # --- [수정 완료] 모델 선택 로직 (2.5 -> 1.5로 변경) ---
                target_model = "gemini-1.5-flash" # 기본값
                
                if "pro" in manual_model:
                    target_model = "gemini-1.5-pro"
                elif "flash" in manual_model:
                    target_model = "gemini-1.5-flash"
                elif "자동" in manual_model:
                    # 파일이 있으면 성능 좋은 Pro, 없으면 빠른 Flash
                    target_model = "gemini-1.5-pro" if uploaded_files else "gemini-1.5-flash"

                model = genai.GenerativeModel(target_model)

                # 키워드 처리
                if not selected_tags:
                    tags_str = "별도 지정 없음. [동기] -> [과정] -> [결과] -> [성장] 순서로 작성."
                else:
                    tags_str = f"핵심 키워드: {', '.join(selected_tags)}"

                # 기본 프롬프트
                base_prompt = f"""
                당신은 고등학교 교과 담당 교사입니다. 입력된 [관찰 내용]과 [첨부 자료]를 바탕으로 '과목 세부능력 및 특기사항'을 작성하세요.
                
                [입력 정보]
                - 텍스트: {student_input if student_input else "없음 (첨부파일 참조)"}
                - 강조 역량: {tags_str}
                - 목표 분량: {target_length}자 내외
                
                [작성 원칙: {mode}]
                - 구체적인 탐구 동기와 과정을 서술할 것.
                - 학생의 학업적 역량이 잘 드러나게 작성할 것.
                - 첨부된 자료(이미지/PDF)의 내용을 구체적으로 반영할 것.

                [출력 양식]
                1. 역량 분석 (개조식 요약)
                ---SPLIT---
                2. 과목 세특 (줄글 본문)
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

                # 글자 수 계산
                char_len = len(body)
                byte_len = sum(3 if ord(c) > 127 else 1 for c in body)

                st.success("작성 완료!")
                
                with st.expander("🔍 역량 분석 보기", expanded=True):
                    st.markdown(analysis)
                
                st.markdown("---")
                st.markdown(f'<div class="count-box">📊 글자 수: {char_len}자 | 💾 {byte_count} Bytes</div>', unsafe_allow_html=True)
                st.text_area("최종 결과", value=body, height=400)
                st.caption(f"Used Model: {target_model}")

            except Exception as e:
                # 에러 메시지 처리
                if "429" in str(e) and "limit: 0" in str(e):
                    st.error("🚨 선택한 모델을 사용할 권한이 없습니다. (1.5 버전을 사용하세요)")
                elif "429" in str(e):
                    st.error("🚨 하루 무료 사용량을 초과했습니다.")
                elif "404" in str(e):
                    st.error("🚨 모델을 찾을 수 없습니다. (API 키를 '새 프로젝트'에서 다시 받아보세요.)")
                else:
                    st.error(f"오류 발생: {e}")
