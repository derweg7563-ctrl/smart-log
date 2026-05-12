import streamlit as st
import datetime
import urllib.parse
from pymongo import MongoClient

# 👇 1. AI 보조교사 모듈 불러오기
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

# 🎯 선생님의 원래 구글 키 적용
try:
    genai.configure(api_key=st.secrets["google"]["api_key"])
except Exception as e:
    st.error("🚨 secrets.toml 파일에 구글 열쇠가 없습니다!")

# 💡 [404 에러 원천 차단 코드] 
def get_anseong_story(keyword):
    try:
        # 1. 선생님의 열쇠로 쓸 수 있는 '진짜' 모델 목록만 가져옵니다.
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 2. 가장 안전한 '1.5-flash'를 먼저 찾습니다.
        best_model = None
        for m in all_models:
            if '1.5-flash' in m.lower():
                best_model = m
                break
        
        # 3. 만약 1.5-flash가 없다면, 다른 flash 모델이라도 찾습니다.
        if not best_model:
            for m in all_models:
                if 'flash' in m.lower():
                    best_model = m
                    break
        
        # 4. 그래도 없으면 무조건 목록에 있는 첫 번째 모델을 씁니다. (없는 모델을 부르는 404 방지!)
        if not best_model:
            best_model = all_models[0]

        model = genai.GenerativeModel(best_model)
        
        # '안성시' 맞춤 프롬프트
        prompt = f"너는 경기도 '안성시'의 향토 역사를 아주 잘 아는 초등학교 선생님이야. 3학년 학생이 '{keyword}'에 대해 검색했어. 이것과 관련된 안성의 옛이야기나 전설을 초등학교 3학년이 이해하기 쉽게 이모지를 섞어서 3~4문장으로 재미있게 이야기해줘."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "앗! AI 역사학자가 지금 너무 많은 질문을 받아서 숨을 고르고 있어요. 1분만 기다렸다가 다시 [이야기 찾기] 버튼을 눌러줄래? 😊"
        return f"앗! AI가 잠시 쉬고 있어요. (오류: {e})"

def show_page():
    st.title("📖 안성의 옛이야기 탐험")
    st.info("💡 궁금한 안성의 장소나 인물(예: 칠장사, 박문수, 남사당패)을 검색하면 AI가 옛이야기를 들려줍니다!")

    current_student = st.session_state.get('username', '학생')

    # AI 검색기
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        search_story = st.text_input("🔍 검색어 입력", key="search_story")
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_story_btn = st.button("이야기 찾기 🚀")
        
    if search_story_btn and search_story:
        with st.spinner('안성의 두꺼운 역사책을 뒤지는 중... 📚'):
            result = get_anseong_story(search_story)
            st.success(f"**🤖 AI 역사학자의 답변:**\n\n{result}")
            
            search_query = urllib.parse.quote(f"안성 {search_story}")
            image_search_url = f"https://search.naver.com/search.naver?where=image&query={search_query}"
            
            st.link_button(f"🖼️ '{search_story}' 실제 사진 구경하기(네이버로 이동)", image_search_url, use_container_width=True)
    
    st.markdown("---")
    
    # 기록 폼
    with st.form("story_form", clear_on_submit=True):
        st.write("✍️ **AI가 찾아준 이야기나 직접 들은 이야기를 내 생각과 함께 정리해 보세요!**")
        story_title = st.text_input("📝 이야기의 제목")
        story_content = st.text_area("🗣️ 이야기 내용 및 나의 생각", height=150)
        
        if st.form_submit_button("우리 동네 백과사전에 저장하기 🚀", use_container_width=True):
            if story_title and story_content:
                if db_connected:
                    collection.insert_one({"type": "옛이야기", "username": current_student, "title": story_title, "content": story_content, "timestamp": datetime.datetime.now()})
                    st.success("🎉 재미있는 옛이야기가 저장되었어요!")
                    st.balloons()
            else:
                st.warning("⚠️ 빈칸을 모두 채워주세요!")

    # ---------------------------------------------------------
    # 🤖 2. AI 보조교사 호출
    # ---------------------------------------------------------
    activity_desc = "이 화면은 궁금한 안성의 장소나 인물(예: 칠장사, 박두진)을 검색하여 AI 역사학자에게 옛이야기를 물어보고, 그 내용을 바탕으로 '동네 백과사전'에 저장하는 곳입니다."
    ai_teacher.show_ai_teacher(activity_name="활동 3-1. 안성의 옛이야기 탐험", context_description=activity_desc)