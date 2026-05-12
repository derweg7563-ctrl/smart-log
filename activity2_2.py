import streamlit as st
import time

# 👇 1. AI 보조교사 모듈 불러오기
import ai_teacher

# 💡 구글 생성형 AI 패키지 불러오기
try:
    import google.generativeai as genai
except ImportError:
    st.error("🚨 `google-generativeai` 패키지가 필요합니다.")

def show_page():
    st.title("🕵️‍♂️ AI 유물 탐정이 되어보기")
    st.subheader("💬 [1단계] 가상현실 박물관을 탐험하고, 진짜 AI 탐정에게 비밀을 물어보세요!")

    # ---------------------------------------------------------
    # 🏛️ 1단계: 구글 아트앤컬쳐 관찰 영역 (상단) - 💡 새롭게 5단계 가이드 적용!
    # ---------------------------------------------------------
    st.markdown("""
        <style>
        /* 선생님께서 만드신 예쁜 버튼 스타일 (색상만 초록색 테마로 맞춤 변경) */
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
    # 🧠 구글 Gemini AI 설정 영역 (자동 탐색 마법)
    # ---------------------------------------------------------
    try:
        genai.configure(api_key=st.secrets["google"]["api_key"])
    except Exception as e:
        st.error("🚨 secrets.toml 파일에 구글 열쇠가 없습니다!")

    if "gemini_chat" not in st.session_state:
        try:
            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not valid_models:
                st.error("🚨 앗! 이 API 키로는 쓸 수 있는 AI 모델이 없습니다.")
                st.stop()
            
            auto_model_name = valid_models[0]
            model = genai.GenerativeModel(auto_model_name)
            st.session_state.gemini_chat = model.start_chat(history=[])
            
        except Exception as e:
            st.error(f"🚨 구글 서버 접속 에러: {e}")
            st.stop()

    # ---------------------------------------------------------
    # 🕵️‍♂️ 2단계: AI 탐정 채팅 영역 (하단)
    # ---------------------------------------------------------
    st.markdown("### 💬 [2단계] 똑똑해진 AI 유물 탐정에게 질문하기")
    st.info("💡 박물관에서 본 아무 유물이나 다 물어보세요! 구글의 지식으로 무장한 AI 탐정이 친절하게 알려줍니다.")

    # 🎯 [핵심 1] 대화 내용이 너무 길어지지 않게 스크롤 박스(height=400) 안에 가둡니다!
    chat_box = st.container(height=400)
    
    with chat_box:
        if "messages_2_2" not in st.session_state:
            st.session_state.messages_2_2 = [
                {"role": "assistant", "content": "안녕하세요! 저는 구글의 인공지능 두뇌를 가진 '진짜' AI 유물 탐정입니다. 🕵️‍♂️ 국립민속박물관에서 어떤 신기한 물건을 보셨나요? 무엇이든 물어보시면 다 대답해 드릴게요!"}
            ]

        for msg in st.session_state.messages_2_2:
            avatar = "🕵️‍♂️" if msg["role"] == "assistant" else "👩‍🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # 🎯 [핵심 2] 맨 밑으로 도망가는 chat_input 대신, 그 자리에 고정되는 일반 폼(Form)을 사용합니다!
    with st.form("chat_form_2_2", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("질문 입력", label_visibility="collapsed", placeholder="아무 유물이나 물어보세요! (예: 떡살이 뭐야?)")
        with col2:
            submit_btn = st.form_submit_button("질문하기 🚀", use_container_width=True)

    if submit_btn and user_input:
        st.session_state.messages_2_2.append({"role": "user", "content": user_input})
        
        with chat_box:
            with st.chat_message("user", avatar="👩‍🎓"):
                st.markdown(user_input)
            
            with st.chat_message("assistant", avatar="🕵️‍♂️"):
                message_placeholder = st.empty()
                prompt = f"너는 초등학생들에게 우리나라 전통 유물과 역사를 친절하게 설명해주는 'AI 유물 탐정'이야. 다음 학생의 질문에 초등학생이 이해하기 쉽게, 이모지를 섞어서 친절하고 재미있게 3~4문장으로 대답해줘. 질문: {user_input}"
                
                try:
                    response = st.session_state.gemini_chat.send_message(prompt, stream=True)
                    full_response = ""
                    for chunk in response:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.05) 
                    message_placeholder.markdown(full_response)
                    st.session_state.messages_2_2.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    error_msg = f"앗, 구글 AI 탐정이 대답을 찾는 데 문제가 생겼어요. (오류: {e})"
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages_2_2.append({"role": "assistant", "content": error_msg})
        
        # 입력 후 화면을 깔끔하게 유지하기 위해 새로고침
        st.rerun()

    # ---------------------------------------------------------
    # 🤖 3. AI 보조교사 호출 (맨 아래)
    # ---------------------------------------------------------
    activity_desc = "이 화면은 VR 박물관을 탐험하고, AI 유물 탐정 챗봇에게 전통 유물에 대해 질문하는 곳입니다."
    ai_teacher.show_ai_teacher(activity_name="활동 2-2. AI 유물 탐정이 되어보기", context_description=activity_desc)