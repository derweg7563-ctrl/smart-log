import streamlit as st
import base64
from pymongo import MongoClient
 
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])
 
try:
    client = init_connection()
    db = client["school_project"]
    col_1_1 = db["student_timeline"]          
    col_1_2 = db["school_footprints"]         
    col_2_1 = db["act2_1"]                    
    col_2_3 = db["exhibition_items"]          
    col_history = db["local_history"]         
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")
 
# 🎯 선생님이 '특정 학생(target_student)'의 이름을 넣어 호출할 수 있게 되었습니다!
def show_page(target_student=None):
    st.markdown("""
        <style>
        .dash-header { text-align: center; background-color: #E8F5E9; padding: 20px; border-radius: 20px; border: 3px solid #81C784; margin-bottom: 25px; }
        .dash-title { color: #2E7D32; font-size: 2rem; font-weight: 900; margin-bottom: 5px; }
        .dash-subtitle { color: #555; font-size: 1.1rem; font-weight: bold; }
        .score-card { text-align: center; background: linear-gradient(135deg, #FFF9C4, #FFECB3); padding: 20px; border-radius: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .score-text { font-size: 1.3rem; font-weight: 900; color: #F57F17; }
        .section-title { font-size: 1.5rem; font-weight: 900; color: #1565C0; margin-top: 40px; margin-bottom: 10px; border-bottom: 3px solid #BBDEFB; padding-bottom: 5px; }
        .section-title.sec2 { color: #2E7D32; border-bottom: 3px solid #C8E6C9; }
        .section-title.sec3 { color: #EF6C00; border-bottom: 3px solid #FFE0B2; }
        .record-card { background-color: #ffffff; padding: 15px; border-radius: 15px; border-left: 5px solid #64B5F6; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }
        .record-tag { display: inline-block; background-color: #E3F2FD; color: #1565C0; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 0.9rem; margin-bottom: 10px; }
        .record-title { font-size: 1.2rem; font-weight: 900; color: #333; margin-bottom: 5px; }
        .record-content { font-size: 1rem; color: #555; line-height: 1.5; }
        .timeline-container { display: flex; flex-direction: column; align-items: center; margin-top: 30px; width: fit-content; margin-left: auto; margin-right: auto; }
        .box { width: 180px; height: 100px; background-color: #FFFFFF; border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold; color: #444; box-shadow: 4px 4px 15px rgba(0,0,0,0.08); border: 5px solid #EEEEEE; text-align: center; line-height: 1.3; padding: 10px; margin: 0 auto 5px auto; }
        .box-1 { border-color: #FFB3BA !important; } .box-2 { border-color: #FFDFBA !important; } .box-3 { border-color: #FFFFBA !important; } .box-4 { border-color: #BAFFC9 !important; } .box-5 { border-color: #BAE1FF !important; } 
        .arrow { font-size: 2.2rem; color: #FF8080; font-weight: bold; text-align: center; margin-top: 35px; }
        .vertical-connector { display: flex; justify-content: flex-end; width: 100%; padding-right: 73px; margin: 30px 0; }
        .arrow-down { font-size: 2.5rem; color: #FF8080; font-weight: bold; width: 35px; text-align: center; }
        .memory-bubble { background-color: #f8f9fa; padding: 10px; border-radius: 10px; font-size: 0.9rem; color: #444; width: 180px; text-align: center; border: 2px dashed #ddd; word-break: keep-all; margin-top: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
        </style>
    """, unsafe_allow_html=True)
 
    current_student = target_student if target_student else st.session_state.get('username', '학생')
 
    st.markdown(f"""
        <div class="dash-header">
            <div class="dash-title">🎓 {current_student} 대원의 탐험 일지</div>
            <div class="dash-subtitle">지금까지 안성 탐험대에서 남긴 모든 발자국을 모아봤어요!</div>
        </div>
    """, unsafe_allow_html=True)
 
    if not db_connected:
        st.warning("⚠️ 데이터베이스에 연결할 수 없어 기록을 불러올 수 없습니다.")
        return
 
    # 🚀 [속도 개선 1] 점수 계산용: 무거운 데이터를 가져오지 않고 개수(count)만 빠르게 셉니다.
    count_1_1 = col_1_1.count_documents({"username": current_student})
    count_1_2 = col_1_2.count_documents({"username": current_student})
    count_2_1 = col_2_1.count_documents({"username": current_student})
    count_2_3 = col_2_3.count_documents({"username": current_student})
    count_3_1 = col_history.count_documents({"username": current_student, "type": "옛이야기"})
    count_3_2 = col_history.count_documents({"username": current_student, "type": "달라진모습"})
    count_3_3 = col_history.count_documents({"username": current_student, "type": "지역명유래"})
 
    rec_1_3_count = 0 if target_student else len(st.session_state.get('my_secret_timeline', []))
    total_records = count_1_1 + count_1_2 + rec_1_3_count + count_2_1 + count_2_3 + count_3_1 + count_3_2 + count_3_3
    
    if total_records >= 10:
        feedback = "🌟 완벽해요! 모든 탐험을 훌륭하게 마치고 꽉 찬 발자국을 남긴 최고의 탐험대원입니다!"
        progress_val = 100
    elif total_records >= 5:
        feedback = "🔥 대단해요! 탐험을 아주 성실하게 진행하고 있군요. 빈 탭을 찾아서 남은 미션도 수행해볼까요?"
        progress_val = min(total_records * 10, 90)
    elif total_records >= 1:
        feedback = "🌱 좋은 시작이에요! 이제 막 탐험의 재미를 알기 시작했군요. 다른 메뉴도 눌러서 미션을 수행해 보세요!"
        progress_val = 20
    else:
        feedback = "👀 아직 남겨진 발자국이 없어요. 첫 번째 탐험을 시작해 보세요!"
        progress_val = 0
 
    st.markdown(f"""
        <div class="score-card">
            <div style="font-size: 3rem; margin-bottom: 10px;">🏆</div>
            <div class="score-text">나의 탐험 성실도: 총 {total_records}개의 발자국 발견!</div>
            <div style="font-size: 1.1rem; color: #555; margin-top: 10px; font-weight: bold;">{feedback}</div>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progress_val)
 
    # 🚀 [속도 개선 2] 화면 표시용: 최신순(_id 내림차순)으로 딱 10개까지만 가져옵니다.
    rec_1_1 = list(col_1_1.find({"username": current_student}).sort("_id", -1).limit(20))
    rec_1_2 = list(col_1_2.find({"username": current_student}).sort("_id", -1).limit(10))
    rec_2_1 = list(col_2_1.find({"username": current_student}).sort("_id", -1).limit(10))
    rec_2_3 = list(col_2_3.find({"username": current_student}).sort("_id", -1).limit(10))
    rec_3_1 = list(col_history.find({"username": current_student, "type": "옛이야기"}).sort("_id", -1).limit(10))
    rec_3_2 = list(col_history.find({"username": current_student, "type": "달라진모습"}).sort("_id", -1).limit(10))
    rec_3_3 = list(col_history.find({"username": current_student, "type": "지역명유래"}).sort("_id", -1).limit(10))
 
    # =========================================================
    # 📘 [1단원] 어제와 오늘의 흐름 따라가기
    # =========================================================
    st.markdown('<div class="section-title">📘 1단계: 어제와 오늘의 흐름 따라가기</div>', unsafe_allow_html=True)
    tab1_1, tab1_2, tab1_3 = st.tabs(["👣 나의 발자국", "🏫 학교 발자국", "⏳ 발자국 연표"])
 
    with tab1_1:
        if count_1_1 == 0:
            st.info("아직 '나의 발자국 살펴보기' 활동을 기록하지 않았어요.")
        else:
            st.success("✨ 기록한 나의 5단계 성장 과정입니다!")
            st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
            
            # 최신 데이터를 우선 적용하기 위해 reversed() 사용
            saved_stages = {r["stage"]: r for r in reversed(rec_1_1)}
            
            def get_photo_box(stage_data, box_class, title_text):
                if not stage_data:
                    return f'''<div style="display: flex; flex-direction: column; align-items: center;"><div class="box {box_class}" style="color: #ccc;">기록 없음</div><div style="margin-top: 3px; font-weight: bold; text-align: center; line-height: 1.2;">{title_text}</div></div>'''
                img_base64 = stage_data.get("image_base64", "")
                content_text = stage_data.get("content", "")
                return f'''
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div class="box {box_class}" style="padding: 0; overflow: hidden; display: flex; justify-content: center; align-items: center; border-width: 5px;">
                        <img src="data:image/jpeg;base64,{img_base64}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 18px;">
                    </div>
                    <div style="margin-top: 5px; color: black; font-weight: bold; text-align: center; line-height: 1.2;">{title_text}</div>
                    <div class="memory-bubble">{content_text}</div>
                </div>
                '''
 
            c1, a1, c2, a2, c3 = st.columns([1, 0.2, 1, 0.2, 1])
            with c1: st.markdown(get_photo_box(saved_stages.get("1단계_태어났을때"), "box-1", "내가<br>태어났을 때"), unsafe_allow_html=True)
            with a1: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
            with c2: st.markdown(get_photo_box(saved_stages.get("2단계_어린이집유치원"), "box-2", "어린이집<br>유치원"), unsafe_allow_html=True)
            with a2: st.markdown('<div class="arrow">→</div>', unsafe_allow_html=True)
            with c3: st.markdown(get_photo_box(saved_stages.get("3단계_입학식"), "box-3", "초등학교<br>입학식"), unsafe_allow_html=True)
            st.markdown('<div class="vertical-connector"><div class="arrow-down">↓</div></div>', unsafe_allow_html=True)
            
            c_down, c5, a3, c4 = st.columns([1, 1, 0.2, 1])
            with c_down: st.write("") 
            with c4: st.markdown(get_photo_box(saved_stages.get("4단계_지금의나"), "box-4", "지금의 나"), unsafe_allow_html=True)
            with a3: st.markdown('<div class="arrow">←</div>', unsafe_allow_html=True)
            with c5: st.markdown(get_photo_box(saved_stages.get("5단계_미래의나"), "box-5", "1년 후의<br>내 모습"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
 
    with tab1_2:
        if count_1_2 == 0:
            st.info("아직 '학교 발자국 알아보기' 활동을 기록하지 않았어요.")
        else:
            for item in rec_1_2:
                with st.container():
                    st.markdown('<div class="record-card">', unsafe_allow_html=True)
                    st.markdown('<span class="record-tag">학교 발자국</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content">"{item.get("content", "")}"</div>', unsafe_allow_html=True)
                    if "image_base64" in item:
                        img_data = base64.b64decode(item["image_base64"])
                        st.image(img_data, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
 
    with tab1_3:
        if target_student:
            st.warning("🔒 1-3 발자국 연표는 학생 개인 컴퓨터에만 임시로 저장되는 '비밀 일기'이므로 선생님 화면에서는 보이지 않습니다.")
        else:
            my_timeline = st.session_state.get('my_secret_timeline', [])
            if len(my_timeline) == 0:
                st.info("아직 나만의 비밀 연표를 만들지 않았어요.")
            else:
                st.success("🔒 이 연표는 나에게만 보이는 비밀 연표입니다.")
                for item in my_timeline:
                    with st.container(border=True):
                        st.markdown(f'**{item["date"]} : {item["title"]}**')
                        st.write(item["desc"])
                        if item["image"] != "":
                            st.markdown(f'<img src="data:image/jpeg;base64,{item["image"]}" style="max-width: 100%; border-radius: 10px; margin-top: 10px;">', unsafe_allow_html=True)
 
    # =========================================================
    # 📗 [2단원] 디지털에서 만나는 옛 모습
    # =========================================================
    st.markdown('<div class="section-title sec2">📗 2단계: 디지털에서 만나는 옛 모습</div>', unsafe_allow_html=True)
    tab2_1, tab2_2, tab2_3 = st.tabs(["🏺 옛 물건 살펴보기", "🕵️‍♂️ AI 유물 탐정", "🖼️ 애장품 전시회"])
 
    with tab2_1:
        if count_2_1 == 0:
            st.info("아직 '옛 물건 살펴보기' 활동을 기록하지 않았어요.")
        else:
            # ✅ [수정된 부분] 기존에는 "기록이 있습니다."만 찍고 끝났는데,
            # AI 분석 내용 + 나의 생각(thought) + 사진을 실제로 보여주도록 변경했습니다.
            for item in rec_2_1:
                with st.container():
                    st.markdown('<div class="record-card">', unsafe_allow_html=True)
                    st.markdown('<span class="record-tag">옛 물건 살펴보기</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content"><b>🤖 AI 분석:</b><br>{item.get("content", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content" style="margin-top:10px;"><b>✍️ 나의 생각:</b> "{item.get("thought", "")}"</div>', unsafe_allow_html=True)
                    if "image_base64" in item and item["image_base64"]:
                        img_data = base64.b64decode(item["image_base64"])
                        st.image(img_data, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
 
    with tab2_2:
        st.info("💡 AI 유물 탐정님과의 즐거운 대화는 탐험대원님의 마음속 지식으로 단단하게 저장되었어요!")
 
    with tab2_3:
        if count_2_3 == 0:
            st.info("아직 '우리 반 애장품 전시회'에 출품한 물건이 없어요.")
        else:
            for item in rec_2_3:
                with st.container():
                    st.markdown('<div class="record-card">', unsafe_allow_html=True)
                    st.markdown('<span class="record-tag" style="background-color:#E8F5E9; color:#2E7D32;">애장품 전시</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-title">📦 {item.get("item_name", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content" style="margin-bottom:10px;">👤 주인: {item.get("item_owner", "")} | ⏳ {item.get("item_era", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content">"{item.get("story", "")}"</div>', unsafe_allow_html=True)
                    if "image_base64" in item:
                        img_data = base64.b64decode(item["image_base64"])
                        st.image(img_data, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
 
    # =========================================================
    # 📙 [3단원] 세대공감, 달라진 모습
    # =========================================================
    st.markdown('<div class="section-title sec3">📙 3단계: 세대공감, 달라진 모습</div>', unsafe_allow_html=True)
    tab3_1, tab3_2, tab3_3 = st.tabs(["📖 옛이야기 탐험", "🔄 달라진 모습", "🏷️ 땅 이름 비밀"])
 
    with tab3_1:
        if count_3_1 == 0:
            st.info("아직 '안성의 옛이야기 탐험' 활동을 기록하지 않았어요.")
        else:
            for item in rec_3_1:
                with st.container():
                    st.markdown('<div class="record-card">', unsafe_allow_html=True)
                    st.markdown('<span class="record-tag" style="background-color:#FFF3E0; color:#E65100;">옛이야기</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-title">📖 {item.get("title", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content">{item.get("content", "")}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
 
    with tab3_2:
        if count_3_2 == 0:
            st.info("아직 '안성의 달라진 모습' 활동을 기록하지 않았어요.")
        else:
            for item in rec_3_2:
                with st.container():
                    st.markdown('<div class="record-card">', unsafe_allow_html=True)
                    st.markdown('<span class="record-tag" style="background-color:#FFF3E0; color:#E65100;">달라진 모습</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content"><b>⏳ 과거:</b> {item.get("past", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content"><b>🏙️ 현재:</b> {item.get("present", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content" style="margin-top:10px;"><b>🤔 달라진 이유:</b> {item.get("reason", "")}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
 
    with tab3_3:
        if count_3_3 == 0:
            st.info("아직 '안성의 땅 이름 비밀 찾기' 활동을 기록하지 않았어요.")
        else:
            for item in rec_3_3:
                with st.container():
                    st.markdown('<div class="record-card">', unsafe_allow_html=True)
                    st.markdown('<span class="record-tag" style="background-color:#FFF3E0; color:#E65100;">지역명 유래</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-title">🏷️ {item.get("place_name", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="record-content">{item.get("origin", "")}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
