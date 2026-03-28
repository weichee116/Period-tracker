import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# ==========================================
# 🌸 全新 UI 优化：CSS 样式注入
# ==========================================
# 我们在这里通过 CSS 给 Streamlit“穿新衣”：
# 1. 设置可爱的字体和软萌的马卡龙色系（粉、蓝、黄）。
# 2. 所有的卡片、按钮、输入框都加上圆角（rounded）。
# 3. 增强布局清晰度。
# 4. 优化卡片阴影效果，更有质感。

st.set_page_config(page_title="野原家·健康助手", page_icon="🍑", layout="centered")

# 定义一个全 App 统一的可爱 tone 调 CSS
st.markdown("""
<style>
    /* 引入一个更圆润可爱的 Google 字体 */
    @import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&display=swap');

    /* 全局基础设置 */
    html, body, [data-testid="stSidebar"], .stApp {
        font-family: 'ZCOOL KuaiLe', 'Microsoft YaHei', sans-serif !important;
        background-color: #FFF5F7 !important; /* 超浅粉色背景 */
    }

    /* 标题样式：加大，更可爱 */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'ZCOOL KuaiLe', sans-serif !important;
        color: #E91E63 !important; /* 粉红 Accent */
        text-align: center;
        margin-top: 10px;
    }

    /* 侧边栏：改变背景色和文字 */
    [data-testid="stSidebar"] {
        background-color: #E1F5FE !important; /* 超浅蓝色侧边栏 */
    }
    [data-testid="stSidebar"] * {
        color: #0277BD !important;
    }

    /* 按钮样式：圆角，可爱色，加大 */
    .stButton>button {
        background-color: #FF80AB !important; /* 亮粉色 */
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        width: 100%;
        font-size: 18px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF4081 !important; /* 悬停变色 */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }

    /* 卡片式容器（Expander 和 Metric Card）：圆角，阴影，亮色 */
    .stExpander {
        background-color: #FFFFFF;
        border-radius: 15px !important;
        border: 2px solid #F8BBD0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        margin-bottom: 20px;
    }
    [data-testid="stMetricValue"] {
        font-family: 'ZCOOL KuaiLe', sans-serif !important;
        color: #FF4081;
    }

    /* 每日信息框：改为黄色可爱风格 */
    [data-testid="stInfo"] {
        background-color: #FFF9C4;
        color: #827717;
        border-radius: 15px !important;
        border: 2px dashed #FFF176 !important;
    }

    /* 折线图配色（虽然不完美，但尽量调整氛围） */
    canvas[data-testid="stDataFrame_chart"] {
        color: #E91E63; 
    }

    /* 输入框样式优化 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 15px !important;
    }

    /* 心情滑块颜色优化 */
    div.stSlider>div>div {
        color: #E91E63;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. 文件路径配置 & 辅助函数 (保持原样) ---
USERS_FILE = "users.csv"
DATA_FILE = "health_log.csv"

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username", "password_hash"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["username", "type", "date", "menses_length", "mood", "symptoms", "notes"]).to_csv(DATA_FILE, index=False)

init_files()

# --- 3. 医生健康知识库（专业建议，融入可爱 Tone 调） ---
doctor_advice = {
    "月经期": {
        "header": "🩸 月经期：关怀时刻 (第1-5天，假设) 😂",
        "diet": ["铁质补充：菠菜、红肉、猪肝、黑木耳", "温热饮食：生姜红糖水、热牛奶", "Omega-3抗炎：三文鱼、核桃"],
        "exercise": ["轻度有氧：慢走、舒缓冥想", "专注于拉伸：避免剧烈跳跃", "倾听身体：不适即止，多休息"],
        "medical": ["腹部保暖：使用暖宝宝或热水袋", "充足睡眠：保证 7-8 小时高质量睡眠", "卫生注意：勤换卫生用品"]
    },
    "滤泡期": {
        "header": "🌿 滤泡期：能量恢复 (经期结束 - 排卵前) 🤔",
        "diet": ["优质蛋白：鸡肉、鱼肉、豆腐", "抗氧化蔬果：蓝莓、西兰花", "复合碳水：地瓜、全麦面包"],
        "exercise": ["恢复训练：可尝试慢跑、游泳", "力量训练：雌激素上升，适合增加中等强度负荷", "精力充沛：适合开始进行结合训练"],
        "medical": ["心态积极：适合安排复杂、具挑战性的工作", "补充维生素D与钙质", "监测体温：如有备孕需求"]
    },
    "排卵期": {
        "header": "✨ 排卵期：黄金时刻 (预测排卵日前后各5天) 🍑",
        "diet": ["叶酸补给：芦笋、鸡蛋、深绿色蔬菜", "抗氧化：草莓、坚果", "保持充足水分：每日 2L+ 水"],
        "exercise": ["精力最旺盛：适合高强度运动 (HIIT、力量训练)", "社交运动：参加团队运动或比赛", "注意运动防护，避免受伤"],
        "medical": ["黄金受孕窗口 (如有意愿)", "心情放松：心态对排卵及受孕至关重要", "留意身体：可能有轻微下腹微胀感"]
    },
    "黄体期": {
        "header": "🍂 黄体期：舒缓与准备 (排卵后 - 下次经期前) 😭",
        "diet": ["复合碳水：全麦面包、糙米，缓解烦躁", "富含镁食物：香蕉、深海鱼，减缓PMS", "低盐饮食：减少水肿风险"],
        "exercise": ["中低强度：瑜伽、普拉提、游泳", "舒缓身心：不适合进行新的高负荷挑战", "注重放松：缓解经前焦虑"],
        "medical": ["留意经前综合征 (PMS)：如乳房胀痛、情绪波动", "保持良好作息：避免熬夜", "调整心态：做好下次经期的身心准备"]
    }
}

# --- 4. 状态管理初始化 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ==========================================
# 模块 A：用户注册与登录系统 (UI 优化版)
# ==========================================
def login_register_page():
    # 顶部加一个可爱的 Shin-chan Header
    # 如果有 URL，可以这里加一张 Shin-chan 挥手的图片链接
    # st.image("https://... shin_chan_header.png", use_container_width=True)
    
    st.title("🌸 野原家·健康周期助手")
    st.write("欢迎！小白、野原家全员都在这里守护您的健康！请登录或注册 🤔")
    
    tab1, tab2 = st.tabs(["🔑 登录", "📝 注册"])
    
    with tab1:
        st.subheader("🔑 用户登录")
        login_user = st.text_input("用户名", key="login_user", placeholder="Weichee")
        login_pwd = st.text_input("密码", type="password", key="login_pwd", placeholder="请输入密码")
        if st.button("开始新的一天！"):
            users_df = pd.read_csv(USERS_FILE)
            if login_user in users_df['username'].values:
                stored_hash = users_df.loc[users_df['username'] == login_user, 'password_hash'].values[0]
                if make_hash(login_pwd) == stored_hash:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.success("登录成功！小白都高兴得转圈圈啦！正在跳转...")
                    st.rerun()
                else:
                    st.error("密码错误！小白都说你错啦！😭")
            else:
                st.error("用户名不存在！是不是打错字啦？🤔")

    with tab2:
        st.subheader("📝 新用户注册")
        reg_user = st.text_input("设置用户名", key="reg_user", placeholder=" Weichee")
        reg_pwd = st.text_input("设置密码", type="password", key="reg_pwd", placeholder="请输入密码")
        reg_pwd2 = st.text_input("确认密码", type="password", key="reg_pwd2", placeholder="请再次确认密码")
        if st.button("一键加入野原家！"):
            users_df = pd.read_csv(USERS_FILE)
            if reg_user in users_df['username'].values:
                st.warning("该用户名已被注册，换个小白的名字吧🤔。")
            elif reg_pwd != reg_pwd2:
                st.error("两次输入的密码不一致！😭")
            elif len(reg_user) < 3 or len(reg_pwd) < 4:
                st.warning("用户名至少3位，密码至少4位。")
            else:
                new_user = pd.DataFrame({"username": [reg_user], "password_hash": [make_hash(reg_pwd)]})
                pd.concat([users_df, new_user], ignore_index=True).to_csv(USERS_FILE, index=False)
                st.success("注册成功！快去登录标签页加入野原家吧！")

# ==========================================
# 模块 B：主控面板 (UI 优化版)
# ==========================================
def main_dashboard():
    # 侧边栏：用户信息与个性化设置 (UI 优化)
    st.sidebar.title(f"👤 您好, {st.session_state.current_user}")
    st.sidebar.caption("这里是侧边栏信息框 🤔")
    
    # 核心设置：设置您的默认经期长度
    user_menses_len = st.sidebar.number_input("您的平均经期持续天数", min_value=2, max_value=10, value=5, help="用于更精确地为您划分生理阶段。")
    
    st.sidebar.divider()
    if st.sidebar.button("👋 退出野原家"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    # 主界面：欢迎标题
    # 如果有 URL，可以这里加一张 Shin-chan Thumbs up 图片链接
    # st.image("https://... shin_chan_dashboard.png", use_container_width=True)
    st.title("📈 Weichee 的周期变变变！")
    st.write("美伢妈妈提醒您：周期记录开始啦！")
    
    # 加载当前用户的数据
    df = pd.read_csv(DATA_FILE)
    user_data = df[df['username'] == st.session_state.current_user].copy()
    user_data['date'] = pd.to_datetime(user_data['date'])
    
    # 筛选出所有的“月经开始日”记录，并按时间排序
    period_records = user_data[user_data['type'] == 'period_start'].sort_values('date')
    
    # ==========================================
    # 功能 1：周期趋势折线图 (UI 优化)
    # ==========================================
    if len(period_records) >= 2:
        st.subheader("📊 周期趋势大作战")
        
        trends_df = period_records.copy()
        trends_df['cycle_days'] = trends_df['date'].diff().dt.days
        trends_df = trends_df.dropna() # 删掉第一个没有差值的记录
        
        if not trends_df.empty:
            chart_data = trends_df[['date', 'cycle_days']].copy()
            chart_data.columns = ['日期', '周期天数']
            
            # 使用简单的 Streamlit 折线图展示
            st.line_chart(chart_data.set_index('日期'))
            
            # 显示简要统计 (加了小新风格 caption)
            col_t1, col_t2 = st.columns(2)
            col_t1.caption(f"📉 最近一次周期：{int(trends_df['cycle_days'].iloc[-1])} 天 🤔")
            col_t2.caption(f"📈 历史最短/最长：{int(trends_df['cycle_days'].min())} / {int(trends_df['cycle_days'].max())} 天 😂")
        else:
            st.info("小白数据处理中，稍后显示趋势。")
    
    st.divider()

    # ==========================================
    # 核心逻辑：动态计算平均周期与预测
    # ==========================================
    avg_cycle = 28 # 默认值
    if len(period_records) >= 2:
        intervals = period_records['date'].diff().dt.days.dropna()
        avg_cycle = int(intervals.mean()) # 取平均值
    
    # --- 顶栏：记录新的月经开始日 ---
    with st.expander("🩸 月经大人来了？一键记录！", expanded=(len(period_records)==0)):
        new_period_date = st.date_input("选择本次月经第一天的日期", datetime.now())
        if st.button("💾 保存月经日期"):
            if not period_records.empty and pd.to_datetime(new_period_date) in period_records['date'].values:
                st.warning("这一天小白记录过啦！🤔")
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

    # --- 功能 2 & 医生伴侣：周期预测面板与每日医生建议 (UI 重塑) ---
    today = datetime.now().date()
    current_phase = ""
    
    st.subheader("🔮 预测大师·小白")
    if len(period_records) == 0:
        st.info("💡 请先在上方记录至少一次您的月经开始日期，小白才能预测哦！")
    else:
        last_period_date = period_records['date'].iloc[-1].date()
        next_period = last_period_date + timedelta(days=avg_cycle)
        ovulation_day = next_period - timedelta(days=14)
        fertile_start = ovulation_day - timedelta(days=5)
        fertile_end = ovulation_day + timedelta(days=1)
        
        # 显示关键数据米
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("最后一次记录 🍑", str(last_period_date))
        col_p2.metric("当前平均周期", f"{avg_cycle} 天", "小白推荐" if len(period_records)>=2 else "默认")
        col_p3.metric("✨ 预测排卵日", str(ovulation_day))
        
        # 将结果显示在一个可爱的 Success Box 里
        st.markdown(f"""
        <div style="background-color: #E1F5FE; color: #0277BD; border-radius: 15px; border: 2px solid #81D4FA; padding: 20px; text_align: center; margin-bottom: 20px;">
            <h3 style="color: #0277BD; margin-top: 0;">🩸 下次月经预测日</h3>
            <h1 style="color: #01579B; font-size: 36px; margin: 10px 0;">{next_period}</h1>
            <p>小白提醒：记得提前准备小白同款卫生小白毛巾哦 🤔！</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()

        # ==========================================
        # 👨🏻‍⚕️ 今日健康陪伴 (专业版建议) (UI 重塑)
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
        
        st.subheader(f"👨🏻‍⚕️ 今日健康关怀陪伴 ({current_phase}) 🤔")
        
        # 使用三个可控 Expanders (医生风格建议)
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.expander("🍽️ **小白推荐·饮食指南**", expanded=True):
                for item in advice['diet']: st.write(f"- {item} 😂")
        with c2:
            with st.expander("🏃🏻‍♀️ **小白推荐·运动方案**", expanded=True):
                for item in advice['exercise']: st.write(f"- {item} 🍑")
        with c3:
            with st.expander("💡 **小白提醒·医学贴士**", expanded=True):
                for item in advice['medical']: st.write(f"- {item} 😭")
        st.divider()


    # ==========================================
    # 功能 3：每日日记记录 (UI 优化版)
    # ==========================================
    st.subheader("📝 今日情绪滑滑梯 (每日症状)")
    with st.form("daily_log_form"):
        log_date = st.date_input("日记日期", datetime.now())
        mood = st.select_slider("今日心情 😂🤔😭", options=["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"], value="😐 平静")
        symptoms = st.multiselect("身体症状 🤔", ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"])
        notes = st.text_area("小白数据处理备注")
        if st.form_submit_button("💾 保存日记"):
            new_log = pd.DataFrame({
                "username": [st.session_state.current_user], "type": ["daily_log"], "date": [log_date.strftime("%Y-%m-%d")],
                "menses_length": [0], "mood": [mood], "symptoms": [", ".join(symptoms)], "notes": [notes]
            })
            pd.concat([df, new_log], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("日记保存成功！正在更新历史记录...")
            st.rerun()

    # --- 历史数据显示 (UI 优化版) ---
    st.divider()
    with st.expander("📖 查看小白历史记录库 (可滚动) 🤔"):
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