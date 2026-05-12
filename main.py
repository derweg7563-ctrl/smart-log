import streamlit as st
import pandas as pd
import os
import base64
from pymongo import MongoClient
import streamlit.components.v1 as components 

import teacher_page, activity, question
import activity1_1, activity1_2, activity1_3
import activity2_1, activity2_2, activity2_3
import activity3_1, activity3_2, activity3_3
import stu_dash

st.set_page_config(page_title="SMART-LOG 디지털 역사 기록장", layout="wide")

@st.cache_resource
def init_connection():
    try: return MongoClient(st.secrets["mongo"]["uri"])
    except: return None

client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]; users_collection = db["users"]

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "role" not in st.session_state: st.session_state.role = ""
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "show_question" not in st.session_state: st.session_state.show_question = False
if "previous_page" not in st.session_state: st.session_state.previous_page = "main"

for i in range(1, 4):
    if f"menu{i}_open" not in st.session_state: st.session_state[f"menu{i}_open"] = False

def go_to(page_name): st.session_state.current_page = page_name
def toggle_menu(menu_num): st.session_state[f"menu{menu_num}_open"] = not st.session_state[f"menu{menu_num}_open"]
def reset_question(): st.session_state.show_question = False

# ======== 💡 현재 페이지인지 확인해서 디자인을 바꿔주는 마법의 함수 ========
def get_hook(page_name, default_hook="sub-menu-hook"):
    if st.session_state.current_page == page_name:
        return "<span class='active-menu-hook'></span>"
    return f"<span class='{default_hook}'></span>"
# ============================================================================

st.markdown("""
    <style>
    div.element-container:has(.login-btn-hook) + div.element-container button,
    div.element-container:has(.q-btn-hook) + div.element-container button { background-color: #1E88E5 !important; border: 2px solid #1E88E5 !important; border-radius: 20px !important; color: #ffffff !important; font-size: 1.2rem !important; font-weight: bold !important; padding: 8px 16px !important; }
    div.element-container:has(.logout-hook) + div.element-container button { background-color: #FFE4E1 !important; border: 2px solid #FFB6C1 !important; border-radius: 20px !important; font-size: 25px !important; font-weight: bold !important; color: #555555 !important; padding: 10px !important; }
    div.element-container:has(.home-btn-hook) + div.element-container button { color: #333333 !important; font-size: 20px !important; font-weight: bold !important; border: 1px solid #ddd !important; border-radius: 10px !important; background-color: #f9f9f9 !important; }
    div.element-container:has(.menu1-hook) + div.element-container button { color: #1565C0 !important; font-size: 30px !important; font-weight: 900 !important; border: 3px solid #1565C0 !important; border-radius: 15px !important; background-color: #ffffff !important; padding: 15px !important; margin-bottom: 5px !important; }
    div.element-container:has(.menu2-hook) + div.element-container button { color: #2E7D32 !important; font-size: 30px !important; font-weight: 900 !important; border: 3px solid #2E7D32 !important; border-radius: 15px !important; background-color: #ffffff !important; padding: 15px !important; margin-bottom: 5px !important; }
    div.element-container:has(.menu3-hook) + div.element-container button { color: #EF6C00 !important; font-size: 30px !important; font-weight: 900 !important; border: 3px solid #EF6C00 !important; border-radius: 15px !important; background-color: #ffffff !important; padding: 15px !important; margin-bottom: 5px !important; }
    div.element-container:has(.sub-menu-hook) + div.element-container button { color: #000000 !important; font-size: 20px !important; font-weight: 700 !important; border-radius: 10px !important; border: 1px solid #ddd !important; padding: 10px !important; margin-bottom: 5px !important; background-color: #f9f9f9 !important; }
    
    /* ======== 💡 선택된(현재) 페이지 버튼 디자인 (짙은 회색 + 흰 글씨) ======== */
    div.element-container:has(.active-menu-hook) + div.element-container button { color: #ffffff !important; font-size: 20px !important; font-weight: 700 !important; border-radius: 10px !important; border: 2px solid #555555 !important; padding: 10px !important; margin-bottom: 5px !important; background-color: #555555 !important; }
    /* ============================================================================ */
    </style>
""", unsafe_allow_html=True)

def set_bg_and_point(bg_file, point_file):
    if os.path.exists(bg_file):
        with open(bg_file, "rb") as f: bg_encoded = base64.b64encode(f.read()).decode()
        point_html = ""
        if os.path.exists(point_file):
            with open(point_file, "rb") as f: point_encoded = base64.b64encode(f.read()).decode()
            point_html = f"""
            <style>
            @keyframes fadeBlink {{ 0% {{ opacity: 0; transform: translateY(0px); }} 50% {{ opacity: 1; transform: translateY(-15px); }} 100% {{ opacity: 0; transform: translateY(0px); }} }}
            .marker-base {{ position: fixed; bottom: 25vh; width: clamp(30px, 5vw, 50px); z-index: 999999; pointer-events: none; animation: fadeBlink 3s infinite ease-in-out; }}
            .marker-left {{ left: calc(60% - 200px); animation-delay: 0s; }} 
            .marker-center {{ left: calc(65% - 100px); animation-delay: 1s; }} 
            .marker-right {{ left: 70%; animation-delay: 2s; }}
            </style>
            <img src="data:image/png;base64,{point_encoded}" class="marker-base marker-left">
            <img src="data:image/png;base64,{point_encoded}" class="marker-base marker-center">
            <img src="data:image/png;base64,{point_encoded}" class="marker-base marker-right">
            """
        st.markdown(f"{point_html}<style>.stApp {{ background-image: url('data:image/png;base64,{bg_encoded}'); background-size: cover; background-position: center bottom !important; background-repeat: no-repeat; background-attachment: fixed; }}</style>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.sidebar.markdown("<div style='text-align:center; font-size:1.6rem; font-weight:700; color:#31333F; margin-bottom:1rem;'>📖 학습 안내 📖</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("""
        <style>
        div[role="radiogroup"] p {
            font-size: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    menu = st.sidebar.radio("메뉴 선택", ["로그인", "회원가입"], on_change=reset_question)
    
    st.sidebar.markdown("""
        <div style="font-size: 20px; color: #4F4F4F; line-height: 1.6;">
            <span style="color: #2E7D32; font-weight: bold;">본 학습</span>을 위해서는<br>
            <span style="color: #FFB300; font-weight: bold;">회원가입</span>이 필요합니다.<br>
            <span style="color: #1976D2; font-weight: bold;">아이디</span>와 <span style="color: #1976D2; font-weight: bold;">비밀번호</span>를<br>
            입력하여 학습을 시작하세요
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True) 
    
    if os.path.exists("question.png"):
        with open("question.png", "rb") as f: q_enc = base64.b64encode(f.read()).decode()
        st.sidebar.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{q_enc}" style="width: 80px; margin-bottom: 10px;"></div>', unsafe_allow_html=True)
        
    st.sidebar.markdown("""
        <div style="text-align:center; font-size: 30px; color: #D81B60; font-weight: bold; line-height: 1.4; margin-bottom: 10px;">
            전체 학습을 위해<br>꼭 확인하세요
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<span class='q-btn-hook'></span>", unsafe_allow_html=True)
    if st.sidebar.button("👉 전체 학습 안내 보기", use_container_width=True):
        st.session_state.show_question = True; st.rerun()

    if st.session_state.show_question:
        question.show_page()  
    else:
        set_bg_and_point("background.png", "point.png")
        st.markdown("""<style>.block-container { background-color: rgba(255,255,255,0.85) !important; padding: 3rem !important; border-radius: 30px !important; margin-top: 15vh !important; max-width: 500px !important; margin-left: auto; margin-right: 5vw; }</style>""", unsafe_allow_html=True)
        
# 수정 후 (복사해서 덮어쓰세요!)
        st.markdown('<h1 style="text-align:center; color:white; text-shadow:2px 2px 4px black; margin-bottom: 30px;">걸어온 길, 스마트 로그<br>발자국으로 되짚다</h1>', unsafe_allow_html=True)

        if menu == "회원가입":
            st.subheader("📝 학생 회원가입")
            new_user = st.text_input("아이디(ID)", key="reg_id")
            new_pw = st.text_input("비밀번호", key="reg_pw") 
            if st.button("가입하기"):
                if db_connected:
                    if users_collection.find_one({"username": new_user}): st.error("이미 존재하는 아이디입니다.")
                    else:
                        users_collection.insert_one({"username": new_user, "password": new_pw, "role": "학생"})
                        st.success("가입 완료! 로그인하세요.")
        else:
            user = st.text_input("아이디", key="login_id")
            pw = st.text_input("비밀번호", key="login_pw") 
            st.markdown("<span class='login-btn-hook'></span>", unsafe_allow_html=True)
            if st.button("로그인", use_container_width=True):
                if user == "admin" and pw == "teacher1234!":
                    st.session_state.update({"logged_in": True, "username": "관리자 선생님", "role": "선생님"}); st.rerun()
                elif db_connected:
                    match = users_collection.find_one({"username": user, "password": pw})
                    if match:
                        st.session_state.update({"logged_in": True, "username": user, "role": "학생"}); st.rerun()
                    else: st.error("정보가 틀렸습니다.")

else:
    st.markdown("<style>.stApp { background-image: none !important; background-color: #ffffff; } .block-container { max-width: 1200px !important; margin: 0 auto !important; padding: 2rem !important; box-shadow: none !important; }</style>", unsafe_allow_html=True)

    st.sidebar.markdown("<div style='text-align:center; color:#2E7D32; font-weight:bold; font-size:30px;'>SMART-LOG 발자국</div>", unsafe_allow_html=True)
    
    role_label = "👨‍🏫 관리자" if st.session_state.role == "선생님" else "👩‍🎓 학생"
    st.sidebar.markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; margin-bottom:15px; color:#1565C0;'>{st.session_state.username}님 접속 중<br>({role_label})</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<span class='logout-hook'></span>", unsafe_allow_html=True)
    if st.sidebar.button("로그아웃", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.current_page = "main"
        st.session_state.menu1_open = False; st.session_state.menu2_open = False; st.session_state.menu3_open = False
        st.rerun()
        
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("<div style='text-align:center; font-weight:bold; font-size:20px;'>🚀 어떤 활동을 해볼까요?</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='font-size:20px; font-weight:bold; margin-bottom:10px;'>활동 소개</div>", unsafe_allow_html=True)

    st.sidebar.markdown("<span class='menu1-hook'></span>", unsafe_allow_html=True)
    st.sidebar.button("어제와 오늘의 흐름 따라가기", on_click=toggle_menu, args=(1,), use_container_width=True)
    if st.session_state.menu1_open:
        st.sidebar.markdown(get_hook("1_1"), unsafe_allow_html=True)
        st.sidebar.button("나의 발자국 살펴보기", on_click=go_to, args=("1_1",), key="btn1_1", use_container_width=True)
        st.sidebar.markdown(get_hook("1_2"), unsafe_allow_html=True)
        st.sidebar.button("학교 발자국 알아보기", on_click=go_to, args=("1_2",), key="btn1_2", use_container_width=True)
        st.sidebar.markdown(get_hook("1_3"), unsafe_allow_html=True)
        st.sidebar.button("발자국 속 연표 만들기", on_click=go_to, args=("1_3",), key="btn1_3", use_container_width=True)

    st.sidebar.markdown("<span class='menu2-hook'></span>", unsafe_allow_html=True)
    st.sidebar.button("디지털에서 만나는 옛 모습", on_click=toggle_menu, args=(2,), use_container_width=True)
    if st.session_state.menu2_open:
        st.sidebar.markdown(get_hook("2_1"), unsafe_allow_html=True)
        st.sidebar.button("옛 물건 살펴보기", on_click=go_to, args=("2_1",), key="btn2_1", use_container_width=True)
        st.sidebar.markdown(get_hook("2_2"), unsafe_allow_html=True)
        st.sidebar.button("AI 유물 탐정이 되어보기", on_click=go_to, args=("2_2",), key="btn2_2", use_container_width=True)
        st.sidebar.markdown(get_hook("2_3"), unsafe_allow_html=True)
        st.sidebar.button("우리 반 애장품 전시회", on_click=go_to, args=("2_3",), key="btn2_3", use_container_width=True)

    st.sidebar.markdown("<span class='menu3-hook'></span>", unsafe_allow_html=True)
    st.sidebar.button("세대공감, 달라진 모습", on_click=toggle_menu, args=(3,), use_container_width=True)
    if st.session_state.menu3_open:
        st.sidebar.markdown(get_hook("3_1"), unsafe_allow_html=True)
        st.sidebar.button("안성의 옛이야기 탐험", on_click=go_to, args=("3_1",), key="btn3_1", use_container_width=True)
        st.sidebar.markdown(get_hook("3_2"), unsafe_allow_html=True)
        st.sidebar.button("안성의 달라진 모습", on_click=go_to, args=("3_2",), key="btn3_2", use_container_width=True)
        st.sidebar.markdown(get_hook("3_3"), unsafe_allow_html=True)
        st.sidebar.button("안성의 땅 이름 비밀 찾기", on_click=go_to, args=("3_3",), key="btn3_3", use_container_width=True)

    st.sidebar.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # 메인화면과 대시보드 버튼에도 색상 변경 마법 적용!
    st.sidebar.markdown(get_hook("main", "home-btn-hook"), unsafe_allow_html=True)
    st.sidebar.button("🏠 메인 화면으로 돌아가기", on_click=go_to, args=("main",), use_container_width=True)

    st.sidebar.markdown(get_hook("stu_dash", "sub-menu-hook"), unsafe_allow_html=True)
    st.sidebar.button("📊 나의 활동 기록 보기", on_click=go_to, args=("stu_dash",), use_container_width=True)

    if st.session_state.role == "선생님": 
        teacher_page.show_page()
    else:
        page = st.session_state.current_page
        if page != st.session_state.previous_page:
            scroll_js = """<script>var mainContent = window.parent.document.querySelector('section.main'); if (mainContent) { mainContent.scrollTo(0, 0); } window.parent.scrollTo(0, 0);</script>"""
            components.html(scroll_js, height=0)
            st.session_state.previous_page = page

        if page == "main": activity.show_page()
        elif page == "1_1": activity1_1.show_page()
        elif page == "1_2": activity1_2.show_page()
        elif page == "1_3": activity1_3.show_page()
        elif page == "2_1": activity2_1.show_page()
        elif page == "2_2": activity2_2.show_page()
        elif page == "2_3": activity2_3.show_page()
        elif page == "3_1": activity3_1.show_page()
        elif page == "3_2": activity3_2.show_page()
        elif page == "3_3": activity3_3.show_page()
        elif page == "stu_dash": stu_dash.show_page()