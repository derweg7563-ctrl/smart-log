import streamlit as st
import io
import base64
import datetime
from pymongo import MongoClient
from PIL import Image

# 👇 AI 보조교사 모듈 불러오기
import ai_teacher
import config


# ---------------------------------------------------------
# 🛠️ 1. MongoDB 연결 설정 (전시회 전용 보관함)
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        return c
    except Exception as e:
        print(f"[DB ERROR] activity2_3: {e}")
        return None


client = init_connection()
db_connected = client is not None
if db_connected:
    db = client["school_project"]
    collection = db["exhibition_items"]      # 애장품 저장 컬렉션


def shrink_image_b64(uploaded_file, max_side=800, quality=80):
    """올린 사진을 작게 줄여 base64 문자열로 바꿔 줍니다."""
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def show_page():
    # 🎨 2. 갤러리 카드 디자인 CSS
    st.markdown("""
        <style>
        .exhibition-card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border-top: 5px solid #2E7D32;
            transition: transform 0.2s;
        }
        .exhibition-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .item-title { font-size: 1.3rem; font-weight: 900; color: #2E7D32; margin-bottom: 5px; }
        .item-owner { font-size: 0.9rem; color: #7f8c8d; margin-bottom: 15px; font-weight: bold; }
        .item-story { font-size: 1rem; color: #333; line-height: 1.5; background-color: #f0f9f0; padding: 10px; border-radius: 10px; }
        .student-name { text-align: right; font-weight: bold; color: #EF6C00; margin-top: 10px; font-size: 0.9rem; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🖼️ 우리 반 애장품 전시회")
    st.info("💡 가족의 소중한 옛 물건을 찾아 얽힌 이야기를 인터뷰해 보고, 우리 반 전시회에 출품해 봅시다!")

    tab1, tab2 = st.tabs(["📸 나의 애장품 출품하기", "🏛️ 전시회 관람하기"])

    current_student = st.session_state.get("username", "학생")

    # ==========================================
    # [탭 1] 나의 애장품 출품하기
    # ==========================================
    with tab1:
        st.subheader("나만의 큐레이터 노트 작성하기 ✍️")
        st.caption("📢 출품한 작품은 우리 반 친구들이 함께 볼 수 있어요. 가족과 이야기 나눈 내용을 예쁘게 적어 주세요!")

        with st.form("curator_form", clear_on_submit=True):
            item_name = st.text_input(
                "1. 옛 물건(애장품)의 이름은 무엇인가요?",
                placeholder="예: 할머니의 낡은 재봉틀, 옛날 동전, 닳은 옥반지 등",
            )

            col1, col2 = st.columns(2)
            with col1:
                item_owner = st.text_input(
                    "2. 이 물건의 원래 주인은 누구셨나요?",
                    placeholder="예: 우리 할아버지, 증조할머니",
                )
            with col2:
                item_era = st.text_input(
                    "3. 언제쯤 쓰던 물건인가요?",
                    placeholder="예: 1970년대, 약 50년 전",
                )

            item_story = st.text_area(
                "4. 가족에게 들은 이 물건의 사연(증언)을 자세히 적어주세요.",
                placeholder="할머니께서 젊은 시절 우리 아빠의 옷을 직접 지어주실 때 쓰던 재봉틀이라고 합니다...",
                height=150,
            )

            uploaded_file = st.file_uploader(
                "5. 애장품의 멋진 사진을 올려주세요! (사진이 없으면 그림을 그려서 찍어도 좋아요)",
                type=["png", "jpg", "jpeg"],
            )

            submitted = st.form_submit_button("🚀 우리 반 전시회에 출품하기", use_container_width=True)

            if submitted:
                if not item_name.strip() or not item_story.strip():
                    st.warning("⚠️ 물건의 이름과 사연은 꼭 적어주세요!")
                elif not db_connected:
                    st.error("서버 연결이 잠시 불안정해요. 선생님께 말씀드려 주세요. 🙂")
                else:
                    try:
                        record = {
                            "username": current_student,
                            "item_name": item_name.strip(),
                            "item_owner": item_owner.strip(),
                            "item_era": item_era.strip(),
                            "story": item_story.strip(),
                            "timestamp": datetime.datetime.now(),
                        }
                        if uploaded_file is not None:
                            record["image_base64"] = shrink_image_b64(uploaded_file)

                        collection.insert_one(record)

                        st.success(
                            "🎉 성공적으로 전시회에 출품되었습니다! "
                            "작성하신 내용이 초기화되었으니 새로운 물건을 계속 추가할 수 있어요. "
                            "(결과는 [전시회 관람하기] 탭에서 확인하세요)"
                        )
                        st.balloons()
                    except Exception as e:
                        print(f"[SAVE ERROR] activity2_3: {e}")
                        st.error("출품하는 중에 문제가 생겼어요. 사진이 너무 크지 않은지 확인하고 다시 해볼까요? 🙂")

        # --- 내가 출품한 작품 관리 ---
        if db_connected:
            try:
                my_items = list(
                    collection.find({"username": current_student}).sort("timestamp", -1)
                )
            except Exception as e:
                print(f"[DB READ ERROR] activity2_3: {e}")
                my_items = []

            if my_items:
                st.markdown("---")
                st.markdown(f"#### 📦 내가 출품한 작품 ({len(my_items)}개)")
                st.caption("잘못 올린 작품이 있다면 여기서 내릴 수 있어요.")

                for it in my_items:
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"• **{it.get('item_name', '이름 없음')}**")

                    del_key = f"confirm_del_{it['_id']}"
                    with c2:
                        if st.session_state.get(del_key):
                            b1, b2 = st.columns(2)
                            if b1.button("삭제", key=f"yes_{it['_id']}"):
                                collection.delete_one({"_id": it["_id"]})
                                st.session_state.pop(del_key, None)
                                st.rerun()
                            if b2.button("취소", key=f"no_{it['_id']}"):
                                st.session_state.pop(del_key, None)
                                st.rerun()
                        else:
                            if st.button("🗑️ 내리기", key=f"del_{it['_id']}"):
                                st.session_state[del_key] = True
                                st.rerun()

    # ==========================================
    # [탭 2] 전시회 관람하기
    # ==========================================
    with tab2:
        st.subheader("🏛️ 온라인 애장품 갤러리")
        st.write("친구들이 가족에게 직접 듣고 찾아온 소중한 옛 물건들을 감상해 봅시다.")
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        if not db_connected:
            st.warning("전시회를 불러올 수 없어요. 잠시 후 다시 들어와 볼까요? 🙂")
        else:
            try:
                items = list(collection.find().sort("timestamp", -1))
            except Exception as e:
                print(f"[DB READ ERROR] activity2_3 gallery: {e}")
                items = []

            if len(items) == 0:
                st.info("아직 전시된 애장품이 없습니다. 첫 번째 큐레이터가 되어주세요!")
            else:
                st.caption(f"지금까지 {len(items)}개의 애장품이 전시되어 있어요! 🎨")

                cols = st.columns(3)
                for idx, item in enumerate(items):
                    col = cols[idx % 3]
                    with col:
                        if item.get("image_base64"):
                            try:
                                st.image(
                                    base64.b64decode(item["image_base64"]),
                                    use_container_width=True,
                                )
                            except Exception as e:
                                print(f"[IMAGE ERROR] activity2_3: {e}")
                                st.write("📷 사진을 불러오지 못했어요")
                        else:
                            st.write("📷 사진 없이 이야기만 담긴 작품이에요")

                        st.markdown(f"""
                            <div class="exhibition-card">
                                <div class="item-title">{item.get("item_name", "이름 없음")}</div>
                                <div class="item-owner">👤 원래 주인: {item.get("item_owner") or "알 수 없음"} | ⏳ {item.get("item_era", "")}</div>
                                <div class="item-story">"{item.get("story", "")}"</div>
                                <div class="student-name">✨ 큐레이터: {item.get("username", "익명")} 학생</div>
                            </div>
                        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🤖 AI 보조교사 호출
    # ---------------------------------------------------------
    activity_desc = (
        "이 화면은 가족의 옛 물건(애장품)을 출품하여 '우리 반 애장품 전시회'에 기록하는 곳입니다. "
        "'나의 애장품 출품하기' 탭에서 물건 이름과 가족에게 들은 사연을 적고 사진을 올립니다. "
        "저장 완료 후 '전시회 관람하기' 탭에서 친구들의 작품을 함께 볼 수 있습니다."
    )
    ai_teacher.show_ai_teacher(
        activity_name="활동 2-3. 우리 반 애장품 전시회",
        context_description=activity_desc,
    )
