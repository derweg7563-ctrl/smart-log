import streamlit as st
import os
import datetime
import base64
from pymongo import MongoClient
from streamlit_image_comparison import image_comparison

# 👇 우리가 만든 AI 선생님 모듈 불러오기!
import ai_teacher 

# ---------------------------------------------------------
# 🛠️ 1. MongoDB 연결 설정 (학교 발자국 전용 보관함)
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]
    collection = db["school_footprints"] 
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

try:
    from streamlit_image_comparison import image_comparison
except ImportError:
    st.error("🚨 `streamlit-image-comparison` 패키지가 필요합니다!")

def show_page():
    # 🎨 2. 디자인 CSS 마법
    st.markdown("""
        <style>
        iframe[title="streamlit_image_comparison.image_comparison"] {
            border-radius: 25px !important;
            border: 8px solid transparent !important;
            background-image: linear-gradient(white, white), 
                              linear-gradient(to right, #FFB3BA, #FFDFBA, #FFFFBA, #BAFFC9, #BAE1FF) !important;
            background-origin: border-box !important;
            background-clip: padding-box, border-box !important;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.1) !important;
            display: block; margin: 0 auto;
        }
        .cute-title { text-align: center; font-size: 1.5rem; font-weight: 800; color: #5A72A0; margin-bottom: 20px; background-color: #F8F9FA; padding: 15px; border-radius: 20px; border: 3px dashed #BAE1FF; }
        .video-desc { text-align: center; font-weight: bold; color: #5A72A0; font-size: 1.1rem; margin-top: 15px; line-height: 1.4; }
        div.stButton { display: flex; justify-content: center; width: 100%; }
        div.stButton > button { border-radius: 50px !important; padding: 8px 30px !important; height: auto !important; min-height: 45px !important; background-color: #ffffff !important; border: 2px solid #FF8080 !important; color: #FF8080 !important; font-size: 1.1rem !important; font-weight: bold !important; transition: all 0.3s ease; }
        div.stButton > button:hover { background-color: #FF8080 !important; color: #ffffff !important; }
        
        /* 학생 아이디 강조 스타일 */
        .student-name-highlight {
            color: #FF8080;
            font-size: 1.8rem;
            text-decoration: underline;
            text-decoration-color: #FFFFBA;
            text-decoration-thickness: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏫 학교 발자국 알아보기")
    st.write("---")
    st.info("💡 우리 학교의 역사가 담긴 장소나 소중한 물건들을 찾아 '발자국'을 남겨보세요.")

    # ---------------------------------------------------------
    # 🌟 3. 과거와 현재 이미지 비교 컴포넌트
    # ---------------------------------------------------------
    st.markdown('<div class="cute-title">👀 우리 학교의 어제와 오늘, 요리조리 비교해 볼까요?</div>', unsafe_allow_html=True)

    img1_path = "school1.png"
    img2_path = "school.jpg"

    if os.path.exists(img1_path) and os.path.exists(img2_path):
        try:
            # 아까 성공했던 완벽한 비율의 가운데 정렬 코드입니다!
            col1, col2, col3 = st.columns([1, 8, 1]) 
            with col2:
                image_comparison(
                    img1=img1_path, 
                    img2=img2_path, 
                    label1="과거", 
                    label2="현재", 
                    width=850,            
                    starting_position=50, 
                    show_labels=True, 
                    make_responsive=True, 
                    in_memory=True
                )
        except NameError:
            pass 
    else:
        st.warning("⚠️ 앗! 학교 사진을 아직 찾을 수 없어요.")

    st.write("---")
    
    # ---------------------------------------------------------
    # 📺 4. 학교 발자국 알아보는 방법
    # ---------------------------------------------------------
    st.subheader("📍 학교 발자국 알아보는 방법")
    st.write("") 

    col1, col2 = st.columns(2)
    with col1:
        st.video("https://youtu.be/rCxpWNuwsrY")
        st.markdown('<div class="video-desc">💻 학교 홈페이지를 통해<br>학교 발자국 알아보기</div>', unsafe_allow_html=True)
    with col2:
        st.video("https://www.youtube.com/watch?v=zxmOUGwIRgk&t=1s")
        st.markdown('<div class="video-desc">📌 학교 게시판을 통해<br>학교 발자국 알아보기</div>', unsafe_allow_html=True)

    st.write("---")

    # ---------------------------------------------------------
    # 📝 5. 접속한 학생별 맞춤형 저장 공간
    # ---------------------------------------------------------
    current_student = st.session_state.get('username', '학생')
    
    st.markdown(f'<h3>📸 <span class="student-name-highlight">{current_student}</span>의 학교 발자국 기록하기</h3>', unsafe_allow_html=True)
    st.info(f"{current_student} 학생이 학교 구석구석에서 발견한 우리 학교만의 특별한 발자국을 영구 보관해 보세요!")

    memory_text = st.text_area(
        "✨ 내가 발견한 학교 발자국을 적고 그 느낌을 자세히 적어보세요\n(*아래 안성저장소도 활용해요* 예: 1985년 운동회 사진을 찾았는데 그 때는 운동장에서 많은 사람들이 모여 재미있는 활동을 하는 모습이 즐거워 보인다.)", 
        height=150
    )
    
    uploaded_file = st.file_uploader("📸 조사한 학교 발자국 사진을 선택해주세요.", type=["png", "jpg", "jpeg"])

    _, btn_col, _ = st.columns([0.5, 4, 0.5])
    with btn_col:
        if st.button("🚀 우리 학교 발자국 영구 저장하기", use_container_width=True):
            if uploaded_file is not None and memory_text != "":
                
                if db_connected:
                    encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    
                    record = {
                        "username": current_student,
                        "content": memory_text,
                        "image_base64": encoded_image,
                        "timestamp": datetime.datetime.now()
                    }
                    
                    collection.update_one(
                        {"username": current_student}, 
                        {"$set": record}, 
                        upsert=True
                    )
                    
                    st.toast(f"🎉 {current_student} 학생의 학교 발자국이 안전하게 저장되었어요!", icon="✅")
                    st.balloons()
                    
                else:
                    st.error("DB가 연결되지 않았습니다.")
            else:
                st.warning("⚠️ 사진을 올리고 내용도 함께 적어주세요!")
                
        # 새롭게 추가된 안성저장소 링크 버튼
        st.write("") 
        st.link_button("🏛️ 안성저장소 바로가기", "https://www.anseong.go.kr/archive/kor/index.do", use_container_width=True)

    # ---------------------------------------------------------
    # 🤖 6. AI 보조교사 호출 (맨 마지막에 딱 붙어있습니다!)
    # ---------------------------------------------------------
    activity_desc = "이 화면은 학교의 과거와 현재 사진을 비교해보고, 학교 홈페이지나 게시판에서 학교의 역사가 담긴 사진을 찾아 저장하는 곳입니다. 학생이 사진을 업로드하고 느낀 점을 적어야 합니다."
    
    ai_teacher.show_ai_teacher(activity_name="활동 1-2. 학교 발자국 알아보기", context_description=activity_desc)
