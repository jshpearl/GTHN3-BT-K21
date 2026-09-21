import streamlit as st
import requests
import json
import os
import re

# ==========================================================
# 1. CẤU HÌNH TRANG WEB & CSS CUSTOMIZATION
# ==========================================================
st.set_page_config(
    page_title="BÀI TẬP HÁN NGỮ 3",
    page_icon="📚",
    layout="wide"
)

# Custom CSS Tông Pastel dịu nhẹ & ép kiểu chữ rõ nét + Ẩn bớt logo/menu
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    [data-testid="stHeader"] {visibility: hidden !important;}

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
    .reading-option-box {
        background-color: #EBF5FB;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #3498DB;
        margin-bottom: 20px;
        font-size: 16px;
        line-height: 1.8;
    }
    .reading-option-item {
        margin-bottom: 8px;
        font-weight: 600;
        color: #2C3E50;
    }
    .q-title-box {
        font-size: 17px;
        font-weight: 600;
        color: #2C3E50;
        line-height: 1.7;
        margin-bottom: 10px;
    }
    .wrong-script-box {
        background-color: #FFF3CD;
        border-left: 5px solid #FFC107;
        padding: 12px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 15px;
        line-height: 1.6;
        color: #856404;
    }
    .correct-script-box {
        background-color: #D4EDDA;
        border-left: 5px solid #28A745;
        padding: 12px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 15px;
        line-height: 1.6;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# Webhook URL Google Sheets chính thức
try:
    GSHEET_URL = st.secrets.get(
        "GOOGLE_SHEET_WEBHOOK", 
        "https://script.google.com/macros/s/AKfycbyZ_pORxb7Hx8cKC-Zi9ARNeTfpE2Bw7bEjWmTK7gBnjbSHmUBJbEWxVUm8DD8cQkJ6/exec"
    )
except Exception:
    GSHEET_URL = "https://script.google.com/macros/s/AKfycbyZ_pORxb7Hx8cKC-Zi9ARNeTfpE2Bw7bEjWmTK7gBnjbSHmUBJbEWxVUm8DD8cQkJ6/exec"

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

def format_q_text(text):
    if not text:
        return ""
    text = re.sub(r'\s*headquarters/\s*', '', text)
    text = re.sub(r'\s*Time/\s*', '', text)
    text = re.sub(r'\s*today/\s*', '', text)
    text = re.sub(r'\s*speech\s*', '', text)
    text = re.sub(r'\s*harvest/\s*', '', text)
    text = re.sub(r'\s*family/\s*', '', text)
    text = re.sub(r'\s*fountain/\s*', '', text)
    text = re.sub(r'\s*profit/\s*', '', text)
    text = re.sub(r'\s*coastal/\s*', '', text)
    
    text = text.replace('\\n', '\n')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return "<br>".join(lines)

def find_audio_file(filename_patt):
    patterns = [filename_patt]
    num_part = filename_patt.split("-")[-1] if "-" in filename_patt else filename_patt
    
    patterns.extend([f"0{num_part}", f"0{int(num_part):02d}", f"{num_part}"])

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
        st.warning(f"🎧 Trình phát audio: Tải tệp '{filename_patt}.mp3' vào cùng thư mục dự án.")

def find_image_file(lesson_num):
    lesson_str = str(lesson_num).strip()
    nums = [lesson_str]
    if lesson_str.isdigit():
        val = int(lesson_str)
        nums.append(f"{val:02d}")
        if val == 5: nums.extend(["41", "05", "5"])
        elif val == 4: nums.extend(["40", "04", "4"])
        elif val == 3: nums.extend(["39", "03", "3"])
        elif val == 2: nums.extend(["38", "02", "2"])

    possible_patterns = []
    for n in nums:
        possible_patterns.extend([
            f"image-{n}", f"image_{n}", f"image{n}",
            f"img-{n}", f"img_{n}", f"img{n}",
            f"pic-{n}", f"pic_{n}", f"pic{n}",
            f"B{n}", f"B_{n}", f"B-{n}"
        ])
    possible_patterns.append("IMG_5090")

    valid_exts = [".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif", ".gif"]
    
    for folder in ["", "images", "img", "assets", "audio", "sound", "pictures"]:
        for patt in possible_patterns:
            for ext in valid_exts + [e.upper() for e in valid_exts]:
                p = os.path.join(folder, patt + ext) if folder else patt + ext
                if os.path.exists(p):
                    return p

    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".venv", "__pycache__", ".streamlit"]):
            continue
        for f in files:
            name, ext = os.path.splitext(f)
            if ext.lower() in valid_exts:
                for patt in possible_patterns:
                    if patt.lower() in name.lower():
                        return os.path.join(root, f)
                for n in nums:
                    if n in name:
                        return os.path.join(root, f)

    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".venv", "__pycache__", ".streamlit"]):
            continue
        for f in files:
            name, ext = os.path.splitext(f)
            if ext.lower() in valid_exts:
                return os.path.join(root, f)

    return None

def load_image_safely(img_path):
    try:
        from PIL import Image
        img = Image.open(img_path)
        return img
    except Exception:
        try:
            with open(img_path, "rb") as f:
                return f.read()
        except Exception:
            return img_path

def display_listening_image(lesson_num):
    found_img = find_image_file(lesson_num)
    if found_img:
        try:
            img_data = load_image_safely(found_img)
            st.image(img_data, caption=f"🖼️ Hình ảnh Lựa chọn Phần 1 (A-F) Bài {lesson_num}", use_container_width=True)
            return
        except Exception as e:
            st.error(f"⚠️ Lỗi hiển thị tệp ảnh '{found_img}': {str(e)}")
    
    st.info(f"💡 [Gợi ý]: Tải ảnh minh họa Phần 1 đặt tên 'image-{lesson_num}.png' vào cùng thư mục với app.py.")

# ==========================================================
# 2. DỮ LIỆU CÁC BÀI HỌC (BÀI 5, BÀI 4, BÀI 3, BÀI 2)
# ==========================================================

LESSON_41_DATA = {
    'title': '第41课：我听过钢琴协奏曲《黄河》 / BÀI 5: TÔI ĐÃ NGHE BẢN HÒA TẤU ĐÀN DƯƠNG CẦM "HOÀNG HÀ"',
    'listening': {
        'part1': [
            {'id': 1, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B', 'script': '男：你再坚持一会儿，马上就到了。\n女：我还从来没爬过这么高的山呢，累死了。'},
            {'id': 2, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F', 'script': '男：我来北京两年了，还没去过长城呢。\n女：是吗？这个周末有时间我陪你一起去。'},
            {'id': 3, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C', 'script': '女：这家饭店的环境真不错，很安静。\n男：对，这儿的菜也好吃极了，我经常和同事来。'},
            {'id': 4, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'E', 'script': '男：这马虽然长得矮，但是跑得很快。\n女：是吗？那我们来比一比，看谁的马能跑第一。'},
            {'id': 5, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A', 'script': '男：你怎么又高兴了？\n女：你工作一直忙，一次电影都没跟我看过。'}
        ],
        'part2': [
            {'id': 6, 'text': '6. ★ 他没看过那部电视剧。', 'correct': '✘', 'script': '那部电视剧太好了，我还想再看一遍。'},
            {'id': 7, 'text': '7. ★ 王丽不会弹钢琴。', 'correct': '✘', 'script': '我问王丽会不会弹钢琴，她说小时候学过，可是弹得不太好。'},
            {'id': 8, 'text': '8. ★ 他下星期要去北京。', 'correct': '✔', 'script': '我下周要去北京旅游，听说你以前去过那儿，能给我介绍几个好玩儿的地方吗？'},
            {'id': 9, 'text': '9. ★ 他身体不好。', 'correct': '✘', 'script': '跟你说了，抽烟对身体不好，别抽了！'},
            {'id': 10, 'text': '10. ★ 这本书一共35课。', 'correct': '✘', 'script': '我们学得很快，这本书我们已经学到第二十五课了，还有五课就学完了。'}
        ],
        'part3': [
            {'id': 11, 'text': '11. 女的今天要去哪儿？', 'options': ['A. 长城', 'B. 博物馆', 'C. 颐和园'], 'correct': 'B', 'script': '男：今天是周末，天气这么好，我们一起去爬长城吧。\n女：上周我去过了。一会儿要和中国朋友一起去军事博物馆。明天一起去颐和园划船怎么样？\n问：女的今天要去哪儿？'},
            {'id': 12, 'text': '12. 女的怎么了？', 'options': ['A. 出差了', 'B. 住院了', 'C. 没上班'], 'correct': 'C', 'script': '男：怎么好几天没见到你了？出差了？\n女：我请假了，妈妈住院了。\n问：女的怎么了？'},
            {'id': 13, 'text': '13. 男的是什么意思？', 'options': ['A. 不太好', 'B. 好极了', 'C. 还可以'], 'correct': 'B', 'script': '女：大强，我这首法文歌唱得怎么样？\n男：这个世界上没有比你唱得更好的了！\n问：男的是什么意思？'},
            {'id': 14, 'text': '14. 今年下了几次雪了？', 'options': ['A. 一次', 'B. 两次', 'C. 三次'], 'correct': 'C', 'script': '男：又下雪了！今年下过几次雪了？\n女：已经下过两次了，这是第三次了。\n问：今年下了几次雪了？'},
            {'id': 15, 'text': '15. 男的应该往哪边走？', 'options': ['A. 东边', 'B. 西边', 'C. 北边'], 'correct': 'A', 'script': '男：你好！请问黄河公园离这儿还有多远？\n女：不远了，你向东再走六七百米就到了。\n问：男的应该往哪边走？'}
        ],
        'part4': [
            {'id': 16, 'text': '16. 女的看过京剧吗？', 'options': ['A. 没看过', 'B. 看过', 'C. 不知道'], 'correct': 'B', 'script': '男：玛丽，来中国以后你看过京剧吗？\n女：和中国朋友一起看过一次。\n男：你觉得有意思吗？能听懂吗？\n女：怎么说呢？我觉得和唱歌不一样，我听不懂。\n问：女的看过京剧吗？'},
            {'id': 17, 'text': '17. 关于男的，可以知道什么？', 'options': ['A. 喜欢夏天', 'B. 不喜欢热', 'C. 四个季节都喜欢'], 'correct': 'B', 'script': '女：大明，一年四季，你最喜欢哪个季节？\n男：我啊，除了夏天以外，我都喜欢。\n女：能告诉我为什么吗？\n男：我怕热啊，这儿的夏天热极了，你不觉得吗？\n问：关于男的，可以知道什么？'},
            {'id': 18, 'text': '18. 他们在吃什么菜？', 'options': ['A. 中国菜', 'B. 日本菜', 'C. 韩国菜'], 'correct': 'C', 'script': '男：田芳，这里的牛肉好吃吗？\n女：嗯，这儿的韩国烤牛肉真好吃！挺贵的吧？\n男：是比较贵！ family/ profit/不过今天我请客，多吃点儿！\n女：谢谢，下次我请你吃中国菜！\n问：他们在吃什么菜？'},
            {'id': 19, 'text': '19. 男的是做什么工作的？', 'options': ['A. 司机', 'B. 校长', 'C. 服务员'], 'correct': 'A', 'script': '女：张叔叔，您开车多久了？\n男：三十多年了，从18岁一直到现在。\n女：一天八小时都在开车，多累啊！没想过换一个工作吗？\n男：但是除了开车我什么都不会啊。\n问：男的是做什么工作的？'},
            {'id': 20, 'text': '20. 男的为什么要做面条儿？', 'options': ['A. 西瓜吃完了', 'B. 没有鸡蛋了', 'C. 女的过生日'], 'correct': 'C', 'script': '男：祝你生日快乐！\n女：谢谢，谢谢。\n男：过生日要吃面条儿，这是我第一次做面条儿，看看好吃不好吃。\n女：一定很好吃。\n问：男的为什么要做面条儿？'}
        ]
    },
    'reading': {
        'ref_part1': [
            'A. 你了解他吗？这么快就和他结婚了！',
            'B. 这本历史书看了吗？',
            'C. 他们很认真、很努力地练习了一个夏天。',
            'D. 你了解中国吗？',
            'E. 当然。我们先坐公共汽车，然后换地铁。',
            'F. 是啊，马上就要到春天了，还没下过雪呢。'
        ],
        'ref_part2': [
            'A. 过',
            'B. 第',
            'C. 虽然',
            'D. 经过',
            'E. 声音',
            'F. 办公室'
        ],
        'part1': [
            {'id': 21, 'text': '21. 今天的节目看了吗？那些学生的表演好极了。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C'},
            {'id': 22, 'text': '22. 今年北京的冬天一点儿都不冷。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F'},
            {'id': 23, 'text': '23. 第一次见面我就喜欢上他了。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A'},
            {'id': 24, 'text': '24. 了解一点儿，但是我知道中国的黄河很有名。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'D'},
            {'id': 25, 'text': '25. 《上下五千年》？我三四年级的时候就读过了。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B'}
        ],
        'part2': [
            {'id': 26, 'text': '26. 来这家银行以前，我在两家公司工作（   ）。', 'options': ['A. 过', 'B. 第', 'C. 虽然', 'D. 经过', 'E. 声音', 'F. 办公室'], 'correct': 'A'},
            {'id': 27, 'text': '27. 你看，这是我上次坐火车（   ）黄河时的照片。', 'options': ['A. 过', 'B. 第', 'C. 虽然', 'D. 经过', 'E. 声音', 'F. 办公室'], 'correct': 'D'},
            {'id': 28, 'text': '28. 我们班小明总是（   ）一个回答老师的问题。', 'options': ['A. 过', 'B. 第', 'C. 虽然', 'D. 经过', 'E. 声音', 'F. 办公室'], 'correct': 'B'},
            {'id': 29, 'text': '29. A：你认识她吗？\n    B：（   ）我不知道她的名字，但是我看过她的照片儿。', 'options': ['A. 过', 'B. 第', 'C. 虽然', 'D. 经过', 'E. 声音', 'F. 办公室'], 'correct': 'C'},
            {'id': 30, 'text': '30. A：请问，万经理的（   ）在哪儿？\n    B：前面左边第一个就是。', 'options': ['A. 过', 'B. 第', 'C. 虽然', 'D. 经过', 'E. 声音', 'F. 办公室'], 'correct': 'F'}
        ],
        'part3': [
            {'id': 31, 'text': '31. 昆明跟北京不一样，那里一年四季都是春天。\n★ 在一年中，哪个城市的气温变化小？', 'options': ['A. 上海', 'B. 昆明', 'C. 北京'], 'correct': 'B'},
            {'id': 32, 'text': '32. 我不会打太极拳，很想学。田芳以前学过，但是她还想再学一学。听说体育老师下星期教太极拳，真是太好了！\n★ 谁会打太极拳？', 'options': ['A. 田芳', 'B. 我和田芳', 'C. 都不会'], 'correct': 'A'},
            {'id': 33, 'text': '33. 我在北京的时候吃过一次北京烤鸭，来这儿以后一次还没吃过呢。\n★ 他吃过烤鸭吗？', 'options': ['A. 从来没吃过', 'B. 在北京吃过一次', 'C. 在这儿吃过一次'], 'correct': 'B'},
            {'id': 34, 'text': '34. 茶是我的最爱，花茶、绿茶、红茶，我都喜欢。天冷了或者你工作累了的时候，喝杯热茶，真是舒服极了。\n★ 关于他，可以知道：', 'options': ['A. 口渴了', 'B. 没完成工作', 'C. 很喜欢喝茶'], 'correct': 'C'},
            {'id': 35, 'text': '35. 这个城市就在黄河边上，环境非常好，夏天一点儿都不热。人们都喜欢这个季节来这儿旅游。\n★ 那个城市：', 'options': ['A. 环境不好', 'B. 夏季不热', 'C. 人们很热情'], 'correct': 'B'}
        ]
    },
    'writing': {
        'part1': [
            {'id': 36, 'words': '36. 我 / 这个人 / 跟 / 见过 / 只 / 一次面', 'valid_answers': ['我只跟这个人见过一次面。']},
            {'id': 37, 'words': '37. 他 / 总是 / 第一个 / 到 / 班里', 'valid_answers': ['他总是第一个到班里。']},
            {'id': 38, 'words': '38. 去黄河 / 哪个季节 / 玩儿 / 你想', 'valid_answers': ['你想哪个季节去黄河玩儿？', '你想哪个季节去黄河玩？']},
            {'id': 39, 'words': '39. 风景 / 极了 / 那儿 / 漂亮的', 'valid_answers': ['那儿的风光漂亮极了！', '那儿的风光漂亮极了。', '那儿的风景漂亮极了！', '那儿的风景漂亮极了。']},
            {'id': 40, 'words': '40. 面包 / 一个 / 商店里 / 没有 / 也', 'valid_answers': ['商店里一个面包也没有。']}
        ],
        'part2': [
            {'id': 41, 'text': '41. 我妈妈生病住（yuàn）了。', 'correct': '院'},
            {'id': 42, 'text': '42. （kǎo）鸭很好吃。', 'correct': '烤'},
            {'id': 43, 'text': '43. 这家饭店的（cài）很好吃。', 'correct': '菜'},
            {'id': 44, 'text': '44. 今天下午我一杯咖啡（yě）没喝。', 'correct': '也'},
            {'id': 45, 'text': '45. 我（cān）加过三次比赛，拿了两次第一，一次第二。', 'correct': '参'}
        ]
    }
}

LESSON_40_DATA = {
    'title': '第40课：快上来吧，要开车了 / BÀI 4: MAU LÊN XE ĐI, XE SẮP CHẠY RỒI',
    'listening': {
        'part1': [
            {'id': 1, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F', 'script': '男：快上来吧，要开车了。\n女：等一下，我拿一下包。'},
            {'id': 2, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'E', 'script': '男：你今天怎么骑自行车来了？\n女：今天天气好，骑车锻炼一下身体。'},
            {'id': 3, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C', 'script': '男：你看见我的护照了吗？\n女：就在桌子上呢，你自己看。'},
            {'id': 4, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C', 'script': '男：先生，请问您买什么？\n女：我想买一条裤子。'},
            {'id': 5, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A', 'script': '男：今天超市人真多。\n女：是啊，大家都在买东西。'}
        ],
        'part2': [
            {'id': 6, 'text': '6. ★ 他回宿舍取照相机。', 'correct': '✔', 'script': '你等等我，照相机忘带了，我回趟宿舍，马上就回来。'},
            {'id': 7, 'text': '7. ★ 那个地方的茶很有名。', 'correct': '✔', 'script': '那里的茶非常有名的，去那儿玩儿的人一般都会买一些带回来，送给家人或者朋友。'},
            {'id': 8, 'text': '8. ★ 现在是夏天。', 'correct': '✘', 'script': '虽然已经是春天了，但天气还是很冷。你这次去开会，要多带点儿衣服，注意别感冒了。'},
            {'id': 9, 'text': '9. ★ 他唱歌水平提高了。', 'correct': '✔', 'script': '在老师的帮助下，经过一段时间的练习，他的唱歌水平有了很大的提高。'},
            {'id': 10, 'text': '10. ★ 这条裤子现在便宜得多。', 'correct': '✔', 'script': '我记得这条裤子上个月是八百元，现在只要四百元，我一次买了两条。'}
        ],
        'part3': [
            {'id': 11, 'text': '11. 男的让女的帮他做什么？', 'options': ['A. 借书', 'B. 换书', 'C. 还书'], 'correct': 'C', 'script': '女：张东，我去图书馆借书，你陪我去好吗？\n男：对不起，我在等人，麻烦你帮我还这两本书吧。\n问：男的让女的帮他做什么？'},
            {'id': 12, 'text': '12. 男的送什么礼物了？', 'options': ['A. 包', 'B. 鲜花', 'C. 自行车'], 'correct': 'A', 'script': '女：谢谢你送我的生日礼物！这个包我非常喜欢。\n男：不客气，祝你生日快乐！\n问：男的送什么礼物了？'},
            {'id': 13, 'text': '13. 他们现在最可能在哪儿？', 'options': ['A. 商店', 'B. 教室', 'C. 银行'], 'correct': 'A', 'script': '女：先生，这是您的裤子，请拿好，欢迎下次再来。\n男：好的，谢谢，再见。\n问：他们现在最可能在哪儿？'},
            {'id': 14, 'text': '14. 男的觉得那张地图怎么样？', 'options': ['A. 很贵', 'B. 字很小', 'C. 太黑了'], 'correct': 'B', 'script': '女：你不是有一张世界地图吗？\n男：那张地图上的字太小了，好多地方都看不清楚。\n问：男的觉得那张地图怎么样？'},
            {'id': 15, 'text': '15. 谁现在不在？', 'options': ['A. 经理', 'B. 校长', 'C. 司机'], 'correct': 'B', 'script': '女：请问，这里是校长办公室吗？\n男：是的，但是校长现在不在，他正在和三年级的老师开会呢。\n问：谁现在不在？'}
        ],
        'part4': [
            {'id': 16, 'text': '16. 他们要去哪儿？', 'options': ['A. 饭店', 'B. 展览馆', 'C. 图书馆'], 'correct': 'A', 'script': '男：喂，我已经到饭店门口了，你在哪儿？\n女：我正往那儿走呢，马上就到。\n男：好，那一会儿见。\n女：好的，再见。\n问：他们要去哪儿？'},
            {'id': 17, 'text': '17. 女的可能在买什么？', 'options': ['A. 裤子', 'B. 大衣', 'C. 鞋'], 'correct': 'B', 'script': '女：麻烦给我拿一下那件红色的。\n男：您穿多大的？\n女：165的。\n男：对不起，红色的没有165的了。\n问：女的可能在买什么？'},
            {'id': 18, 'text': '18. 男的希望女的做什么？', 'options': ['A. 走右边', 'B. 写名字', 'C. 给他介绍花'], 'correct': 'C', 'script': '男：你好，我想买些花送给妈妈。\n女：你想要哪一种呢？\n男：我也不知道，能给我介绍一下吗？\n女：当然可以，您先来左边这儿看看。\n问：男的希望女的做什么？'},
            {'id': 19, 'text': '19. 电影几点开始？', 'options': ['A. 七点十五分', 'B. 七点半', 'C. 七点四十五分'], 'correct': 'B', 'script': '女：喂，已经七点一刻了，你怎么还没到啊？\n男：电影不是还有十五分钟才开始吗？我马上就到。\n女：我还没吃晚饭，你呢？\n男：吃了一碗面条儿，给你买了面包。\n问：电影几点开始？'},
            {'id': 20, 'text': '20. 男的不喜欢吃什么？', 'options': ['A. 米饭', 'B. 面包', 'C. 面条儿'], 'correct': 'C', 'script': '男：天黑了，怎么不开灯呢？\n女：正想着晚上吃什么呢，忘了开了。\n男：除了面条儿，你做什么我都爱吃。\n女：好，先去洗个澡吧，半小时后吃饭。\n问：男的不喜欢吃什么？'}
        ]
    },
    'reading': {
        'ref_part1': [
            'A. 银行马上就要关门了。',
            'B. 服务员，这条裤子有点儿短，帮我再换一条吧。',
            'C. 知道了，妈妈，我马上就开始复习。',
            'D. 下周公司派我去上海，别忘了给鱼换水。',
            'E. 当然。我们先坐公共汽车，然后换地铁。',
            'F. 这是我送 your/你的礼物，你看喜不喜欢？'
        ],
        'ref_part2': [
            'A. 双',
            'B. 送',
            'C. 注意',
            'D. 裤子',
            'E. 声音',
            'F. 清楚'
        ],
        'part1': [
            {'id': 21, 'text': '21. 没问题！大概要几天换一次水？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'D'},
            {'id': 22, 'text': '22. 没关系，我明天去也可以。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A'},
            {'id': 23, 'text': '23. 哥，祝你生日快乐！', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F'},
            {'id': 24, 'text': '24. 他正在买衣服。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B'},
            {'id': 25, 'text': '25. 别看电视了，你应该准备明天的考试了。', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C'}
        ],
        'part2': [
            {'id': 26, 'text': '26. 天气冷了，请（   ）身体。', 'options': ['A. 双', 'B. 送', 'C. 注意', 'D. 裤子', 'E. 声音', 'F. 清楚'], 'correct': 'C'},
            {'id': 27, 'text': '27. 这儿的茶特别有名，你买点儿带回去（   ）给朋友吧。', 'options': ['A. 双', 'B. 送', 'C. 注意', 'D. 裤子', 'E. 声音', 'F. 清楚'], 'correct': 'B'},
            {'id': 28, 'text': '28. 周末你是不是要带学生去爬山？穿这条（   ）吧。', 'options': ['A. 双', 'B. 送', 'C. 注意', 'D. 裤子', 'E. 声音', 'F. 清楚'], 'correct': 'D'},
            {'id': 29, 'text': '29. A：您好，请问这附近有中国银行吗？\n    B：对不起，我也不太（   ），你再问问别人吧。', 'options': ['A. 双', 'B. 送', 'C. 注意', 'D. 裤子', 'E. 声音', 'F. 清楚'], 'correct': 'F'},
            {'id': 30, 'text': '30. A：服务员，我们这桌少了一（   ）筷子。\n    B：对不起，我马上给您拿。', 'options': ['A. 双', 'B. 送', 'C. 注意', 'D. 裤子', 'E. 声音', 'F. 清楚'], 'correct': 'A'}
        ],
        'part3': [
            {'id': 31, 'text': '31. 这条裤子颜色、肥瘦都很合适，要是再长一点儿就好了。\n★ 这条裤子哪儿不合适？', 'options': ['A. 颜色', 'B. 肥瘦', 'C. 长短'], 'correct': 'C'},
            {'id': 32, 'text': '32. 我12号从北京出发，先去台湾，五天后再从台湾去香港。\n★ 他16号可能在哪儿？', 'options': ['A. 北京', 'B. 台湾', 'C. 香港'], 'correct': 'B'},
            {'id': 33, 'text': '33. 你要是去办公室找王明，最好先给他打个电话，他有的时候出去办事，不一定每天都在。\n★ 根据上面的句子，可以知道王明：', 'options': ['A. 每天都在办公室', 'B. 总出差', 'C. 有时候出去办事'], 'correct': 'C'},
            {'id': 34, 'text': '34. 小时候爸爸妈妈对我的要求是：好好学习，天天向上。意思是要努力学习，每天都有提高，得到更好的成绩。\n★ 爸爸妈妈希望“我”：', 'options': ['A. 学习好', 'B. 身体好', 'C. 工作好'], 'correct': 'A'},
            {'id': 35, 'text': '35. 他刚才给我打电话，说那本书里还有一个问题，一会儿你去他那儿看看。以后要注意，一定要认真。\n★ 那本书：', 'options': ['A. 很有意思', 'B. 还有问题', 'C. 有不少错字'], 'correct': 'B'}
        ]
    },
    'writing': {
        'part1': [
            {'id': 36, 'words': '36. 教室 / 请 / 进来 / 快', 'valid_answers': ['请快进教室来。', '请快进来教室。']},
            {'id': 37, 'words': '37. 快要 / 电影 / 了 / 开始 / 马上', 'valid_answers': ['电影马上就要开始了。', '马上电影就要开始了。']},
            {'id': 38, 'words': '38. 她 / 带 / 忘了 / 护照', 'valid_answers': ['她忘了带护照。']},
            {'id': 39, 'words': '39. 这条 / 长 / 了 / 裤子 / 太', 'valid_answers': ['这条裤子太长了！', '这条裤子太长了。']},
            {'id': 40, 'words': '40. 生日礼物 / 我打算 / 一个 / 送她', 'valid_answers': ['我打算送她一个生日礼物。']}
        ],
        'part2': [
            {'id': 41, 'text': '41. 妈妈给我写了一（fēng）信。', 'correct': '封'},
            {'id': 42, 'text': '42. 您（màn）走，欢迎下次再来。', 'correct': '慢'},
            {'id': 43, 'text': '43. 下课以后我（mǎ）上回家吃饭。', 'correct': '马'},
            {'id': 44, 'text': '44. （sòng）给你一个小礼物，希望你能喜欢。', 'correct': '送'},
            {'id': 45, 'text': '45. 经（guò）半年多的努力学习，她的汉语水平有了很大提高。', 'correct': '过'}
        ]
    }
}

LESSON_39_DATA = {
    'title': '第39课：冬天快要到了 / BÀI 3: MÙA ĐÔNG SẮP ĐẾN RỒI',
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
            {'id': 20, 'text': '20. 他们最可能在哪儿？', 'options': ['A. 商店', 'B. 饭店', 'C. 银行'], 'correct': 'A', 'script': '女：还需要别的水果吗？\n男：不用了，就 these香蕉。多少钱？\n女：十三元五角。\n男：给你钱。\n女：好的，欢迎您下次再来，再见。\n问：他们最可能在哪儿？'}
        ]
    },
    'reading': {
        'ref_part1': [
            'A. 好，我看完这个节目就去睡。',
            'B. 没什么，就是告诉你外面阴了，可能要下雪。',
            'C. 不行，我正在听课文录音呢，明天就要考试了。',
            'D. 那儿一年四季都像春天一样，哪个季节去都很舒服。',
            'E. 当然。我们先坐公共汽车，然后换地铁。',
            'F. 你妹妹也爱看体育节目吗？'
        ],
        'ref_part2': [
            'A. 晴',
            'B. 该',
            'C. 愿意',
            'D. 旅游',
            'E. 声音',
            'F. 滑冰'
        ],
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
            {'id': 35, 'text': '35. 小芳生病了，这几天都没怎么吃东西，等她想吃东西的时候就是她的病快好了。\n★ 小芳怎么了？', 'options': ['A. 生病了', 'B. 喜欢吃东西', 'C. 病好了'], 'correct': 'A'}
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

LESSON_38_DATA = {
    'title': '第38课：我们那儿的冬天跟北京一样冷 / BÀI 2: MÙA ĐÔNG Ở CHỖ CHÚNG TÔI LẠNH NHƯ Ở BẮC KINH',
    'listening': {
        'part1': [
            {'id': 1, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A', 'script': '男：我不喜欢坐飞机，不但票价贵，而且还总晚点。\n女：那是是因为最近天气不好。去远一点儿的地方还是坐飞机舒服。'},
            {'id': 2, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C', 'script': '男：你想什么呢？要出去吗？\n女：明天同学结婚，我在想穿哪双鞋好呢。'},
            {'id': 3, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F', 'script': '女：你看！那边真漂亮！有山有水，有树有花，还有几个小房子，美得像画一样。\n男：那还等什么？快过去看看吧。'},
            {'id': 4, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B', 'script': '男：小姐，这么长您看可以吗？\n女：再短一些吧。夏天到了，头发还是短一点儿好。'},
            {'id': 5, 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'E', 'script': '男：雪下得真大，谁也没想到今年冬天能下这么大的雪。\n女：是啊，你看孩子们玩儿得多高兴。'}
        ],
        'part2': [
            {'id': 6, 'text': '6. ★ 李华现在不在楼里。', 'correct': '✔', 'script': '我到楼里时，看见李华刚出去。'},
            {'id': 7, 'text': '7. ★ 这些学生都是中国人。', 'correct': '✘', 'script': '我们班的十五名同学来自世界各个国家，大家一起学习汉语，互相关心、互相帮助，像一家人一样。'},
            {'id': 8, 'text': '8. ★ 他喜欢音乐，也喜欢运动。', 'correct': '✔', 'script': '他有很多爱好，唱歌、画画儿、踢足球、玩儿音乐，什么都会，而且水平也都特别高。'},
            {'id': 9, 'text': '9. ★ 现在西瓜一元钱一斤。', 'correct': '✘', 'script': '这个季节的西瓜真贵，一公斤要十几块钱，还是夏天好，几角钱就能买一斤。'},
            {'id': 10, 'text': '10. ★ 小晴对那儿非常了解。', 'correct': '✘', 'script': '小晴，你来这儿没多久，对这儿的环境应该还不太了解，哪天我带你去附近走走。'}
        ],
        'part3': [
            {'id': 11, 'text': '11. 男的最近怎么样？', 'options': ['A. 比较忙', 'B. 很难过', 'C. 感冒了'], 'correct': 'A', 'script': '女：周末有时间吗？\n男：不好说，最近公司事情比较多，你有什么事情吗？\n问：男的最近怎么样？'},
            {'id': 12, 'text': '12. 男的想什么时候去爬山？', 'options': ['A. 明天上午', 'B. 这个周末', 'C. 下个星期'], 'correct': 'B', 'script': '女：我们明天一起去爬山，怎么样？\n男：明天可能会刮风，周末再去吧，周末天气好。\n问：男的想什么时候去爬山？'},
            {'id': 13, 'text': '13. 现在是什么季节？', 'options': ['A. 春天', 'B. 夏天', 'C. 冬天'], 'correct': 'C', 'script': '男：北方这个时候都下雪了，但是这儿还是像春天一样。\n女：所以啊，我们这儿也叫“春城”。\n问：现在是什么季节？'},
            {'id': 14, 'text': '14. 女的想让男的做什么？', 'options': ['A. 运动一下', 'B. 去办事', 'C. 穿衣服'], 'correct': 'A', 'script': '女：今晚你吃得太多了，出去走走吧。\n男：行，我穿了衣服就去。\n问：女的想让男的做什么？'},
            {'id': 15, 'text': '15. 男的怎么了？', 'options': ['A. 他高兴了', 'B. 眼睛里有东西', 'C. 不喜欢刮风'], 'correct': 'B', 'script': '女：你哭了？\n男：没有啊，刚才风刮得太大，眼睛里进东西了。\n问：男的怎么了？'}
        ],
        'part4': [
            {'id': 16, 'text': '16. 今年放寒假的时间和以前一样吗？', 'options': ['A. 一样', 'B. 比以前早', 'C. 比以前晚'], 'correct': 'B', 'script': '男：老师，我们什么时候开始放寒假？\n女：一月二十二号。\n男：今年怎么这么晚呢？\n女：今年中国的春节比较晚，在二月十四号，开学也比以前晚一周。\n问：今年放寒假的时间和以前一样吗？'},
            {'id': 17, 'text': '17. 男的为什么没去踢足球？', 'options': ['A. 口渴了', 'B. 风太大', 'C. 不舒服'], 'correct': 'B', 'script': '女：你怎么没去踢足球？你们今天 headquarters/不是和三班踢吗？\n男：今天不踢了。\n女：为什么不踢了？\n男：天气不好，外面风刮得太大。\n问：男的为什么没去踢足球？'.replace(' headquarters/', '')},
            {'id': 18, 'text': '18. 男的想做什么？', 'options': ['A. 唱歌', 'B. 跳舞', 'C. 踢足球'], 'correct': 'C', 'script': '男：外面还刮风吗？\n女：是，刮得很大。你要出去吗？\n男：我一会儿要和同学去踢足球，也不知道能不能踢。\n女：明天吧，明天天气可能好一些。\n问：男的想做什么？'},
            {'id': 19, 'text': '19. 男的可能是做什么的？', 'options': ['A. 大夫', 'B. 服务员', 'C. 校长'], 'correct': 'A', 'script': '女：这么晚了，你还出去啊？\n男：接到老李的电话，有个病人出了一些问题。\n女：那你快去吧。\n男：你先睡吧，别等我了。\n问：男的可能是做什么的？'},
            {'id': 20, 'text': '20. 他们要去哪儿？', 'options': ['A. 眼镜店', 'B. 博物馆', 'C. 国家图书馆'], 'correct': 'A', 'script': '男：还有多远啊？\n女：不远了，看见国家图书馆了吧？\n男：看见了。\n女：那个眼镜店就在它的西边，再走500米就到了。\n问：他们要去哪儿？'}
        ]
    },
    'reading': {
        'ref_part1': [
            'A. 你别总在屋里学习，应该出去走走。',
            'B. 最东边那个。但是他上午出去开会了，您下午再来？',
            'C. 今天学校里一个人都没有，大家都去哪儿了？',
            'D. 当然是春天。',
            'E. 当然。我们先坐公共汽车，然后换地铁。',
            'F. 在宿舍休息或者跟朋友一起出去玩儿。'
        ],
        'ref_part2': [
            'A. 刮',
            'B. 绿',
            'C. 季节',
            'D. 了解',
            'E. 声音',
            'F. 而且'
        ],
        'part1': [
            {'id': 21, 'text': '21. 你周末一般怎么过？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'F'},
            {'id': 22, 'text': '22. 是啊，春天到了，我要和朋友一起去公园玩儿玩儿！', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'A'},
            {'id': 23, 'text': '23. 你最喜欢什么季节？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'D'},
            {'id': 24, 'text': '24. 请问，张校长的办公室是哪一间？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'B'},
            {'id': 25, 'text': '25. 今天是周末，你去学校做什么？', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'correct': 'C'}
        ],
        'part2': [
            {'id': 26, 'text': '26. 虽然京剧不容易懂，但是我们应该（   ）京剧。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'D'},
            {'id': 27, 'text': '27. 春、夏、秋、冬，你最喜欢哪个（   ）？', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'C'},
            {'id': 28, 'text': '28. 请帮我关一下门，（   ）风了。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'A'},
            {'id': 29, 'text': '29. A：那本书你还了？\n    B：对，没什么意思，（   ）很多地方看不懂。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'F'},
            {'id': 30, 'text': '30. A：今天天气真好，我们去爬山吧？\n    B：好啊，春天到了，山上的树应该都（   ）了。', 'options': ['A. 刮', 'B. 绿', 'C. 季节', 'D. 了解', 'E. 声音', 'F. 而且'], 'correct': 'B'}
        ],
        'part3': [
            {'id': 31, 'text': '31. 李经理周末在家休息，我星期六或者星期天去找他儿。\n★ 他可能星期几去找李经理？', 'options': ['A. 星期二', 'B. 星期五', 'C. 星期天'], 'correct': 'C'},
            {'id': 32, 'text': '32. 小刚的爱好比较多，喜欢游泳、跑步、打篮球。他每天早上都坚持跑步，周末游泳和打篮球。\n★ 小刚周末都做什么运动？', 'options': ['A. 游泳', 'B. 跑步和打篮球', 'C. 游泳、跑步和打篮球'], 'correct': 'C'},
            {'id': 33, 'text': '33. 我刚买了一辆20万的新车，牌子跟原来那辆不一样，颜色一样，是黑色的。价钱比原来贵两万多。\n★ 他原来的车大概多少钱？', 'options': ['A. 18万', 'B. 20万', 'C. 22万'], 'correct': 'A'},
            {'id': 34, 'text': '34. 要了解一个人，除了要听他怎么说，还要看他怎么做。\n★ 了解一个人：', 'options': ['A. 要关心他', 'B. 要看他怎么做', 'C. 不需要听他回答什么'], 'correct': 'B'},
            {'id': 35, 'text': '35. 北京的春天一般在4月和5月，很短，风很大。夏天时间也不长，但是温度比较高。秋天是北京最美的季节，人们都喜欢在这个时候去爬长城 headquarters/或者去香山。', 'options': ['A. 春天', 'B. 夏天', 'C. 秋天'], 'correct': 'C'}
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

tabs = st.tabs(["📚 BÀI 5", "📚 BÀI 4", "📚 BÀI 3", "📚 BÀI 2"])

def render_lesson_ui(lesson_key, lesson_data, audio_prefix, img_lesson_num):
    st.markdown(f"### 📘 {lesson_data['title']}")
    sec_listening, sec_reading, sec_writing = st.tabs(["I. PHẦN NGHE (听力)", "II. PHẦN ĐỌC (阅读)", "III. PHẦN VIẾT (书写)"])

    submitted_key = f"submitted_{lesson_key}"
    if submitted_key not in st.session_state:
        st.session_state[submitted_key] = {}

    # --- PHẦN NGHE ---
    with sec_listening:
        st.subheader("I. 听力 - PHẦN NGHE (20 câu)")
        
        # Phần 1
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
        # Phần 2
        st.markdown("#### **第二部分 (Phần 2 - Câu 6-10): Nghe câu, phán đoán Đúng (✔) / Sai (✘)**")
        play_audio(f"{audio_prefix}-2")
        
        ans_lis_p2 = {}
        for q in lesson_data['listening']['part2']:
            q_id = q['id']
            formatted_q = format_q_text(q['text'])
            st.markdown(f"<div class='q-title-box'>{formatted_q}</div>", unsafe_allow_html=True)
            ans_lis_p2[q_id] = st.radio(
                f"Chọn đáp án câu {q_id}:",
                ["Chưa chọn", "✔", "✘"],
                key=f"{lesson_key}_lis_p2_{q_id}",
                horizontal=True
            )

        st.markdown("---")
        # Phần 3
        st.markdown("#### **第三部分 (Phần 3 - Câu 11-15): Nghe đối thoại ngắn, chọn đáp án**")
        play_audio(f"{audio_prefix}-3")
        
        ans_lis_p3 = {}
        for q in lesson_data['listening']['part3']:
            q_id = q['id']
            formatted_q = format_q_text(q['text'])
            st.markdown(f"<div class='q-title-box'>{formatted_q}</div>", unsafe_allow_html=True)
            ans_lis_p3[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_lis_p3_{q_id}"
            )

        st.markdown("---")
        # Phần 4
        st.markdown("#### **第四部分 (Phần 4 - Câu 16-20): Nghe đối thoại dài, chọn đáp án**")
        play_audio(f"{audio_prefix}-4")
        
        ans_lis_p4 = {}
        for q in lesson_data['listening']['part4']:
            q_id = q['id']
            formatted_q = format_q_text(q['text'])
            st.markdown(f"<div class='q-title-box'>{formatted_q}</div>", unsafe_allow_html=True)
            ans_lis_p4[q_id] = st.radio(
                f"Lựa chọn câu {q_id}:",
                ["Chưa chọn"] + q['options'],
                key=f"{lesson_key}_lis_p4_{q_id}"
            )

        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns([2, 2])
        with col_btn1:
            sub_lis = st.button(f"🚀 NỘP BÀI PHẦN NGHE ({lesson_key.upper()})", key=f"sub_lis_{lesson_key}")
        with col_btn2:
            reset_lis = st.button(f"🔄 LÀM LẠI PHẦN NGHE ({lesson_key.upper()})", key=f"reset_lis_{lesson_key}")

        if reset_lis:
            st.session_state[submitted_key]['listening'] = False
            st.rerun()

        if sub_lis:
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                st.session_state[submitted_key]['listening'] = True

        if st.session_state[submitted_key].get('listening', False):
            score = 0
            wrong_q_ids = []
            
            all_listening_questions = []
            all_listening_questions.extend([(q, ans_lis_p1[q['id']], 'p1') for q in lesson_data['listening']['part1']])
            all_listening_questions.extend([(q, ans_lis_p2[q['id']], 'p2') for q in lesson_data['listening']['part2']])
            all_listening_questions.extend([(q, ans_lis_p3[q['id']], 'p3') for q in lesson_data['listening']['part3']])
            all_listening_questions.extend([(q, ans_lis_p4[q['id']], 'p4') for q in lesson_data['listening']['part4']])

            for q, user_ans, ptype in all_listening_questions:
                is_correct = False
                if ptype in ['p1', 'p2']:
                    if user_ans == q['correct']: is_correct = True
                else:
                    if user_ans.startswith(q['correct']): is_correct = True
                
                if is_correct:
                    score += 1
                else:
                    wrong_q_ids.append(q['id'])

            score_str = f"{score}/20"
            pct = (score / 20) * 100
            st.balloons()
            st.success(f"🎉 **KẾT QUẢ PHẦN NGHE BÀI {img_lesson_num}**: **{score_str}** ({pct:.0f}% câu đúng)!")
            send_results_to_gsheet(student_name, f"Bài {img_lesson_num}", "PHẦN NGHE", score_str)

            if wrong_q_ids:
                wrong_str = ", ".join([f"Câu {qid}" for qid in wrong_q_ids])
                st.warning(f"🔔 **NHẮC NHỞ HỌC VIÊN {student_name.upper()}**: Bạn có **{len(wrong_q_ids)} câu chưa đúng** ({wrong_str}). Vui lòng cuộn xuống kiểm tra chi tiết các câu làm sai và đọc kỹ Script Nghe bên dưới để rút kinh nghiệm nhé!")

            st.markdown("### 📊 CHẤM ĐIỂM CHI TIẾT VÀ SCRIPT NGHE TỪNG CÂU")
            for q, user_ans, ptype in all_listening_questions:
                qid = q['id']
                is_correct = False
                if ptype in ['p1', 'p2']:
                    if user_ans == q['correct']: is_correct = True
                else:
                    if user_ans.startswith(q['correct']): is_correct = True

                with st.expander(f"Câu {qid}: {'✅ ĐÚNG' if is_correct else '❌ SAI'} | Bạn chọn: {user_ans} | Đáp án: {q['correct']}", expanded=(not is_correct)):
                    if is_correct:
                        st.success(f"✅ **Chính xác!** Đáp án đúng là: **{q['correct']}**")
                        formatted_script = format_q_text(q['script'])
                        st.markdown(f"<div class='correct-script-box'><b>📖 Script Nghe Câu {qid}:</b><br>{formatted_script}</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"❌ **Chưa đúng!** Bạn đã chọn: `{user_ans}`. Đáp án đúng chuẩn: **{q['correct']}**")
                        formatted_script = format_q_text(q['script'])
                        st.markdown(f"<div class='wrong-script-box'><b>⚠️ Script Nghe Câu {qid} (Cần xem lại):</b><br>{formatted_script}</div>", unsafe_allow_html=True)

    # --- PHẦN ĐỌC ---
    with sec_reading:
        st.subheader("II. 阅读 - PHẦN ĐỌC (15 câu)")
        
        # Phần 1
        st.markdown("#### **第一部分 (Phần 1 - Câu 21-25): Ghép câu phù hợp (A - F)**")
        if 'ref_part1' in lesson_data['reading']:
            st.markdown("**📋 DANH SÁCH LỰA CHỌN CÂU (MỖI CÂU 1 DÒNG):**")
            ref_html = "<div class='reading-option-box'>" + "".join([f"<div class='reading-option-item'>{opt}</div>" for opt in lesson_data['reading']['ref_part1']]) + "</div>"
            st.markdown(ref_html, unsafe_allow_html=True)
        
        ans_read_p1 = {}
        for q in lesson_data['reading']['part1']:
            q_id = q['id']
            with st.container(border=True):
                formatted_q = format_q_text(q['text'])
                st.markdown(f"<div class='q-title-box'>{formatted_q}</div>", unsafe_allow_html=True)
                ans_read_p1[q_id] = st.selectbox(
                    f"Nối với đáp án câu {q_id}:",
                    ["Chưa chọn"] + q['options'],
                    key=f"{lesson_key}_read_p1_{q_id}"
                )

        st.markdown("---")
        # Phần 2
        st.markdown("#### **第二部分 (Phần 2 - Câu 26-30): Chọn từ điền vào chỗ trống (A - F)**")
        if 'ref_part2' in lesson_data['reading']:
            st.markdown("**📋 DANH SÁCH TỪ VỰNG (MỖI CÂU / TỪ 1 DÒNG):**")
            ref_html2 = "<div class='reading-option-box'>" + "".join([f"<div class='reading-option-item'>{opt}</div>" for opt in lesson_data['reading']['ref_part2']]) + "</div>"
            st.markdown(ref_html2, unsafe_allow_html=True)

        ans_read_p2 = {}
        for q in lesson_data['reading']['part2']:
            q_id = q['id']
            with st.container(border=True):
                formatted_q = format_q_text(q['text'])
                st.markdown(f"<div class='q-title-box'>{formatted_q}</div>", unsafe_allow_html=True)
                ans_read_p2[q_id] = st.selectbox(
                    f"Chọn từ câu {q_id}:",
                    ["Chưa chọn"] + q['options'],
                    key=f"{lesson_key}_read_p2_{q_id}"
                )

        st.markdown("---")
        # Phần 3
        st.markdown("#### **第三部分 (Phần 3 - Câu 31-35): Chọn đáp án đúng**")
        
        ans_read_p3 = {}
        for q in lesson_data['reading']['part3']:
            q_id = q['id']
            with st.container(border=True):
                formatted_q = format_q_text(q['text'])
                st.markdown(f"<div class='q-title-box'>{formatted_q}</div>", unsafe_allow_html=True)
                ans_read_p3[q_id] = st.radio(
                    f"Lựa chọn câu {q_id}:",
                    ["Chưa chọn"] + q['options'],
                    key=f"{lesson_key}_read_p3_{q_id}"
                )

        st.markdown("---")
        
        col_r1, col_r2 = st.columns([2, 2])
        with col_r1:
            sub_read = st.button(f"🚀 NỘP BÀI PHẦN ĐỌC ({lesson_key.upper()})", key=f"sub_read_{lesson_key}")
        with col_r2:
            reset_read = st.button(f"🔄 LÀM LẠI PHẦN ĐỌC ({lesson_key.upper()})", key=f"reset_read_{lesson_key}")

        if reset_read:
            st.session_state[submitted_key]['reading'] = False
            st.rerun()

        if sub_read:
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                st.session_state[submitted_key]['reading'] = True

        if st.session_state[submitted_key].get('reading', False):
            score = 0
            wrong_q_ids = []
            
            all_reading_questions = []
            all_reading_questions.extend([(q, ans_read_p1[q['id']], 'p1') for q in lesson_data['reading']['part1']])
            all_reading_questions.extend([(q, ans_read_p2[q['id']], 'p2') for q in lesson_data['reading']['part2']])
            all_reading_questions.extend([(q, ans_read_p3[q['id']], 'p3') for q in lesson_data['reading']['part3']])

            for q, user_ans, ptype in all_reading_questions:
                is_correct = False
                if ptype == 'p1':
                    if user_ans == q['correct']: is_correct = True
                else:
                    if user_ans.startswith(q['correct']): is_correct = True
                
                if is_correct: score += 1
                else: wrong_q_ids.append(q['id'])

            score_str = f"{score}/15"
            pct = (score / 15) * 100
            st.balloons()
            st.success(f"🎉 **KẾT QUẢ PHẦN ĐỌC BÀI {img_lesson_num}**: **{score_str}** ({pct:.0f}% câu đúng)!")
            send_results_to_gsheet(student_name, f"Bài {img_lesson_num}", "PHẦN ĐỌC", score_str)

            if wrong_q_ids:
                wrong_str = ", ".join([f"Câu {qid}" for qid in wrong_q_ids])
                st.warning(f"🔔 **NHẮC NHỞ HỌC VIÊN {student_name.upper()}**: Bạn có **{len(wrong_q_ids)} câu chưa đúng** ({wrong_str}). Vui lòng kiểm tra lại đáp án từng câu bên dưới!")

            st.markdown("### 📊 CHẤM ĐIỂM CHI TIẾT PHẦN ĐỌC")
            for q, user_ans, ptype in all_reading_questions:
                qid = q['id']
                is_correct = False
                if ptype == 'p1':
                    if user_ans == q['correct']: is_correct = True
                else:
                    if user_ans.startswith(q['correct']): is_correct = True

                with st.expander(f"Câu {qid}: {'✅ ĐÚNG' if is_correct else '❌ SAI'} | Bạn chọn: {user_ans} | Đáp án chuẩn: {q['correct']}", expanded=(not is_correct)):
                    if is_correct:
                        st.success(f"✅ **Chính xác!** Đáp án đúng là: **{q['correct']}**")
                    else:
                        st.error(f"❌ **Chưa đúng!** Bạn đã chọn: `{user_ans}`. Đáp án chuẩn: **{q['correct']}**")

    # --- PHẦN VIẾT ---
    with sec_writing:
        st.subheader("III. 书写 - PHẦN VIẾT (10 câu)")
        st.warning("⚠️ **Lưu ý**: Phần viết yêu cầu chính xác đến từng dấu câu (dấu chấm 。, dấu phẩy ，).")

        st.markdown("#### **第一部分 (Phần 1 - Câu 36-40): Sắp xếp từ thành câu**")
        ans_write_p1 = {}
        for q in lesson_data['writing']['part1']:
            q_id = q['id']
            with st.container(border=True):
                st.markdown(f"**Câu {q_id}:** {q['words']}")
                ans_write_p1[q_id] = st.text_input(
                    f"Nhập câu hoàn chỉnh cho câu {q_id}:",
                    key=f"{lesson_key}_write_p1_{q_id}"
                ).strip()

        st.markdown("---")
        st.markdown("#### **第二部分 (Phần 2 - Câu 41-45): Xem phiên âm, viết chữ Hán**")
        ans_write_p2 = {}
        for q in lesson_data['writing']['part2']:
            q_id = q['id']
            with st.container(border=True):
                formatted_q = format_q_text(q['text'])
                st.markdown(f"<div class='q-title-box'>{formatted_q}</div>", unsafe_allow_html=True)
                ans_write_p2[q_id] = st.text_input(
                    f"Nhập chữ Hán cho câu {q_id}:",
                    key=f"{lesson_key}_write_p2_{q_id}"
                ).strip()

        st.markdown("---")
        
        col_w1, col_w2 = st.columns([2, 2])
        with col_w1:
            sub_write = st.button(f"🚀 NỘP BÀI PHẦN VIẾT ({lesson_key.upper()})", key=f"sub_write_{lesson_key}")
        with col_w2:
            reset_write = st.button(f"🔄 LÀM LẠI PHẦN VIẾT ({lesson_key.upper()})", key=f"reset_write_{lesson_key}")

        if reset_write:
            st.session_state[submitted_key]['writing'] = False
            st.rerun()

        if sub_write:
            if not student_name:
                st.error("⚠️ Vui lòng nhập Họ tên ở đầu trang trước khi nộp bài!")
            else:
                st.session_state[submitted_key]['writing'] = True

        if st.session_state[submitted_key].get('writing', False):
            score = 0
            wrong_q_ids = []
            
            all_writing_questions = []
            all_writing_questions.extend([(q, ans_write_p1[q['id']], 'p1') for q in lesson_data['writing']['part1']])
            all_writing_questions.extend([(q, ans_write_p2[q['id']], 'p2') for q in lesson_data['writing']['part2']])

            for q, user_ans, ptype in all_writing_questions:
                is_correct = False
                if ptype == 'p1':
                    if user_ans in q['valid_answers']: is_correct = True
                else:
                    if user_ans == q['correct']: is_correct = True
                
                if is_correct: score += 1
                else: wrong_q_ids.append(q['id'])

            score_str = f"{score}/10"
            pct = (score / 10) * 100
            st.balloons()
            st.success(f"🎉 **KẾT QUẢ PHẦN VIẾT BÀI {img_lesson_num}**: **{score_str}** ({pct:.0f}% câu đúng)!")
            send_results_to_gsheet(student_name, f"Bài {img_lesson_num}", "PHẦN VIẾT", score_str)

            if wrong_q_ids:
                wrong_str = ", ".join([f"Câu {qid}" for qid in wrong_q_ids])
                st.warning(f"🔔 **NHẮC NHỞ HỌC VIÊN {student_name.upper()}**: Bạn có **{len(wrong_q_ids)} câu chưa đúng** ({wrong_str}). Vui lòng đối chiếu với đáp án chuẩn bên dưới!")

            st.markdown("### 📊 CHẤM ĐIỂM CHI TIẾT PHẦN VIẾT")
            for q, user_ans, ptype in all_writing_questions:
                qid = q['id']
                is_correct = False
                if ptype == 'p1':
                    if user_ans in q['valid_answers']: is_correct = True
                    correct_val = q['valid_answers'][0]
                else:
                    if user_ans == q['correct']: is_correct = True
                    correct_val = q['correct']

                with st.expander(f"Câu {qid}: {'✅ ĐÚNG' if is_correct else '❌ SAI'} | Câu trả lời của bạn: {user_ans if user_ans else '(Chưa nhập)'} | Đáp án chuẩn: {correct_val}", expanded=(not is_correct)):
                    if is_correct:
                        st.success(f"✅ **Chính xác!** Đáp án đúng: **{correct_val}**")
                    else:
                        st.error(f"❌ **Chưa đúng!** Bạn đã nhập: `{user_ans}`. Đáp án chuẩn: **{correct_val}**")

# BÀI MỚI NHẤT Ở TAB ĐẦU TIÊN
with tabs[0]:
    render_lesson_ui("bai5", LESSON_41_DATA, "05", "5")

with tabs[1]:
    render_lesson_ui("bai4", LESSON_40_DATA, "04", "4")

with tabs[2]:
    render_lesson_ui("bai3", LESSON_39_DATA, "03", "3")

with tabs[3]:
    render_lesson_ui("bai2", LESSON_38_DATA, "02", "2")

st.markdown('<div class="footer-teacher">黄宝玉老师</div>', unsafe_allow_html=True)
