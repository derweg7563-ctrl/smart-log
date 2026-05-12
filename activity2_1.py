import streamlit as st
import datetime
import base64
import requests
import xml.etree.ElementTree as ET
from pymongo import MongoClient
from PIL import Image
import io

# 👇 1. AI 보조교사 모듈 불러오기
import ai_teacher

# 구글 생성형 AI 패키지
try:
    import google.generativeai as genai
except ImportError:
    st.error("🚨 `google-generativeai` 패키지가 필요합니다.")

# DB 연결
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]
    collection = db["act2_1"] 
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

# 구글 AI 설정
try:
    genai.configure(api_key=st.secrets["google"]["api_key"])
except Exception as e:
    st.error("🚨 secrets.toml 파일에 구글 열쇠가 없습니다!")

# ==========================================
# 🔍 기능 1: AI 유물 사진 분석기
# ==========================================
def analyze_artifact(image):
    try:
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(valid_models[0])
        prompt = """
        너는 우리나라의 옛날 물건(전통 유물, 민속품 등)을 아주 잘 아는 친절한 초등학교 선생님이야. 
        학생이 사진을 하나 올렸어. 이 사진 속 물건이 무엇인지 분석해서, 
        초등학교 3학년 학생이 이해하기 쉽게 존댓말로 다음 양식에 맞춰서 설명해줘.
        이모지도 듬뿍 넣어줘!

        * **이름:** (물건의 이름)
        * **용도:** (어디에 쓰던 물건인가요?)
        * **특징:** (어떤 특징이 있나요? 2~3문장으로 재미있게)
        """
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"앗! AI 분석 중 에러가 났어요. (오류: {e})"

# ==========================================
# 💡 기능 1-2: AI 유물 이름 설명기
# ==========================================
def generate_ai_desc(relic_name):
    try:
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(valid_models[0])
        prompt = f"너는 초등학교 3학년 선생님이야. 학생이 박물관에서 '{relic_name}'(이)라는 유물을 발견했는데 설명이 없어서 궁금해해. 이 유물이 주로 어떤 시대에 쓰였고, 어디에 쓰는 물건인지 초등학교 3학년이 이해하기 쉽게 3문장 정도로 친절하게 설명해줘. 이모지도 꼭 넣어줘."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "앗! AI 선생님이 잠시 자리를 비웠어요."

# ==========================================
# 🏛️ 기능 2: 국립중앙박물관 유물 검색기
# ==========================================
def search_museum_relics(keyword):
    url = 'http://www.emuseum.go.kr/openapi/relic/list' 
    my_key = st.secrets["museum"]["api_key"]
    
    params = {
        'serviceKey': my_key,
        'pageNo': '1',
        'numOfRows': '5',
        'name': keyword   
    }
    
    try:
        response = requests.get(url, params=params)
        root = ET.fromstring(response.content)
        
        err_msg = root.findtext('.//returnAuthMsg') or root.findtext('.//errMsg')
        if err_msg:
            return {"error": err_msg, "raw": response.text}
            
        result_code = root.findtext('.//resultCode')
        if result_code and result_code != '0000':
            return {"error": f"API 에러코드 {result_code}", "raw": response.text}

        data_nodes = root.findall('.//data')
        results = []
        
        for data in data_nodes:
            relic_info = {"name": "이름 없음", "desc": "설명이 등록되지 않았습니다.", "img_uri": ""}
            for item in data.findall('.//item'):
                key = item.get('key')
                val = item.get('value')
                if key in ['nameKr', 'nameKo', 'name'] and val:
                    relic_info["name"] = val
                elif key in ['desc', 'description'] and val:
                    relic_info["desc"] = val
                elif key in ['imgUri', 'imgThumUriL', 'imgThumUriM'] and val:
                    if not relic_info["img_uri"]: 
                        relic_info["img_uri"] = val
            results.append(relic_info)
            
        if len(results) == 0:
            return {"empty": True, "raw": response.text}
            
        return results
    except Exception as e:
        return {"error": str(e), "raw": "알 수 없는 에러 발생"}

# ==========================================
# 💻 화면 그리기 (show_page)
# ==========================================
def show_page():
    st.title("🔍 옛 물건 살펴보기")
    current_student = st.session_state.get('username', '학생')

    # --- 탭 1: AI 사진 분석기 ---
    st.markdown("### 📸 1. 내가 찾은 옛 물건 AI 분석하기")
    st.success("💡 박물관에서 본 유물이나 집에 있는 옛날 물건 사진을 올리면 AI 탐정이 분석해 줍니다.")

    uploaded_file = st.file_uploader("옛 물건 사진 업로드", type=['png', 'jpg', 'jpeg'], key="u_file_2_1")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='내가 찾은 옛 물건', width=400)
        
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = ""
            st.session_state.analyzed_file = ""

        if st.session_state.analyzed_file != uploaded_file.name:
            st.session_state.analysis_result = ""
            st.session_state.analyzed_file = uploaded_file.name

        if st.button("AI 유물 분석 시작 ✨", use_container_width=True):
            with st.spinner('AI 탐정이 유물을 꼼꼼히 관찰하고 있습니다... 🔎'):
                st.session_state.analysis_result = analyze_artifact(image)
                st.rerun()

        if st.session_state.analysis_result:
            st.info(st.session_state.analysis_result)
            
            with st.form("save_act2_1", clear_on_submit=True):
                st.write("✍️ **AI의 설명을 읽고, 나의 생각을 적어보세요!**")
                student_thought = st.text_area("나의 생각 적기", placeholder="예: 맷돌의 손잡이 이름이 어처구니라니 신기하다!")
                
                if st.form_submit_button("내 발자국(대시보드)에 저장하기 🚀", use_container_width=True):
                    if student_thought and db_connected:
                        encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                        record = {
                            "username": current_student,
                            "content": st.session_state.analysis_result,
                            "thought": student_thought,
                            "image_base64": encoded_image,
                            "timestamp": datetime.datetime.now()
                        }
                        collection.insert_one(record)
                        st.success("🎉 기록이 내 대시보드에 멋지게 저장되었어요!")
                        st.balloons()
                    else:
                        st.warning("⚠️ 나의 생각을 한 줄이라도 적어주세요!")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")

    # --- 탭 2: 국립중앙박물관 공공데이터 검색기 ---
    st.markdown("### 🏛️ 2. 국립중앙박물관 공식 유물 검색기")
    st.info("실제 박물관에는 어떤 유물들이 있을까요? 궁금한 유물 이름(예: 맷돌, 백자)이나 지역(예: 평택, 안성)을 검색해 보세요!")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_keyword = st.text_input("🔍 유물 검색어 입력", placeholder="예: 평택, 맷돌, 갓")
    with col_s2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_btn = st.button("박물관 창고 열기 🚀", use_container_width=True)

    # 💡 [핵심] 검색 버튼을 누르면 결과를 '기억 상자'에 저장합니다!
    if search_btn and search_keyword:
        with st.spinner('국립중앙박물관 서버에서 자료를 가져오고 있습니다... 🏃‍♂️'):
            st.session_state.museum_results = search_museum_relics(search_keyword)
            # 새로운 검색을 하면 예전 AI 설명 기억도 깔끔하게 지웁니다.
            if "ai_explanations" in st.session_state:
                del st.session_state["ai_explanations"]

    # 💡 [핵심] 기억 상자에 결과가 남아있다면 화면이 지워지지 않고 계속 그려집니다!
    if "museum_results" in st.session_state and st.session_state.museum_results:
        museum_results = st.session_state.museum_results
        
        # AI 설명을 저장할 특별한 기억 상자 준비
        if "ai_explanations" not in st.session_state:
            st.session_state.ai_explanations = {}
            
        if type(museum_results) is dict and "error" in museum_results:
            st.error("🚨 박물관 서버가 선생님의 열쇠를 거절했습니다!")
            st.warning(f"**거절 사유:** {museum_results['error']}")
        elif type(museum_results) is dict and "empty" in museum_results:
            st.warning(f"'{search_keyword}'에 대한 박물관 검색 결과가 없습니다.")
        else:
            st.success(f"🎉 총 {len(museum_results)}개의 유물을 박물관에서 찾아왔습니다!")
            
            for idx, item in enumerate(museum_results):
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        if item["img_uri"]:
                            st.image(item["img_uri"], use_container_width=True)
                        else:
                            st.write("📷 사진 없음")
                    with col_txt:
                        st.markdown(f"**🏷️ 유물명:** {item['name']}")
                        
                        if item['desc'] == "설명이 등록되지 않았습니다.":
                            # 💡 이미 기억 상자에 이 유물에 대한 AI 설명이 있다면 바로 보여주기!
                            if idx in st.session_state.ai_explanations:
                                st.info(f"**🤖 AI 선생님:**\n\n{st.session_state.ai_explanations[idx]}")
                            else:
                                st.markdown("📖 **설명:** 박물관 공식 설명이 없습니다.")
                                if st.button(f"🤖 AI 선생님, 이게 뭐예요?", key=f"ai_btn_{idx}"):
                                    with st.spinner('AI가 똑똑한 설명을 뚝딱뚝딱 만들고 있어요... 🪄'):
                                        # 설명을 만들어서 기억 상자에 쏙 넣고 화면을 새로고침합니다!
                                        ai_explanation = generate_ai_desc(item['name'])
                                        st.session_state.ai_explanations[idx] = ai_explanation
                                        st.rerun()
                        else:
                            st.markdown(f"**📖 설명:** {item['desc']}")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # 🤖 3. AI 보조교사 호출 (파일 맨 아래)
    # ---------------------------------------------------------
    activity_desc = "이 화면은 옛 물건 사진을 올려 구글 AI의 분석을 받고, 박물관 API를 검색하는 페이지입니다. 박물관 설명이 없을 경우 AI에게 직접 설명을 요청할 수 있습니다."
    ai_teacher.show_ai_teacher(activity_name="활동 2-1. 옛 물건 살펴보기", context_description=activity_desc)