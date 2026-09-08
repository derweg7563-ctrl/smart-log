import streamlit as st
import io
import base64
import datetime
import html as html_lib
from PIL import Image

# 👇 AI 보조교사 모듈 불러오기!
import ai_teacher
import config


def shrink_image_b64(uploaded_file, max_side=800, quality=80):
    """올린 사진을 작게 줄여 base64 문자열로 바꿔 줍니다."""
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def build_timeline_html(items, student_name):
    """내려받기용 HTML 파일을 만듭니다. (사진까지 파일 안에 담깁니다)"""
    cards = []
    for it in items:
        img_tag = ""
        if it.get("image"):
            img_tag = (
                f'<img src="data:image/jpeg;base64,{it["image"]}" '
                f'style="max-width:100%;border-radius:10px;margin-top:10px;">'
            )
        cards.append(f"""
        <div class="card">
            <div class="date">{html_lib.escape(it["date"])} : {html_lib.escape(it["title"])}</div>
            <div class="desc">{html_lib.escape(it.get("desc", ""))}</div>
            {img_tag}
        </div>
        """)

    today = datetime.date.today().strftime("%Y년 %m월 %d일")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{html_lib.escape(student_name)}의 비밀 연표</title>
<style>
  body {{ font-family: 'Malgun Gothic', sans-serif; background:#FAFAFA; padding:30px; max-width:800px; margin:0 auto; }}
  h1 {{ text-align:center; color:#5A72A0; }}
  .made {{ text-align:center; color:#888; font-size:0.9rem; margin-bottom:30px; }}
  .card {{ background:#fff; border-radius:15px; padding:15px 20px; margin-bottom:15px;
           border-left:6px solid #FFDFBA; box-shadow:2px 4px 10px rgba(0,0,0,0.05); }}
  .date {{ font-weight:900; color:#82A284; font-size:1.1rem; margin-bottom:5px; }}
  .desc {{ font-size:1.05rem; color:#444; }}
</style>
</head>
<body>
  <h1>⏳ {html_lib.escape(student_name)}의 비밀 연표</h1>
  <div class="made">{today}에 만들었어요</div>
  {"".join(cards)}
</body>
</html>"""


def show_page():
    # 🎨 1. 디자인 CSS
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
        div[data-testid="stDownloadButton"] > button {
            border-radius: 50px !important; padding: 8px 30px !important; min-height: 45px !important;
            background-color: #ffffff !important; border: 2px solid #4D96FF !important; color: #4D96FF !important;
            font-size: 1.1rem !important; font-weight: bold !important; width: 100% !important;
        }
        div[data-testid="stDownloadButton"] > button:hover { background-color: #4D96FF !important; color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("⏳ 발자국 속 연표 만들기")
    st.write("---")

    # =========================================================
    # 🗓️ [상단] 선생님이 들려주는 우리 반 1학기 발자국
    # =========================================================
    st.markdown('<div class="cute-title">🏫 우리 반 1학기 발자국 (선생님이 들려주는 이야기)</div>', unsafe_allow_html=True)
    st.info("우리가 1학기 동안 함께 울고 웃으며 만들어온 소중한 교육 활동들을 시간 순서대로 돌아보아요!")

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
    # 🎨 [하단] 나만의 주제 연표 만들기 (서버 저장 없음)
    # =========================================================
    st.markdown('<div class="cute-title">🎨 나만의 비밀 연표 만들기</div>', unsafe_allow_html=True)
    st.warning(
        "🔒 **여러분이 만드는 연표는 서버에 저장되지 않아요.** (다른 친구들에게 보이지 않는 나만의 비밀 공간이에요!)\n\n"
        "⚠️ 그래서 **화면을 새로고침하거나 로그아웃하면 사라져요.** "
        "다 만든 뒤에는 아래 **[내 연표 파일로 저장하기]** 버튼을 꼭 눌러 내 기기에 보관하세요!"
    )
    st.write("나의 1학기, 내가 좋아하는 책, 우리 가족의 여행 등 나만의 특별한 주제를 정해서 연표를 직접 만들어 보세요.")

    if "my_secret_timeline" not in st.session_state:
        st.session_state["my_secret_timeline"] = []

    with st.form("secret_timeline_form", clear_on_submit=True, border=True):
        st.markdown('<div class="sub-title" style="margin-top: 0;">📝 새로운 발자국 추가하기</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            # 달력에서 고르므로 날짜 형식이 항상 같아 정렬이 정확합니다.
            t_date = st.date_input(
                "📅 날짜",
                value=datetime.date.today(),
                min_value=datetime.date(2000, 1, 1),
                max_value=datetime.date(2100, 12, 31),
                format="YYYY.MM.DD",
            )
        with col2:
            t_title = st.text_input("📌 제목 (예: 가족과 제주도 여행)")

        t_desc = st.text_area("✨ 자세한 내용", height=100)
        t_img = st.file_uploader("📸 사진이 있다면 올려주세요 (선택사항)", type=["png", "jpg", "jpeg"])

        _, btn_col, _ = st.columns([0.5, 4, 0.5])
        with btn_col:
            submitted = st.form_submit_button("➕ 내 연표에 추가하기")

        if submitted:
            if t_title.strip():
                img_str = ""
                if t_img is not None:
                    try:
                        img_str = shrink_image_b64(t_img)
                    except Exception as e:
                        print(f"[IMAGE ERROR] activity1_3: {e}")
                        st.warning("사진을 불러오지 못했어요. 글만 저장할게요. 🙂")

                st.session_state["my_secret_timeline"].append({
                    "sort_key": t_date.isoformat(),          # 정렬용 (2026-04-15)
                    "date": t_date.strftime("%Y.%m.%d"),     # 보여주기용 (2026.04.15)
                    "title": t_title.strip(),
                    "desc": t_desc,
                    "image": img_str,
                })
                st.toast("🎉 나만의 연표에 새로운 발자국이 추가되었어요!", icon="✅")
            else:
                st.error("⚠️ 제목은 꼭 적어주세요!")

    # ---------------------------------------------------------
    # 🌟 내가 만든 연표 보여주기
    # ---------------------------------------------------------
    items = st.session_state["my_secret_timeline"]
    if len(items) > 0:
        st.markdown('<div class="sub-title">👇 내가 만든 멋진 연표</div>', unsafe_allow_html=True)

        # 날짜 기준 오름차순(오래된 순) 정렬
        sorted_timeline = sorted(items, key=lambda x: x.get("sort_key", x["date"]))

        for idx, item in enumerate(sorted_timeline):
            with st.container(border=True):
                st.markdown(
                    f'<div class="timeline-date">{item["date"]} : {item["title"]}</div>',
                    unsafe_allow_html=True,
                )
                st.write(item["desc"])
                if item["image"]:
                    st.markdown(
                        f'<img src="data:image/jpeg;base64,{item["image"]}" '
                        f'style="max-width: 100%; border-radius: 10px; margin-top: 10px;">',
                        unsafe_allow_html=True,
                    )

        st.write("")

        # 💾 내려받기 (서버에 남기지 않고 내 기기에 보관)
        student_name = st.session_state.get("username", "나")
        html_data = build_timeline_html(sorted_timeline, student_name)

        d_col, r_col = st.columns(2)
        with d_col:
            st.download_button(
                "💾 내 연표 파일로 저장하기",
                data=html_data.encode("utf-8"),
                file_name=f"{student_name}의_비밀연표.html",
                mime="text/html",
                use_container_width=True,
            )
            st.caption("내려받은 파일을 두 번 누르면 언제든 다시 볼 수 있어요! 📂")

        with r_col:
            if st.session_state.get("confirm_reset_timeline"):
                st.error("정말 모두 지울까요? 되돌릴 수 없어요!")
                b1, b2 = st.columns(2)
                if b1.button("네, 지울래요", use_container_width=True):
                    st.session_state["my_secret_timeline"] = []
                    st.session_state.pop("confirm_reset_timeline", None)
                    st.rerun()
                if b2.button("아니요", use_container_width=True):
                    st.session_state.pop("confirm_reset_timeline", None)
                    st.rerun()
            else:
                if st.button("🗑️ 내 연표 모두 지우기", use_container_width=True):
                    st.session_state["confirm_reset_timeline"] = True
                    st.rerun()

    # =========================================================
    # 🤖 [최하단] AI 보조교사 호출
    # =========================================================
    activity_desc = (
        "이 화면은 선생님이 제공한 1학기 학교 행사 연표를 확인하고, "
        "학생 스스로 특별한 주제(예: 나의 1학기, 가족 여행 등)를 정해 "
        "날짜, 제목, 내용, 사진을 입력하여 '나만의 비밀 연표'를 만들어보는 활동입니다. "
        "만든 연표는 서버에 저장되지 않으므로, 파일로 내려받아 보관해야 합니다."
    )
    ai_teacher.show_ai_teacher(
        activity_name="활동 1-3. 발자국 속 연표 만들기",
        context_description=activity_desc,
    )
