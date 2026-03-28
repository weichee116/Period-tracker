import streamlit as st
from datetime import datetime, timedelta

# --- 第一步：页面基础设置 ---
st.set_page_config(page_title="女性健康与周期助手", page_icon="🌸", layout="centered")

# --- 第二步：健康知识库字典 ---
health_advice = {
    "月经期": {
        "eat": "富含铁质的食物（菠菜、红肉、猪肝）、黑巧克力（缓解情绪）。",
        "drink": "生姜红糖水、温热水，绝对忌冷饮。",
        "tips": "🩸 避免剧烈运动（如跳跃、负重），注意腹部保暖，保证充足睡眠。"
    },
    "滤泡期": { 
        "eat": "优质蛋白（鸡胸肉、豆腐、鸡蛋）、深绿色蔬菜。",
        "drink": "柠檬水、绿茶（帮助抗氧化）。",
        "tips": "🌿 此时雌激素上升，体力恢复，适合开始进行中高强度的有氧运动或力量训练。"
    },
    "排卵期": {
        "eat": "抗氧化食物（蓝莓、草莓）、坚果（核桃、葵花籽）。",
        "drink": "保持充足水分（每日至少 2L）。",
        "tips": "✨ 精力最旺盛的时期，是备孕或安排高强度工作、社交的黄金期。"
    },
    "黄体期": { 
        "eat": "复合碳水（地瓜、全麦面包）、富含镁的食物（香蕉、深海鱼）。",
        "drink": "洋甘菊茶、热牛奶（有助于缓解经前焦虑和助眠）。",
        "tips": "🍂 可能会出现经前综合征 (PMS)，容易暴躁疲劳。注意减少盐分摄入以防水肿，适合做瑜伽等舒缓运动。"
    }
}

# --- 第三步：界面与计算逻辑 ---
st.title("🌸 女性经期与排卵预测助手")
st.sidebar.header("输入个人数据")

# 侧边栏输入
last_period = st.sidebar.date_input("最后一次月经开始日期", datetime.now())
cycle_length = st.sidebar.number_input("平均周期长度 (天)", min_value=21, max_value=45, value=28)
period_days = st.sidebar.number_input("经期持续天数", min_value=2, max_value=10, value=5)

# 核心计算
next_period = last_period + timedelta(days=cycle_length)
ovulation_day = next_period - timedelta(days=14)
fertile_window_start = ovulation_day - timedelta(days=5)
fertile_window_end = ovulation_day + timedelta(days=1)

today = datetime.now().date()

# 显示预测结果
col1, col2 = st.columns(2)
with col1:
    st.metric("🩸 预测下次月经", str(next_period))
with col2:
    st.metric("✨ 预测排卵日", str(ovulation_day))

st.divider()

# 判断当前处于哪个阶段
if last_period <= today <= (last_period + timedelta(days=period_days-1)):
    status = "月经期"
elif fertile_window_start <= today <= fertile_window_end:
    status = "排卵期"
elif last_period + timedelta(days=period_days) <= today < fertile_window_start:
    status = "滤泡期"
else:
    status = "黄体期"

# 显示对应的健康建议
st.subheader(f"📅 当前阶段：{status}")
st.write(f"**🍽️ 推荐吃什么：** {health_advice[status]['eat']}")
st.write(f"**🍵 推荐喝什么：** {health_advice[status]['drink']}")
st.info(f"**💡 专业建议：** {health_advice[status]['tips']}")


# --- 第四步：添加到手机日历功能 (.ics 生成) ---
st.divider()
st.subheader("⏰ 设置手机提醒")
st.write("点击下方按钮，将重要日子直接加入你的手机自带日历！")

# 定义一个生成日历文件的函数
def create_ics(title, event_date, description):
    # 将日期转换为日历标准格式 (YYYYMMDD)
    date_str = event_date.strftime("%Y%m%d")
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;VALUE=DATE:{date_str}
SUMMARY:{title}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR"""
    return ics_content

col3, col4 = st.columns(2)

# 按钮 1：提醒下次月经
with col3:
    period_ics = create_ics(
        "🩸 预计月经期", 
        next_period, 
        f"记得准备卫生用品，多喝温水！建议：{health_advice['月经期']['tips']}"
    )
    st.download_button(
        label="📅 添加【下次月经】",
        data=period_ics,
        file_name="next_period.ics",
        mime="text/calendar"
    )

# 按钮 2：提醒排卵日
with col4:
    ovulation_ics = create_ics(
        "✨ 预计排卵日", 
        ovulation_day, 
        f"今天是排卵日！建议：{health_advice['排卵期']['tips']}"
    )
    st.download_button(
        label="📅 添加【排卵日】",
        data=ovulation_ics,
        file_name="ovulation_day.ics",
        mime="text/calendar"
    )