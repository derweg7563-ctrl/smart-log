import streamlit as st
import datetime
from pymongo import MongoClient

# 👇 AI 보조교사 · AI 모델 모듈 불러오기
import ai_teacher
import ai_model

ai_model.configure()


# ---------------------------------------------------------
# DB 연결 (AI 탐정 질문 기록 보관)
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        return c
    except Exception as e:
        print(f"[DB ERROR] activity2_2: {e}")
        return None


client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]
    chat_collection = db["ai_detective_log"]


# ---------------------------------------------------------
# AI 유물 탐정 프롬프트
# ---------------------------------------------------------
DETECTIVE_PROMPT = """
너는 초등학교 3학년 학생에게 우리나라 전통 유물과 역사를 알려주는 'AI 유물 탐정'이야.

[반드시 지켜야 할 규칙]
1. 3~4문장 이내로만 대답해. 길게 쓰지 마.
2. 초등학교 3학년이 아는 낱말만 써. 어려운 한자어는 쓰지 마.
3. 확실하지 않은 것은 "정확한 것은 박물관 누리집에서 찾아보면 좋겠어요"라고 말해.
   절대 지어내지 마. 모르는 것은 모른다고 솔직하게 말하는 것이 좋은 탐정이야.
4. 옛 물건이나 역사와 관계없는 질문(게임, 숙제 대신 해주기, 다른 과목 등)에는
   "지금은 옛 물건 탐정 활동을 도와줄게요!"라고 안내하고 유물 이야기로 돌아와.
5. 학생이 스스로 생각할 수 있도록, 답을 다 알려주기보다 "왜 그럴까요?" 같은
   되묻는 질문을 한 번씩 섞어 줘.
6. 존댓말을 쓰고, 이모지를 한두 개 섞어서 친근하게 말해.

학생의 질문: {question}
"""

# 학생이 바로 눌러 볼 수 있는 예시 질문
QUICK_QUESTIONS = [
    "떡살은 무엇에 쓰던 물건인가요?",
    "옛날 사람들은 무엇으로 밥을 지었나요?",
    "이 물건은 언제 사용했나요?",
]


def save_question_log(student, question, answer):
    """학생 질문과 AI 답변을 기록합니다. (학습 과정 분석용)"""
    if not db_connected:
        return
    try:
        chat_collection.insert_one({
            "username": student,
            "question": question,
            "answer": answer,
            "timestamp": datetime.datetime.now(),
        })
    except Exception as e:
        print(f"[LOG SAVE ERROR] activity2_2: {e}")


def show_page():
    st.title("🕵️‍♂️ AI 유물 탐정이 되어보기")
    st.subheader("💬 [1단계] 가상현실 박물관을 탐험하고, AI 탐정과 함께 유물의 비밀을 찾아보세요!")

    current_student = st.session_state.get("username", "학생")

    # ---------------------------------------------------------
    # 🏛️ 1단계: VR 박물관 관찰 영역
    # ---------------------------------------------------------
    st.markdown("""
        <style>
        .gac-btn {
            background-color: #2E7D32; color: #ffffff !important; padding: 15px 40px;
            border-radius: 50px; font-weight: 900; font-size: 1.2rem; text-decoration: none; display: inline-block;
            transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .gac-btn:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0,0,0,0.2); background-color: #1B5E20; color: #ffffff !important; }
        </style>

        <div style='background-color: #E8F5E9; padding: 25px; border-radius: 20px; border: 3px solid #81C784; margin-bottom: 20px;'>
            <h3 style='color: #2E7D32; margin-top: 0; text-align: center; margin-bottom: 20px;'>👀 박물관에 입장하면 이렇게 탐험하세요!</h3>
            <ol style='font-size: 1.1rem; color: #333; line-height: 1.8; margin-bottom: 25px; padding-left: 20px; font-weight: 500;'>
                <li>아래 <b>초록색 버튼</b>을 눌러 박물관으로 순간이동합니다. 🚀</li>
                <li>화면을 조금만 아래로 내려서 <b>'가상으로 방문하기'</b> 글자를 찾으세요.</li>
                <li>그림 아래에 있는 까만색 <b>[Explore]</b> 버튼을 콕! 누르세요. <br><span style="font-size:0.95rem; color:#555;">(오른쪽 실내 전시실 사진의 [Explore]를 누르면 박물관 안으로 바로 들어가요!)</span></li>
                <li>마우스나 손가락으로 화면을 빙글빙글 돌려가며 진짜처럼 걸어 다녀 보세요. 🚶‍♂️</li>
                <li>가장 신기하고 궁금한 옛날 물건을 하나 마음속에 찜! 하세요.</li>
            </ol>
            <div style="text-align: center;">
                <a href="https://artsandculture.google.com/partner/national-folk-museum-of-korea?hl=ko" target="_blank" class="gac-btn">
                    🚪 국립민속박물관 VR 탐험하러 가기 (새 창 열림)
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🕵️‍♂️ 2단계: AI 탐정 채팅 영역
    # ---------------------------------------------------------
    st.markdown("### 💬 [2단계] AI 유물 탐정에게 질문하기")
    st.info(
        "💡 박물관에서 본 옛 물건에 대해 궁금한 점을 물어보세요!\n\n"
        "🤔 **AI 탐정도 모르는 것이 있고, 가끔 틀리기도 해요.** "
        "중요한 내용은 박물관 누리집에서 꼭 다시 확인해 보세요!"
    )

    if "messages_2_2" not in st.session_state:
        st.session_state.messages_2_2 = [{
            "role": "assistant",
            "content": (
                "안녕하세요! 저는 옛 물건을 함께 살펴보는 AI 유물 탐정입니다. 🕵️‍♂️\n\n"
                "국립민속박물관에서 어떤 신기한 물건을 보셨나요? "
                "궁금한 점을 물어보시면 함께 알아볼게요! "
                "다만 제가 모르는 것도 있으니, 확실하지 않을 때는 그렇다고 말씀드릴게요."
            ),
        }]

    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.messages_2_2:
            avatar = "🕵️‍♂️" if msg["role"] == "assistant" else "👩‍🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # 예시 질문 버튼 (자유 입력의 예측 불가능성을 줄이는 장치)
    st.caption("👇 이렇게 물어볼 수 있어요")
    q_cols = st.columns(3)
    picked = None
    for col, q in zip(q_cols, QUICK_QUESTIONS):
        if col.button(q, use_container_width=True, key=f"q22_{q}"):
            picked = q

    with st.form("chat_form_2_2", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "질문 입력",
                label_visibility="collapsed",
                placeholder="궁금한 옛 물건을 물어보세요! (예: 떡살이 뭐야?)",
            )
        with col2:
            submit_btn = st.form_submit_button("질문하기 🚀", use_container_width=True)

    question = picked or (user_input if submit_btn else None)

    if question:
        st.session_state.messages_2_2.append({"role": "user", "content": question})

        with st.spinner("AI 탐정이 단서를 찾고 있어요... 🔎"):
            answer = ai_model.ask(DETECTIVE_PROMPT.format(question=question))

        st.session_state.messages_2_2.append({"role": "assistant", "content": answer})
        save_question_log(current_student, question, answer)
        st.rerun()

    # ---------------------------------------------------------
    # 📒 내가 물어본 질문 다시 보기
    # ---------------------------------------------------------
    if db_connected:
        try:
            my_logs = list(
                chat_collection.find({"username": current_student}).sort("timestamp", -1)
            )
        except Exception as e:
            print(f"[DB READ ERROR] activity2_2: {e}")
            my_logs = []

        if my_logs:
            with st.expander(f"📒 내가 AI 탐정에게 물어본 질문 {len(my_logs)}개 다시 보기", expanded=False):
                for lg in my_logs:
                    st.markdown(f"**❓ {lg.get('question', '')}**")
                    st.caption(lg.get("answer", ""))
                    st.markdown("---")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🤖 3. AI 보조교사 호출
    # ---------------------------------------------------------
    activity_desc = (
        "이 화면은 국립민속박물관 VR 전시관을 탐험하고, "
        "AI 유물 탐정 챗봇에게 전통 유물에 대해 질문하는 곳입니다. "
        "학생이 궁금한 옛 물건에 대해 스스로 질문을 만들어 보는 것이 중요합니다."
    )
    ai_teacher.show_ai_teacher(
        activity_name="활동 2-2. AI 유물 탐정이 되어보기",
        context_description=activity_desc,
    )
