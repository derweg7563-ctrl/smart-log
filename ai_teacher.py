import streamlit as st
import google.generativeai as genai

# 선생님의 AI 열쇠 설정
try:
    genai.configure(api_key=st.secrets["google"]["api_key"])
except Exception as e:
    st.error("🚨 secrets.toml 파일에 구글 열쇠가 없습니다!")

def show_ai_teacher(activity_name, context_description):
    st.markdown("---")
    st.markdown("### 🤖 무엇이든 물어보세요! (AI 보조교사)")
    st.caption("활동을 하다가 어려운 점이 있거나 궁금한 점이 생기면 편하게 질문해 주세요!")

    # 현재 접속한 학생의 이름을 가져옵니다.
    current_student = st.session_state.get('username', '학생')

    # 기억 상자 이름표에 '학생 이름'을 붙여서 서로 섞이지 않게 분리합니다!
    chat_key = f"chat_history_{current_student}_{activity_name}"
    
    # 이 학생의 대화 기록이 없으면 처음 인사말을 건넵니다.
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [{"role": "ai", "content": f"안녕 **{current_student}** 탐험대원! 👋 나는 이 앱의 보조교사야. 지금 '{activity_name}' 활동을 하고 있구나! 도움이 필요하면 언제든 말해줘. 그럼 화면을 위로 올려 시작해볼까? 😊"}]

    # 이전 대화 내용 화면에 보여주기
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 학생이 질문을 입력하는 창
    user_question = st.chat_input("여기에 질문을 입력하세요 (예: 이 화면에서는 뭘 해야 해?)")

    if user_question:
        with st.chat_message("user"):
            st.markdown(user_question)
        st.session_state[chat_key].append({"role": "user", "content": user_question})

        system_prompt = f"""
        너는 경기도 안성시의 초등학교 3학년 학생들을 돕는 친절하고 다정한 'AI 보조교사'야.
        학생 이름은 '{current_student}' 이고, 현재 앱에서 [{activity_name}] 활동을 하고 있어.
        이 활동의 목적과 내용은 다음과 같아: {context_description}
        
        학생이 이 활동을 하면서 어려움을 겪고 질문을 했어. 
        초등학교 3학년 눈높이에 맞춰, 존댓말로 아주 친절하고 알기 쉽게, 그리고 이모지를 섞어서 대답해줘. 
        대답은 너무 길지 않게 3~4문장 정도로 핵심만 말해줘.
        """

        with st.chat_message("ai"):
            with st.spinner("AI 선생님이 생각하는 중... 🤔"):
                try:
                    # 🎯 [원상복구 완료] 컴퓨터가 스스로 가장 잘 맞는 모델을 찾도록 되돌렸습니다!
                    valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model = genai.GenerativeModel(valid_models[0])
                    
                    full_prompt = system_prompt + "\n\n학생의 질문: " + user_question
                    response = model.generate_content(full_prompt)
                    ai_answer = response.text
                except Exception as e:
                    ai_answer = f"앗! 선생님이 잠깐 자리를 비웠어요. 다시 질문해 줄래요? (오류: {e})"
                
                st.markdown(ai_answer)
                
        st.session_state[chat_key].append({"role": "ai", "content": ai_answer})