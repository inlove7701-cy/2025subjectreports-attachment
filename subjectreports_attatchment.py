import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 영어 세특 메이트 (안전모드)",
    page_icon="🛡️",
    layout="centered"
)

# --- 2. [디자인] 스타일 설정 ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; color: #2F4F3A; } 
    .stButton button { background-color: #557C64 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; padding: 0.8rem; }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; text-align: right; border: 1px solid #C4D7CD; }
    .semester-header { color: #2F4F3A; font-weight: bold; margin-bottom: 5px; border-bottom: 2px solid #557C64; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. [핵심] 사용 가능한 모델 자동 찾기 함수 ---
def get_best_available_model():
    """현재 API 키로 사용 가능한 모델 중 가장 좋은 것을 찾습니다."""
    try:
        # 사용 가능한 모델 리스트 조회
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 우선순위: 1.5-flash -> 1.5-pro -> 1.0-pro -> 그냥 gemini-pro
        priority_list = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.0-pro",
            "models/gemini-pro"
        ]
        
        for model_name in priority_list:
            if model_name in available_models:
                return model_name
        
        # 우선순위에 없으면 리스트의 첫 번째 모델 반환
        return available_models[0] if available_models else "gemini-pro"
    except Exception:
        # 리스트 조회조차 실패하면 가장 기본 모델 반환
        return "gemini-pro"

# --- 4. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

# --- 5. 헤더 영역 ---
st.title("🛡️ 영어 세특 메이트 (자동연결)")
st.markdown("<p class='subtitle'>Available Model Auto-Detection System</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

st.markdown("""
<div class="guide-box">
    <b>💡 안심하고 사용하세요</b><br>
    이 프로그램은 <b>사용 가능한 AI 모델을 자동으로 검색</b>하여 연결합니다.<br>
    404 오류가 발생하지 않도록 최적의 모델을 스스로 찾아냅니다.
</div>
""", unsafe_allow_html=True)

# --- 6. 입력 영역 ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="semester-header">📝 1학기 (요약)</p>', unsafe_allow_html=True)
    input_sem1 = st.text_area("1학기 내용", height=250, placeholder="기존 1학기 내용을 입력하세요.", label_visibility="collapsed")

with col2:
    st.markdown('<p class="semester-header">✨ 2학기 (생성)</p>', unsafe_allow_html=True)
    input_sem2 = st.text_area("2학기 내용", height=250, placeholder="2학기 활동 소재를 입력하세요.", label_visibility="collapsed")

# --- 7. 옵션 및 실행 ---
st.markdown("### 🎯 강조 키워드")
filter_options = ["🗣️ 유창한 말하기", "📖 심화 독해", "✍️ 논리적 글쓰기", "👂 직청직해", "🌍 문화적 이해", "📚 고급 어휘 활용", "🔗 진로 연계"]
try:
    selected_tags = st.pills("키워드", filter_options, selection_mode="multi", label_visibility="collapsed")
except:
    selected_tags = st.multiselect("키워드", filter_options, label_visibility="collapsed")

st.markdown("")
if st.button("✨ 세특 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 없습니다.")
    elif not input_sem1 and not input_sem2:
        st.warning("⚠️ 내용을 입력해주세요.")
    else:
        with st.spinner('사용 가능한 최적의 AI 모델을 찾는 중...'):
            try:
                genai.configure(api_key=api_key)
                
                # [핵심] 자동으로 모델 찾아서 할당
                target_model_name = get_best_available_model()
                # st.caption(f"🤖 연결된 모델: {target_model_name}") # 디버깅용 (필요시 주석 해제)

                tags_str = f"2학기 키워드: {', '.join(selected_tags)}" if selected_tags else "키워드: 영어 종합 역량"
                
                prompt = f"""
                당신은 고등학교 영어 교사입니다. 
                1학기 내용은 요약하고, 2학기 내용은 구체화하여 총 500자 미만으로 세특을 작성하세요.
                
                [1학기]: {input_sem1}
                [2학기]: {input_sem2}
                [키워드]: {tags_str}
                
                형식:
                ---1학기---
                (내용)
                ---2학기---
                (내용)
                """

                model = genai.GenerativeModel(target_model_name)
                response = model.generate_content(prompt)
                full_text = response.text

                # 파싱 로직
                if "---2학기---" in full_text:
                    parts = full_text.split("---2학기---")
                    sem1_res = parts[0].replace("---1학기---", "").strip()
                    sem2_res = parts[1].strip()
                else:
                    sem1_res = full_text.replace("---1학기---", "").strip()
                    sem2_res = ""

                # 결과 출력
                total_len = len(sem1_res + sem2_res)
                st.success(f"작성 완료! (모델: {target_model_name.replace('models/', '')})")
                st.markdown(f"<div class='count-box'>📊 총 {total_len}자</div>", unsafe_allow_html=True)

                r1, r2 = st.columns(2)
                with r1:
                    st.info("📉 1학기")
                    st.text_area("res1", sem1_res, height=300)
                with r2:
                    st.success("📈 2학기")
                    st.text_area("res2", sem2_res, height=300)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
