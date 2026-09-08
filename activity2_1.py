import streamlit as st
import config
import re
import datetime
import requests
import xml.etree.ElementTree as ET
from pymongo import MongoClient
from PIL import Image

# 👇 AI 보조교사 · AI 모델 모듈 불러오기
import ai_teacher
import ai_model

ai_model.configure()


# ---------------------------------------------------------
# DB 연결
#  - 연결 실패를 캐시에 남기지 않도록 분리했습니다.
# ---------------------------------------------------------
@st.cache_resource
def _connect():
    c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
    c.admin.command("ping")
    return c


def get_collection():
    try:
        return _connect()["school_project"]["act2_1"]
    except Exception as e:
        print(f"[DB ERROR] activity2_1: {e}")
        return None


# ==========================================
# 🔍 기능 1: AI 유물 사진 분석기
# ==========================================
ANALYZE_PROMPT = """
너는 우리나라의 옛날 물건(전통 유물, 민속품 등)을 아주 잘 아는 친절한 초등학교 선생님이야.
학생이 사진을 하나 올렸어. 이 사진 속 물건이 무엇인지 분석해서,
초등학교 3학년 학생이 이해하기 쉽게 존댓말로 다음 양식에 맞춰서 설명해줘.
이모지도 듬뿍 넣어줘!

* **이름:** (물건의 이름)
* **용도:** (어디에 쓰던 물건인가요?)
* **특징:** (어떤 특징이 있나요? 2~3문장으로 재미있게)

[반드시 지켜야 할 규칙]
1. 초등학교 3학년이 아는 낱말만 써. 어려운 한자어는 쓰지 마.
2. 사진이 흐리거나 무엇인지 확실하지 않으면, 이름 칸에 "잘 모르겠어요"라고 솔직하게 쓰고
   왜 알기 어려운지 알려줘. 절대 지어내지 마.
3. 확실하지 않은 내용은 "~인 것 같아요"처럼 조심스럽게 말해줘.
4. 옛날 물건이 아니라 요즘 물건이면, 그렇다고 솔직하게 알려줘.
5. 전체 길이는 6문장을 넘기지 마.
"""


def analyze_artifact(image):
    return ai_model.ask([ANALYZE_PROMPT, image])


def extract_relic_name(analysis_text):
    """AI 분석 결과에서 물건 이름만 뽑아냅니다."""
    if not analysis_text:
        return ""
    m = re.search(r"\*\*이름:?\*\*\s*(.+)", analysis_text)
    if not m:
        m = re.search(r"이름\s*:\s*(.+)", analysis_text)
    if m:
        name = m.group(1).strip()
        name = re.sub(r"[*_#]", "", name).strip()
        return name[:40]
    return ""


# ==========================================
# 💡 기능 1-2: AI 유물 이름 설명기
# ==========================================
def generate_ai_desc(relic_name):
    prompt = f"""
너는 초등학교 3학년 선생님이야.
학생이 박물관에서 '{relic_name}'(이)라는 유물을 발견했는데 설명이 없어서 궁금해해.
이 유물이 주로 어떤 시대에 쓰였고, 어디에 쓰는 물건인지
초등학교 3학년이 이해하기 쉽게 3문장 정도로 친절하게 설명해줘. 이모지도 꼭 넣어줘.

[규칙]
- 확실하지 않으면 "정확한 것은 박물관 누리집에서 찾아보면 좋겠어요"라고 말해. 지어내지 마.
- 어려운 한자어는 쓰지 마.
"""
    return ai_model.ask(prompt)


# ==========================================
# 🏛️ 기능 2: 국립중앙박물관 유물 검색기
# ==========================================
def search_museum_relics(keyword):
    url = "http://www.emuseum.go.kr/openapi/relic/list"  # https는 지원 안 됨
    my_key = st.secrets["museum"]["api_key"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {
        "serviceKey": my_key,
        "pageNo": "1",
        "numOfRows": "5",
        "name": keyword,
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        root = ET.fromstring(response.content)

        err_msg = root.findtext(".//returnAuthMsg") or root.findtext(".//errMsg")
        if err_msg:
            print(f"[MUSEUM API] {err_msg}")
            return {"error": "박물관 창고 열쇠에 문제가 있어요. 선생님께 말씀드려 주세요."}

        result_code = root.findtext(".//resultCode")
        if result_code and result_code != "0000":
            print(f"[MUSEUM API] code={result_code}")
            return {"error": "박물관 서버가 지금 답을 주지 않아요. 잠시 후 다시 해볼까요?"}

        data_nodes = root.findall(".//data")
        results = []

        for data in data_nodes:
            relic_info = {"name": "이름 없음", "desc": "설명이 등록되지 않았습니다.", "img_uri": ""}
            for item in data.findall(".//item"):
                key = item.get("key")
                val = item.get("value")
                if key in ["nameKr", "nameKo", "name"] and val:
                    relic_info["name"] = val
                elif key in ["desc", "description"] and val:
                    relic_info["desc"] = val
                elif key in ["imgUri", "imgThumUriL", "imgThumUriM"] and val:
                    if not relic_info["img_uri"]:
                        relic_info["img_uri"] = val
            results.append(relic_info)

        if len(results) == 0:
            return {"empty": True}

        return results

    except requests.exceptions.RequestException as e:
        print(f"[MUSEUM API ERROR] {e}")
        return {"error": "박물관 서버가 지금 문을 닫았나 봐요. 잠시 후 다시 시도해 주세요!"}
    except Exception as e:
        print(f"[MUSEUM PARSE ERROR] {e}")
        return {"error": "박물관 자료를 정리하다가 문제가 생겼어요. 다시 검색해 볼까요?"}


# ==========================================
# 💻 화면 그리기 (show_page)
# ==========================================
def show_page():
    REGION = config.get_region()
    collection = get_collection()

    st.markdown("""
        <style>
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            border-radius: 50px !important;
            padding: 8px 30px !important;
            min-height: 45px !important;
            background-color: #ffffff !important;
            border: 2px solid #FF8080 !important;
            color: #FF8080 !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #FF8080 !important; color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title("🔍 옛 물건 살펴보기")
    current_student = st.session_state.get("username", "학생")

    # --- 1. AI 사진 분석기 ---
    st.markdown("### 📸 1. 내가 찾은 옛 물건 AI 분석하기")
    st.success("💡 박물관에서 본 유물이나 집에 있는 옛날 물건 사진을 올리면 AI 탐정이 분석해 줍니다.")

    uploaded_file = st.file_uploader(
        "옛 물건 사진 업로드", type=["png", "jpg", "jpeg"], key="u_file_2_1"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="내가 찾은 옛 물건", width=400)

        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = ""
            st.session_state.analyzed_file = ""

        if st.session_state.analyzed_file != uploaded_file.name:
            st.session_state.analysis_result = ""
            st.session_state.analyzed_file = uploaded_file.name

        if st.button("AI 유물 분석 시작 ✨", use_container_width=True):
            with st.spinner("AI 탐정이 유물을 꼼꼼히 관찰하고 있습니다... 🔎"):
                st.session_state.analysis_result = analyze_artifact(image)
                st.rerun()

        if st.session_state.analysis_result:
            st.info(st.session_state.analysis_result)
            st.caption("🤔 AI의 설명이 항상 맞는 것은 아니에요. 아래 박물관 검색기로 꼭 확인해 보세요!")
