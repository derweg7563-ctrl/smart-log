"""
AI 모델 설정 공통 모듈
- 모델 이름이 바뀌면 이 파일의 MODEL_CANDIDATES만 수정하면 됩니다.
- 앞의 모델부터 시도하고, 사용할 수 없으면 다음 모델로 넘어갑니다.
"""

import streamlit as st
import google.generativeai as genai

MODEL_CANDIDATES = [
    "gemini-3.1-flash-lite",    # 1순위: 정식 버전, 저렴·빠름, 이미지 입력 지원
    "gemini-3-flash-preview",   # 2순위: 폴백 (현재 동작이 확인된 모델)
]

# 학생에게 보여줄 안내 문구 (에러 원문은 절대 노출하지 않음)
FRIENDLY_ERROR = "앗! 선생님이 잠깐 자리를 비웠어요. 잠시 뒤에 다시 물어봐 줄래요? 🙂"


def configure():
    """API 키 설정. 앱 시작 시 한 번만 호출하면 됩니다."""
    try:
        genai.configure(api_key=st.secrets["google"]["api_key"])
        return True
    except Exception as e:
        print(f"[CONFIG ERROR] {e}")
        return False


@st.cache_resource
def get_model():
    """
    사용 가능한 첫 번째 모델을 반환합니다.
    모두 실패하면 None을 반환합니다.
    """
    for name in MODEL_CANDIDATES:
        try:
            m = genai.GenerativeModel(name)
            m.generate_content("안녕")      # 실제 호출로 사용 가능 여부 확인
            print(f"[MODEL OK] {name}")
            return m
        except Exception as e:
            print(f"[MODEL SKIP] {name}: {e}")
            continue
    print("[MODEL ERROR] 사용 가능한 모델이 없습니다.")
    return None


def ask(prompt_parts):
    """
    모델에게 질문하고 텍스트 답변을 돌려줍니다.
    prompt_parts: 문자열 또는 [문자열, 이미지] 형태의 리스트
    실패하면 학생용 안내 문구를 반환합니다.
    """
    model = get_model()
    if model is None:
        return FRIENDLY_ERROR
    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return FRIENDLY_ERROR