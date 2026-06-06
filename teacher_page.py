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
    
    # 👇 선생님께서 작성하신 '진짜' 서랍 이름들 완벽 적용!
    timeline_collection = db["student_timeline"]      # 1-1. 나의 발자국
    school_collection = db["school_footprints"]       # 1-2. 학교 발자국
    old_items_collection = db["act2_1"]               # 2-1. 옛 물건 살펴보기
    exhibition_collection = db["exhibition_items"]    # 2-3. 애장품 전시회
    local_history_collection = db["local_history"]    # 3-1, 3-2, 3-3 통합 보관함
    
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

    # 학생 목록 불러오기
    students = list(users_collection.find({"role": "학생"}))

    # ==========================================
    # 👥 1. 학생 회원 계정 관리 영역
    # ==========================================
    st.markdown("### 👥 가입한 학생 명단 및 관리")
    
    if len(students) == 0:
        st.write("아직 가입한 학생이 없습니다.")
    else:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1: st.markdown("**순번**")
        with col2: st.markdown("**학생 아이디 (이름)**")
        with col3: st.markdown("**계정 관리**")
        st.markdown("---")

        for idx, student in enumerate(students):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.write(idx + 1)
            with c2: st.write(f"**{student['username']}**")
            with c3:
                if st.button("🗑️ 회원 삭제", key=f"del_user_{student['username']}", help="이 학생의 계정을 완전히 삭제합니다."):
                    users_collection.delete_one({"username": student["username"]})
                    st.success(f"'{student['username']}' 학생 계정이 삭제되었습니다.")
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ==========================================
    # 🎓 2. 학생별 탐험 일지 확인 및 개별 작품 삭제 영역
    # ==========================================
    st.markdown("### 🎓 학생별 탐험 일지 및 작품 개별 관리")
    
    if len(students) == 0:
        st.write("확인할 학생 기록이 없습니다.")
    else:
        st.write("아래에서 기록을 확인할 학생을 선택해 주세요! 한 명씩 불러오기 때문에 화면이 멈추지 않습니다. ⚡")
        student_names = [student["username"] for student in students]
        selected_student = st.selectbox("👤 탐험 일지를 확인할 학생을 선택하세요:", ["선택하세요"] + student_names)

        if selected_student != "선택하세요":
            
            # 🛠️ 전체 작품 관리 아코디언 메뉴
            with st.expander(f"🛠️ [관리자 전용] {selected_student} 학생 전체 활동 기록 삭제 메뉴", expanded=True):
                st.info("💡 각 단계별로 잘못 올린 작품을 개별적으로 삭제할 수 있습니다. (삭제 후 학생이 재업로드 가능)")
                
                # 📌 1-1. 나의 발자국 살펴보기
                st.markdown("##### 👣 1-1. 나의 발자국 살펴보기")
                works_1_1 = list(timeline_collection.find({"username": selected_student}))
                if not works_1_1: st.caption("저장된 기록이 없습니다.")
                for w in works_1_1:
                    title = w.get("stage", "기록")
                    c1, c2 = st.columns([4, 1])
                    with c1: st.write(f"• **{title}**")
                    with c2:
                        if st.button("🗑️ 삭제", key=f"del_1_1_{w['_id']}"):
                            timeline_collection.delete_one({"_id": w["_id"]})
                            st.rerun()
                st.markdown("---")

                # 📌 1-2. 학교 발자국 기록하기
                st.markdown("##### 🏫 1-2. 학교 발자국 기록하기")
                works_1_2 = list(school_collection.find({"username": selected_student}))
                if not works_1_2: st.caption("저장된 기록이 없습니다.")
                for w in works_1_2:
                    c1, c2 = st.columns([4, 1])
                    with c1: st.write(f"• **학교 발자국 탐험 기록**")
                    with c2:
                        if st.button("🗑️ 삭제", key=f"del_1_2_{w['_id']}"):
                            school_collection.delete_one({"_id": w["_id"]})
                            st.rerun()
                st.markdown("---")

                # 📌 2-1. 찾은 옛 물건 AI 분석하기
                st.markdown("##### 🏺 2-1. 찾은 옛 물건 AI 분석 기록")
                works_2_1 = list(old_items_collection.find({"username": selected_student}))
                if not works_2_1: st.caption("저장된 기록이 없습니다.")
                for w in works_2_1:
                    c1, c2 = st.columns([4, 1])
                    with c1: st.write(f"• **유물 분석 및 나의 생각**")
                    with c2:
                        if st.button("🗑️ 삭제", key=f"del_2_1_{w['_id']}"):
                            old_items_collection.delete_one({"_id": w["_id"]})
                            st.rerun()
                st.markdown("---")

                # 📌 2-3. 우리 반 애장품 전시회
                st.markdown("##### 🖼️ 2-3. 우리 반 애장품 전시회 출품작")
                works_2_3 = list(exhibition_collection.find({"username": selected_student}))
                if not works_2_3: st.caption("저장된 기록이 없습니다.")
                for w in works_2_3:
                    title = w.get("item_name", "애장품")
                    c1, c2 = st.columns([4, 1])
                    with c1: st.write(f"• **{title}**")
                    with c2:
                        if st.button("🗑️ 삭제", key=f"del_2_3_{w['_id']}"):
                            exhibition_collection.delete_one({"_id": w["_id"]})
                            st.rerun()
                st.markdown("---")

                # 📌 3단원. 안성의 역사 탐험 (3-1, 3-2, 3-3 통합)
                st.markdown("##### 📖 3단원. 안성의 역사 탐험 기록 (옛이야기, 달라진모습, 지역명)")
                works_3 = list(local_history_collection.find({"username": selected_student}))
                if not works_3: st.caption("저장된 기록이 없습니다.")
                for w in works_3:
                    rtype = w.get("type", "기록")
                    if rtype == "옛이야기":
                        title = f"[3-1. 옛이야기] {w.get('title', '제목 없음')}"
                    elif rtype == "달라진모습":
                        title = "[3-2. 달라진모습] 카카오맵 비교 기록"
                    elif rtype == "지역명유래":
                        title = f"[3-3. 땅 이름] {w.get('place_name', '장소 없음')}"
                    else:
                        title = "3단원 기록"

                    c1, c2 = st.columns([4, 1])
                    with c1: st.write(f"• **{title}**")
                    with c2:
                        if st.button("🗑️ 삭제", key=f"del_3_{w['_id']}"):
                            local_history_collection.delete_one({"_id": w["_id"]})
                            st.rerun()

            st.markdown("<br><br>", unsafe_allow_html=True)

            # 삭제 메뉴 밑에 학생의 전체 대시보드를 보여줍니다.
            st.markdown(f"#### 📂 {selected_student} 학생의 탐험 일지 모아보기")
            st.markdown("---")
            stu_dash.show_page(target_student=selected_student)
