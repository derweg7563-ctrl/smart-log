import streamlit as st
from pymongo import MongoClient

DEFAULTS = {
    "region": "우리 고장",
    "archive_name": "우리 고장 기록관",
    "archive_url": "",
    "map_lat": "",
    "map_lng": "",
}


@st.cache_resource
def _connect_db():
    c = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
    c.admin.command("ping")
    return c


def _get_db():
    try:
        return _connect_db()["school_project"]
    except Exception as e:
        print(f"[DB ERROR] config: {e}")
        return None

@st.cache_data(ttl=30)
def _load_settings():
    """설정값을 한 번에 읽어 30초간 재사용합니다. (매번 DB를 두드리지 않도록)"""
    values = {}
    db = _get_db()
    if db is not None:
        try:
            for doc in db["settings"].find({}):
                if doc.get("value"):
                    values[doc["key"]] = doc["value"]
        except Exception as e:
            print(f"[SETTING READ ERROR] {e}")
    return values


def get_setting(key, default=None):
    """설정값 하나를 가져옵니다. DB → secrets → 기본값 순서로 찾습니다."""
    if default is None:
        default = DEFAULTS.get(key, "")
    db_values = _load_settings()
    if db_values.get(key):
        return db_values[key]
    secret_val = st.secrets.get("app", {}).get(key, "")
    if secret_val:
        return secret_val
    return default


def save_setting(key, value):
    """교사 대시보드에서 설정을 저장할 때 씁니다."""
    db = _get_db()
    if db is None:
        return False
    try:
        value = (value or "").strip()
        db["settings"].update_one({"key": key}, {"$set": {"value": value}}, upsert=True)
        _load_settings.clear()          # 캐시를 비워 바로 반영되게 합니다.
        return True
    except Exception as e:
        print(f"[SETTING SAVE ERROR] {e}")
        return False


def get_region():
    return get_setting("region")


def get_archive_name():
    return get_setting("archive_name")


def get_archive_url():
    return get_setting("archive_url")
