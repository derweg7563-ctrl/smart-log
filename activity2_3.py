import streamlit as st
import base64
import datetime
from pymongo import MongoClient

# 👇 1. AI 보조교사 모듈 불러오기
import ai_teacher

# ---------------------------------------------------------
# 🛠️ 1. MongoDB 연결 설정 (전시회 전용 보관함)
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]
    collection = db["exhibition_items"] # 애장품 저장 컬렉션
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

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

    current_student = st.session_state.get('username', '학생')

    # ==========================================
    # [탭 1] 나의 애장품 출품하기 (초기화 기능 추가)
    # ==========================================
    with tab1:
        st.subheader("나만의 큐레이터 노트 작성하기 ✍️")
        
        # 💡 [핵심] st.form을 사용하여 묶어줍니다. clear_on_submit=True가 제출 후 창을 비워줍니다!
        with st.form("curator_form", clear_on_submit=True):
            item_name = st.text_input("1. 옛 물건(애장품)의 이름은 무엇인가요?", placeholder="예: 할머니의 낡은 재봉틀, 옛날 동전, 닳은 옥반지 등")
            
            col1, col2 = st.columns(2)
            with col1:
                item_owner = st.text_input("2. 이 물건의 원래 주인은 누구셨나요?", placeholder="예: 우리 할아버지, 증조할머니")
            with col2:
                item_era = st.text_input("3. 언제쯤 쓰던 물건인가요?", placeholder="예: 1970년대, 약 50년 전")
                
            item_story = st.text_area("4. 가족에게 들은 이 물건의 사연(증언)을 자세히 적어주세요.", 
                                      placeholder="할머니께서 젊은 시절 우리 아빠의 옷을 직접 지어주실 때 쓰던 재봉틀이라고 합니다...", height=150)
            
            uploaded_file = st.file_uploader("5. 애장품의 멋진 사진을 올려주세요!", type=["png", "jpg", "jpeg"])

            # 💡 기존 st.button 대신 st.form_submit_button을 사용해야 폼이 작동합니다.
            submitted = st.form_submit_button("🚀 우리 반 전시회에 출품하기", use_container_width=True)

            if submitted:
                if item_name and item_story and uploaded_file:
                    if db_connected:
                        # 이미지 인코딩
                        encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                        
                        # DB에 저장할 데이터 구성
                        record = {
                            "username": current_student,
                            "item_name": item_name,
                            "item_owner": item_owner,
                            "item_era": item_era,
                            "story": item_story,
                            "image_base64": encoded_image,
                            "timestamp": datetime.datetime.now()
                        }
                        
                        # DB에 데이터 삽입
                        collection.insert_one(record)
                        
                        st.success("🎉 성공적으로 전시회에 출품되었습니다! 작성하신 내용이 초기화되었으니 새로운 물건을 계속 추가할 수 있어요. (결과는 [전시회 관람하기] 탭에서 확인하세요)")
                        st.balloons()
                    else:
                        st.error("DB가 연결되지 않았습니다.")
                else:
                    st.warning("⚠️ 사진을 올리고 빈칸(이름, 사연)을 모두 채워주세요!")

    # ==========================================
    # [탭 2] 전시회 관람하기
    # ==========================================
    with tab2:
        st.subheader("🏛️ 온라인 애장품 갤러리")
        st.write("친구들이 가족에게 직접 듣고 찾아온 소중한 옛 물건들을 감상해 봅시다.")
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        if db_connected:
            # 최신순으로 모든 전시품 불러오기
            items = list(collection.find().sort("timestamp", -1))
            
            if len(items) == 0:
                st.info("아직 전시된 애장품이 없습니다. 첫 번째 큐레이터가 되어주세요!")
            else:
                # 3열(바둑판) 형태로 예쁘게 전시
                cols = st.columns(3)
                for idx, item in enumerate(items):
                    col = cols[idx % 3] 
                    
                    with col:
                        # 🖼️ 이미지가 있으면 표시
                        if "image_base64" in item:
                            img_data = base64.b64decode(item["image_base64"])
                            st.image(img_data, use_container_width=True)
                        
                        # 📝 전시 캡션 카드 디자인 적용
                        st.markdown(f"""
                            <div class="exhibition-card">
                                <div class="item-title">{item.get("item_name", "이름 없음")}</div>
                                <div class="item-owner">👤 원래 주인: {item.get("item_owner", "알 수 없음")} | ⏳ {item.get("item_era", "")}</div>
                                <div class="item-story">"{item.get("story", "")}"</div>
                                <div class="student-name">✨ 큐레이터: {item.get("username", "익명")} 학생</div>
                            </div>
                        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🤖 2. AI 보조교사 호출 (파일 맨 아래)
    # ---------------------------------------------------------
    activity_desc = "이 화면은 가족의 옛 물건(애장품)을 출품하여 '우리 반 애장품 전시회'에 기록하는 곳입니다. '나의 애장품 출품하기' 탭에서 사진과 사연을 적어야 하며, 저장 완료 후 '전시회 관람하기' 탭에서 확인해 보세요."
    ai_teacher.show_ai_teacher(activity_name="활동 2-3. 우리 반 애장품 전시회", context_description=activity_desc)