import streamlit as st
import os
import io
import datetime
import base64
from pymongo import MongoClient
from PIL import Image

# 👇 우리가 만든 AI 선생님 모듈 불러오기!
import ai_teacher

try:
    from streamlit_image_comparison import image_comparison
    HAS_COMPARISON = True
except ImportError:
    HAS_COMPARISON = False

# 지역 아카이브 정보 (다른 지역 적용 시 이 부분만 변경)
REGION = st.secrets.get("app", {}).get("region", "우리 고장")
ARCHIVE_NAME = st.secrets.get("app", {}).get("archive_name", "")
ARCHIVE_URL = st.secrets.get("app", {}).get("archive_url", "")


# ---------------------------------------------------------
# 🛠️ 1. MongoDB 연결 설정 (학교 발자국 전용 보관함)
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        return c
    except Exception as e:
        print(f"[DB ERROR] activity1_2: {e}")
        return None


client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]
    collection = db["school_footprints"]


def shrink_image_b64(uploaded_file, max_side=800, quality=80):
    """업로드한 사진을 작게 줄여 base64 문자열로 바꿔 줍니다."""
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def show_page():
    # 🎨 2. 디자인 CSS
    st.markdown("""
        <style>
        iframe[title="streamlit_image_comparison.image_comparison"] {
            border-radius: 25px !important;
            border: 8px solid transparent !important;
            background-image: linear-gradient(white, white),
                              linear-gradient(to right, #FFB3BA, #FFDFBA, #FFFFBA, #BAFFC9, #BAE1FF) !important;
            background-origin: border-box !important;
            background-clip: padding-box, border-box !important;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.1) !important;
            display: block; margin: 0 auto;
        }
        .cute-title { text-align: center; font-size: 1.5rem; font-weight: 800; color: #5A72A0; margin-bottom: 20px; background-color: #F8F9FA; padding: 15px; border-radius: 20px; border: 3px dashed #BAE1FF; }
        .video-desc { text-align: center; font-weight: bold; color: #5A72A0; font-size: 1.1rem; margin-top: 15px; line-height: 1.4; }
        div.stButton { display: flex; justify-content: center; width: 100%; }
        div.stButton > button { border-radius: 50px !important; padding: 8px 30px !important; height: auto !important; min-height: 45px !important; background-color: #ffffff !important; border: 2px solid #FF8080 !important; color: #FF8080 !important; font-size: 1.1rem !important; font-weight: bold !important; transition: all 0.3s ease; }
        div.stButton > button:hover { background-color: #FF8080 !important; color: #ffffff !important; }

        .student-name-highlight {
            color: #FF8080;
            font-size: 1.8rem;
            text-decoration: underline;
            text-decoration-color: #FFFFBA;
            text-decoration-thickness: 5px;
        }
        .archive-card {
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            aspect-ratio: 16 / 9; width: 100%;
            background: linear-gradient(135deg, #E8F0FE, #F8F9FA);
            border: 3px solid #BAE1FF; border-radius: 15px;
            text-decoration: none !important;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        }
        .archive-card:hover { transform: translateY(-4px); box-shadow: 0 8px 18px rgba(0,0,0,0.15); border-color: #5A72A0; }
        .archive-card .icon { font-size: 3.5rem; margin-bottom: 10px; }
        .archive-card .label { font-size: 1.2rem; font-weight: 900; color: #5A72A0; text-align: center; line-height: 1.4; }
        .archive-card .sub { font-size: 0.9rem; color: #888; margin-top: 8px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏫 학교 발자국 알아보기")
    st.write("---")
    st.info("💡 우리 학교의 역사가 담긴 장소나 소중한 물건들을 찾아 '발자국'을 남겨보세요.")

    # ---------------------------------------------------------
    # 🌟 3. 과거와 현재 이미지 비교
    # ---------------------------------------------------------
    st.markdown('<div class="cute-title">👀 우리 학교의 어제와 오늘, 요리조리 비교해 볼까요?</div>', unsafe_allow_html=True)

    img1_path = "school1.png"
    img2_path = "school.jpg"

    if HAS_COMPARISON and os.path.exists(img1_path) and os.path.exists(img2_path):
        try:
            col1, col2, col3 = st.columns([1, 8, 1])
            with col2:
                image_comparison(
                    img1=img1_path,
                    img2=img2_path,
                    label1="과거",
                    label2="현재",
                    width=850,
                    starting_position=50,
                    show_labels=True,
                    make_responsive=True,
                    in_memory=True,
                )
        except Exception as e:
            print(f"[COMPARISON ERROR] {e}")
            c1, c2 = st.columns(2)
            c1.image(img1_path, caption="과거", use_container_width=True)
            c2.image(img2_path, caption="현재", use_container_width=True)
    else:
        st.warning("⚠️ 앗! 학교 사진을 아직 찾을 수 없어요.")

    st.write("---")

    # ---------------------------------------------------------
    # 📺 4. 학교 발자국 알아보는 방법
    # ---------------------------------------------------------
    st.subheader("📍 학교 발자국 알아보는 방법")
    st.write("")

    # 아카이브 링크가 설정되어 있으면 3칸, 없으면 2칸
    if ARCHIVE_URL:
        col1, col2, col3 = st.columns(3)
    else:
        col1, col2 = st.columns(2)
        col3 = None

    with col1:
        st.video("https://youtu.be/rCxpWNuwsrY")
        st.markdown('<div class="video-desc">💻 학교 홈페이지를 통해<br>학교 발자국 알아보기</div>', unsafe_allow_html=True)
    with col2:
        st.video("https://www.youtube.com/watch?v=zxmOUGwIRgk&t=1s")
        st.markdown('<div class="video-desc">📌 학교 게시판을 통해<br>학교 발자국 알아보기</div>', unsafe_allow_html=True)

    if col3 is not None:
        label = ARCHIVE_NAME or f"{REGION} 기록 저장소"
        with col3:
            st.markdown(f"""
                <a href="{ARCHIVE_URL}" target="_blank" class="archive-card">
                    <div class="icon">🏛️</div>
                    <div class="label">{label}<br>바로가기</div>
                    <div class="sub">(클릭하면 새 창이 열려요)</div>
                </a>
            """, unsafe_allow_html=True)
            st.markdown(
                f'<div class="video-desc" style="margin-top: 33px;">🏛️ {label}를 통해<br>학교 발자국 알아보기</div>',
                unsafe_allow_html=True,
            )

    st.write("---")

    # ---------------------------------------------------------
    # 📝 5. 접속한 학생별 맞춤형 저장 공간
    # ---------------------------------------------------------
    current_student = st.session_state.get("username", "학생")

    st.markdown(
        f'<h3>📸 <span class="student-name-highlight">{current_student}</span>의 학교 발자국 기록하기</h3>',
        unsafe_allow_html=True,
    )
    st.info(f"{current_student} 학생이 학교 구석구석에서 발견한 우리 학교만의 특별한 발자국을 영구 보관해 보세요!")

    # 이전에 저장한 기록 보여주기
    my_records = []
    if db_connected:
        try:
            my_records = list(collection.find({"username": current_student}).sort("timestamp", -1))
        except Exception as e:
            print(f"[DB READ ERROR] activity1_2: {e}")

    if my_records:
        st.success(f"📚 지금까지 {len(my_records)}개의 발자국을 남겼어요!")
        with st.expander("내가 남긴 발자국 다시 보기", expanded=False):
            for r in my_records:
                c1, c2 = st.columns([1, 3])
                if r.get("image_base64"):
                    c1.image(f"data:image/jpeg;base64,{r['image_base64']}", use_container_width=True)
                c2.write(r.get("content", ""))
                st.markdown("---")

    archive_hint = f"위의 {ARCHIVE_NAME or REGION + ' 기록 저장소'}를 검색하거나 " if ARCHIVE_URL else ""
    memory_text = st.text_area(
        f"✨ 학교 곳곳을 찾거나 {archive_hint}내가 발견한 학교 발자국을 적고 그 느낌을 자세히 적어보세요\n"
        "(예: 1985년 운동회 사진을 찾았는데 그 때는 운동장에서 많은 사람들이 모여 재미있는 활동을 하는 모습이 즐거워 보인다.)",
        height=150,
        key="text_1_2",
    )

    uploaded_file = st.file_uploader(
        "📸 조사한 학교 발자국 사진을 선택해주세요. (없으면 글만 먼저 저장해도 괜찮아요)",
        type=["png", "jpg", "jpeg"],
        key="file_1_2",
    )

    _, btn_col, _ = st.columns([0.5, 4, 0.5])
    with btn_col:
        if st.button("🚀 우리 학교 발자국 영구 저장하기", use_container_width=True):
            if not memory_text.strip():
                st.warning("⚠️ 내가 발견한 것과 느낀 점을 한 줄이라도 적어주세요!")
            elif not db_connected:
                st.error("서버 연결이 잠시 불안정해요. 선생님께 말씀드려 주세요. 🙂")
            else:
                try:
                    record = {
                        "username": current_student,
                        "content": memory_text,
                        "timestamp": datetime.datetime.now(),
                    }
                    if uploaded_file is not None:
                        record["image_base64"] = shrink_image_b64(uploaded_file)

                    # 덮어쓰지 않고 새 기록으로 쌓습니다.
                    collection.insert_one(record)

                    st.toast(f"🎉 {current_student} 학생의 학교 발자국이 안전하게 저장되었어요!", icon="✅")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    print(f"[SAVE ERROR] activity1_2: {e}")
                    st.error("저장하는 중에 문제가 생겼어요. 사진이 너무 크지 않은지 확인하고 다시 해볼까요? 🙂")

    # ---------------------------------------------------------
    # 🤖 6. AI 보조교사 호출
    # ---------------------------------------------------------
    archive_desc = f", {ARCHIVE_NAME or REGION + ' 기록 저장소'}" if ARCHIVE_URL else ""
    activity_desc = (
        f"이 화면은 학교의 과거와 현재 사진을 비교해보고, 학교 홈페이지나 게시판{archive_desc}에서 "
        "학교의 역사가 담긴 사진을 찾아 저장하는 곳입니다. "
        "학생이 사진을 올리고 느낀 점을 적어야 합니다."
    )
    ai_teacher.show_ai_teacher(
        activity_name="활동 1-2. 학교 발자국 알아보기",
        context_description=activity_desc,
    )
