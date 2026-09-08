import streamlit as st
import datetime
import urllib.parse
from pymongo import MongoClient

# 👇 AI 보조교사 · AI 모델 모듈 불러오기
import ai_teacher
import ai_model
import config

ai_model.configure()



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
        print(f"[DB ERROR] activity3_1: {e}")
        return None


client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]
    collection = db["local_history"]


# ---------------------------------------------------------
# AI 역사학자
# ---------------------------------------------------------
def get_local_story(keyword):
    REGION = config.get_region()
    prompt = f"""
너는 {REGION}의 향토 역사를 학생들에게 알려주는 초등학교 선생님이야.
초등학교 3학년 학생이 '{keyword}'에 대해 검색했어.

[반드시 지켜야 할 규칙 — 이것이 가장 중요해]
1. **네가 확실히 아는 내용만 말해.** {REGION}의 '{keyword}'에 대해 잘 모르거나
   확실하지 않으면, 이야기를 지어내지 말고 이렇게 말해:
   "제가 {REGION}의 {keyword}에 대해서는 정확히 알지 못해요. 😅
    시청 누리집이나 어른께 여쭤보면 더 정확한 이야기를 들을 수 있어요!"
2. 전설이나 옛이야기를 **절대 새로 만들어 내지 마.** 재미있게 꾸미는 것보다
   사실대로 말하는 것이 훨씬 중요해.
3. 확실하지 않은 부분은 "~라고 전해져요", "~인 것 같아요"처럼 조심스럽게 말해.
4. 초등학교 3학년이 아는 낱말만 쓰고, 3~4문장 이내로 짧게 말해.
5. 이모지를 한두 개 섞어서 친근하게 말해.
6. 마지막에 "이 이야기가 맞는지 꼭 확인해 보세요!"라고 한 줄 덧붙여 줘.
"""
    return ai_model.ask(prompt)


# 학생이 고를 수 있는 확인 방법
CHECK_OPTIONS = [
    "아직 확인하지 못했어요",
    "가족이나 어른께 여쭤봤어요",
    "인터넷(시청 누리집 등)에서 찾아봤어요",
    "책이나 자료에서 봤어요",
    "직접 그곳에 가 본 적이 있어요",
]


def show_page():
    REGION = config.get_region()
    st.markdown("""
        <style>
        div.stButton > button {
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
        div.stButton > button:hover { background-color: #FF8080 !important; color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"📖 {REGION}의 옛이야기 탐험")
    st.info(f"💡 궁금한 {REGION}의 장소나 인물을 검색하면 AI가 알고 있는 이야기를 들려줍니다!")

    current_student = st.session_state.get("username", "학생")

    # --- AI 검색기 ---
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        search_story = st.text_input("🔍 검색어 입력", key="search_story")
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_story_btn = st.button("이야기 찾기 🚀")

    if search_story_btn and search_story:
        with st.spinner(f"{REGION}의 두꺼운 역사책을 뒤지는 중... 📚"):
            st.session_state["story_result"] = get_local_story(search_story)
            st.session_state["story_keyword"] = search_story

    if st.session_state.get("story_result"):
        keyword = st.session_state.get("story_keyword", "")
        st.success(f"**🤖 AI 역사학자의 답변:**\n\n{st.session_state['story_result']}")

        # 🔍 비판적 검증 안내
        st.warning(
            "🕵️ **탐정처럼 확인해 볼까요?**\n\n"
            "AI는 우리 고장의 이야기를 정확히 모를 수 있어요. "
            "지어낸 이야기를 사실처럼 말하기도 한답니다.\n\n"
            "아래 버튼으로 사진과 자료를 찾아보고, 가족이나 선생님께도 여쭤보세요!"
        )

        c1, c2 = st.columns(2)
        with c1:
            img_url = (
                "https://search.naver.com/search.naver?where=image&query="
                + urllib.parse.quote(f"{REGION} {keyword}")
            )
            st.link_button(f"🖼️ '{keyword}' 사진 찾아보기", img_url, use_container_width=True)
        with c2:
            web_url = (
                "https://search.naver.com/search.naver?query="
                + urllib.parse.quote(f"{REGION} {keyword} 유래")
            )
            st.link_button(f"🔎 '{keyword}' 자료 찾아보기", web_url, use_container_width=True)

    st.markdown("---")

    # --- 기록 폼 ---
    with st.form("story_form", clear_on_submit=True):
        st.write("✍️ **AI가 찾아준 이야기나 직접 들은 이야기를 내 생각과 함께 정리해 보세요!**")
        story_title = st.text_input("📝 이야기의 제목")
        story_content = st.text_area("🗣️ 이야기 내용 및 나의 생각", height=150)

        st.markdown("**🕵️ 이 이야기가 진짜인지 어떻게 확인했나요?**")
        st.caption("확인하지 않았다면 솔직하게 골라도 괜찮아요. 확인하는 습관이 중요하답니다!")
        check_method = st.radio(
            "확인 방법",
            CHECK_OPTIONS,
            label_visibility="collapsed",
        )

        if st.form_submit_button("우리 동네 백과사전에 저장하기 🚀", use_container_width=True):
            if not story_title.strip() or not story_content.strip():
                st.warning("⚠️ 제목과 내용을 모두 채워주세요!")
            elif not db_connected:
                st.error("서버 연결이 잠시 불안정해요. 선생님께 말씀드려 주세요. 🙂")
            else:
                try:
                    collection.insert_one({
                        "type": "옛이야기",
                        "username": current_student,
                        "title": story_title.strip(),
                        "content": story_content.strip(),
                        "check_method": check_method,
                        "timestamp": datetime.datetime.now(),
                    })
                    st.success("🎉 재미있는 옛이야기가 저장되었어요!")
                    st.balloons()
                except Exception as e:
                    print(f"[SAVE ERROR] activity3_1: {e}")
                    st.error("저장하는 중에 문제가 생겼어요. 다시 한 번 눌러줄래요? 🙂")

    # --- 내가 저장한 이야기 ---
    if db_connected:
        try:
            my_stories = list(
                collection.find({"username": current_student, "type": "옛이야기"}).sort("timestamp", -1)
            )
        except Exception as e:
            print(f"[DB READ ERROR] activity3_1: {e}")
            my_stories = []

        if my_stories:
            with st.expander(f"📚 내가 모은 옛이야기 {len(my_stories)}개 다시 보기", expanded=False):
                for s in my_stories:
                    st.markdown(f"**📖 {s.get('title', '')}**")
                    st.write(s.get("content", ""))
                    if s.get("check_method"):
                        st.caption(f"🕵️ 확인 방법: {s['check_method']}")
                    st.markdown("---")

    # ---------------------------------------------------------
    # 🤖 AI 보조교사 호출
    # ---------------------------------------------------------
    activity_desc = (
        f"이 화면은 궁금한 {REGION}의 장소나 인물을 검색하여 AI 역사학자에게 옛이야기를 물어보고, "
        "그 이야기가 사실인지 사진·자료 검색과 가족 인터뷰로 확인한 뒤 "
        "'우리 동네 백과사전'에 저장하는 곳입니다. "
        "AI가 지어낸 이야기일 수 있으므로 확인하는 과정이 중요합니다."
    )
    ai_teacher.show_ai_teacher(
        activity_name=f"활동 3-1. {REGION}의 옛이야기 탐험",
        context_description=activity_desc,
    )
