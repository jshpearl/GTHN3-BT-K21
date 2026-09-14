import streamlit as st
import requests
import json
import os

# ==========================================================
# 1. CẤU HÌNH TRANG WEB & CSS CUSTOMIZATION
# ==========================================================
st.set_page_config(
    page_title="BÀI TẬP HÁN NGỮ 3 - BÀI 39",
    page_icon="📚",
    layout="wide"
)

# Custom CSS Tông Pastel dịu nhẹ & ép kiểu chữ rõ nét
st.markdown("""
<style>
    .main {
        background-color: #F8F9FA;
    }
    h1 {
        color: #2C3E50;
        text-align: center;
        font-weight: 700;
        padding-bottom: 10px;
    }
    h2, h3, h4 {
        color: #34495E;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .footer-teacher {
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        color: #8E44AD;
        margin-top: 50px;
        padding: 20px;
        border-top: 2px dashed #BDC3C7;
    }
</style>
""", unsafe_allow_html=True)

# Webhook URL Google Sheets (Thay link App Script của bạn vào đây)
GSHEET_URL = st.secrets.get("GOOGLE_SHEET_WEBHOOK", "https://script.google.com/macros/s/AKfycbyZ_pORxb7Hx8cKC-Zi9ARNeTfpE2Bw7bEjWmTK7gBnjbSHmUBJbEWxVUm8DD8cQkJ6/exec")

def send_results_to_gsheet(student_name, lesson_title, section_name, score_str):
    if not GSHEET_URL:
        st.info("💡 Điểm số đã được tính! (Vui lòng cấu hình link Google App Script để tự động gửi điểm về Sheet).")
        return
    
    payload = {
        "name": student_name,
        "student_name": student_name,
        "lesson": lesson_title,
        "section": section_name,
        "score": score_str
    }
    try:
        requests.post(GSHEET_URL, json=payload, timeout=5)
        st.success(f"✅ Đã gửi kết quả {section_name} ({score_str}) về Google Sheet thành công!")
    except Exception as e:
        st.warning(f"⚠️ Chưa gửi được kết quả về Google Sheet: {str(e)}")

# Hàm tìm kiếm file audio tải lên trực tiếp (cùng vị trí với ảnh & app.py)
def find_audio_file(filename_patt):
    patterns = [filename_patt, f"03-{filename_patt.split('-')[-1]}", f"39-{filename_patt.split('-')[-1]}"]
    # Tìm trực tiếp tại thư mục gốc ("") trước, sau đó mới tìm các thư mục con
    for folder in ["", "audio", "Audio", "assets", "sound", "sounds"]:
        for ext in [".mp3", ".MP3", ".wav", ".WAV", ".m4a"]:
            for patt in patterns:
                p = os.path.join(folder, patt + ext) if folder else patt + ext
                if os.path.exists(p):
                    return p
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".venv", "__pycache__", ".streamlit"]):
            continue
        for f in files:
            name, ext = os.path.splitext(f)
            for patt in patterns:
                if patt.lower() in f.lower() and ext.lower() in [".mp3", ".wav", ".m4a"]:
                    return os.path.join(root, f)
    return None

def play_audio(filename_patt):
    found_path = find_audio_file(filename_patt)
    if found_path:
        try:
            with open(found_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        except Exception as e:
            st.error(f"⚠️ Lỗi phát âm thanh '{found_path}': {str(e)}")
    else:
        st.warning(f"🎧 Trình phát audio: Chưa tìm thấy tệp âm thanh '{filename_patt}.mp3' (ví dụ: 03-1.mp3) tải lên trực tiếp cùng thư mục với ảnh.")

# Tìm hình ảnh ghép câu 1-5 phần nghe (nằm trực tiếp ở thư mục gốc)
def display_listening_image():
    for img_name in ["image-03", "image-03.png", "image-03.jpg", "image-39", "image-39.png", "image-39.jpg"]:
        for folder in ["", "images", "img", "assets"]:
            p = os.path.join(folder, img_name) if folder else img_name
            if os.path.exists(p):
                st.image(p, caption="Hình ảnh Lựa chọn Phần 1 (A-F)", use_container_width=True)
                return
    st.info("💡 [Gợi ý]: Tải ảnh minh họa Phần 1 đặt tên là 'image-03.png' trực tiếp vào cùng thư mục với app.py.")

# ==========================================================
# 2. DỮ LIỆU CÂU HỎI BÀI 39
# ==========================================================
LESSON_39_DATA = {
    'title': '第39课：冬天快要到了 / BÀI 39: MÙA ĐÔNG SẮP ĐẾN RỒI',
    'listening': {
        'part1': [
            {'id': 1, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F', 'script': '女：这是哪儿啊？你开错了吧？我们怎么回家啊？\n男：别着急，车上有电子地图。'},
            {'id': 2, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B', 'script': '男：今天这么热，你怎么骑自行车去了？\n女：我每天都骑车，而且，我就喜欢这样的大晴天。'},
            {'id': 3, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A', 'script': '女：快来吃水果。\n男：我刚才吃了几块西瓜，现在不想吃了。'},
            {'id': 4, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'E', 'script': '男：告诉我你想看什么节目。\n女：没什么好看的，我还是读我的书吧。'},
            {'id': 5, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C', 'script': '女：你都睡了十几点/个钟头了，快要迟到了！\n男：我想多睡会儿，太累了。'}
        ],
        'part2': [
            {'id': 6, 'text': '6. ★ 他看比赛看到很晚。', 'correct': '✔', 'script': '为看足球比赛，我一直到今天早上三点多才睡，起床后头非常地疼。'},
            {'id': 7, 'text': '7. ★ 那天麦克表坏了。', 'correct': '✘', 'script': '我们班的麦克上课总迟到，有一天他早来了二十分钟，后来一问才知道，是他看错表了。'},
            {'id': 8, 'text': '8. ★ 北京的冬天很安静。', 'correct': '✘', 'script': '北京的秋天不冷也不热，是一年中最好的季节。这时候去北京旅游的人是最多的。'},
            {'id': 9, 'text': '9. ★ 田芳和玛丽住在同一个宿舍。', 'correct': '✔', 'script': '我去找田芳时，她不在，她的同屋玛丽告诉我，田芳去图书馆了。'},
            {'id': 10, 'text': '10. ★ 今天天气很冷。', 'correct': '✔', 'script': '今天是阴天，外面很冷，希望别刮风。你多拿件衣服，看完电影早点儿回来。'}
        ],
        'part3': [
            {'id': 11, 'text': '11. 小王怎么了？', 'options': ['A. 要结婚了', 'B. 要毕业了', 'C. 要出国了'], 'correct': 'A', 'script': '男：听说了吗？咱们公司的小王下个月就要结婚了。\n女：是吗？他毕业才半年呀。\n问：小王怎么了？'},
            {'id': 12, 'text': '12. 女的去北京做什么？', 'options': ['A. 旅游', 'B. 买东西', 'C. 看表演'], 'correct': 'A', 'script': '男：最近一直没看到你，你去哪儿了？\n女：我去北京旅游了，昨天中午才回来。\n问：女的去北京做什么？'},
            {'id': 13, 'text': '13. 女的对什么没有兴趣？', 'options': ['A. 看电视', 'B. 运动', 'C. 周末'], 'correct': 'B', 'script': '男：你周末喜欢做什么？\n女：我不爱运动，周末就在家看看电视。\n问：女的对什么没有兴趣？'},
            {'id': 14, 'text': '14. 女的是什么意思？', 'options': ['A. 买两个', 'B. 买三个', 'C. 少买一点儿'], 'correct': 'C', 'script': '男：前边有卖水果的，我们买点儿苹果吧？\n女：现在是换季的时候，苹果不一定好吃，别买太多，买两三个就行。\n问：女的是什么意思？'},
            {'id': 15, 'text': '15. 女的为什么喜欢秋天？', 'options': ['A. 天气舒服', 'B. 特别漂亮', 'C. 水果很多'], 'correct': 'C', 'script': '男：我最喜欢秋天了，天气不冷也不热，很舒服。\n女：我喜欢秋天是因为能吃到很多种水果。\n问：女的为什么喜欢秋天？'}
        ],
        'part4': [
            {'id': 16, 'text': '16. 男的想看什么节目？', 'options': ['A. 音乐', 'B. 体育', 'C. 电视剧'], 'correct': 'B', 'script': '女：明天休息，今晚想看什么节目啊？\n男：今晚有足球，现在八点了吗？\n女：现在才七点一刻，还有四十五分钟呢。\n男：不会吧？你的手表慢了吧？\n问：男的想看什么节目？'},
            {'id': 17, 'text': '17. 关于女的，可以知道什么？', 'options': ['A. 正在复习', 'B. 明天没课', 'C. 打算明天还书'], 'correct': 'C', 'script': '男：小王，那两本书怎么样？\n女：很好看。我还在看，明天还你可以吗？\n男：不着急。我是说，我这儿还有几本，想看就找我。\n女：好的。再见，明天见。\n问：关于女的，可以知道什么？'},
            {'id': 18, 'text': '18. 他们最可能几点见面？', 'options': ['A. 19:00', 'B. 20:15', 'C. 21:30'], 'correct': 'B', 'script': '女：我们晚上去唱歌，你和小张也来吧？\n男：我先问问她，然后再告诉你。你们打算去哪儿唱？\n女：就在公司附近。我们八点一刻在公司门口见。\n男：好的，我知道了。\n问：他们最可能几点见面？'},
            {'id': 19, 'text': '19. 关于女的，可以知道什么？', 'options': ['A. 还没回家', 'B. 不着急', 'C. 很着急'], 'correct': 'C', 'script': '女：你怎么还不吃饭？\n男：东东还没回来呢。\n男：你别着急，吃饭吧。\n女：都这么晚了，我能不着急吗？\n问：关于女的，可以知道什么？'},
            {'id': 20, 'text': '20. 他们最可能在哪儿？', 'options': ['A. 商店', 'B. 饭店', 'C. 银行'], 'correct': 'A', 'script': '女：还需要别的水果吗？\n男：不用了，就这些香蕉。多少钱？\n女：十三元五角。\n男：给你钱。\n女：好的，欢迎您下次再来，再见。\n问：他们最可能在哪儿？'}
        ]
    },
    'reading': {
        'part1': [
            {'id': 21, 'text': '21. 休息一会儿吧，听听音乐。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C'},
            {'id': 22, 'text': '22. 是的，特别是足球比赛，她喜欢踢足球。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F'},
            {'id': 23, 'text': '23. 我刚才洗澡去了，有事吗？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B'},
            {'id': 24, 'text': '24. 早点儿休息吧，都10点半了。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A'},
            {'id': 25, 'text': '25. 什么时候去那个城市旅游比较好？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'D'}
        ],
        'part2': [
            {'id': 26, 'text': '26. 小丽，快点儿！（   ）我们班拍照了。', 'options': ['A. 晴', 'B. 该', 'C. 愿意', 'D. 旅游', 'E. 声音', 'F. 滑冰'], 'correct': 'B'},
            {'id': 27, 'text': '27. 我的爱好很多，比如游泳、（   ）、画画儿和跳舞。', 'options': ['A. 晴', 'B. 该', 'C. 愿意', 'D. 旅游', 'E. 声音', 'F. 滑冰'], 'correct': 'F'},
            {'id': 28, 'text': '28. 明天天气和今天一样，也是（   ）天，我们去爬山吧。', 'options': ['A. 晴', 'B. 该', 'C. 愿意', 'D. 旅游', 'E. 声音', 'F. 滑冰'], 'correct': 'A'},
            {'id': 29, 'text': '29. A：最近怎么一直没看见他？\n    B：他去（   ）了，可能这个周末才能回来。', 'options': ['A. 晴', 'B. 该', 'C. 愿意', 'D. 旅游', 'E. 声音', 'F. 滑冰'], 'correct': 'D'},
            {'id': 30, 'text': '30. A：我想问问你，你（   ）跟我结婚吗？\n    B：当然，我等这句话已经等了一年了。', 'options': ['A. 晴', 'B. 该', 'C. 愿意', 'D. 旅游', 'E. 声音', 'F. 滑冰'], 'correct': 'C'}
        ],
        'part3': [
            {'id': 31, 'text': '31. 我们8点10分在火车站见，不是在汽车站，别迟到。\n★ 他们在哪儿见面？', 'options': ['A. 汽车站', 'B. 火车站', 'C. 机场'], 'correct': 'B'},
            {'id': 32, 'text': '32. 田芳对中国的历史和文化感兴趣，我只对汉语感兴趣。\n★ 他对什么感兴趣？', 'options': ['A. 汉语', 'B. 中国历史', 'C. 中国文化'], 'correct': 'A'},
            {'id': 33, 'text': '33. 那儿的冬天特别冷，但是下雪的时候，孩子们还是会高兴地跑出去，在雪地里玩儿。\n★ 下雪的时候，孩子们：', 'options': ['A. 很快乐', 'B. 很少出门', 'C. 喜欢睡觉'], 'correct': 'A'},
            {'id': 34, 'text': '34. 北京有很多名的山，不冷的时候，很多人爬山锻炼身体。秋天山上非常漂亮，很多人来旅游。\n★ 在什么季节北京的山上人可能很少？', 'options': ['A. 春天', 'B. 秋天', 'C. 冬天'], 'correct': 'C'},
            {'id': 35, 'text': '35. 小芳生病了，这几天都没怎么吃东西，等她想吃东西的时候就是 headquarters/她的病快好了。\n★ 小芳怎么了？', 'options': ['A. 生病了', 'B. 喜欢吃东西', 'C. 病好了'], 'correct': 'A'}
        ]
    },
    'writing': {
        'part1': [
            {'id': 36, 'words': '36. 一直 / 阴天 / 最近 / 都是', 'valid_answers': ['最近一直都是阴天。']},
            {'id': 37, 'words': '37. 离婚 / 很多 / 瘦了 / 以后 / 她', 'valid_answers': ['她离婚以后瘦了很多。']},
            {'id': 38, 'words': '38. 最 / 吃 / 我 / 西瓜 / 爱', 'valid_answers': ['我最爱吃西瓜。']},
            {'id': 39, 'words': '39. 游泳 / 除了 / 我 / 爬山 / 愿意 / 也', 'valid_answers': ['除了游泳， headquarters/我也愿意爬山。'.replace(' headquarters/', ''), '除了爬山， headquarters/我也愿意游泳。'.replace(' headquarters/', '')]},
            {'id': 40, 'words': '40. 姐姐 / 下 / 就 / 来 / 了 / 要 / 个月 / 北京', 'valid_answers': ['姐姐下个月就要来北京了。', '下个月姐姐就要来北京了。']}
        ],
        'part2': [
            {'id': 41, 'text': '41. 从图书馆借来的书（gāi）还了。', 'correct': '该'},
            {'id': 42, 'text': '42. 厨房里的灯（huài）了多长时间了？', 'correct': '坏'},
            {'id': 43, 'text': '43. 感（mào）了要多喝水，多吃水果。', 'correct': '冒'},
            {'id': 44, 'text': '44. 他（gào）诉我，他姓周，今年20岁。', 'correct': '告'},
            {'id': 45, 'text': '45. 这个城市已经有一千多年的历史了，非常（yǒu）名。', 'correct': '有'}
        ]
    }
}

# ==========================================================
# 3. GIAO DIỆN CHÍNH
# ==========================================================
st.title("📚 HỆ THỐNG BÀI TẬP HÁN NGỮ 3")
st.subheader("BÀI 39: 冬天快要到了 - MÙA ĐÔNG SẮP ĐẾN RỒI")

# Khởi tạo thông tin học sinh
if "student_name" not in st.session_state:
    st.session_state["student_name"] = ""

student_name = st.text_input("📝 NHẬP HỌ VÀ TÊN HỌC SINH:", value=st.session_state["student_name"]).strip()
st.session_state["student_name"] = student_name

if not student_name:
    st.warning("⚠️ Vui lòng nhập Họ và Tên ở đầu trang trước khi bắt đầu làm bài.")

# Cấu hình Tabs cho các Bài
tabs = st.tabs(["📚 BÀI 39", "📚 BÀI 38 (Mẫu)", "📚 BÀI 37 (Mẫu)"])

# ----------------------------------------------------------
# TAB BÀI 39
# ----------------------------------------------------------
with tabs[0]:
    st.markdown("### 📘 Bài 39: 冬天快要到了")
    
    # Tạo 3 tab con cho từng Phần làm bài
    sec_listening, sec_reading, sec_writing = st.tabs(["I. PHẦN NGHE (听力)", "II. PHẦN ĐỌC (阅读)", "III. PHẦN VIẾT (书写)"])

    # ------------------------------------------------------
    # I. PHẦN NGHE
    # ------------------------------------------------------
    with sec_listening:
        st.subheader("I. 听力 - PHẦN NGHE (20 câu)")
        
        # --- Phần 1 ---
        st.markdown("#### **第一部分 (Phần 1 - Câu 1-5): Nghe đối thoại, nối hình (A - F)**")
        play_audio("03-1") # Audio 03-1
        display_listening_image() # Hiển thị image-03
        
        ans_lis_p1 = {}
        for q in LESSON_39_DATA['listening']['part1']:
            q_id = q['id']
            ans_lis_p1[q_id] = st.selectbox(
                f"Câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"lis_p1_{q_id}"
            )

        st.markdown("---")
        # --- Phần 2 ---
        st.markdown("#### **第二部分 (Phần 2 - Câu 6-10): Nghe câu, phán đoán Đúng (✔) / Sai (✘)**")
        play_audio("03-2") # Audio 03-2
        
        ans_lis_p2 = {}
        for q in LESSON_39_DATA['listening']['part2']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_lis_p2[q_id] = st.radio(
                f"Chọn đáp án câu {q_id}:",
                ["Chưa chọn", "✔", "✘"],
                key=f"lis_p2_{q_id}",
                horizontal=True
            )

        st.markdown("---")
        # --- Phần 3 ---
        st.markdown("#### **第三部分 (Phần 3 - Câu 11-15): Nghe đối thoại ngắn, chọn đáp án**")
        play_audio("03-3") # Audio 03-3
        
        ans_lis_p3 = {}
        for q in LESSON_39_DATA['listening']['part3']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_lis_p3[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"lis_p3_{q_id}"
            )

        st.markdown("---")
        # --- Phần 4 ---
        st.markdown("#### **第四部分 (Phần 4 - Câu 16-20): Nghe đối thoại dài, chọn đáp án**")
        play_audio("03-4") # Audio 03-4
        
        ans_lis_p4 = {}
        for q in LESSON_39_DATA['listening']['part4']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_lis_p4[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"lis_p4_{q_id}"
            )

        st.markdown("---")
        # Nút nộp riêng cho Phần Nghe
        if st.button("🚀 NỘP BÀI PHẦN NGHE", key="sub_listening"):
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                score = 0
                total = 20
                # Chấm P1
                for q in LESSON_39_DATA['listening']['part1']:
                    if ans_lis_p1[q['id']] == q['correct']:
                        score += 1
                # Chấm P2
                for q in LESSON_39_DATA['listening']['part2']:
                    if ans_lis_p2[q['id']] == q['correct']:
                        score += 1
                # Chấm P3
                for q in LESSON_39_DATA['listening']['part3']:
                    if ans_lis_p3[q['id']].startswith(q['correct']):
                        score += 1
                # Chấm P4
                for q in LESSON_39_DATA['listening']['part4']:
                    if ans_lis_p4[q['id']].startswith(q['correct']):
                        score += 1

                score_str = f"{score}/{total}"
                st.balloons()
                st.success(f"🎉 Kết quả Phần Nghe của **{student_name}**: **{score_str}** câu đúng!")
                send_results_to_gsheet(student_name, "Bài 39", "PHẦN NGHE", score_str)

                # Hiển thị Script Nghe
                with st.expander("📖 Xem Văn bản ghi âm (Script Nghe) & Giải thích"):
                    st.markdown("### 录音文本 (Văn bản ghi âm Bài 39)")
                    st.markdown("**第一部分**")
                    for q in LESSON_39_DATA['listening']['part1']:
                        st.text(f"Câu {q['id']}: Đáp án {q['correct']}\n{q['script']}\n")
                    st.markdown("**第二部分**")
                    for q in LESSON_39_DATA['listening']['part2']:
                        st.text(f"Câu {q['id']}: Đáp án {q['correct']}\n{q['script']}\n")
                    st.markdown("**第三部分**")
                    for q in LESSON_39_DATA['listening']['part3']:
                        st.text(f"Câu {q['id']}: Đáp án {q['correct']}\n{q['script']}\n")
                    st.markdown("**第四部分**")
                    for q in LESSON_39_DATA['listening']['part4']:
                        st.text(f"Câu {q['id']}: Đáp án {q['correct']}\n{q['script']}\n")

    # ------------------------------------------------------
    # II. PHẦN ĐỌC
    # ------------------------------------------------------
    with sec_reading:
        st.subheader("II. 阅读 - PHẦN ĐỌC (15 câu)")
        
        # --- Phần 1 ---
        st.markdown("#### **第一部分 (Phần 1 - Câu 21-25): Ghép câu phù hợp (A - F)**")
        st.info("A. 好，我看完这个节目就去睡。\nB. 没什么，就是告诉你外面阴了，可能要下雪。\nC. 不行，我正在听课文录音呢，明天就要考试了。\nD. 那儿一年四季都像春天一样，哪个季节去都很舒服。\nE. 当然。我们先坐公共汽车，然后换地铁。\nF. 你妹妹也爱看体育节目吗？")
        
        ans_read_p1 = {}
        for q in LESSON_39_DATA['reading']['part1']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_read_p1[q_id] = st.selectbox(
                f"Nối với đáp án câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"read_p1_{q_id}"
            )

        st.markdown("---")
        # --- Phần 2 ---
        st.markdown("#### **第二部分 (Phần 2 - Câu 26-30): Chọn từ điền vào chỗ trống**")
        st.info("A 晴 | B 该 | C 愿意 | D 旅游 | E 声音 | F 滑冰")
        
        ans_read_p2 = {}
        for q in LESSON_39_DATA['reading']['part2']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_read_p2[q_id] = st.selectbox(
                f"Chọn từ câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"read_p2_{q_id}"
            )

        st.markdown("---")
        # --- Phần 3 ---
        st.markdown("#### **第三部分 (Phần 3 - Câu 31-35): Chọn đáp án đúng**")
        
        ans_read_p3 = {}
        for q in LESSON_39_DATA['reading']['part3']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_read_p3[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"read_p3_{q_id}"
            )

        st.markdown("---")
        # Nút nộp riêng cho Phần Đọc
        if st.button("🚀 NỘP BÀI PHẦN ĐỌC", key="sub_reading"):
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                score = 0
                total = 15
                # Chấm P1
                for q in LESSON_39_DATA['reading']['part1']:
                    if ans_read_p1[q['id']] == q['correct']:
                        score += 1
                # Chấm P2
                for q in LESSON_39_DATA['reading']['part2']:
                    if ans_read_p2[q['id']].startswith(q['correct']):
                        score += 1
                # Chấm P3
                for q in LESSON_39_DATA['reading']['part3']:
                    if ans_read_p3[q['id']].startswith(q['correct']):
                        score += 1

                score_str = f"{score}/{total}"
                st.balloons()
                st.success(f"🎉 Kết quả Phần Đọc của **{student_name}**: **{score_str}** câu đúng!")
                send_results_to_gsheet(student_name, "Bài 39", "PHẦN ĐỌC", score_str)

    # ------------------------------------------------------
    # III. PHẦN VIẾT
    # ------------------------------------------------------
    with sec_writing:
        st.subheader("III. 书写 - PHẦN VIẾT (10 câu)")
        st.warning("⚠️ **Lưu ý**: Phần viết yêu cầu chính xác đến từng dấu câu (dấu chấm 。, dấu phẩy ，).")

        # --- Phần 1 ---
        st.markdown("#### **第一部分 (Phần 1 - Câu 36-40): Sắp xếp từ thành câu**")
        
        ans_write_p1 = {}
        for q in LESSON_39_DATA['writing']['part1']:
            q_id = q['id']
            st.markdown(f"**{q['words']}**")
            ans_write_p1[q_id] = st.text_input(
                f"Nhập câu hoàn chỉnh cho câu {q_id}:",
                key=f"write_p1_{q_id}"
            ).strip()

        st.markdown("---")
        # --- Phần 2 ---
        st.markdown("#### **第二部分 (Phần 2 - Câu 41-45): Xem phiên âm, viết chữ Hán**")
        
        ans_write_p2 = {}
        for q in LESSON_39_DATA['writing']['part2']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_write_p2[q_id] = st.text_input(
                f"Nhập chữ Hán cho câu {q_id}:",
                key=f"write_p2_{q_id}"
            ).strip()

        st.markdown("---")
        # Nút nộp riêng cho Phần Viết
        if st.button("🚀 NỘP BÀI PHẦN VIẾT", key="sub_writing"):
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                score = 0
                total = 10
                # Chấm P1 (kiểm tra chính xác từng dấu câu)
                for q in LESSON_39_DATA['writing']['part1']:
                    user_ans = ans_write_p1[q['id']]
                    if user_ans in q['valid_answers']:
                        score += 1
                        st.success(f"Câu {q['id']}: Chính xác!")
                    else:
                        st.error(f"Câu {q['id']}: Chưa chính xác. Đáp án đúng: {q['valid_answers'][0]}")

                # Chấm P2
                for q in LESSON_39_DATA['writing']['part2']:
                    user_ans = ans_write_p2[q['id']]
                    if user_ans == q['correct']:
                        score += 1
                        st.success(f"Câu {q['id']}: Chính xác!")
                    else:
                        st.error(f"Câu {q['id']}: Chưa chính xác. Đáp án đúng: {q['correct']}")

                score_str = f"{score}/{total}"
                st.balloons()
                st.success(f"🎉 Kết quả Phần Viết của **{student_name}**: **{score_str}** câu đúng!")
                send_results_to_gsheet(student_name, "Bài 39", "PHẦN VIẾT", score_str)

# ----------------------------------------------------------
# TAB BÀI KHÁC (MẪU MỞ RỘNG)
# ----------------------------------------------------------
with tabs[1]:
    st.markdown("### 📘 Bài 38: 随时保持联系")
    st.info("Nội dung Bài 38 có thể thêm vào ngân hàng câu hỏi tương tự Bài 39.")

with tabs[2]:
    st.markdown("### 📘 Bài 37: 阳光总在风雨后")
    st.info("Nội dung Bài 37 có thể thêm vào ngân hàng câu hỏi tương tự Bài 39.")

# ==========================================================
# FOOTER BẮT BUỘC
# ==========================================================
st.markdown('<div class="footer-teacher">黄宝玉老师</div>', unsafe_allow_html=True)
