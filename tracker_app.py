import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# --- 1. 页面基础设置 ---
st.set_page_config(page_title="女性健康助手 专业版", page_icon="🌸", layout="centered")

# --- 2. 文件路径配置 ---
USERS_FILE = "users.csv"
DATA_FILE = "health_log.csv"

# --- 3. 辅助函数 ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username", "password_hash"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["username", "type", "date", "menses_length", "mood", "symptoms", "notes"]).to_csv(DATA_FILE, index=False)

init_files()

# --- 4. 医生健康知识库（专业版） ---
doctor_advice = {
    "月经期": {
        "header": "🩸 月经期：关怀与补给 (第1-5天，假设)",
        "diet": ["铁质补充： spinach、红肉、猪肝、黑木耳", "温热饮食：生姜红糖水、热牛奶", "Omega-3抗炎：三文鱼、核桃"],
        "exercise": ["轻度有氧：慢走、舒缓冥想", "专注于拉伸：避免剧烈跳跃或负重训练", "倾听身体：不适即止，多休息"],
        "medical": ["腹部保暖：使用暖宝宝或热水袋", "充足睡眠：保证 7-8 小时高质量睡眠", "卫生注意：勤换卫生用品"]
    },
    "滤泡期": {
        "header": "🌿 滤泡期：能量恢复 (经期结束 - 排卵前)",
        "diet": ["优质蛋白：鸡肉、鱼肉、豆腐", "抗氧化蔬果：蓝莓、西兰花", "复合碳水：地瓜、全麦面包"],
        "exercise": ["恢复训练：可尝试慢跑、游泳", "力量训练：雌激素上升，适合增加中等强度负荷", "精力充沛：适合开始进行有氧和无氧结合训练"],
        "medical": ["心态积极：适合安排复杂、具挑战性的工作", "补充维生素D与钙质", "监测体温：如有备孕需求"]
    },
    "排卵期": {
        "header": "✨ 排卵期：黄金时刻 (预测排卵日前后各5天)",
        "diet": ["叶酸补给：芦笋、鸡蛋、深绿色蔬菜", "抗氧化：草莓、坚果", "保持充足水分：每日 2L+ 水"],
        "exercise": ["精力最旺盛：适合高强度运动 (HIIT、力量训练)", "社交运动：参加团队运动或比赛", "注意运动防护，避免受伤"],
        "medical": ["黄金受孕窗口 (如有意愿)", "心情放松：心态对排卵及受孕至关重要", "留意身体：可能有轻微下腹微胀感"]
    },
    "黄体期": {
        "header": "🍂 黄体期：舒缓与准备 (排卵后 - 下次经期前)",
        "diet": ["复合碳水：全麦面包、糙米，缓解烦躁", "富含镁食物：香蕉、深海鱼，减缓PMS", "低盐饮食：减少水肿风险"],
        "exercise": ["中低强度：瑜伽、普拉提、游泳", "舒缓身心：不适合进行新的高负荷挑战", "注重放松：缓解经前焦虑"],
        "medical": ["留意经前综合征 (PMS)：如乳房胀痛、情绪波动", "保持良好作息：避免熬夜", "调整心态：做好下次经期的身心准备"]
    }
}

# --- 5. 状态管理初始化 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ==========================================
# 模块 A：用户注册与登录系统
# ==========================================
def login_register_page():
    st.title("🌸 女性健康助手 专业版")
    st.write("欢迎！请登录或注册以管理您的专属动态健康数据。")
    
    tab1, tab2 = st.tabs(["🔑 登录", "📝 注册"])
    
    with tab1:
        st.subheader("用户登录")
        login_user = st.text_input("用户名", key="login_user")
        login_pwd = st.text_input("密码", type="password", key="login_pwd")
        if st.button("登录"):
            users_df = pd.read_csv(USERS_FILE)
            if login_user in users_df['username'].values:
                stored_hash = users_df.loc[users_df['username'] == login_user, 'password_hash'].values[0]
                if make_hash(login_pwd) == stored_hash:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.success("登录成功！正在跳转...")
                    st.rerun()
                else:
                    st.error("密码错误！")
            else:
                st.error("用户名不存在！")

    with tab tabs:
        st.subheader("新用户注册")
        reg_user = st.text_input("设置用户名", key="reg_user")
        reg_pwd = st.text_input("设置密码", type="password", key="reg_pwd")
        reg_pwd2 = st.text_input("确认密码", type="password", key="reg_pwd2")
        if st.button("注册"):
            users_df = pd.read_csv(USERS_FILE)
            if reg_user in users_df['username'].values:
                st.warning("该用户名已被注册，请换一个。")
            elif reg_pwd != reg_pwd2:
                st.error("两次输入的密码不一致！")
            elif len(reg_user) < 3 or len(reg_pwd) < 4:
                st.warning("用户名至少3位，密码至少4位。")
            else:
                new_user = pd.DataFrame({"username": [reg_user], "password_hash": [make_hash(reg_pwd)]})
                pd.concat([users_df, new_user], ignore_index=True).to_csv(USERS_FILE, index=False)
                st.success("注册成功！请切换到登录标签页进行登录。")

# ==========================================
# 模块 B：主控面板 (登录后可见)
# ==========================================
def main_dashboard():
    # 侧边栏：用户信息与个性化设置
    st.sidebar.title(f"👤 您好, {st.session_state.current_user}")
    
    # 核心设置：设置您的默认经期长度（计算阶段用）
    user_menses_len = st.sidebar.number_input("您的平均经期持续天数", min_value=2, max_value=10, value=5, help="用于更精确地为您划分生理阶段。")
    
    if st.sidebar.button("退出登录"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    st.title("📊 我的健康数据看板")
    
    # 加载当前用户的数据
    df = pd.read_csv(DATA_FILE)
    user_data = df[df['username'] == st.session_state.current_user].copy()
    user_data['date'] = pd.to_datetime(user_data['date'])
    
    # 筛选出所有的“月经开始日”记录，并按时间排序
    period_records = user_data[user_data['type'] == 'period_start'].sort_values('date')
    
    # ==========================================
    # 功能 1：周期趋势折线图 (Chart Section)
    # ==========================================
    if len(period_records) >= 2:
        st.subheader("📊 周期趋势图")
        
        # 计算相邻两次月经的间隔天数（真正的周期）
        trends_df = period_records.copy()
        trends_df['cycle_days'] = trends_df['date'].diff().dt.days
        trends_df = trends_df.dropna() # 删掉第一个没有差值的记录
        
        if not trends_df.empty:
            # 准备画图数据
            chart_data = trends_df[['date', 'cycle_days']].copy()
            chart_data.columns = ['日期', '周期天数']
            
            # 使用简单的 Streamlit 折线图展示
            # 如果想展示最新的周期在右侧，数据需要按日期升序
            st.line_chart(chart_data.set_index('日期'))
            
            # 显示简要统计
            col_t1, col_t2 = st.columns(2)
            col_t1.caption(f"📉 最近一次周期：{int(trends_df['cycle_days'].iloc[-1])} 天")
            col_t2.caption(f"📈 历史最短/最长：{int(trends_df['cycle_days'].min())} / {int(trends_df['cycle_days'].max())} 天")
        else:
            st.info("数据处理中，稍后显示趋势。")
    
    st.divider()

    # ==========================================
    # 核心逻辑：动态计算平均周期与预测
    # ==========================================
    avg_cycle = 28 # 默认值
    if len(period_records) >= 2:
        intervals = period_records['date'].diff().dt.days.dropna()
        avg_cycle = int(intervals.mean()) # 取平均值
    
    # --- 顶栏：记录新的月经开始日 ---
    with st.expander("🩸 记录新的月经开始日", expanded=(len(period_records)==0)):
        new_period_date = st.date_input("选择本次月经第一天的日期", datetime.now())
        if st.button("保存月经日期"):
            if not period_records.empty and pd.to_datetime(new_period_date) in period_records['date'].values:
                st.warning("这一天已经记录过啦！")
            else:
                new_record = pd.DataFrame({
                    "username": [st.session_state.current_user],
                    "type": ["period_start"],
                    "date": [new_period_date.strftime("%Y-%m-%d")],
                    "menses_length": [0], "mood": [""], "symptoms": [""], "notes": [""]
                })
                pd.concat([df, new_record], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.success("记录成功！正在更新预测...")
                st.rerun()

    st.divider()

    # --- 预测面板与每日医生建议 ---
    today = datetime.now().date()
    current_phase = ""
    
    st.subheader("🔮 周期预测")
    if len(period_records) == 0:
        st.info("💡 请先在上方记录至少一次您的月经开始日期，以启动预测功能。记录两次以上预测会更准确哦！")
    else:
        last_period_date = period_records['date'].iloc[-1].date()
        next_period = last_period_date + timedelta(days=avg_cycle)
        ovulation_day = next_period - timedelta(days=14)
        fertile_start = ovulation_day - timedelta(days=5)
        fertile_end = ovulation_day + timedelta(days=1)
        
        # 显示关键数据米
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("最后一次记录", str(last_period_date))
        col_p2.metric("当前个人平均周期", f"{avg_cycle} 天", "动态计算" if len(period_records)>=2 else "默认")
        col_p3.metric("✨ 预测下次排卵日", str(ovulation_day))
        
        st.success(f"**🩸 预测下次月经日：{next_period}**")
        st.divider()

        # ==========================================
        # 功能 2：👨🏻‍⚕️ 医生每日建议 (Daily Companion)
        # ==========================================
        # 精确划分当前阶段
        if last_period_date <= today < (last_period_date + timedelta(days=user_menses_len)):
            current_phase = "月经期"
        elif fertile_start <= today <= fertile_end:
            current_phase = "排卵期"
        elif (last_period_date + timedelta(days=user_menses_len)) <= today < fertile_start:
            current_phase = "滤泡期"
        else:
            current_phase = "黄体期"
        
        advice = doctor_advice[current_phase]
        
        st.subheader(f"👨🏻‍⚕️ 今日健康陪伴：{advice['header']}")
        st.write("您的专属数字医生已为您准备了今日的关怀建议：")
        
        # 使用信息框优雅地展示不同类别的建议
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.expander("🍽️ **饮食推荐**", expanded=True):
                for item in advice['diet']: st.write(f"- {item}")
        with c2:
            with st.expander("🏃🏻‍♀️ **运动方案**", expanded=True):
                for item in advice['exercise']: st.write(f"- {item}")
        with c3:
            with st.expander("💡 **医学生活贴士**", expanded=True):
                for item in advice['medical']: st.write(f"- {item}")
        st.divider()


    # --- 每日日记功能 ---
    st.subheader("📝 每日健康日记")
    with st.form("daily_log_form"):
        log_date = st.date_input("日记日期", datetime.now())
        mood = st.select_slider("今日心情", options=["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"], value="😐 平静")
        symptoms = st.multiselect("身体症状", ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"])
        notes = st.text_area("其他备注")
        if st.form_submit_button("保存日记"):
            new_log = pd.DataFrame({
                "username": [st.session_state.current_user], "type": ["daily_log"], "date": [log_date.strftime("%Y-%m-%d")],
                "menses_length": [0], "mood": [mood], "symptoms": [", ".join(symptoms)], "notes": [notes]
            })
            pd.concat([df, new_log], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("日记保存成功！正在更新历史记录...")
            st.rerun()

    # --- 历史数据显示 ---
    st.divider()
    with st.expander("📖 查看我的历史记录 (可滚动)"):
        display_df = user_data[['date', 'type', 'mood', 'symptoms', 'notes']].sort_values('date', ascending=False)
        # 把 type 翻译成中文好看些
        display_df['type'] = display_df['type'].replace({'period_start': '🩸 月经开始', 'daily_log': '📝 每日日记'})
        st.dataframe(display_df, use_container_width=True, hide_index=True)


# ==========================================
# 页面路由控制
# ==========================================
if st.session_state.logged_in:
    main_dashboard()
else:
    login_register_page()