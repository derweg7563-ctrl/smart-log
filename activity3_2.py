import streamlit as st
import datetime
from pymongo import MongoClient

# 👇 1. AI 보조교사 모듈 불러오기
import ai_teacher

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

def show_page():
    st.title("🔄 평택의 달라진 모습")
    st.info("💡 카카오맵 타임머신을 타고, 우리 동네가 어떻게 변했는지 직접 탐험해 보세요!")

    current_student = st.session_state.get('username', '학생')

    # ---------------------------------------------------------
    # 🔎 1단계: 선생님 영상 보고 카카오맵 탐험하기
    # ---------------------------------------------------------
    st.markdown("### 🔎 [1단계] 타임머신 타고 옛날 모습 구경하기")
    
    col_video, col_desc = st.columns([1, 1])
    
    with col_video:
        st.write("📺 **카카오맵 타임머신 타는 방법**")
        # 💡 선생님 필수 작업: 나중에 직접 만드신 유튜브 영상 주소를 아래 쌍따옴표 안에 넣어주세요!
        # (지금은 선생님이 확인하실 수 있게 임시로 귀여운 영상을 넣어두었습니다.)
        st.video("https://youtu.be/SYUBOLP00W0") 
        st.caption("▲ 선생님이 만든 영상을 보고 방법을 잘 기억해 두세요!")

    with col_desc:
        st.markdown("""
        <div style='background-color:#FFF9C4; padding:20px; border-radius:10px; height:85%; margin-top: 30px;'>
            <b>🚗 직접 과거로 떠나볼까요?</b><br><br>
             영상을 잘 보았나요?<br>
            이제 아래 버튼을 눌러 카카오맵을 켜고, 평택 시내나 우리 학교 주변의 도로, 건물이 10년, 15년 전에 어땠는지 직접 탐험해 보세요!
        </div>
        """, unsafe_allow_html=True)
        st.link_button("카카오맵으로 탐험 가기 🗺️", "https://map.kakao.com/", use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # ✍️ 2단계: 학생 기록 폼 (기존 3단계에서 올라옴)
    # ---------------------------------------------------------
    st.markdown("### ✍️ [2단계] 내가 발견한 달라진 점 기록하기")
    with st.form("change_form", clear_on_submit=True):
        col_past, col_present = st.columns(2)
        with col_past:
            past_view = st.text_area("⏳ 옛날에는 어땠나요? (과거)", placeholder="예: 높은 건물이 없고 흙길이었어요.", height=150)
        with col_present:
            present_view = st.text_area("🏙️ 지금은 어떻게 변했나요? (현재)", placeholder="예: 멋진 산책로와 높은 아파트가 생겼어요.", height=150)
        
        change_reason = st.text_input("🤔 왜 이렇게 모습이 달라졌을까요? (나의 생각)", placeholder="사람들이 많이 살게 되어서, 도로가 필요해져서 등")
        
        if st.form_submit_button("달라진 모습 기록하기 🚀", use_container_width=True):
            if past_view and present_view:
                if db_connected:
                    collection.insert_one({"type": "달라진모습", "username": current_student, "past": past_view, "present": present_view, "reason": change_reason, "timestamp": datetime.datetime.now()})
                    st.success("🎉 평택의 변화된 모습이 멋지게 기록되었어요!")
                    st.balloons()
            else:
                st.warning("⚠️ 과거와 현재의 모습을 모두 적어주세요!")

    # ---------------------------------------------------------
    # 🤖 2. AI 보조교사 호출 (파일 맨 아래)
    # ---------------------------------------------------------
    activity_desc = "이 화면은 카카오맵의 '로드뷰/타임머신' 기능을 활용하여 평택의 과거모습과 현재모습을 비교해보고, 달라진 점과 그 이유를 기록하는 곳입니다. 직접 탐험 후 아래 글쓰기 창에서 기록해야 합니다."
    ai_teacher.show_ai_teacher(activity_name="활동 3-2. 평택의 달라진 모습", context_description=activity_desc)