import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# ==========================================
# 🌸 全新 UI 优化：现代清新质感风 (Modern Pastel)
# ==========================================
st.set_page_config(page_title="Glow Cycle Tracker", page_icon="🌸", layout="centered")

st.markdown("""
<style>
    /* 引入更优雅圆润的英文字体 */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    }
    
    /* 整体背景：极浅的玫瑰粉色 */
    .stApp {
        background-color: #FFFDFD !important;
    }

    /* 侧边栏：柔和的浅色调 */
    [data-testid="stSidebar"] {
        background-color: #FFF0F5 !important;
        border-right: 1px solid #FCE4EC;
    }

    /* 标题与文字颜色优化 */
    h1, h2, h3 {
        color: #FF6B81 !important; /* 柔和的高级粉 */
        font-weight: 800 !important;
    }
    p, label, .stMarkdown {
        color: #4A4A4A !important;
    }

    /* 按钮：高级渐变色 + 圆角阴影 */
    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
        color: #B71C1C !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: 800 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 154, 158, 0.6) !important;
    }

    /* 卡片 (Expander) 优化：纯白背景，柔和边框，悬浮阴影 */
    .stExpander {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #FFEBEF !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
        overflow: hidden;
    }

    /* 数据指标 (Metric) 居中并调色 */
    [data-testid="stMetricValue"] {
        color: #FF6B81 !important;
        font-weight: 800 !important;
    }
    
    /* 成功提示框优化 */
    [data-testid="stSuccess"] {
        background-color: #F0FFF4;
        color: #2F855A;
        border-radius: 12px !important;
        border: 1px solid #C6F6D5 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 🌐 双语系统配置 (i18n)
# ==========================================
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh' # 默认中文

# 翻译字典
lang_dict = {
    'zh': {
        'app_title': "🌸 Glow 周期健康助手",
        'welcome': "欢迎！请登录或注册以管理您的专属健康数据。",
        'tab_login': "🔑 登录", 'tab_reg': "📝 注册",
        'username': "用户名", 'pwd': "密码", 'pwd_confirm': "确认密码",
        'btn_login': "登录账号", 'btn_reg': "注册新账号",
        'login_ok': "登录成功！正在跳转...", 'login_fail': "密码错误！", 'user_none': "用户名不存在！",
        'reg_ok': "注册成功！请切换到登录页。", 'reg_pwd_err': "两次输入的密码不一致！",
        'sidebar_hi': "👤 您好", 'sidebar_len': "您的平均经期天数", 'btn_logout': "👋 退出登录",
        'dash_title': "📊 我的健康数据看板",
        'chart_title': "📊 周期趋势图", 'chart_latest': "📉 最近一次周期", 'chart_minmax': "📈 历史最短/最长",
        'record_title': "🩸 记录新的月经开始日", 'record_date': "选择本次月经第一天的日期", 'btn_save_date': "💾 保存日期",
        'pred_title': "🔮 周期预测", 'pred_last': "最后一次记录", 'pred_avg': "当前平均周期", 'pred_next': "✨ 预测排卵日",
        'pred_result': "预测下次月经日",
        'adv_title': "今日健康关怀", 'adv_diet': "🍽️ 饮食推荐", 'adv_exe': "🏃🏻‍♀️ 运动方案", 'adv_med': "💡 医学贴士",
        'log_title': "📝 每日健康日记", 'log_date': "日记日期", 'log_mood': "今日心情", 'log_sym': "身体症状", 'log_note': "其他备注", 'btn_save_log': "💾 保存日记",
        'hist_title': "📖 查看历史记录",
        # 医生建议与阶段 (保留内部英文 Key 匹配，翻译显示内容)
        'phase_menstrual': "月经期 (Menstrual)", 'phase_follicular': "滤泡期 (Follicular)", 'phase_ovulation': "排卵期 (Ovulation)", 'phase_luteal': "黄体期 (Luteal)",
        'moods': ["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"],
        'syms': ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"]
    },
    'en': {
        'app_title': "🌸 Glow Cycle Tracker",
        'welcome': "Welcome! Please login or register to manage your health data.",
        'tab_login': "🔑 Login", 'tab_reg': "📝 Register",
        'username': "Username", 'pwd': "Password", 'pwd_confirm': "Confirm Password",
        'btn_login': "Sign In", 'btn_reg': "Sign Up",
        'login_ok': "Login successful! Redirecting...", 'login_fail': "Incorrect password!", 'user_none': "User not found!",
        'reg_ok': "Registration successful! Please login.", 'reg_pwd_err': "Passwords do not match!",
        'sidebar_hi': "👤 Hello", 'sidebar_len': "Average period length (days)", 'btn_logout': "👋 Logout",
        'dash_title': "📊 My Health Dashboard",
        'chart_title': "📊 Cycle Trends", 'chart_latest': "📉 Latest Cycle", 'chart_minmax': "📈 Min/Max Cycle",
        'record_title': "🩸 Log New Period Start Date", 'record_date': "Select the first day of your period", 'btn_save_date': "💾 Save Date",
        'pred_title': "🔮 Cycle Predictions", 'pred_last': "Last Recorded", 'pred_avg': "Current Avg Cycle", 'pred_next': "✨ Est. Ovulation",
        'pred_result': "Est. Next Period",
        'adv_title': "Today's Wellness Guide", 'adv_diet': "🍽️ Diet Tips", 'adv_exe': "🏃🏻‍♀️ Exercise", 'adv_med': "💡 Health Tips",
        'log_title': "📝 Daily Journal", 'log_date': "Date", 'log_mood': "Today's Mood", 'log_sym': "Symptoms", 'log_note': "Notes", 'btn_save_log': "💾 Save Log",
        'hist_title': "📖 View History Log",
        'phase_menstrual': "Menstrual Phase", 'phase_follicular': "Follicular Phase", 'phase_ovulation': "Ovulation Phase", 'phase_luteal': "Luteal Phase",
        'moods': ["😭 Awful", "😔 Sad", "😐 Okay", "🙂 Good", "😄 Great"],
        'syms': ["Cramps", "Headache", "Tender Breasts", "Fatigue", "Acne", "Backache", "None"]
    }
}

# 快捷翻译函数
def t(key):
    return lang_dict[st.session_state.lang].get(key, key)


# --- 核心数据配置 ---
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

# --- 医生知识库 (双语结构) ---
doctor_advice = {
    "menstrual": {
        "zh": {"diet": ["补充铁质：菠菜、红肉", "温热饮食：生姜茶", "Omega-3：三文鱼"], "exe": ["轻度有氧：慢走", "舒缓拉伸", "多休息"], "med": ["注意腹部保暖", "保证充足睡眠"]},
        "en": {"diet": ["Iron rich: Spinach, Red meat", "Warm drinks: Ginger tea", "Omega-3: Salmon"], "exe": ["Light walking", "Gentle stretching", "Rest well"], "med": ["Keep abdomen warm", "Get enough sleep"]}
    },
    "follicular": {
        "zh": {"diet": ["优质蛋白：鸡肉、鱼肉", "抗氧化：蓝莓、西兰花"], "exe": ["恢复训练：慢跑、游泳", "可增加中等强度负荷"], "med": ["精力充沛，适合复杂工作", "补充维生素D"]},
        "en": {"diet": ["High protein: Chicken, Fish", "Antioxidants: Blueberries"], "exe": ["Jogging, Swimming", "Increase moderate load"], "med": ["High energy for complex tasks", "Vitamin D intake"]}
    },
    "ovulation": {
        "zh": {"diet": ["叶酸补给：芦笋、鸡蛋", "多喝水：每日 2L+"], "exe": ["适合高强度运动 (HIIT)", "参加社交运动"], "med": ["受孕黄金期", "保持心情放松"]},
        "en": {"diet": ["Folic acid: Asparagus, Eggs", "Hydration: 2L+ water daily"], "exe": ["High intensity (HIIT)", "Social sports"], "med": ["Prime fertility window", "Stay relaxed"]}
    },
    "luteal": {
        "zh": {"diet": ["复合碳水：全麦面包", "富含镁：香蕉、深海鱼", "低盐防浮肿"], "exe": ["中低强度：瑜伽、普拉提", "舒缓身心为主"], "med": ["留意经前综合征 (PMS)", "避免熬夜"]},
        "en": {"diet": ["Complex carbs: Whole grains", "Magnesium: Bananas", "Low sodium"], "exe": ["Low impact: Yoga, Pilates", "Focus on relaxation"], "med": ["Watch for PMS symptoms", "Avoid late nights"]}
    }
}

# --- 状态管理初始化 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ==========================================
# 侧边栏：语言切换器 (全局显示)
# ==========================================
st.sidebar.markdown("### 🌐 Language / 语言")
lang_choice = st.sidebar.radio(" ", ["中文", "English"], index=0 if st.session_state.lang == 'zh' else 1, label_visibility="collapsed")
if lang_choice == "中文" and st.session_state.lang != 'zh':
    st.session_state.lang = 'zh'
    st.rerun()
elif lang_choice == "English" and st.session_state.lang != 'en':
    st.session_state.lang = 'en'
    st.rerun()
st.sidebar.divider()

# ==========================================
# 模块 A：用户注册与登录
# ==========================================
def login_register_page():
    st.title(t('app_title'))
    st.write(t('welcome'))
    
    tab1, tab2 = st.tabs([t('tab_login'), t('tab_reg')])
    
    with tab1:
        login_user = st.text_input(t('username'), key="login_user")
        login_pwd = st.text_input(t('pwd'), type="password", key="login_pwd")
        if st.button(t('btn_login')):
            users_df = pd.read_csv(USERS_FILE)
            if login_user in users_df['username'].values:
                stored_hash = users_df.loc[users_df['username'] == login_user, 'password_hash'].values[0]
                if make_hash(login_pwd) == stored_hash:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.success(t('login_ok'))
                    st.rerun()
                else:
                    st.error(t('login_fail'))
            else:
                st.error(t('user_none'))

    with tab2:
        reg_user = st.text_input(t('username'), key="reg_user")
        reg_pwd = st.text_input(t('pwd'), type="password", key="reg_pwd")
        reg_pwd2 = st.text_input(t('pwd_confirm'), type="password", key="reg_pwd2")
        if st.button(t('btn_reg')):
            users_df = pd.read_csv(USERS_FILE)
            if reg_pwd != reg_pwd2:
                st.error(t('reg_pwd_err'))
            elif len(reg_user) >= 3 and len(reg_pwd) >= 4:
                new_user = pd.DataFrame({"username": [reg_user], "password_hash": [make_hash(reg_pwd)]})
                pd.concat([users_df, new_user], ignore_index=True).to_csv(USERS_FILE, index=False)
                st.success(t('reg_ok'))

# ==========================================
# 模块 B：主控面板
# ==========================================
def main_dashboard():
    # 侧边栏
    st.sidebar.title(f"{t('sidebar_hi')}, {st.session_state.current_user} ✨")
    user_menses_len = st.sidebar.number_input(t('sidebar_len'), min_value=2, max_value=10, value=5)
    
    if st.sidebar.button(t('btn_logout')):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    st.title(t('dash_title'))
    
    df = pd.read_csv(DATA_FILE)
    user_data = df[df['username'] == st.session_state.current_user].copy()
    user_data['date'] = pd.to_datetime(user_data['date'])
    period_records = user_data[user_data['type'] == 'period_start'].sort_values('date')
    
    # --- 趋势图 ---
    if len(period_records) >= 2:
        st.subheader(t('chart_title'))
        trends_df = period_records.copy()
        trends_df['cycle_days'] = trends_df['date'].diff().dt.days.dropna()
        
        if not trends_df['cycle_days'].empty:
            chart_data = trends_df[['date', 'cycle_days']].dropna()
            st.line_chart(chart_data.set_index('date'))
            c1, c2 = st.columns(2)
            c1.caption(f"{t('chart_latest')}: {int(trends_df['cycle_days'].iloc[-1])} d")
            c2.caption(f"{t('chart_minmax')}: {int(trends_df['cycle_days'].min())} / {int(trends_df['cycle_days'].max())} d")
    
    st.divider()

    # --- 记录新日期 ---
    avg_cycle = 28
    if len(period_records) >= 2:
        avg_cycle = int(period_records['date'].diff().dt.days.dropna().mean())
    
    with st.expander(t('record_title'), expanded=(len(period_records)==0)):
        new_period_date = st.date_input(t('record_date'), datetime.now())
        if st.button(t('btn_save_date')):
            new_record = pd.DataFrame({
                "username": [st.session_state.current_user], "type": ["period_start"], 
                "date": [new_period_date.strftime("%Y-%m-%d")],
                "menses_length": [0], "mood": [""], "symptoms": [""], "notes": [""]
            })
            pd.concat([df, new_record], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    st.divider()

    # --- 预测与医生建议 ---
    today = datetime.now().date()
    current_phase_key = ""
    
    st.subheader(t('pred_title'))
    if len(period_records) > 0:
        last_period_date = period_records['date'].iloc[-1].date()
        next_period = last_period_date + timedelta(days=avg_cycle)
        ovulation_day = next_period - timedelta(days=14)
        fertile_start = ovulation_day - timedelta(days=5)
        fertile_end = ovulation_day + timedelta(days=1)
        
        col1, col2, col3 = st.columns(3)
        col1.metric(t('pred_last'), str(last_period_date))
        col2.metric(t('pred_avg'), f"{avg_cycle} d")
        col3.metric(t('pred_next'), str(ovulation_day))
        
        st.success(f"**🩸 {t('pred_result')}: {next_period}**")
        st.divider()

        # 阶段判断
        if last_period_date <= today < (last_period_date + timedelta(days=user_menses_len)):
            current_phase_key = "menstrual"
        elif fertile_start <= today <= fertile_end:
            current_phase_key = "ovulation"
        elif (last_period_date + timedelta(days=user_menses_len)) <= today < fertile_start:
            current_phase_key = "follicular"
        else:
            current_phase_key = "luteal"
            
        phase_name = t(f'phase_{current_phase_key}')
        advice = doctor_advice[current_phase_key][st.session_state.lang]
        
        st.subheader(f"🌿 {t('adv_title')} - {phase_name}")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            with st.expander(t('adv_diet'), expanded=True):
                for i in advice['diet']: st.write(f"• {i}")
        with ac2:
            with st.expander(t('adv_exe'), expanded=True):
                for i in advice['exe']: st.write(f"• {i}")
        with ac3:
            with st.expander(t('adv_med'), expanded=True):
                for i in advice['med']: st.write(f"• {i}")
        st.divider()

    # --- 每日日记 ---
    st.subheader(t('log_title'))
    with st.form("daily_log_form"):
        log_date = st.date_input(t('log_date'), datetime.now())
        mood = st.select_slider(t('log_mood'), options=t('moods'))
        symptoms = st.multiselect(t('log_sym'), t('syms'))
        notes = st.text_area(t('log_note'))
        if st.form_submit_button(t('btn_save_log')):
            new_log = pd.DataFrame({
                "username": [st.session_state.current_user], "type": ["daily_log"], "date": [log_date.strftime("%Y-%m-%d")],
                "menses_length": [0], "mood": [mood], "symptoms": [", ".join(symptoms)], "notes": [notes]
            })
            pd.concat([df, new_log], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    # --- 历史记录 ---
    st.divider()
    with st.expander(t('hist_title')):
        display_df = user_data[['date', 'type', 'mood', 'symptoms', 'notes']].sort_values('date', ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ==========================================
# 页面路由
# ==========================================
if st.session_state.logged_in:
    main_dashboard()
else:
    login_register_page()