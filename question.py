import streamlit as st

def show_page():
    # 환영 인사와 디자인
    st.markdown("""
        <div style='text-align: center; background-color: #F0F8FF; padding: 30px; border-radius: 20px; border: 3px dashed #BAE1FF;'>
            <h1 style='color: #0056b3;'>🗺️ 안성 탐험대에 오신 것을 환영합니다!</h1>
            <p style='font-size: 18px; color: #333;'>우리 동네 안성의 숨겨진 비밀과 학교의 역사를 찾아 떠나는 신나는 여행!</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

    st.write("안성 탐험대 대원 여러분! 왼쪽 메뉴를 눌러 아래의 3가지 탐험을 순서대로 진행해 보세요. 🚀")
    
    # 각 단원별 설명 (아코디언 형태)
    with st.expander("👣 1단계: 어제와 오늘의 흐름 따라가기", expanded=True):
        st.write("""
        * **어떤 활동인가요?:** 시간 순서대로 일어난 일에 대해 되짚어 보아요
        * **미션:** 나의 살아온 순간, 우리 학교의 역사, 그리고 나의 경험을 저장하고 공유해 봅시다!
        """)
        
    with st.expander("🏘️ 디지털에서 만나는 옛 모습"):
        st.write("""
        * **어떤 활동인가요?:** 사이버공간을 통해 옛 모습을 살펴보아요
        * **미션:** 옛 물건을 살펴보고, 그것의 의미를 찾아보세요. 그리고 애장품을 전시해봅시다. 
        """)

    with st.expander("📜 세대공감, 달라진 모습"):
        st.write("""
        * **어떤 활동인가요?:** 옛 세대와 지금 세대가 함께 할 수 있는 공간을 만들어보아요
        * **미션:** 우리 지역의 옛이야기를 살펴보고 지역의 변화된 모습을 찾아보세요. 그리고 그 비밀을 밝혀봅시다.
        """)

    st.info("💡 **도움이 필요할 때는?**\n\n각 활동 화면 아래에는 **'🤖 AI 보조교사'**가 기다리고 있어요. 모르는 것이 있거나 무엇을 해야 할지 헷갈릴 때는 언제든 질문해 주세요!")