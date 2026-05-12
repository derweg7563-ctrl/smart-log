import streamlit as st
import datetime
import urllib.parse
from pymongo import MongoClient

# AI 보조교사 모듈 불러오기
import ai_teacher

# 구글 생성형 AI 패키지
try:
    import google.generativeai as genai
except ImportError:
    st.error("🚨 `google-generativeai` 패키지가 필요합니다.")

# DB 연결
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]
    collection = db["local_history"] 
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

# 구글 키 적용
try:
    genai.configure(api_key=st.secrets["google"]["api_key"])
except Exception as e:
    st.error("🚨 secrets.toml 파일에 구글 열쇠가 없습니다!")

# AI 지역학자 API 호출 (404 에러 방지 적용)
def get_origin_story(keyword):
    try:
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        best_model = None
        for m in all_models:
            if '1.5-flash' in m.lower():
                best_model = m
                break
                
        if not best_model:
            for m in all_models:
                if 'flash' in m.lower():
                    best_model = m
                    break
                    
        if not best_model:
            best_model = all_models[0]

        model = genai.GenerativeModel(best_model)
        
        prompt = f"너는 경기도 '안성시'의 향토 역사를 아주 잘 아는 초등학교 선생님이야. 3학년 학생이 '{keyword}'라는 지명(땅, 산, 호수 이름)을 검색했어. 이 이름이 왜 붙여졌는지 그 유래와 한자 뜻을 초등학교 3학년이 이해하기 쉽게 이모지를 섞어서 3~4문장으로 재미있게 설명해줘."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "앗! AI 지역학자가 지금 너무 많은 질문을 받아서 숨을 고르고 있어요. 1분만 기다렸다가 다시 [유래 찾기] 버튼을 눌러줄래? 😊"
        return f"앗! AI가 잠시 쉬고 있어요. (오류: {e})"

def show_page():
    # 🎨 [수정됨] 중앙 정렬 및 둥근 직사각형 버튼 디자인 적용
    st.markdown("""
        <style>
        .dash-praise {
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: #2E7D32;
            background-color: #E8F5E9;
            padding: 20px;
            border-radius: 20px;
            border: 3px dashed #81C784;
            margin-top: 40px;
            margin-bottom: 30px;
        }
        /* 특정 훅(hook)이 있는 컬럼 안의 버튼만 예쁘게 꾸밉니다. */
        div[data-testid="column"]:has(.dash-btn-hook) button {
            height: 70px !important;
            border-radius: 25px !important; /* 동그라미(50%)에서 둥근 직사각형(25px)으로 변경 */
            background: linear-gradient(135deg, #FFD54F, #FFB300) !important;
            color: #4E342E !important;
            font-size: 1.3rem !important;
            font-weight: 900 !important;
            border: 4px solid #FFF8E1 !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
            transition: all 0.3s ease !important;
            white-space: pre-wrap !important;
        }
        div[data-testid="column"]:has(.dash-btn-hook) button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.25) !important;
            background: linear-gradient(135deg, #FFC107, #FFA000) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏷️ 안성의 땅 이름 비밀 찾기")
    st.info("💡 우리 동네 이름, 산, 호수 이름(예: 보개면, 비봉산, 고삼호수)을 검색하면 이름의 유래를 알려줍니다!")

    current_student = st.session_state.get('username', '학생')

    # AI 검색기
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        search_origin = st.text_input("📍 검색어 입력", key="search_origin")
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_origin_btn = st.button("유래 찾기 🚀")
        
    if search_origin_btn and search_origin:
        with st.spinner('지역 사전을 펼치고 뜻을 풀이하는 중... 📜'):
            result = get_origin_story(search_origin)
            st.success(f"**🤖 AI 역사학자의 답변:**\n\n{result}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("👀 **검색한 장소의 실제 모습이 궁금하다면?**")
            
            encoded_keyword = urllib.parse.quote(f"안성 {search_origin}")
            naver_url = f"https://search.naver.com/search.naver?where=image&sm=tab_jum&query={encoded_keyword}"
            st.link_button(f"'{search_origin}' 네이버 이미지 검색하기 🔍", naver_url, use_container_width=True)
            
    st.markdown("---")

    # 기록 폼
    with st.form("name_origin_form", clear_on_submit=True):
        st.write("✍️ **조사한 땅 이름의 뜻을 친구들에게 소개하듯 정리해 보세요.**")
        place_name = st.text_input("📍 장소 이름")
        place_origin = st.text_area("📖 이름에 담긴 뜻과 유래 (나의 생각 포함)", height=150)
        
        if st.form_submit_button("이름의 비밀 백과사전에 저장하기 🚀", use_container_width=True):
            if place_name and place_origin:
                if db_connected:
                    collection.insert_one({"type": "지역명유래", "username": current_student, "place_name": place_name, "origin": place_origin, "timestamp": datetime.datetime.now()})
                    st.success("🎉 땅 이름의 비밀이 기록 완료되었어요!")
                    st.balloons()
            else:
                st.warning("⚠️ 장소 이름과 유래를 꼼꼼하게 적어주세요!")

    # =========================================================
    # 🏅 칭찬 메시지 & 대시보드로 가는 버튼 (중앙 정렬 완벽 적용!)
    # =========================================================
    st.markdown(f'<div class="dash-praise">🎉 지금까지 열심히 공부한 <span style="color:#E65100;">{current_student}</span> 대원을 칭찬해!<br>우리가 얼마나 열심히 했는지 알아볼까? 👀</div>', unsafe_allow_html=True)
    
    # [수정됨] 화면을 3칸으로 나누고 가운데 칸(col_btn2)에 버튼을 넣어서 무조건 정중앙에 오도록 만듭니다.
    col_empty1, col_btn2, col_empty3 = st.columns([1, 1.5, 1])
    
    with col_btn2:
        st.markdown("<span class='dash-btn-hook'></span>", unsafe_allow_html=True)
        if st.button("📊 나의 발자국 확인하기", use_container_width=True):
            st.session_state.current_page = "stu_dash"  
            st.rerun()

    # ---------------------------------------------------------
    # 🤖 AI 보조교사 호출
    # ---------------------------------------------------------
    activity_desc = "이 화면은 안성의 땅 이름(비봉산, 고삼호수 등)을 검색하여 AI 지역학자에게 유래를 물어보고 백과사전에 기록하는 곳입니다. 모든 활동의 마지막 단계이므로, 학생이 잘 마무리하고 '나의 발자국 확인하기' 버튼을 누르도록 독려해 주세요."
    ai_teacher.show_ai_teacher(activity_name="활동 3-3. 안성의 땅 이름 비밀 찾기", context_description=activity_desc)