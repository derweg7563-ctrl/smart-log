import streamlit as st
from pymongo import MongoClient
import stu_dash

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]
    users_collection = db["users"]
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

def show_page(*args, **kwargs):
    st.title("👩‍🏫 선생님 전용 관리 대시보드")
    st.info("우리 반 학생들의 가입 현황을 관리하고, 학생들의 학습 진행도를 한눈에 확인하는 공간입니다.")
    
    if not db_connected:
        st.warning("데이터베이스에 연결할 수 없습니다.")
        return

    # 학생 목록은 계정 관리를 위해 매번 최신 상태로 가져옵니다. 
    students = list(users_collection.find({"role": "학생"}))

    st.markdown("### 👥 가입한 학생 명단 및 관리")
    
    if len(students) == 0:
        st.write("아직 가입한 학생이 없습니다.")
    else:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1: st.markdown("**순번**")
        with col2: st.markdown("**학생 아이디 (이름)**")
        with col3: st.markdown("**관리**")
        st.markdown("---")

        for idx, student in enumerate(students):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.write(idx + 1)
            with c2: st.write(f"**{student['username']}**")
            with c3:
                if st.button("🗑️ 삭제", key=f"del_{student['username']}", help="이 학생의 계정을 삭제합니다."):
                    users_collection.delete_one({"username": student["username"]})
                    st.success(f"'{student['username']}' 학생 계정이 삭제되었습니다.")
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 🚀 [핵심 최적화 구간] 30명의 일지를 한 번에 실행하지 않고, 선택한 1명만 즉시 불러옵니다!
    st.markdown("### 🎓 학생별 탐험 일지 (대시보드) 확인")
    
    if len(students) == 0:
        st.write("확인할 학생 기록이 없습니다.")
    else:
        st.write("아래에서 기록을 확인할 학생을 선택해 주세요! 한 명씩 불러오기 때문에 화면이 멈추지 않습니다. ⚡")
        
        # 1. 드롭다운(Selectbox)에 넣을 학생 이름 목록을 만듭니다.
        student_names = [student["username"] for student in students]
        
        # 2. 선생님이 확인할 학생을 선택하도록 합니다.
        selected_student = st.selectbox("👤 탐험 일지를 확인할 학생을 선택하세요:", ["선택하세요"] + student_names)
        
        # 3. '선택하세요'가 아닐 때(특정 학생을 선택했을 때)만 그 학생의 데이터를 불러와 화면에 그립니다.
        if selected_student != "선택하세요":
            st.markdown(f"#### 📂 {selected_student} 학생의 탐험 일지")
            st.markdown("---")
            stu_dash.show_page(target_student=selected_student)