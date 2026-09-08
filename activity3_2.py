import streamlit as st
import datetime
import urllib.parse
from pymongo import MongoClient

# 👇 AI 보조교사 모듈 불러오기
import ai_teacher
import config


# ---------------------------------------------------------
# DB 연결
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        return c
    except Exception as e:
        print(f"[DB ERROR] activity3_2: {e}")
        return None


client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]
    collection = db["local_history"]


def show_page():
    REGION = config.get_region()
    # 버튼 디자인 (다른 활동 화면과 통일)
    st.markdown("""
        <style>
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            border-radius: 50px !important;
            padding: 8px 30px !important;
            min-height: 45px !important;
            background-color: #ffffff !important;
            border: 2px solid #FF8080 !important;
            color: #FF8080 !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #FF8080 !important; color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"🔄 {REGION}의 달라진 모습")
    st.info("💡 카카오맵 타임머신을 타고, 우리 동네가 어떻게 변했는지 직접 탐험해 보세요!")

    current_student = st.session_state.get("username", "학생")

    # ---------------------------------------------------------
    # 🔎 1단계: 영상 보고 카카오맵 탐험하기
    # ---------------------------------------------------------
    st.markdown("### 🔎 [1단계] 타임머신 타고 옛날 모습 구경하기")

    col_video, col_desc = st.columns([1, 1])

    with col_video:
        st.write("📺 **카카오맵 타임머신 타는 방법**")
        st.video("https://youtu.be/SYUBOLP00W0")
        st.caption("▲ 선생님이 만든 영상을 보고 방법을 잘 기억해 두세요!")

    with col_desc:
        st.markdown(f"""
        <div style='background-color:#FFF9C4; padding:20px; border-radius:10px; height:85%; margin-top: 30px;'>
            <b>🚗 직접 과거로 떠나볼까요?</b><br><br>
            영상을 잘 보았나요?<br>
            이제 아래 버튼을 눌러 카카오맵을 켜고, {REGION} 시내나 우리 학교 주변의 도로, 건물이
            10년, 15년 전에 어땠는지 직접 탐험해 보세요!
        </div>
        """, unsafe_allow_html=True)

        # 설정한 고장 이름으로 지도를 열어 줍니다.
        map_url = "https://map.kakao.com/?q=" + urllib.parse.quote(REGION)
        st.link_button(f"🗺️ 카카오맵에서 {REGION} 탐험하기", map_url, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # ✍️ 2단계: 학생 기록 폼
    # ---------------------------------------------------------
    st.markdown("### ✍️ [2단계] 내가 발견한 달라진 점 기록하기")

    with st.form("change_form", clear_on_submit=True):
        place_name = st.text_input(
            "📍 어디를 살펴보았나요?",
            placeholder="예: 우리 학교 앞 사거리, ○○공원",
        )

        col_past, col_present = st.columns(2)
        with col_past:
            past_view = st.text_area(
                "⏳ 옛날에는 어땠나요? (과거)",
                placeholder="예: 높은 건물이 없고 흙길이었어요.",
                height=150,
            )
        with col_present:
            present_view = st.text_area(
                "🏙️ 지금은 어떻게 변했나요? (현재)",
                placeholder="예: 멋진 산책로와 높은 아파트가 생겼어요.",
                height=150,
            )

        change_reason = st.text_input(
            "🤔 왜 이렇게 모습이 달라졌을까요? (나의 생각)",
            placeholder="사람들이 많이 살게 되어서, 도로가 필요해져서 등",
        )

        if st.form_submit_button("달라진 모습 기록하기 🚀", use_container_width=True):
            if not past_view.strip() or not present_view.strip():
                st.warning("⚠️ 과거와 현재의 모습을 모두 적어주세요!")
            elif not db_connected:
                st.error("서버 연결이 잠시 불안정해요. 선생님께 말씀드려 주세요. 🙂")
            else:
                try:
                    collection.insert_one({
                        "type": "달라진모습",
                        "username": current_student,
                        "place": place_name.strip(),
                        "past": past_view.strip(),
                        "present": present_view.strip(),
                        "reason": change_reason.strip(),
                        "timestamp": datetime.datetime.now(),
                    })
                    st.success(f"🎉 {REGION}의 변화된 모습이 멋지게 기록되었어요!")
                    st.balloons()
                except Exception as e:
                    print(f"[SAVE ERROR] activity3_2: {e}")
                    st.error("저장하는 중에 문제가 생겼어요. 다시 한 번 눌러줄래요? 🙂")

    # ---------------------------------------------------------
    # 📚 내가 기록한 변화 다시 보기
    # ---------------------------------------------------------
    if db_connected:
        try:
            my_records = list(
                collection.find({"username": current_student, "type": "달라진모습"})
                .sort("timestamp", -1)
            )
        except Exception as e:
            print(f"[DB READ ERROR] activity3_2: {e}")
            my_records = []

        if my_records:
            with st.expander(f"📚 내가 찾은 달라진 모습 {len(my_records)}개 다시 보기", expanded=False):
                for r in my_records:
                    place = r.get("place") or "장소를 적지 않았어요"
                    st.markdown(f"**📍 {place}**")
                    c1, c2 = st.columns(2)
                    c1.markdown(f"⏳ **옛날**\n\n{r.get('past', '')}")
                    c2.markdown(f"🏙️ **지금**\n\n{r.get('present', '')}")
                    if r.get("reason"):
                        st.caption(f"🤔 달라진 까닭: {r['reason']}")
                    st.markdown("---")

    # ---------------------------------------------------------
    # 🤖 AI 보조교사 호출
    # ---------------------------------------------------------
    activity_desc = (
        f"이 화면은 카카오맵의 '로드뷰/타임머신' 기능을 활용하여 {REGION}의 과거 모습과 현재 모습을 "
        "비교해 보고, 달라진 점과 그 이유를 기록하는 곳입니다. "
        "직접 지도를 탐험한 뒤 아래 글쓰기 창에서 기록해야 합니다."
    )
    ai_teacher.show_ai_teacher(
        activity_name=f"활동 3-2. {REGION}의 달라진 모습",
        context_description=activity_desc,
    )
