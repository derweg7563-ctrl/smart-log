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
        print(f"[DB ERROR] activity3_3: {e}")
        return None


client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]
    collection = db["local_history"]


# ---------------------------------------------------------
# AI 지역학자
# ---------------------------------------------------------
def get_origin_story(keyword):
    REGION = config.get_region()
    prompt = f"""
너는 {REGION}의 향토 지리를 학생들에게 알려주는 초등학교 선생님이야.
초등학교 3학년 학생이 '{keyword}'라는 지명(땅, 산, 호수 이름)을 검색했어.
이 이름이 왜 붙여졌는지 그 유래와 한자 뜻을 알려줘.

[반드시 지켜야 할 규칙 — 이것이 가장 중요해]
1. **네가 확실히 아는 내용만 말해.** {REGION}의 '{keyword}' 유래를 잘 모르거나
   확실하지 않으면, 지어내지 말고 이렇게 말해:
   "제가 {keyword}라는 이름의 유래는 정확히 알지 못해요. 😅
    시청 누리집이나 마을 어른께 여쭤보면 더 정확한 이야기를 들을 수 있어요!"
2. 지명 유래는 여러 가지 이야기가 전해지기도 해. 확실하지 않은 것은
   "~라고 전해져요", "~라는 이야기도 있어요"처럼 조심스럽게 말해.
3. 한자 뜻을 알려줄 때도 확실하지 않으면 억지로 풀이하지 마.
4. 초등학교 3학년이 아는 낱말만 쓰고, 3~4문장 이내로 짧게 말해.
5. 이모지를 한두 개 섞어서 친근하게 말해.
6. 마지막에 "이 이야기가 맞는지 꼭 확인해 보세요!"라고 한 줄 덧붙여 줘.
"""
    return ai_model.ask(prompt)


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
        .dash-praise {
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: #2E7D32;
            background-color: #E8F5E9;
            padding: 20px;
            border-radius: 20px;
            border: 3px dashed #81C784;
            margin-top: 40px;
            margin-bottom: 30px;
        }
        div[data-testid="column"]:has(.dash-btn-hook) button {
            height: 70px !important;
            border-radius: 25px !important;
            background: linear-gradient(135deg, #FFD54F, #FFB300) !important;
            color: #4E342E !important;
            font-size: 1.3rem !important;
            font-weight: 900 !important;
            border: 4px solid #FFF8E1 !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
            transition: all 0.3s ease !important;
            white-space: pre-wrap !important;
        }
        div[data-testid="column"]:has(.dash-btn-hook) button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.25) !important;
            background: linear-gradient(135deg, #FFC107, #FFA000) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"🏷️ {REGION}의 땅 이름 비밀 찾기")
    st.info("💡 우리 동네 이름, 산, 호수 이름을 검색하면 이름에 담긴 뜻을 함께 찾아봅니다!")

    current_student = st.session_state.get("username", "학생")

    # --- AI 검색기 ---
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        search_origin = st.text_input("📍 검색어 입력", key="search_origin")
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_origin_btn = st.button("유래 찾기 🚀")

    if search_origin_btn and search_origin:
        with st.spinner("지역 사전을 펼치고 뜻을 풀이하는 중... 📜"):
            st.session_state["origin_result"] = get_origin_story(search_origin)
            st.session_state["origin_keyword"] = search_origin

    if st.session_state.get("origin_result"):
        keyword = st.session_state.get("origin_keyword", "")
        st.success(f"**🤖 AI 지역학자의 답변:**\n\n{st.session_state['origin_result']}")

        st.warning(
            "🕵️ **탐정처럼 확인해 볼까요?**\n\n"
            "땅 이름의 유래는 여러 이야기가 전해지기도 하고, "
            "AI가 잘못 알고 있을 수도 있어요.\n\n"
            "아래 버튼으로 실제 모습과 자료를 찾아보고, 마을 어른께도 여쭤보세요!"
        )

        c1, c2 = st.columns(2)
        with c1:
            img_url = (
                "https://search.naver.com/search.naver?where=image&sm=tab_jum&query="
                + urllib.parse.quote(f"{REGION} {keyword}")
            )
            st.link_button(f"🖼️ '{keyword}' 사진 찾아보기", img_url, use_container_width=True)
        with c2:
            web_url = (
                "https://search.naver.com/search.naver?query="
                + urllib.parse.quote(f"{REGION} {keyword} 지명 유래")
            )
            st.link_button(f"🔎 '{keyword}' 자료 찾아보기", web_url, use_container_width=True)

    st.markdown("---")

    # --- 기록 폼 ---
    with st.form("name_origin_form", clear_on_submit=True):
        st.write("✍️ **조사한 땅 이름의 뜻을 친구들에게 소개하듯 정리해 보세요.**")
        place_name = st.text_input("📍 장소 이름")
        place_origin = st.text_area("📖 이름에 담긴 뜻과 유래 (나의 생각 포함)", height=150)

        st.markdown("**🕵️ 이 유래가 맞는지 어떻게 확인했나요?**")
        st.caption("확인하지 않았다면 솔직하게 골라도 괜찮아요. 확인하는 습관이 중요하답니다!")
        check_method = st.radio("확인 방법", CHECK_OPTIONS, label_visibility="collapsed")

        if st.form_submit_button("이름의 비밀 백과사전에 저장하기 🚀", use_container_width=True):
            if not place_name.strip() or not place_origin.strip():
                st.warning("⚠️ 장소 이름과 유래를 꼼꼼하게 적어주세요!")
            elif not db_connected:
                st.error("서버 연결이 잠시 불안정해요. 선생님께 말씀드려 주세요. 🙂")
            else:
                try:
                    collection.insert_one({
                        "type": "지역명유래",
                        "username": current_student,
                        "place_name": place_name.strip(),
                        "origin": place_origin.strip(),
                        "check_method": check_method,
                        "timestamp": datetime.datetime.now(),
                    })
                    st.success("🎉 땅 이름의 비밀이 기록 완료되었어요!")
                    st.balloons()
                except Exception as e:
                    print(f"[SAVE ERROR] activity3_3: {e}")
                    st.error("저장하는 중에 문제가 생겼어요. 다시 한 번 눌러줄래요? 🙂")

    # --- 내가 찾은 땅 이름 ---
    if db_connected:
        try:
            my_places = list(
                collection.find({"username": current_student, "type": "지역명유래"})
                .sort("timestamp", -1)
            )
        except Exception as e:
            print(f"[DB READ ERROR] activity3_3: {e}")
            my_places = []

        if my_places:
            with st.expander(f"📚 내가 찾은 땅 이름 {len(my_places)}개 다시 보기", expanded=False):
                for p in my_places:
                    st.markdown(f"**📍 {p.get('place_name', '')}**")
                    st.write(p.get("origin", ""))
                    if p.get("check_method"):
                        st.caption(f"🕵️ 확인 방법: {p['check_method']}")
                    st.markdown("---")

    # --- 칭찬 메시지 ---
    st.markdown(
        f'<div class="dash-praise">🎉 지금까지 열심히 공부한 '
        f'<span style="color:#E65100;">{current_student}</span> 대원을 칭찬해!<br>'
        f'우리가 얼마나 열심히 했는지 알아볼까? 👀</div>',
        unsafe_allow_html=True,
    )

    # --- 나의 발자국 확인하기 ---
    col_empty1, col_btn2, col_empty3 = st.columns([1, 1.5, 1])
    with col_btn2:
        st.markdown("<span class='dash-btn-hook'></span>", unsafe_allow_html=True)
        if st.button("📊 나의 발자국 확인하기", use_container_width=True):
            st.session_state.current_page = "stu_dash"
            st.rerun()

    # --- AI 보조교사 호출 ---
    activity_desc = (
        f"이 화면은 {REGION}의 땅 이름(산, 호수, 마을 이름 등)을 검색하여 "
        "AI 지역학자에게 유래를 물어보고, 그 내용이 맞는지 확인한 뒤 백과사전에 기록하는 곳입니다. "
        "모든 활동의 마지막 단계이므로, 학생이 잘 마무리하고 "
        "'나의 발자국 확인하기' 버튼을 누르도록 독려해 주세요."
    )
    ai_teacher.show_ai_teacher(
        activity_name=f"활동 3-3. {REGION}의 땅 이름 비밀 찾기",
        context_description=activity_desc,
    )
