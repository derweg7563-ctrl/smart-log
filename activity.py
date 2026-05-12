import streamlit as st
import os
import base64

def show_page():
    # 💡 1. 화살표 및 타이틀 이미지 읽기
    arrow_tag = ""
    if os.path.exists("arrow.png"):
        with open("arrow.png", "rb") as f: enc = base64.b64encode(f.read()).decode()
        # 원본 오른쪽 화살표를 아래(90도)로 회전하여 수직 흐름 만들기
        arrow_tag = f"""
        <div style="text-align: center; margin: 10px 0;">
            <img src="data:image/png;base64,{enc}" style="width: 60px; transform: rotate(90deg); opacity: 0.8;">
        </div>
        """

    # 💡 2. 환영 인사말 (양옆 이모지 추가)
    st.markdown("""
        <div style="text-align: center; font-size: 25px; font-weight: bold; margin-bottom: 5px; color: #333;">
            🎉 여러분과 함께 발자국을 따라 디지털 여행을 시작하게 되어 정말 기뻐요 🎉
        </div>
        <div style="text-align: center; font-size: 25px; font-weight: bold; color: #333;">
            🚀 우리 모두 함께 힘찬 기운으로 여행을 떠나볼까요? 🚀
        </div>
        <div style="height: 30px;"></div>
    """, unsafe_allow_html=True)

    # 3. 첫 번째 카드 (파랑)
    st.markdown("""
        <div style="border: 4px solid #1565C0; border-radius: 20px; padding: 30px; background-color: #f0f7ff;">
            <div style="text-align: center; font-size: 30px; font-weight: bold; color: #1565C0; margin-bottom: 10px;">
                어제와 오늘의 흐름 따라가기
            </div>
            <div style="text-align: center; font-size: 20px; font-weight: bold; color: #1565C0;">
                시간 순서대로 일어난 일에 대해 되짚어 보아요
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 👇 첫 번째와 두 번째 카드 사이 화살표
    if arrow_tag: st.markdown(arrow_tag, unsafe_allow_html=True)

    # 4. 두 번째 카드 (초록)
    st.markdown("""
        <div style="border: 4px solid #2E7D32; border-radius: 20px; padding: 30px; background-color: #f0f9f0;">
            <div style="text-align: center; font-size: 30px; font-weight: bold; color: #2E7D32; margin-bottom: 10px;">
                디지털에서 만나는 옛 모습
            </div>
            <div style="text-align: center; font-size: 20px; font-weight: bold; color: #2E7D32;">
                사이버공간을 통해 옛 모습을 살펴보아요
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 👇 두 번째와 세 번째 카드 사이 화살표
    if arrow_tag: st.markdown(arrow_tag, unsafe_allow_html=True)

    # 5. 세 번째 카드 (주황)
    st.markdown("""
        <div style="border: 4px solid #EF6C00; border-radius: 20px; padding: 30px; background-color: #fffaf0;">
            <div style="text-align: center; font-size: 30px; font-weight: bold; color: #EF6C00; margin-bottom: 10px;">
                세대공감, 달라진 모습 살펴보기
            </div>
            <div style="text-align: center; font-size: 20px; font-weight: bold; color: #EF6C00;">
                옛 세대와 지금 세대가 함께 할 수 있는 공간을 만들어보아요
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 💡 6. 화면 맨 오른쪽 아래 타이틀 이미지 (title.png)
    if os.path.exists("title.png"):
        with open("title.png", "rb") as f: t_enc = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin-top: 50px; padding-right: 10px;">
            <img src="data:image/png;base64,{t_enc}" style="max-width: 350px; width: 100%;">
        </div>
        """, unsafe_allow_html=True)