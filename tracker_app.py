import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os

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
st.write("⏰ **设置手机提醒：** 点击下方按钮，将重要日子直接加入你的手机自带日历！")

def create_ics(title, event_date, description):
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
with col3:
    period_ics = create_ics("🩸 预计月经期", next_period, f"建议：{health_advice['月经期']['tips']}")
    st.download_button("📅 添加【下次月经】", data=period_ics, file_name="next_period.ics", mime="text/calendar")
with col4:
    ovulation_ics = create_ics("✨ 预计排卵日", ovulation_day, f"建议：{health_advice['排卵期']['tips']}")
    st.download_button("📅 添加【排卵日】", data=ovulation_ics, file_name="ovulation_day.ics", mime="text/calendar")


# --- 第五步：每日症状与心情记录 ---
st.divider()
st.subheader("📝 每日症状与心情日记")

# 定义保存数据的文件名
DATA_FILE = "symptoms_log.csv"

# 初始化或读取历史数据
if os.path.exists(DATA_FILE):
    df_history = pd.read_csv(DATA_FILE)
else:
    df_history = pd.DataFrame(columns=["日期", "心情", "症状", "备注"])

# 记录表单 (使用 expander 可以折叠，让界面更整洁)
with st.expander("➕ 添加 / 更新今日记录", expanded=True):
    with st.form("symptom_form"):
        record_date = st.date_input("记录日期", today)
        mood = st.select_slider("今日心情", options=["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"], value="😐 平静")
        symptoms = st.multiselect("身体症状 (可多选)", ["腹痛", "头痛", "胸部胀痛", "疲劳", "情绪波动", "长痘", "嗜睡", "腰酸", "无不适"])
        notes = st.text_area("其他备注 / 饮食日记", placeholder="今天吃了什么？感觉怎么样？")
        
        submitted = st.form_submit_button("💾 保存记录")
        
        if submitted:
            # 创建新数据行
            new_data = pd.DataFrame({
                "日期": [str(record_date)],
                "心情": [mood],
                "症状": [", ".join(symptoms) if symptoms else "无"],
                "备注": [notes]
            })
            
            # 合并新数据并保存到本地 CSV 文件
            df_history = pd.concat([df_history, new_data], ignore_index=True)
            # 按日期倒序排列（最新的在最上面），并去除同一天的重复记录（保留最新的）
            df_history = df_history.drop_duplicates(subset=['日期'], keep='last').sort_values(by="日期", ascending=False)
            df_history.to_csv(DATA_FILE, index=False)
            
            st.success("✅ 记录保存成功！请刷新页面查看最新表格。")

# 显示历史记录表格
if not df_history.empty:
    st.write("📖 **你的历史记录：**")
    # 使用 dataframe 展示，隐藏左侧的默认数字索引
    st.dataframe(df_history, use_container_width=True, hide_index=True)