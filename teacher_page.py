import streamlit as st
import config
from pymongo import MongoClient
import stu_dash
from config import get_setting, save_setting

# ============================================================
# DB 연결 (실제 접속까지 확인)
# ============================================================
@st.cache_resource
def init_connection():
    try:
        c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        return c
    except Exception as e:
        print(f"[DB ERROR] teacher_page: {e}")
        return None


client = init_connection()
db_connected = client is not None

if db_connected:
    db = client["school_project"]
    users_collection = db["users"]
    settings_collection = db["settings"]                  # 고장 설정 저장소

    timeline_collection = db["student_timeline"]          # 1-1. 나의 발자국
    school_collection = db["school_footprints"]           # 1-2. 학교 발자국
    old_items_collection = db["act2_1"]                   # 2-1. 옛 물건 살펴보기
    exhibition_collection = db["exhibition_items"]        # 2-3. 애장품 전시회
    local_history_collection = db["local_history"]        # 3-1, 3-2, 3-3 통합


# ============================================================
# 학생 한 명의 활동별 기록 개수
# ============================================================
ACTIVITY_MAP = [
    ("1-1 나의 발자국", "timeline"),
    ("1-2 학교 발자국", "school"),
    ("2-1 옛 물건", "old_items"),
    ("2-3 애장품 전시회", "exhibition"),
    ("3단원 고장 탐험", "local"),
]


def count_works(username):
    return {
        "timeline": timeline_collection.count_documents({"username": username}),
        "school": school_collection.count_documents({"username": username}),
        "old_items": old_items_collection.count_documents({"username": username}),
        "exhibition": exhibition_collection.count_documents({"username": username}),
        "local": local_history_collection.count_documents({"username": username}),
    }


def delete_all_works(username):
    """회원 삭제 시 활동 기록도 함께 지웁니다. (고아 데이터 방지)"""
    for col in [timeline_collection, school_collection, old_items_collection,
                exhibition_collection, local_history_collection]:
        col.delete_many({"username": username})


# ============================================================
# 화면
# ============================================================
def show_page(*args, **kwargs):
    st.title("👩‍🏫 선생님 전용 관리 대시보드")
    st.info("우리 반 학생들의 가입 현황을 관리하고, 학생들의 학습 진행도를 한눈에 확인하는 공간입니다.")

    if not db_connected:
        st.warning("데이터베이스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.")
        return

    REGION = get_setting("region")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 학습 현황", "👥 학생 계정 관리", "🎓 학생별 일지 확인", "⚙️ 우리 고장 설정"]
    )

    students = list(users_collection.find({"role": "학생"}))
    student_names = [s["username"] for s in students]

    # ------------------------------------------------------
    # 📊 탭 1. 학습 현황 한눈에 보기
    # ------------------------------------------------------
    with tab1:
        st.markdown("### 📊 우리 반 학습 진행 현황")

        if not students:
            st.write("아직 가입한 학생이 없습니다.")
        else:
            rows = []
            totals = {k: 0 for _, k in ACTIVITY_MAP}
            for name in student_names:
                c = count_works(name)
                for _, k in ACTIVITY_MAP:
                    totals[k] += 1 if c[k] > 0 else 0
                rows.append((name, c))

            st.markdown("#### 활동별 참여 학생 수")
            cols = st.columns(len(ACTIVITY_MAP))
            for col, (label, key) in zip(cols, ACTIVITY_MAP):
                done = totals[key]
                rate = round(done / len(students) * 100)
                col.metric(label, f"{done}/{len(students)}", f"{rate}%")

            st.markdown("---")
            st.markdown("#### 학생별 기록 개수")
            st.caption("숫자는 저장된 기록의 개수입니다. 0인 칸은 아직 활동하지 않은 부분입니다.")

            header = st.columns([2] + [1] * len(ACTIVITY_MAP))
            header[0].markdown("**학생**")
            for col, (label, _) in zip(header[1:], ACTIVITY_MAP):
                col.markdown(f"**{label}**")

            for name, c in rows:
                line = st.columns([2] + [1] * len(ACTIVITY_MAP))
                line[0].write(name)
                for col, (_, key) in zip(line[1:], ACTIVITY_MAP):
                    col.write(c[key] if c[key] else "-")

    # ------------------------------------------------------
    # 👥 탭 2. 학생 계정 관리
    # ------------------------------------------------------
    with tab2:
        st.markdown("### 👥 가입한 학생 명단 및 관리")

        if not students:
            st.write("아직 가입한 학생이 없습니다.")
        else:
            st.warning("⚠️ 회원을 삭제하면 그 학생의 활동 기록도 모두 함께 지워집니다.")

            col1, col2, col3 = st.columns([1, 3, 2])
            col1.markdown("**순번**")
            col2.markdown("**학생 아이디**")
            col3.markdown("**계정 관리**")
            st.markdown("---")

            for idx, student in enumerate(students):
                name = student["username"]
                c1, c2, c3 = st.columns([1, 3, 2])
                c1.write(idx + 1)
                c2.write(f"**{name}**")

                confirm_key = f"confirm_del_{name}"
                with c3:
                    if st.session_state.get(confirm_key):
                        b1, b2 = st.columns(2)
                        if b1.button("정말 삭제", key=f"yes_{name}"):
                            delete_all_works(name)
                            users_collection.delete_one({"username": name})
                            st.session_state.pop(confirm_key, None)
                            st.success(f"'{name}' 학생의 계정과 기록을 삭제했습니다.")
                            st.rerun()
                        if b2.button("취소", key=f"no_{name}"):
                            st.session_state.pop(confirm_key, None)
                            st.rerun()
                    else:
                        if st.button("🗑️ 회원 삭제", key=f"del_user_{name}"):
                            st.session_state[confirm_key] = True
                            st.rerun()

    # ------------------------------------------------------
    # 🎓 탭 3. 학생별 탐험 일지
    # ------------------------------------------------------
    with tab3:
        st.markdown("### 🎓 학생별 탐험 일지 및 작품 개별 관리")

        if not students:
            st.write("확인할 학생 기록이 없습니다.")
        else:
            st.write("아래에서 기록을 확인할 학생을 선택해 주세요. 한 명씩 불러오기 때문에 화면이 멈추지 않습니다. ⚡")
            selected_student = st.selectbox(
                "👤 탐험 일지를 확인할 학생을 선택하세요:", ["선택하세요"] + student_names
            )

            if selected_student != "선택하세요":
                with st.expander(f"🛠️ [관리자 전용] {selected_student} 학생 활동 기록 삭제 메뉴", expanded=False):
                    st.info("💡 각 단계별로 잘못 올린 작품을 개별적으로 삭제할 수 있습니다. (삭제 후 학생이 재업로드 가능)")

                    def work_list(header, collection, works, label_fn, key_prefix):
                        st.markdown(header)
                        if not works:
                            st.caption("저장된 기록이 없습니다.")
                        for w in works:
                            c1, c2 = st.columns([4, 1])
                            c1.write(f"• **{label_fn(w)}**")
                            if c2.button("🗑️ 삭제", key=f"{key_prefix}_{w['_id']}"):
                                collection.delete_one({"_id": w["_id"]})
                                st.rerun()
                        st.markdown("---")

                    work_list(
                        "##### 👣 1-1. 나의 발자국 살펴보기",
                        timeline_collection,
                        list(timeline_collection.find({"username": selected_student})),
                        lambda w: w.get("stage", "기록"),
                        "del_1_1",
                    )
                    work_list(
                        "##### 🏫 1-2. 학교 발자국 기록하기",
                        school_collection,
                        list(school_collection.find({"username": selected_student})),
                        lambda w: "학교 발자국 탐험 기록",
                        "del_1_2",
                    )
                    work_list(
                        "##### 🏺 2-1. 찾은 옛 물건 AI 분석 기록",
                        old_items_collection,
                        list(old_items_collection.find({"username": selected_student})),
                        lambda w: "유물 분석 및 나의 생각",
                        "del_2_1",
                    )
                    work_list(
                        "##### 🖼️ 2-3. 우리 반 애장품 전시회 출품작",
                        exhibition_collection,
                        list(exhibition_collection.find({"username": selected_student})),
                        lambda w: w.get("item_name", "애장품"),
                        "del_2_3",
                    )

                    def label_3(w):
                        rtype = w.get("type", "기록")
                        if rtype == "옛이야기":
                            return f"[3-1. 옛이야기] {w.get('title', '제목 없음')}"
                        if rtype == "달라진모습":
                            return "[3-2. 달라진모습] 지도 비교 기록"
                        if rtype == "지역명유래":
                            return f"[3-3. 땅 이름] {w.get('place_name', '장소 없음')}"
                        return "3단원 기록"

                    work_list(
                        f"##### 📖 3단원. {REGION}의 역사 탐험 기록",
                        local_history_collection,
                        list(local_history_collection.find({"username": selected_student})),
                        label_3,
                        "del_3",
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"#### 📂 {selected_student} 학생의 탐험 일지 모아보기")
                st.markdown("---")
                stu_dash.show_page(target_student=selected_student)

    # ------------------------------------------------------
    # ⚙️ 탭 4. 우리 고장 설정
    # ------------------------------------------------------
    with tab4:
        st.markdown("### ⚙️ 우리 고장 설정")
        st.info(
            "이 프로그램은 특정 지역에 고정되어 있지 않습니다. "
            "아래 값을 바꾸면 학생 화면의 지역명과 AI·검색 기능이 함께 바뀌므로, "
            "다른 지역 학교에서도 그대로 사용할 수 있습니다."
        )

        new_region = st.text_input(
            "🏘️ 고장 이름", value=get_setting("region"),
            help="예: 안성, 평택, 여수. 메뉴 이름과 AI 검색어에 함께 사용됩니다."
        )

        st.markdown("#### 🗺️ 지도 중심 좌표 (선택)")
        st.caption("비워 두면 지도 기능이 기본 위치로 열립니다.")
        c1, c2 = st.columns(2)
        new_lat = c1.text_input("위도(latitude)", value=get_setting("map_lat"))
        new_lng = c2.text_input("경도(longitude)", value=get_setting("map_lng"))

        st.markdown("#### 📚 지역 아카이브 링크 (선택)")
        st.caption("우리 고장의 옛 사진·자료를 모아 둔 사이트가 있다면 주소를 넣어 주세요. 비워 두면 해당 링크가 숨겨집니다.")
        new_archive_name = st.text_input(
            "아카이브 이름", value=get_setting("archive_name"),
            help="예: 안성저장소, 평택시 기록관"
        )
        new_archive = st.text_input("아카이브 주소", value=get_setting("archive_url"))

        if st.button("💾 설정 저장하기", use_container_width=True):
            if not new_region.strip():
                st.warning("고장 이름은 비워 둘 수 없습니다.")
            else:
                save_setting("region", new_region.strip())
                save_setting("map_lat", new_lat.strip())
                save_setting("map_lng", new_lng.strip())
                save_setting("archive_name", new_archive_name.strip())
                save_setting("archive_url", new_archive.strip())
                st.success(f"'{new_region.strip()}'(으)로 설정되었습니다.")
                st.rerun()
