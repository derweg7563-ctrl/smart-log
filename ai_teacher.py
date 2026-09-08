import streamlit as st
import ai_model
import config

# API 키 설정
ai_model.configure()


def show_ai_teacher(activity_name, context_description):
    st.markdown("""
        <style>
        div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stDownloadButton"] > button,
        div[data-testid="stPopover"] > button,
        div[data-testid="stChatInput"] button,
        div[data-testid="stChatInputSubmitButton"] {
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
        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover,
        div[data-testid="stPopover"] > button:hover,
        div[data-testid="stChatInput"] button:hover {
            background-color: #FF8080 !important;
            color: #ffffff !important;
        }
        div.stButton > button:focus:not(:active),
        div[data-testid="stFormSubmitButton"] > button:focus:not(:active) {
            border-color: #FF8080 !important;
            color: #FF8080 !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    REGION = config.get_region()
    st.markdown("---")
    st.markdown("### 🤖 무엇이든 물어보세요! (AI 보조교사)")
    st.caption("활동을 하다가 어려운 점이 있거나 궁금한 점이 생기면 편하게 질문해 주세요!")

    # 현재 접속한 학생의 이름을 가져옵니다.
    current_student = st.session_state.get("username", "탐험대원")

    # 기억 상자 이름표에 '학생 이름'을 붙여서 서로 섞이지 않게 분리합니다.
    chat_key = f"chat_history_{current_student}_{activity_name}"

    # 이 학생의 대화 기록이 없으면 처음 인사말을 건넵니다.
    if chat_key not in st.session_state:
        greeting = (
            f"안녕 **{current_student}** 탐험대원! 👋 나는 이 앱의 보조교사야. "
            f"지금 '{activity_name}' 활동을 하고 있구나! "
            f"도움이 필요하면 언제든 말해줘. 그럼 화면을 위로 올려 시작해볼까? 😊"
        )
        st.session_state[chat_key] = [{"role": "ai", "content": greeting}]

    # 이전 대화 내용 화면에 보여주기
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ------------------------------------------------------------
    # 자주 묻는 질문 버튼 (자유 입력의 예측 불가능성을 줄이기 위한 장치)
    # ------------------------------------------------------------
    st.caption("👇 이런 것이 궁금하다면 눌러보세요")
    quick_cols = st.columns(3)
    quick_questions = [
        "이 화면에서는 뭘 해야 해?",
        "어떻게 저장하는 거야?",
        "잘 모르겠어요, 도와주세요",
    ]
    picked = None
    for col, q in zip(quick_cols, quick_questions):
        if col.button(q, use_container_width=True, key=f"quick_{activity_name}_{q}"):
            picked = q

    # 학생이 질문을 입력하는 창
    typed = st.chat_input("여기에 질문을 입력하세요 (예: 이 화면에서는 뭘 해야 해?)")
    user_question = picked or typed

    if user_question:
        with st.chat_message("user"):
            st.markdown(user_question)
        st.session_state[chat_key].append({"role": "user", "content": user_question})

        system_prompt = f"""
너는 {REGION}의 초등학교 3학년 학생들을 돕는 친절하고 다정한 'AI 보조교사'야.
학생 이름은 '{current_student}' 이고, 현재 앱에서 [{activity_name}] 활동을 하고 있어.
이 활동의 목적과 내용은 다음과 같아: {context_description}

[반드시 지켜야 할 규칙]
1. 3~4문장 이내로만 대답해. 길게 쓰지 마.
2. 초등학교 3학년이 아는 낱말만 써. 어려운 한자어나 영어는 쓰지 마.
3. 확실하지 않은 것은 "그건 선생님께 여쭤보는 게 좋겠어요"라고 말해. 절대 지어내지 마.
4. 이 활동과 관계없는 질문(숙제 대신 해주기, 게임, 다른 과목 등)에는
   "지금은 이 활동을 도와줄게요!"라고 부드럽게 안내하고 활동 이야기로 돌아와.
5. 학생이 해야 할 답을 대신 써 주지 마. 스스로 생각하도록 힌트만 줘.
6. 존댓말을 쓰고, 이모지를 한두 개 섞어서 친근하게 말해.
"""

        with st.chat_message("ai"):
            with st.spinner("AI 선생님이 생각하는 중... 🤔"):
                full_prompt = system_prompt + "\n\n학생의 질문: " + user_question
                ai_answer = ai_model.ask(full_prompt)
                st.markdown(ai_answer)

        st.session_state[chat_key].append({"role": "ai", "content": ai_answer})
