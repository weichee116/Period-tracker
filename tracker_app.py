import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 第一步：可愛 Tone 调全覆盖 ( image_5.png 設計理念) ---
# 設置頁面屬性，使用可愛的 emoji 🤔 🤔 🤔 和柔和的顏色，並參考 `image_5.png` 的標題
st.set_page_config(page_title="野原家·小白同款·健康週期助手", page_icon="🍑", layout="centered")

# --- 第二步：醫生 Tone 调建議庫 (合併專業內容並注入 emoji 😂 Peach 哭哭 🤔) ---
health_advice_pro = {
    "月經期": {
        "header": "🩸 月经期：关怀时刻 🤔",
        "diet": ["铁质补充： spinach、红肉、木耳", "温热饮食：生姜红糖水、温热水", "Omega-3抗炎：三文鱼、核桃", "黑巧克力（緩解情緒）。"],
        "exercise": ["轻度有氧：慢走、冥想", "专注于拉伸：避免剧烈", "倾听身体：不适即止，多休息"],
        "medical": ["腹部保暖：暖宝宝或热水袋", "充足睡眠：保证 7-8 小时高质量睡眠", "卫生注意：勤换用品"]
    },
    "排卵期": {
        "header": "✨ 排卵期：黄金时刻 🤔",
        "diet": ["抗氧化食物：蓝莓、坚果", "优质蛋白：鸡肉、鱼肉", "充足水分：每日 2L+ 水"],
        "exercise": ["精力充沛：适合强度有氧", "力量训练：雌激素上升，适合增加强度"],
        "medical": ["受孕窗口：如有备孕需求", "心态放松：留意身體訊號 🤔", "留意 PMS：情绪波动、乳房胀痛"]
    },
    "濾泡期": {
        "header": "🌿 滤泡期：能量恢复 🤔",
        "diet": ["优质蛋白：雞胸肉、豆腐", "深绿色蔬菜", "维生素C：柑橘类水果"],
        "exercise": ["恢复训练：游泳、有氧", "结合训练：逐步增加強度"],
        "medical": ["能量回升：適合開始新項目 🤔", "补充维生素D与钙质"]
    },
    "黃體期": {
        "header": "🍂 黄体期：舒缓与准备 🤔",
        "diet": ["复合碳水：糙米、全麦", "富含镁食物：香蕉、深海鱼", "减少盐分：减少浮肿"],
        "exercise": ["舒缓运动：瑜伽、普拉提", "放松身心：注意減少壓力"],
        "medical": ["PMS 提醒：心情可能會低落😭", "作息规律：避免熬夜"]
    }
}


# --- 第三步：界面與數據計算邏輯 (適合手機的手機排版) ---
st.sidebar.title("🌸 输入你的秘密數據")
st.sidebar.caption("小白會好好保管哦～ 😂 🤔 😭")

last_period = st.sidebar.date_input("最后一次月经开始日期", datetime.now())
cycle_days = st.sidebar.number_input("平均周期长度 (天)", min_value=21, max_value=45, value=28)
menses_days = st.sidebar.number_input("经期持续天数", min_value=2, max_value=10, value=5)

# 核心計算
next_period = last_period + timedelta(days=cycle_days)
ovulation_day = next_period - timedelta(days=14)
fertile_window_start = ovulation_day - timedelta(days=5)
fertile_window_end = ovulation_day + timedelta(days=1)

today = datetime.now().date()

# 核心數據米 (適合手機的突出顯示)
col1, col2 = st.columns(2)
with col1:
    st.metric("🩸 下次經期預測", str(next_period))
with col2:
    st.metric("✨ 下次排卵日預測", str(ovulation_day))

st.divider()

# 精確劃分生理階段
if last_period <= today <= (last_period + timedelta(days=menses_days - 1)):
    status = "月經期"
elif fertile_window_start <= today <= fertile_window_end:
    status = "排卵期"
elif last_period + timedelta(days=menses_days) <= today < fertile_window_start:
    status = "濾泡期"
else:
    status = "黃体期"

# 顯示大字標題和小白的提醒 (美伢媽媽 Tone 調)
st.subheader(f"📅 當前階段：野原家健康專家小白推薦 ({status}) 😂 🤔 🍑")
st.write("小白說要注意身體哦～🤔")


# --- 第四步：界面與建議卡片 (UI 核心：垂直堆疊 Expander，參考 image_5.png) ---
# 使用 st.columns 在寬屏上並排展示，但在手機上會自動堆疊為垂直單列
c1, c2, c3 = st.columns(3)

with c1:
    with st.expander("🍽️ **小白推薦·飲食指南** (🤔)"):
        st.write("小白數據處理中... 😂")
        for item in health_advice_pro[status]['diet']:
            st.write(f"- {item}")
        st.caption("😂 🍑 😭 小白喜歡這個哦～")

with c2:
    with st.expander("🏃🏻‍♀️ **小白推薦·運動方案** (🍑)"):
        st.write("小白也喜歡運動哦～ 🍑")
        for item in health_advice_pro[status]['exercise']:
            st.write(f"- {item}")
        st.caption("😂 🍑 😭 动起来！")

with c3:
    with st.expander("💡 **小白提醒·醫學醫學生活医学贴士** (😭)"):
        st.write("小白關心你哦～ 😭")
        for item in health_advice_pro[status]['medical']:
            st.write(f"- {item}")
        st.caption("😂 🍑 😭 注意啦！")

# --- 第五步：日誌與功能 (小白提醒) ---
st.divider()
st.subheader("📋 小白數據處理日誌")
st.write("美伢媽媽說要記清楚哦～ 🤔 🤔 🤔")

# 這部分你可以加入用戶註冊和日誌記錄代碼
# 為保持 UI 代碼簡潔，這裡只保留一個簡單的 Expander 用戶日誌展示
with st.expander("📖 查看用戶日誌... 🤔"):
    st.write("😂 🍑 😭 日誌處理中...")
    # st.dataframe(pd.DataFrame(columns=["日期", "狀態", "備忘录"])) # 示例

st.sidebar.divider()
st.sidebar.caption("小白與你一起加油哦！😂 🍑 😭")