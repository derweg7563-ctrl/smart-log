import streamlit as st
import config
import os
import io
import datetime
import base64
from pymongo import MongoClient
from PIL import Image

# ---------------------------------------------------------
# 🛠️ 1. MongoDB 연결 설정
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        return c
    except Exception as e:
        print(f"[DB ERROR] activity1_1: {e}")
        return None


client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]
    collection = db["student_timeline"]


# ---------------------------------------------------------
# 사진 용량 줄이기 (저장 실패 방지)
# ---------------------------------------------------------
def shrink_image_b64(uploaded_file, max_side=800, quality=80):
    """업로드한 사진을 작게 줄여 base64 문자열로 바꿔 줍니다."""
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


STEPS = [
    ("1단계_태어났을때", "box-1", "내가<br>태어났을 때"),
    ("2단계_어린이집유치원", "box-2", "어린이집<br>유치원"),
    ("3단계_입학식", "box-3", "초등학교<br>입학식"),
    ("4단계_지금의나", "box-4", "지금의 나"),
    ("5단계_미래의나", "box-5", "1년 후의<br>내 모습"),
]

# 단계별 안내 문구 (사진을 구하기 어려운 경우를 돕기 위함)
STEP_HINTS = {
    "1단계_태어났을때": "아기 때 사진이 없다면, 그때의 내 모습을 상상해서 그림으로 그린 뒤 찍어도 좋아요! 🎨",
    "2단계_어린이집유치원": "사진을 못 찾았다면 그때 기억나는 장면을 그림으로 그려도 괜찮아요! 🎨",
    "3단계_입학식": "입학식 사진이 없다면 학교에 처음 온 날을 떠올리며 그려 보세요! 🎨",
    "4단계_지금의나": "지금 내 모습을 바로 찍어서 올려도 좋아요! 📸",
    "5단계_미래의나": "1년 뒤는 아직 오지 않았으니, 상상해서 그린 그림을 찍어 올려 주세요! 🎨",
}


def show_page():
    if "current_step" not in st.session_state:
        st.session_state.current_step = None
    if "show_growth" not in st.session_state:
        st.session_state.show_growth = False

    # 🎨 2. 디자인 설정
    st.markdown("""
        <style>
        .timeline-container { display: flex; flex-direction: column; align-items: center; margin-top: 30px; width: fit-content; margin-left: auto; margin-right: auto; }
        .box { width: 180px; height: 100px; background-color: #FFFFFF; border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold; color: #444; box-shadow: 4px 4px 15px rgba(0,0,0,0.08); border: 5px solid #EEEEEE; text-align: center; line-height: 1.3; padding: 10px; margin: 0 auto 5px auto; }
        .box-1 { border-color: #FFB3BA !important; } .box-2 { border-color: #FFDFBA !important; } .box-3 { border-color: #FFFFBA !important; } .box-4 { border-color: #BAFFC9 !important; } .box-5 { border-color: #BAE1FF !important; }

        div.stButton > button {
            border-radius: 50px !important;
            padding: 8px 30px !important;
            height: auto !important;
            min-height: 45px !important;
            background-color: #ffffff !important;
            border: 2px solid #FF8080 !important;
            color: #FF8080 !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover { background-color: #FF8080 !important; color: #ffffff !important; }

        .download-btn-container button { width: 175px !important; height: 70px !important; border: 3px solid #4D96FF !important; color: #4D96FF !important; background-color: #ffffff !important; border-radius: 50px !important; box-shadow: 0px 4px 10px rgba(77, 150, 255, 0.2) !important; white-space: pre-wrap !important; transition: all 0.3s ease; display: block; margin: 0 auto; }
        .download-btn-container button p { font-size: 1.25rem !important; font-weight: 900 !important; line-height: 1.3 !important; margin: 0 !important; }
        .download-btn-container button:hover { background-color: #4D96FF !important; color: #ffffff !important; }
        .arrow { font-size: 2.2rem; color: #FF8080; font-weight: bold; text-align: center; margin-top: 35px; }
        .vertical-connector { display: flex; justify-content: flex-end; width: 100%; padding-right: 73px; margin: 30px 0; }
        .arrow-down { font-size: 2.5rem; color: #FF8080; font-weight: bold; width: 35px; text-align: center; }
        .done-badge { text-align: center; color: #2E7D32; font-weight: bold; font-size: 0.95rem; margin-bottom: 4px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("👣 나의 발자국 살펴보기")

    user_id = st.session_state.get("username", "test_student")

    # 이미 저장한 단계 확인 (진행 상황 표시용)
    saved_stages = {}
    if db_connected:
        try:
            for r in collection.find({"username": user_id}):
                saved_stages[r["stage"]] = r
        except Exception as e:
            print(f"[DB READ ERROR] activity1_1: {e}")

    # 진행 상황 안내
    done_count = len(saved_stages)
    st.progress(done_count / 5, text=f"나의 발자국 {done_count} / 5 단계 완성!")
    if done_count < 5:
        st.info("💡 사진보다는 자신의 그림을 활동지(아래에서 다운로드)에 그린 후 카메라 앱으로 찍어 올리세요. 나중에도 추가할 수 있어요!  *<저장하기 누르면 아래에 입력 창이 나옵니다.>*")

    def step_button(key_name, label_key):
        """단계별 저장 버튼. 이미 저장했으면 표시를 바꿔 줍니다."""
        done = key_name in saved_stages
        if done:
            st.markdown('<div class="done-badge">✅ 기록 완료</div>', unsafe_allow_html=True)
        label = "✏️ 다시 쓰기" if done else "💾 저장하기"
        if st.button(label, key=label_key):
            st.session_state.current_step = key_name

    # --- 타임라인 UI 시작 ---
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    c1, a1, c2, a2, c3 = st.columns([1, 0.2, 1, 0.2, 1])
    with c1:
        st.markdown('<div class="box box-1">내가<br>태어났을 때</div>', unsafe_allow_html=True)
        step_button("1단계_태어났을때", "save1")
    with a1:
        st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="box box-2">어린이집<br>유치원</div>', unsafe_allow_html=True)
        step_button("2단계_어린이집유치원", "save2")
    with a2:
        st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="box box-3">초등학교<br>입학식</div>', unsafe_allow_html=True)
        step_button("3단계_입학식", "save3")

    st.markdown('<div class="vertical-connector"><div class="arrow-down">↓</div></div>', unsafe_allow_html=True)

    c_down, c5, a3, c4 = st.columns([1, 1, 0.2, 1])
    with c_down:
        st.markdown('<div class="download-btn-container">', unsafe_allow_html=True)
        pdf_file_path = "letter.pdf"
        if os.path.exists(pdf_file_path):
            with open(pdf_file_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 활동지\n다운로드",
                    data=pdf_file.read(),
                    file_name="letter.pdf",
                    mime="application/pdf",
                    key="download_work",
                )
        else:
            st.button("📄 활동지\n(준비 중)", key="no_file_btn", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="box box-4">지금의 나</div>', unsafe_allow_html=True)
        step_button("4단계_지금의나", "save4")
    with a3:
        st.markdown('<div class="arrow">←</div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="box box-5">1년 후의<br>내 모습</div>', unsafe_allow_html=True)
        step_button("5단계_미래의나", "save5")

    st.markdown('</div>', unsafe_allow_html=True)
    # --- 타임라인 UI 끝 ---

    # ---------------------------------------------------------
    # 📝 3. 데이터베이스 저장 영역
    # ---------------------------------------------------------
    if st.session_state.current_step:
        step_key = st.session_state.current_step
        st.divider()
        display_name = step_key.split("_")[1]
        st.subheader(f"📍 '{display_name}' 단계 기록하기")

        # 단계별 도움말
        hint = STEP_HINTS.get(step_key, "")
        if hint:
            st.caption(hint)

        prev = saved_stages.get(step_key)
        prev_text = prev.get("content", "") if prev else ""
        prev_image = prev.get("image_base64", "") if prev else ""

        if prev_image:
            st.markdown("**지금 올려 둔 사진**")
            st.image(f"data:image/jpeg;base64,{prev_image}", width=200)

        memory_text = st.text_area(
            "✨ 이 때의 나에게 하고 싶은 말이나 기억나는 점을 적어보세요!",
            value=prev_text,
            height=100,
            key=f"text_{step_key}",
        )
        uploaded_file = st.file_uploader(
            "📸 사진 파일을 선택해주세요. (없으면 글만 먼저 저장해도 괜찮아요)",
            type=["png", "jpg", "jpeg"],
            key=f"file_{step_key}",
        )

        if st.button("🚀 내 발자국 영구 저장하기", type="primary"):
            if not memory_text.strip():
                st.warning("⚠️ 이 때의 기억이나 하고 싶은 말을 한 줄이라도 적어주세요!")
            elif not db_connected:
                st.error("서버 연결이 잠시 불안정해요. 선생님께 말씀드려 주세요. 🙂")
            else:
                try:
                    record = {
                        "username": user_id,
                        "stage": step_key,
                        "content": memory_text,
                        "timestamp": datetime.datetime.now(),
                    }
                    # 새 사진이 있으면 줄여서 저장, 없으면 기존 사진 유지
                    if uploaded_file is not None:
                        record["image_base64"] = shrink_image_b64(uploaded_file)
                    elif prev_image:
                        record["image_base64"] = prev_image

                    collection.update_one(
                        {"username": user_id, "stage": step_key},
                        {"$set": record},
                        upsert=True,
                    )

                    if "image_base64" in record:
                        st.toast(f"🎉 '{display_name}' 발자국이 안전하게 저장되었어요!", icon="✅")
                        st.balloons()
                    else:
                        st.toast("📝 글을 저장했어요! 사진은 나중에 더해도 괜찮아요.", icon="✅")

                    st.session_state.current_step = None
                    st.rerun()
                except Exception as e:
                    print(f"[SAVE ERROR] activity1_1: {e}")
                    st.error("저장하는 중에 문제가 생겼어요. 사진이 너무 크지 않은지 확인하고 다시 해볼까요? 🙂")

    # ---------------------------------------------------------
    # 🌟 4. '나의 성장 과정' 한눈에 보기
    # ---------------------------------------------------------
    if db_connected:
        photo_stages = {
            k: v.get("image_base64", "")
            for k, v in saved_stages.items()
            if v.get("image_base64")
        }

        if len(photo_stages) >= 5:
            st.divider()

            _, btn_col, _ = st.columns([0.5, 4, 0.5])
            with btn_col:
                if st.button("🌟 나의 성장 과정", use_container_width=True):
                    st.session_state.show_growth = not st.session_state.show_growth

            if st.session_state.show_growth:
                st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

                def get_photo_box(img_base64, box_class, title_text):
                    return f'''
                    <div style="display: flex; flex-direction: column; align-items: center;">
                        <div class="box {box_class}" style="padding: 0; overflow: hidden; display: flex; justify-content: center; align-items: center; border-width: 5px;">
                            <img src="data:image/jpeg;base64,{img_base64}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 18px;">
                        </div>
                        <div style="margin-top: 3px; color: black; font-weight: bold; text-align: center; line-height: 1.2;">
                            {title_text}
                        </div>
                    </div>
                    '''

                c1, a1, c2, a2, c3 = st.columns([1, 0.2, 1, 0.2, 1])
                with c1: st.markdown(get_photo_box(photo_stages.get("1단계_태어났을때", ""), "box-1", "내가<br>태어났을 때"), unsafe_allow_html=True)
                with a1: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
                with c2: st.markdown(get_photo_box(photo_stages.get("2단계_어린이집유치원", ""), "box-2", "어린이집<br>유치원"), unsafe_allow_html=True)
                with a2: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
                with c3: st.markdown(get_photo_box(photo_stages.get("3단계_입학식", ""), "box-3", "초등학교<br>입학식"), unsafe_allow_html=True)

                st.markdown('<div class="vertical-connector"><div class="arrow-down">↓</div></div>', unsafe_allow_html=True)

                c_down, c5, a3, c4 = st.columns([1, 1, 0.2, 1])
                with c_down: st.write("")
                with c4: st.markdown(get_photo_box(photo_stages.get("4단계_지금의나", ""), "box-4", "지금의 나"), unsafe_allow_html=True)
                with a3: st.markdown('<div class="arrow">←</div>', unsafe_allow_html=True)
                with c5: st.markdown(get_photo_box(photo_stages.get("5단계_미래의나", ""), "box-5", "1년 후의<br>내 모습"), unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
