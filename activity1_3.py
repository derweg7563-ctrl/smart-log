import streamlit as st
import datetime
import base64

# 👇 AI 보조교사 모듈 불러오기!
import ai_teacher

def show_page():
    # 🎨 1. 디자인 CSS 마법
    st.markdown("""
        <style>
        .cute-title { text-align: center; font-size: 1.5rem; font-weight: 800; color: #5A72A0; margin-bottom: 20px; background-color: #F8F9FA; padding: 15px; border-radius: 20px; border: 3px dashed #BAE1FF; }
        .sub-title { font-size: 1.3rem; font-weight: bold; color: #FF8080; margin-top: 30px; margin-bottom: 15px; border-left: 5px solid #FF8080; padding-left: 10px; }
        
        .timeline-card {
            background: white;
            border-radius: 15px;
            padding: 15px 20px;
            margin-bottom: 15px;
            border-left: 6px solid #FFDFBA;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .timeline-card:hover { transform: translateY(-3px); box-shadow: 2px 6px 15px rgba(0,0,0,0.1); }
        .timeline-date { font-weight: 900; color: #82A284; font-size: 1.1rem; margin-bottom: 5px; }
        .timeline-content { font-size: 1.05rem; color: #444; font-weight: bold; }
        
        .month-header {
            background-color: #BAE1FF;
            color: #5A72A0;
            font-weight: 900;
            font-size: 1.2rem;
            padding: 8px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        div.stButton { display: flex; justify-content: center; width: 100%; }
        div[data-testid="stFormSubmitButton"] > button, div.stButton > button { 
            border-radius: 50px !important; padding: 8px 30px !important; height: auto !important; min-height: 45px !important; background-color: #ffffff !important; border: 2px solid #FF8080 !important; color: #FF8080 !important; font-size: 1.1rem !important; font-weight: bold !important; transition: all 0.3s ease; width: 100% !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover, div.stButton > button:hover { background-color: #FF8080 !important; color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("⏳ 발자국 속 연표 만들기")
    st.write("---")
    
    # =========================================================
    # 🗓️ [상단] 선생님이 들려주는 우리 반 1학기 발자국
    # =========================================================
    st.markdown('<div class="cute-title">🏫 우리 반 1학기 발자국 (선생님이 들려주는 이야기)</div>', unsafe_allow_html=True)
    st.info("우리가 1학기 동안 함께 울고 웃으며 만들어온 소중한 교육 활동들을 시간 순서대로 돌아보아요!")
    
    # 💡 [핵심 수정!] expanded=False 로 변경하여 처음엔 닫혀 있도록 했습니다.
    with st.expander("✨ 여기를 눌러 우리 반의 1학기 전체 연표를 펼쳐보세요!", expanded=False):
        # 3월
        st.markdown('<div class="month-header">🌸 3월의 발자국</div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">3.3(화)</div><div class="timeline-content">새로운 시작, 시업식 🎉</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">3.9(월)</div><div class="timeline-content">학급임원선거 🗳️</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">3.27(금)</div><div class="timeline-content">친구사랑주간 🤝</div></div>', unsafe_allow_html=True)

        # 4월
        st.markdown('<div class="month-header">🌱 4월의 발자국</div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">4.6(월)</div><div class="timeline-content">교육활동공개주간 👩‍🏫</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">4.14(화)</div><div class="timeline-content">비보이 공연 관람 🕺 & 장애이해교육주간 💛</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">4.21(화)</div><div class="timeline-content">과학의날 행사주간 🔬</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">4.28(화)</div><div class="timeline-content">정보윤리교육주간 💻</div></div>', unsafe_allow_html=True)

        # 5월
        st.markdown('<div class="month-header">🎈 5월의 발자국</div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">5.4(월) ~ 5.5(화)</div><div class="timeline-content">학교장재량휴업일 & 신나는 어린이날 🎁</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">5.12(화) ~ 5.13(수)</div><div class="timeline-content">도박예방교육주간 & 합동소방훈련 🚒</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">5.19(화)</div><div class="timeline-content">통일교육주간 🕊️</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">5.25(월) ~ 5.26(화)</div><div class="timeline-content">대체휴일 & 흡연예방교육주간 🚭</div></div>', unsafe_allow_html=True)

        # 6월 & 7월
        st.markdown('<div class="month-header">☀️ 6월 ~ 7월의 발자국</div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">6.2(화) ~ 6.3(수)</div><div class="timeline-content">생태환경교육주간 🌿 & 지방선거일 🗳️</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">6.9(화) ~ 6.12(금)</div><div class="timeline-content">다문화교육주간 🌏 & 양성평등교육주간 ⚖️</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">6.16(화) ~ 18주차</div><div class="timeline-content">북콘서트 작가만남 📚 & 생존수영(12시간) 🏊</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-card"><div class="timeline-date">7.1(수)</div><div class="timeline-content">재난대피훈련 🚨</div></div>', unsafe_allow_html=True)

    st.write("---")

    # =========================================================
    # 🎨 [하단] 나만의 주제 연표 만들기 (DB 공유 안 됨, 개인 보관용)
    # =========================================================
    st.markdown('<div class="cute-title">🎨 나만의 비밀 연표 만들기</div>', unsafe_allow_html=True)
    st.warning("🔒 **여러분이 저장하는 파일은 본인에게만 보입니다.** (서버에 저장되거나 다른 친구들과 공유되지 않는 나만의 비밀 공간이에요!)")
    st.write("나의 1학기, 내가 좋아하는 책, 우리 가족의 여행 등 나만의 특별한 주제를 정해서 연표를 직접 만들어 보세요.")

    if 'my_secret_timeline' not in st.session_state:
        st.session_state['my_secret_timeline'] = []

    with st.form("secret_timeline_form", clear_on_submit=True, border=True):
        st.markdown('<div class="sub-title" style="margin-top: 0;">📝 새로운 발자국 추가하기</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            t_date = st.text_input("📅 날짜 (예: 2026.04.15)")
        with col2:
            t_title = st.text_input("📌 제목 (예: 가족과 제주도 여행)")
            
        t_desc = st.text_area("✨ 자세한 내용", height=100)
        t_img = st.file_uploader("📸 사진이 있다면 올려주세요 (선택사항)", type=["png", "jpg", "jpeg"])

        _, btn_col, _ = st.columns([0.5, 4, 0.5])
        with btn_col:
            submitted = st.form_submit_button("➕ 내 연표에 추가하기")
            
        if submitted:
            if t_date and t_title:
                img_str = ""
                if t_img is not None:
                    img_str = base64.b64encode(t_img.getvalue()).decode('utf-8')
                    
                new_item = {
                    "date": t_date,
                    "title": t_title,
                    "desc": t_desc,
                    "image": img_str
                }
                st.session_state['my_secret_timeline'].append(new_item)
                st.toast("🎉 나만의 연표에 새로운 발자국이 추가되었어요!", icon="✅")
            else:
                st.error("⚠️ 날짜와 제목은 꼭 적어주세요!")

    # ---------------------------------------------------------
    # 🌟 내가 만든 연표 보여주기 영역
    # ---------------------------------------------------------
    if len(st.session_state['my_secret_timeline']) > 0:
        st.markdown('<div class="sub-title">👇 내가 만든 멋진 연표</div>', unsafe_allow_html=True)
        
        for item in st.session_state['my_secret_timeline']:
            with st.container(border=True):
                st.markdown(f'<div class="timeline-date">{item["date"]} : {item["title"]}</div>', unsafe_allow_html=True)
                st.write(item["desc"])
                
                if item["image"] != "":
                    st.markdown(f'<img src="data:image/jpeg;base64,{item["image"]}" style="max-width: 100%; border-radius: 10px; margin-top: 10px;">', unsafe_allow_html=True)

        st.write("")
        if st.button("🗑️ 내 연표 모두 지우고 새로 시작하기"):
            st.session_state['my_secret_timeline'] = []
            st.rerun()

    # =========================================================
    # 🤖 [최하단] AI 보조교사 호출
    # =========================================================
    activity_desc = "이 화면은 선생님이 제공한 1학기 학교 행사 연표를 확인하고, 학생 스스로 특별한 주제(예: 나의 1학기, 가족 여행 등)를 정해 날짜, 제목, 내용, 사진을 입력하여 '나만의 비밀 연표'를 만들어보는 활동입니다."
    ai_teacher.show_ai_teacher(activity_name="활동 1-3. 발자국 속 연표 만들기", context_description=activity_desc)