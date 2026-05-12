import streamlit as st
import os
import datetime
import base64
from pymongo import MongoClient

# ---------------------------------------------------------
# 🛠️ 1. MongoDB 연결 설정
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]       
    collection = db["student_timeline"] 
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

def show_page():
    if "current_step" not in st.session_state:
        st.session_state.current_step = None
    if "show_growth" not in st.session_state:
        st.session_state.show_growth = False

    # 🎨 2. 디자인 설정
    st.markdown("""
        <style>
        .timeline-container { display: flex; flex-direction: column; align-items: center; margin-top: 30px; width: fit-content; margin-left: auto; margin-right: auto; }
        .box { width: 180px; height: 100px; background-color: #FFFFFF; border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold; color: #444; box-shadow: 4px 4px 15px rgba(0,0,0,0.08); border: 5px solid #EEEEEE; text-align: center; line-height: 1.3; padding: 10px; margin: 0 auto 5px auto; }
        .box-1 { border-color: #FFB3BA !important; } .box-2 { border-color: #FFDFBA !important; } .box-3 { border-color: #FFFFBA !important; } .box-4 { border-color: #BAFFC9 !important; } .box-5 { border-color: #BAE1FF !important; } 
        
        /* 💡 수정된 부분: 가로 길이(width) 130px 제한을 삭제하고 여백(padding)으로 버튼을 시원하게 늘립니다! */
        div.stButton > button { 
            border-radius: 50px !important; 
            padding: 8px 30px !important; /* 좌우 여백을 넉넉하게 주어 버튼이 길어지도록 함 */
            height: auto !important; 
            min-height: 45px !important;
            background-color: #ffffff !important; 
            border: 2px solid #FF8080 !important; 
            color: #FF8080 !important; 
            font-size: 1.1rem !important;
            font-weight: bold !important; 
            transition: all 0.3s ease; 
        }
        div.stButton > button:hover { background-color: #FF8080 !important; color: #ffffff !important; }
        
        .download-btn-container button { width: 175px !important; height: 70px !important; border: 3px solid #4D96FF !important; color: #4D96FF !important; background-color: #ffffff !important; border-radius: 50px !important; box-shadow: 0px 4px 10px rgba(77, 150, 255, 0.2) !important; white-space: pre-wrap !important; transition: all 0.3s ease; display: block; margin: 0 auto; }
        .download-btn-container button p { font-size: 1.25rem !important; font-weight: 900 !important; line-height: 1.3 !important; margin: 0 !important; }
        .download-btn-container button:hover { background-color: #4D96FF !important; color: #ffffff !important; }
        .arrow { font-size: 2.2rem; color: #FF8080; font-weight: bold; text-align: center; margin-top: 35px; }
        .vertical-connector { display: flex; justify-content: flex-end; width: 100%; padding-right: 73px; margin: 30px 0; }
        .arrow-down { font-size: 2.5rem; color: #FF8080; font-weight: bold; width: 35px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    st.title("👣 나의 발자국 살펴보기")
    
    # --- 타임라인 UI 시작 ---
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    c1, a1, c2, a2, c3 = st.columns([1, 0.2, 1, 0.2, 1])
    with c1:
        st.markdown('<div class="box box-1">내가<br>태어났을 때</div>', unsafe_allow_html=True)
        if st.button("💾 저장하기", key="save1"): st.session_state.current_step = "1단계_태어났을때"
    with a1: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="box box-2">어린이집<br>유치원</div>', unsafe_allow_html=True)
        if st.button("💾 저장하기", key="save2"): st.session_state.current_step = "2단계_어린이집유치원"
    with a2: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="box box-3">초등학교<br>입학식</div>', unsafe_allow_html=True)
        if st.button("💾 저장하기", key="save3"): st.session_state.current_step = "3단계_입학식"

    st.markdown('<div class="vertical-connector"><div class="arrow-down">↓</div></div>', unsafe_allow_html=True)

    c_down, c5, a3, c4 = st.columns([1, 1, 0.2, 1])
    with c_down:
        st.markdown('<div class="download-btn-container">', unsafe_allow_html=True)
        pdf_file_path = "letter.pdf" 
        if os.path.exists(pdf_file_path):
            with open(pdf_file_path, "rb") as pdf_file:
                st.download_button(label="📄 활동지\n다운로드", data=pdf_file.read(), file_name="letter.pdf", mime="application/pdf", key="download_work")
        else:
            st.button("📄 활동지\n(준비 중)", key="no_file_btn", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="box box-4">지금의 나</div>', unsafe_allow_html=True)
        if st.button("💾 저장하기", key="save4"): st.session_state.current_step = "4단계_지금의나"
    with a3: st.markdown('<div class="arrow">←</div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="box box-5">1년 후의<br>내 모습</div>', unsafe_allow_html=True)
        if st.button("💾 저장하기", key="save5"): st.session_state.current_step = "5단계_미래의나"

    st.markdown('</div>', unsafe_allow_html=True)
    # --- 타임라인 UI 끝 ---

    # ---------------------------------------------------------
    # 📝 3. 데이터베이스 저장 영역
    # ---------------------------------------------------------
    if st.session_state.current_step:
        st.divider()
        display_name = st.session_state.current_step.split("_")[1]
        st.subheader(f"📍 '{display_name}' 단계 기록하기")
        
        memory_text = st.text_area("✨ 이 때의 나에게 하고 싶은 말이나 기억나는 점을 적어보세요!", height=100)
        uploaded_file = st.file_uploader("📸 사진 파일을 선택해주세요.", type=["png", "jpg", "jpeg"], key="file_uploader_key")

        if st.button("🚀 내 발자국 영구 저장하기", type="primary"):
            if uploaded_file is not None and memory_text != "":
                if db_connected:
                    user_id = st.session_state.get('username', 'test_student')
                    encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    
                    record = {
                        "username": user_id,
                        "stage": st.session_state.current_step,
                        "content": memory_text,
                        "image_base64": encoded_image,
                        "timestamp": datetime.datetime.now()
                    }
                    
                    collection.update_one(
                        {"username": user_id, "stage": st.session_state.current_step}, 
                        {"$set": record}, 
                        upsert=True
                    )
                    
                    st.toast(f"🎉 '{display_name}' 발자국이 안전하게 저장되었어요!", icon="✅")
                    st.balloons()
                    st.session_state.current_step = None 
                    st.rerun() 
                else:
                    st.error("DB가 연결되지 않았습니다.")
            else:
                st.warning("⚠️ 사진을 올리고 내용도 함께 적어주세요!")

    # ---------------------------------------------------------
    # 🌟 4. '나의 성장 과정' 한눈에 보기
    # ---------------------------------------------------------
    if db_connected:
        user_id = st.session_state.get('username', 'test_student')
        user_records = list(collection.find({"username": user_id}))
        saved_stages = {r["stage"]: r.get("image_base64", "") for r in user_records if "image_base64" in r}
        
        if len(saved_stages) >= 5:
            st.divider()
            
            # 💡 수정된 부분: 버튼을 화면 중앙에 아주 넓게 꽉 채워지도록 컬럼 비율을 [0.5, 4, 0.5]로 대폭 늘렸습니다!
            _, btn_col, _ = st.columns([0.5, 4, 0.5])
            with btn_col:
                if st.button("🌟 나의 성장 과정", use_container_width=True):
                    st.session_state.show_growth = not st.session_state.show_growth
                    
            if st.session_state.show_growth:
                st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
                
                def get_photo_box(img_base64, box_class, title_text):
                    return f'''
                    <div style="display: flex; flex-direction: column; align-items: center;">
                        <div class="box {box_class}" style="padding: 0; overflow: hidden; display: flex; justify-content: center; align-items: center; border-width: 5px;">
                            <img src="data:image/jpeg;base64,{img_base64}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 18px;">
                        </div>
                        <div style="margin-top: 3px; color: black; font-weight: bold; text-align: center; line-height: 1.2;">
                            {title_text}
                        </div>
                    </div>
                    '''

                c1, a1, c2, a2, c3 = st.columns([1, 0.2, 1, 0.2, 1])
                with c1: st.markdown(get_photo_box(saved_stages.get("1단계_태어났을때", ""), "box-1", "내가<br>태어났을 때"), unsafe_allow_html=True)
                with a1: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
                with c2: st.markdown(get_photo_box(saved_stages.get("2단계_어린이집유치원", ""), "box-2", "어린이집<br>유치원"), unsafe_allow_html=True)
                with a2: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
                with c3: st.markdown(get_photo_box(saved_stages.get("3단계_입학식", ""), "box-3", "초등학교<br>입학식"), unsafe_allow_html=True)
                
                st.markdown('<div class="vertical-connector"><div class="arrow-down">↓</div></div>', unsafe_allow_html=True)
                
                c_down, c5, a3, c4 = st.columns([1, 1, 0.2, 1])
                with c_down: st.write("") 
                with c4: st.markdown(get_photo_box(saved_stages.get("4단계_지금의나", ""), "box-4", "지금의 나"), unsafe_allow_html=True)
                with a3: st.markdown('<div class="arrow">←</div>', unsafe_allow_html=True)
                with c5: st.markdown(get_photo_box(saved_stages.get("5단계_미래의나", ""), "box-5", "1년 후의<br>내 모습"), unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.info("💡 각 단계를 따라가며 옛 기억을 떠올리고 미래를 생각해보세요.")
    st.info("💡 '활동지 다운로드'를 눌러 활동지를 다운 받아 직접 그림과 글로 표현해보세요.")