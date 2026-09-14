import streamlit as st
import requests
import json
import os

# ==========================================================
# 1. CẤU HÌNH TRANG WEB & CSS CUSTOMIZATION
# ==========================================================
st.set_page_config(
    page_title="BÀI TẬP HÁN NGỮ 3 - BÀI 38 & BÀI 39",
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

# Webhook URL Google Sheets chính thức
GSHEET_URL = st.secrets.get(
    "GOOGLE_SHEET_WEBHOOK", 
    "https://script.google.com/macros/s/AKfycbyZ_pORxb7Hx8cKC-Zi9ARNeTfpE2Bw7bEjWmTK7gBnjbSHmUBJbEWxVUm8DD8cQkJ6/exec"
)

def send_results_to_gsheet(student_name, lesson_title, section_name, score_str):
    if not GSHEET_URL:
        st.info("💡 Điểm số đã được tính!")
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

# Hàm tìm kiếm file audio (hỗ trợ cả 02-1, 03-1, 38-1, 39-1...)
def find_audio_file(filename_patt):
    patterns = [filename_patt]
    num_part = filename_patt.split("-")[-1] if "-" in filename_patt else filename_patt
    if "38" in filename_patt or "02" in filename_patt:
        patterns.extend([f"02-{num_part}", f"38-{num_part}"])
    elif "39" in filename_patt or "03" in filename_patt:
        patterns.extend([f"03-{num_part}", f"39-{num_part}"])

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
        st.warning(f"🎧 Trình phát audio: Tải tệp '{filename_patt}.mp3' (hoặc 02-1.mp3, 38-1.mp3...) vào cùng thư mục dự án.")

def display_listening_image(lesson_num):
    img_names = [f"image-{lesson_num}", f"image-{lesson_num}.png", f"image-{lesson_num}.jpg", f"image-0{lesson_num[-1]}", f"image-0{lesson_num[-1]}.png"]
    for img_name in img_names:
        for folder in ["", "images", "img", "assets"]:
            p = os.path.join(folder, img_name) if folder else img_name
            if os.path.exists(p):
                st.image(p, caption=f"Hình ảnh Lựa chọn Phần 1 (A-F) Bài {lesson_num}", use_container_width=True)
                return
    st.info(f"💡 [Gợi ý]: Tải ảnh minh họa Phần 1 đặt tên 'image-{lesson_num}.png' (hoặc image-02.png) vào cùng thư mục.")

# ==========================================================
# 2. DỮ LIỆU BÀI 38 & BÀI 39
# ==========================================================
LESSON_38_DATA = {
    'title': '第38课：我们那儿的冬天跟北京一样冷 / BÀI 38: MÙA ĐÔNG Ở CHỖ CHÚNG TÔI LẠNH NHƯ Ở BẮC KINH',
    'listening': {
        'part1': [
            {'id': 1, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A', 'script': '男：我不喜欢坐飞机，不但票价贵，而且还总晚点。
女：那是是因为最近天气不好。去远一点儿的地方还是坐飞机舒服。'},
            {'id': 2, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C', 'script': '男：你想什么呢？要出去吗？
女：明天同学结婚，我在想穿哪双鞋好呢。'},
            {'id': 3, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F', 'script': '女：你看！那边真漂亮！有山有水，有树有花，还有几个小房子，美得像画一样。
男：那还等什么？快过去看看吧。'},
            {'id': 4, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B', 'script': '男：小姐，这么长您看可以吗？
女：再短一些吧。夏天到了，头发还是短一点儿好。'},
            {'id': 5, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'E', 'script': '男：雪下得真大，谁也没想到今年冬天能下这么大的雪。
女：是啊，你看孩子们玩儿得多高兴。'}
        ],
        'part2': [
            {'id': 6, 'text': '6. ★ 李华现在不在楼里。', 'correct': '✔', 'script': '我到楼里时，看见李华刚出去。'},
            {'id': 7, 'text': '7. ★ 这些学生都是中国人。', 'correct': '✘', 'script': '我们班的十五名同学来自世界各个国家，大家一起学习汉语，互相关心、互相帮助，像一家人一样。'},
            {'id': 8, 'text': '8. ★ 他喜欢音乐，也喜欢运动。', 'correct': '✔', 'script': '他有很多爱好，唱歌、画画儿、踢足球、玩儿音乐，什么都会，而且水平也都特别高。'},
            {'id': 9, 'text': '9. ★ 现在西瓜一元钱一斤。', 'correct': '✘', 'script': '这个季节的西瓜真贵，一公斤要十几块钱，还是夏天好，几角钱就能买一斤。'},
            {'id': 10, 'text': '10. ★ 小晴对那儿非常了解。', 'correct': '✘', 'script': '小晴，你来这儿没多久，对这儿的环境应该还不太了解，哪天我带你去附近走走。'}
        ],
        'part3': [
            {'id': 11, 'text': '11. 男的最近怎么样？', 'options': ['A. 比较忙', 'B. 很难过', 'C. 感冒了'], 'correct': 'A', 'script': '女：周末有时间吗？
男：不好说，最近公司事情比较多，你有什么事情吗？
问：男的最近怎么样？'},
            {'id': 12, 'text': '12. 男的想什么时候去爬山？', 'options': ['A. 明天上午', 'B. 这个周末', 'C. 下个星期'], 'correct': 'B', 'script': '女：我们明天一起去爬山，怎么样？
男：明天可能会刮风，周末再去吧，周末天气好。
问：男的想什么时候去爬山？'},
            {'id': 13, 'text': '13. 现在是什么季节？', 'options': ['A. 春天', 'B. 夏天', 'C. 冬天'], 'correct': 'C', 'script': '男：北方这个时候都下雪了，但是这儿还是像春天一样。
女：所以啊，我们这儿也叫“春城”。
问：现在是什么季节？'},
            {'id': 14, 'text': '14. 女的想让男的做什么？', 'options': ['A. 运动一下', 'B. 去办事', 'C. 穿衣服'], 'correct': 'A', 'script': '女：今晚你吃得太多了，出去走走吧。
男：行，我穿了衣服就去。
问：女的想让男的做什么？'},
            {'id': 15, 'text': '15. 男的怎么了？', 'options': ['A. 他高兴了', 'B. 眼睛里有东西', 'C. 不喜欢刮风'], 'correct': 'B', 'script': '女：你哭了？
男：没有啊，刚才风刮得太大，眼睛里进东西了。
问：男的怎么了？'}
        ],
        'part4': [
            {'id': 16, 'text': '16. 今年放寒假的时间和以前一样吗？', 'options': ['A. 一样', 'B. 比以前早', 'C. 比以前晚'], 'correct': 'B', 'script': '男：老师，我们什么时候开始放寒假？
女：一月二十二号。
男：今年怎么这么晚呢？
女：今年中国的春节比较晚，在二月十四号，开学也比以前晚一周。
问：今年放寒假 Time/的时间和以前一样吗？'},
            {'id': 17, 'text': '17. 男的为什么没去踢足球？', 'options': ['A. 口渴了', 'B. 风太大', 'C. 不舒服'], 'correct': 'B', 'script': '女：你怎么没去踢足球？你们 today/今天不是和三班踢吗？
男：今天不踢了。
女：为什么不踢了？
男：天气不好，外面风刮得太大。
问：男的为什么没去踢足球？'},
            {'id': 18, 'text': '18. 男的想做什么？', 'options': ['A. 唱歌', 'B. 跳舞', 'C. 踢足球'], 'correct': 'C', 'script': '男：外面还刮风吗？
女：是，刮得很大。你要出去吗？
男：我一会儿要和同学去踢足球，也不知道能不能踢。
女：明天吧，明天天气可能好一些。
问：男的想做什么？'},
            {'id': 19, 'text': '19. 男的可能是做什么的？', 'options': ['A. 大夫', 'B. 服务员', 'C. 校长'], 'correct': 'A', 'script': '女：这么晚了，你还出去啊？
男：接到老李的电话，有个病人出了一些问题。
女：那你快去吧。
男：你先睡吧，别等我了。
问：男的可能是做什么的？'},
            {'id': 20, 'text': '20. 他们要去哪儿？', 'options': ['A. 眼镜店', 'B. 博物馆', 'C. 国家图书馆'], 'correct': 'A', 'script': '男：还有多远啊？
女：不远了，看见国家图书馆了吧？
男：看见了。
女：那个眼镜店就在它的西边，再走500米就到了。
问：他们要去哪儿？'}
        ]
    },
    'reading': {
        'part1': [
            {'id': 21, 'text': '21. 你周末一般怎么过？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F'},
            {'id': 22, 'text': '22. 是啊，春天到了，我要和朋友一起去公园玩儿玩儿！', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A'},
            {'id': 23, 'text': '23. 你最喜欢什么季节？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'D'},
            {'id': 24, 'text': '24. 请问，张校长的办公室是哪一间？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B'},
            {'id': 25, 'text': '25. 今天是周末，你去学校做什么？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C'}
        ],
        'part2': [
            {'id': 26, 'text': '26. 虽然京剧不容易懂， headquarters/ 但是我们应该（   ）京剧。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'D'},
            {'id': 27, 'text': '27. 春、夏、秋、冬，你最喜欢哪个（   ）？', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'C'},
            {'id': 28, 'text': '28. 请帮我关一下门，（   ）风了。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'A'},
            {'id': 29, 'text': '29. A：那本书你还了？
    B：对，没什么意思，（   ）很多地方看不懂。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'F'},
            {'id': 30, 'text': '30. A：今天天气真好，我们去爬山吧？
    B：好啊，春天到了，山上的树应该都（   ）了。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'B'}
        ],
        'part3': [
            {'id': 31, 'text': '31. 李经理周末在家休息，我星期六或者星期天去找他儿。
★ 他可能星期几去找李经理？', 'options': ['A. 星期二', 'B. 星期五', 'C. 星期天'], 'correct': 'C'},
            {'id': 32, 'text': '32. 小刚的爱好比较多，喜欢游泳、跑步、打篮球。他每天早上都坚持跑步，周末游泳和打篮球。
★ 小刚周末都做什么运动？', 'options': ['A. 游泳', 'B. 跑步和打篮球', 'C. 游泳、跑步和打篮球'], 'correct': 'C'},
            {'id': 33, 'text': '33. 我刚买了一辆20万的新车，牌子跟原来那辆不一样，颜色一样，是黑色的。价钱比原来贵两万多。
★ 他原来的车大概多少钱？', 'options': ['A. 18万', 'B. 20万', 'C. 22万'], 'correct': 'A'},
            {'id': 34, 'text': '34. 要了解一个人，除了要听他怎么说，还要看他怎么做。
★ 了解一个人：', 'options': ['A. 要关心他', 'B. 要看他怎么做', 'C. 不需要听他回答什么'], 'correct': 'B'},
            {'id': 35, 'text': '35. 北京的春天一般在4月和5月，很短，风很大。夏天时间也不长，但是温度比较高。秋天是北京最美的季节，人们都喜欢在这个时候去爬长城 headquarters/ 或者去香山。
★ 哪个季节去北京旅行最好？', 'options': ['A. 春天', 'B. 夏天', 'C. 秋天'], 'correct': 'C'}
        ]
    },
    'writing': {
        'part1': [
            {'id': 36, 'words': '36. 跟 / 我弟弟 / 妈妈 / 一样 / 高', 'valid_answers': ['我弟弟跟妈妈一样高。', '妈妈跟我弟弟一样高。']},
            {'id': 37, 'words': '37. 感冒 / 季节 / 这个 / 容易', 'valid_answers': ['这个季节容易感冒。']},
            {'id': 38, 'words': '38. 经常 / 的 / 春天 / 刮风 / 这个城市', 'valid_answers': ['这个城市的春天经常刮风。']},
            {'id': 39, 'words': '39. 不到 / 一米七 / 她 / 身高', 'valid_answers': ['她身高不到一米七。']},
            {'id': 40, 'words': '40. 你 / 国家 的 / 了解 / 这个 / 文化 / 吗', 'valid_answers': ['你了解这个国家的文化吗？']}
        ],
        'part2': [
            {'id': 41, 'text': '41. 这个季（jié）的西瓜最好吃了。', 'correct': '节'},
            {'id': 42, 'text': '42. 从昨天晚上开始，外面就一直在下（xuě）。', 'correct': '雪'},
            {'id': 43, 'text': '43. 今天是（zhōu）末，不用去公司上班。', 'correct': '周'},
            {'id': 44, 'text': '44. 他工作很（rèn）真，经理很喜欢他。', 'correct': '认'},
            {'id': 45, 'text': '45. 我来中国，除了学习汉语，还希望了（jiě）更多的中国文化。', 'correct': '解'}
        ]
    }
}

# ==========================================================
# 3. GIAO DIỆN CHÍNH STREAMLIT
# ==========================================================
st.title("📚 HỆ THỐNG BÀI TẬP HÁN NGỮ 3")

if "student_name" not in st.session_state:
    st.session_state["student_name"] = ""

student_name = st.text_input("📝 NHẬP HỌ VÀ TÊN HỌC SINH:", value=st.session_state["student_name"]).strip()
st.session_state["student_name"] = student_name

if not student_name:
    st.warning("⚠️ Vui lòng nhập Họ và Tên ở đầu trang trước khi bắt đầu làm bài.")

tabs = st.tabs(["📚 BÀI 38", "📚 BÀI 39", "📚 BÀI 37 (Mẫu)"])

def render_lesson_ui(lesson_key, lesson_data, audio_prefix, img_lesson_num):
    st.markdown(f"### 📘 {lesson_data['title']}")
    sec_listening, sec_reading, sec_writing = st.tabs(["I. PHẦN NGHE (听力)", "II. PHẦN ĐỌC (阅读)", "III. PHẦN VIẾT (书写)"])

    # --- PHẦN NGHE ---
    with sec_listening:
        st.subheader("I. 听力 - PHẦN NGHE (20 câu)")
        st.markdown("#### **第一部分 (Phần 1 - Câu 1-5): Nghe đối thoại, nối hình (A - F)**")
        play_audio(f"{audio_prefix}-1")
        display_listening_image(img_lesson_num)
        
        ans_lis_p1 = {}
        for q in lesson_data['listening']['part1']:
            q_id = q['id']
            ans_lis_p1[q_id] = st.selectbox(
                f"Câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_lis_p1_{q_id}"
            )

        st.markdown("---")
        st.markdown("#### **第二部分 (Phần 2 - Câu 6-10): Nghe câu, phán đoán Đúng (✔) / Sai (✘)**")
        play_audio(f"{audio_prefix}-2")
        
        ans_lis_p2 = {}
        for q in lesson_data['listening']['part2']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_lis_p2[q_id] = st.radio(
                f"Chọn đáp án câu {q_id}:",
                ["Chưa chọn", "✔", "✘"],
                key=f"{lesson_key}_lis_p2_{q_id}",
                horizontal=True
            )

        st.markdown("---")
        st.markdown("#### **第三部分 (Phần 3 - Câu 11-15): Nghe đối thoại ngắn, chọn đáp án**")
        play_audio(f"{audio_prefix}-3")
        
        ans_lis_p3 = {}
        for q in lesson_data['listening']['part3']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_lis_p3[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_lis_p3_{q_id}"
            )

        st.markdown("---")
        st.markdown("#### **第四部分 (Phần 4 - Câu 16-20): Nghe đối thoại dài, chọn đáp án**")
        play_audio(f"{audio_prefix}-4")
        
        ans_lis_p4 = {}
        for q in lesson_data['listening']['part4']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_lis_p4[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_lis_p4_{q_id}"
            )

        st.markdown("---")
        if st.button(f"🚀 NỘP BÀI PHẦN NGHE ({lesson_key.upper()})", key=f"sub_lis_{lesson_key}"):
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                score = 0
                for q in lesson_data['listening']['part1']:
                    if ans_lis_p1[q['id']] == q['correct']: score += 1
                for q in lesson_data['listening']['part2']:
                    if ans_lis_p2[q['id']] == q['correct']: score += 1
                for q in lesson_data['listening']['part3']:
                    if ans_lis_p3[q['id']].startswith(q['correct']): score += 1
                for q in lesson_data['listening']['part4']:
                    if ans_lis_p4[q['id']].startswith(q['correct']): score += 1

                score_str = f"{score}/20"
                st.balloons()
                st.success(f"🎉 Kết quả Phần Nghe {lesson_key.upper()} của **{student_name}**: **{score_str}** câu đúng!")
                send_results_to_gsheet(student_name, f"Bài {img_lesson_num}", "PHẦN NGHE", score_str)

                with st.expander("📖 Xem Văn bản ghi âm (Script Nghe) & Giải thích"):
                    st.markdown(f"### 录音文本 (Văn bản ghi âm Bài {img_lesson_num})")
                    for p in ['part1', 'part2', 'part3', 'part4']:
                        for q in lesson_data['listening'][p]:
                            st.text(f"Câu {q['id']}: Đáp án {q['correct']}
{q['script']}
")

    # --- PHẦN ĐỌC ---
    with sec_reading:
        st.subheader("II. 阅读 - PHẦN ĐỌC (15 câu)")
        st.markdown("#### **第一部分 (Phần 1 - Câu 21-25): Ghép câu phù hợp (A - F)**")
        
        ans_read_p1 = {}
        for q in lesson_data['reading']['part1']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_read_p1[q_id] = st.selectbox(
                f"Nối với đáp án câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_read_p1_{q_id}"
            )

        st.markdown("---")
        st.markdown("#### **第二部分 (Phần 2 - Câu 26-30): Chọn từ điền vào chỗ trống**")
        
        ans_read_p2 = {}
        for q in lesson_data['reading']['part2']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_read_p2[q_id] = st.selectbox(
                f"Chọn từ câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_read_p2_{q_id}"
            )

        st.markdown("---")
        st.markdown("#### **第三部分 (Phần 3 - Câu 31-35): Chọn đáp án đúng**")
        
        ans_read_p3 = {}
        for q in lesson_data['reading']['part3']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_read_p3[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_read_p3_{q_id}"
            )

        st.markdown("---")
        if st.button(f"🚀 NỘP BÀI PHẦN ĐỌC ({lesson_key.upper()})", key=f"sub_read_{lesson_key}"):
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                score = 0
                for q in lesson_data['reading']['part1']:
                    if ans_read_p1[q['id']] == q['correct']: score += 1
                for q in lesson_data['reading']['part2']:
                    if ans_read_p2[q['id']].startswith(q['correct']): score += 1
                for q in lesson_data['reading']['part3']:
                    if ans_read_p3[q['id']].startswith(q['correct']): score += 1

                score_str = f"{score}/15"
                st.balloons()
                st.success(f"🎉 Kết quả Phần Đọc {lesson_key.upper()} của **{student_name}**: **{score_str}** câu đúng!")
                send_results_to_gsheet(student_name, f"Bài {img_lesson_num}", "PHẦN ĐỌC", score_str)

    # --- PHẦN VIẾT ---
    with sec_writing:
        st.subheader("III. 书写 - PHẦN VIẾT (10 câu)")
        st.warning("⚠️ **Lưu ý**: Phần viết yêu cầu chính xác đến từng dấu câu (dấu chấm 。, dấu phẩy ，).")

        st.markdown("#### **第一部分 (Phần 1 - Câu 36-40): Sắp xếp từ thành câu**")
        ans_write_p1 = {}
        for q in lesson_data['writing']['part1']:
            q_id = q['id']
            st.markdown(f"**{q['words']}**")
            ans_write_p1[q_id] = st.text_input(
                f"Nhập câu hoàn chỉnh cho câu {q_id}:",
                key=f"{lesson_key}_write_p1_{q_id}"
            ).strip()

        st.markdown("---")
        st.markdown("#### **第二部分 (Phần 2 - Câu 41-45): Xem phiên âm, viết chữ Hán**")
        ans_write_p2 = {}
        for q in lesson_data['writing']['part2']:
            q_id = q['id']
            st.markdown(f"**{q['text']}**")
            ans_write_p2[q_id] = st.text_input(
                f"Nhập chữ Hán cho câu {q_id}:",
                key=f"{lesson_key}_write_p2_{q_id}"
            ).strip()

        st.markdown("---")
        if st.button(f"🚀 NỘP BÀI PHẦN VIẾT ({lesson_key.upper()})", key=f"sub_write_{lesson_key}"):
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                score = 0
                for q in lesson_data['writing']['part1']:
                    user_ans = ans_write_p1[q['id']]
                    if user_ans in q['valid_answers']:
                        score += 1
                        st.success(f"Câu {q['id']}: Chính xác!")
                    else:
                        st.error(f"Câu {q['id']}: Chưa chính xác. Đáp án đúng: {q['valid_answers'][0]}")

                for q in lesson_data['writing']['part2']:
                    user_ans = ans_write_p2[q['id']]
                    if user_ans == q['correct']:
                        score += 1
                        st.success(f"Câu {q['id']}: Chính xác!")
                    else:
                        st.error(f"Câu {q['id']}: Chưa chính xác. Đáp án đúng: {q['correct']}")

                score_str = f"{score}/10"
                st.balloons()
                st.success(f"🎉 Kết quả Phần Viết {lesson_key.upper()} của **{student_name}**: **{score_str}** câu đúng!")
                send_results_to_gsheet(student_name, f"Bài {img_lesson_num}", "PHẦN VIẾT", score_str)

# TAB BÀI 38
with tabs[0]:
    render_lesson_ui("bai38", LESSON_38_DATA, "02", "38")

# TAB BÀI 39
with tabs[1]:
    # Import Bài 39 nếu có sẵn
    from app import LESSON_39_DATA
    render_lesson_ui("bai39", LESSON_39_DATA, "03", "39")

# TAB BÀI 37
with tabs[2]:
    st.markdown("### 📘 Bài 37: 阳光总在风雨后")
    st.info("Nội dung Bài 37 mở rộng tương tự Bài 38 và Bài 39.")

st.markdown('<div class="footer-teacher">黄宝玉老师</div>', unsafe_allow_html=True)
