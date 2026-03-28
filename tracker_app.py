import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# ==========================================
# 🌸 UI 升级：现代清新版 + PWA 手机适配代码
# ==========================================
st.set_page_config(
    page_title="Glow Cycle Tracker", 
    page_icon="🌸", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 这里加入了你要求的 iPhone 适配代码（图标和全屏模式）
st.markdown("""
<head>
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3667/3667231.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
</head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    }
    
    .stApp {
        background-color: #FFFDFD !important;
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #FFF0F5 !important;
        border-right: 1px solid #FCE4EC;
    }

    h1, h2, h3 {
        color: #FF6B81 !important;
        font-weight: 800 !important;
    }

    /* 按钮：渐变粉色 */
    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
        color: #B71C1C !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: 800 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 154, 158, 0.6) !important;
    }

    /* 卡片容器 */
    .stExpander {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #FFEBEF !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
        margin-bottom: 1rem;
    }

    [data-testid="stMetricValue"] {
        color: #FF6B81 !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 🌐 多语言系统
# ==========================================
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

lang_dict = {
    'zh': {
        'app_title': "🌸 Glow 周期健康助手",
        'welcome': "欢迎回来！请登录管理您的健康数据。",
        'tab_login': "🔑 登录", 'tab_reg': "📝 注册",
        'username': "用户名", 'pwd': "密码", 'pwd_confirm': "确认密码",
        'btn_login': "开启 Glow 之旅", 'btn_reg': "加入我们",
        'login_ok': "登录成功！", 'login_fail': "密码错误！", 'user_none': "用户不存在！",
        'reg_ok': "注册成功！", 'reg_pwd_err': "两次输入的密码不一致！",
        'sidebar_hi': "👤 您好", 'sidebar_len': "平均经期天数", 'btn_logout': "👋 退出登录",
        'dash_title': "📊 健康看板",
        'chart_title': "📊 周期趋势", 'chart_latest': "📉 最近一次", 'chart_minmax': "📈 极值",
        'record_title': "🩸 记录经期开始", 'record_date': "选择第一天日期", 'btn_save_date': "💾 保存日期",
        'pred_title': "🔮 智能预测", 'pred_last': "上次日期", 'pred_avg': "平均周期", 'pred_next': "✨ 排卵日",
        'pred_result': "预测下次月经日",
        'adv_title': "今日医生建议", 'adv_diet': "🍽️ 饮食推荐", 'adv_exe': "🏃🏻‍♀️ 运动方案", 'adv_med': "💡 医学贴士",
        'log_title': "📝 每日日记", 'log_date': "日期", 'log_mood': "心情", 'log_sym': "症状", 'log_note': "备注", 'btn_save_log': "💾 保存日记",
        'hist_title': "📖 历史记录",
        'phase_menstrual': "月经期", 'phase_follicular': "滤泡期", 'phase_ovulation': "排卵期", 'phase_luteal': "黄体期",
        'moods': ["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"],
        'syms': ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"]
    },
    'en': {
        'app_title': "🌸 Glow Tracker",
        'welcome': "Welcome back! Keep tracking your health.",
        'tab_login': "🔑 Login", 'tab_reg': "📝 Register",
        'username': "Username", 'pwd': "Password", 'pwd_confirm': "Confirm Pwd",
        'btn_login': "Start Journey", 'btn_reg': "Sign Up",
        'login_ok': "Success!", 'login_fail': "Wrong password!", 'user_none': "No user!",
        'reg_ok': "Account created!", 'reg_pwd_err': "Passwords mismatch!",
        'sidebar_hi': "👤 Hi", 'sidebar_len': "Avg period days", 'btn_logout': "👋 Logout",
        'dash_title': "📊 Health Dashboard",
        'chart_title': "📊 Trends", 'chart_latest': "📉 Latest", 'chart_minmax': "📈 Min/Max",
        'record_title': "🩸 Log Period Start", 'record_date': "Select Date", 'btn_save_date': "💾 Save Date",
        'pred_title': "🔮 Predictions", 'pred_last': "Last Log", 'pred_avg': "Avg Cycle", 'pred_next': "✨ Ovulation",
        'pred_result': "Next Period",
        'adv_title': "Doctor's Advice", 'adv_diet': "🍽️ Diet", 'adv_exe': "🏃🏻‍♀️ Exercise", 'adv_med': "💡 Tips",
        'log_title': "📝 Daily Journal", 'log_date': "Date", 'log_mood': "Mood", 'log_sym': "Symptoms", 'log_note': "Notes", 'btn_save_log': "💾 Save Log",
        'hist_title': "📖 History",
        'phase_menstrual': "Menstrual", 'phase_follicular': "Follicular", 'phase_ovulation': "Ovulation", 'phase_luteal': "Luteal",
        'moods': ["😭 Awful", "😔 Sad", "😐 Okay", "🙂 Good", "😄 Great"],
        'syms': ["Cramps", "Headache", "Tender", "Fatigue", "Acne", "Backache", "None"]
    }
}

def t(key):
    return lang_dict[st.session_state.lang].get(key, key)

# --- 数据与文件逻辑 ---
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

doctor_advice = {
    "menstrual": {
        "zh": {"diet": ["补充铁质：菠菜、红肉", "温热饮食：生姜茶"], "exe": ["轻度有氧：慢走", "多休息"], "med": ["注意腹部保暖", "保证充足睡眠"]},
        "en": {"diet": ["Iron rich: Spinach", "Warm drinks: Ginger tea"], "exe": ["Light walking", "Rest well"], "med": ["Keep abdomen warm", "Enough sleep"]}
    },
    "follicular": {
        "zh": {"diet": ["优质蛋白：鱼肉", "抗氧化：蓝莓"], "exe": ["恢复训练：慢跑", "可增加强度"], "med": ["精力充沛，适合工作", "补充维生素D"]},
        "en": {"diet": ["Protein: Fish", "Antioxidants: Berries"], "exe": ["Jogging, Swimming", "Increase load"], "med": ["High energy", "Vitamin D"]}
    },
    "ovulation": {
        "zh": {"diet": ["叶酸补给：鸡蛋", "多喝水：2L+"], "exe": ["高强度运动 (HIIT)", "社交运动"], "med": ["黄金受孕期", "保持放松"]},
        "en": {"diet": ["Folic acid: Eggs", "2L+ water daily"], "exe": ["High intensity (HIIT)", "Socialize"], "med": ["Prime fertility", "Stay relaxed"]}
    },
    "luteal": {
        "zh": {"diet": ["复合碳水：全麦", "富含镁：香蕉", "低盐防浮肿"], "exe": ["瑜伽、普拉提", "舒缓为主"], "med": ["留意经前综合征", "避免熬夜"]},
        "en": {"diet": ["Complex carbs", "Magnesium: Bananas", "Low sodium"], "exe": ["Yoga, Pilates", "Focus on relax"], "med": ["Watch for PMS", "Avoid late nights"]}
    }
}

# --- 登录持久化逻辑 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ==========================================
# 页面内容
# ==========================================
st.sidebar.markdown("### 🌐 Language")
lang_choice = st.sidebar.radio(" ", ["中文", "English"], index=0 if st.session_state.lang == 'zh' else 1, label_visibility="collapsed")
if lang_choice == "中文" and st.session_state.lang != 'zh':
    st.session_state.lang = 'zh'
    st.rerun()
elif lang_choice == "English" and st.session_state.lang != 'en':
    st.session_state.lang = 'en'
    st.rerun()
st.sidebar.divider()

if not st.session_state.logged_in:
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
                    st.rerun()
                else: st.error(t('login_fail'))
            else: st.error(t('user_none'))
    with tab2:
        reg_user = st.text_input(t('username'), key="reg_user")
        reg_pwd = st.text_input(t('pwd'), type="password", key="reg_pwd")
        reg_pwd2 = st.text_input(t('pwd_confirm'), type="password", key="reg_pwd2")
        if st.button(t('btn_reg')):
            users_df = pd.read_csv(USERS_FILE)
            if reg_pwd != reg_pwd2: st.error(t('reg_pwd_err'))
            elif len(reg_user) >= 3:
                new_user = pd.DataFrame({"username": [reg_user], "password_hash": [make_hash(reg_pwd)]})
                pd.concat([users_df, new_user], ignore_index=True).to_csv(USERS_FILE, index=False)
                st.success(t('reg_ok'))
else:
    # 登录后的面板
    st.sidebar.title(f"{t('sidebar_hi')}, {st.session_state.current_user}")
    user_menses_len = st.sidebar.number_input(t('sidebar_len'), 2, 10, 5)
    if st.sidebar.button(t('btn_logout')):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    st.title(t('dash_title'))
    df = pd.read_csv(DATA_FILE)
    user_data = df[df['username'] == st.session_state.current_user].copy()
    user_data['date'] = pd.to_datetime(user_data['date'])
    period_records = user_data[user_data['type'] == 'period_start'].sort_values('date')

    if len(period_records) >= 2:
        st.subheader(t('chart_title'))
        trends_df = period_records.copy()
        trends_df['cycle_days'] = trends_df['date'].diff().dt.days.dropna()
        if not trends_df['cycle_days'].empty:
            st.line_chart(trends_df[['date', 'cycle_days']].dropna().set_index('date'))

    avg_cycle = 28
    if len(period_records) >= 2:
        avg_cycle = int(period_records['date'].diff().dt.days.dropna().mean())

    with st.expander(t('record_title'), expanded=(len(period_records)==0)):
        new_date = st.date_input(t('record_date'), datetime.now())
        if st.button(t('btn_save_date')):
            new_rec = pd.DataFrame({"username": [st.session_state.current_user], "type": ["period_start"], "date": [new_date.strftime("%Y-%m-%d")], "menses_length": [0], "mood": [""], "symptoms": [""], "notes": [""]})
            pd.concat([df, new_rec], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    if len(period_records) > 0:
        st.subheader(t('pred_title'))
        last_date = period_records['date'].iloc[-1].date()
        next_p = last_date + timedelta(days=avg_cycle)
        ovu = next_p - timedelta(days=14)
        c1, c2, c3 = st.columns(3)
        c1.metric(t('pred_last'), str(last_date))
        c2.metric(t('pred_avg'), f"{avg_cycle} d")
        c3.metric(t('pred_next'), str(ovu))
        st.success(f"**🩸 {t('pred_result')}: {next_p}**")

        today = datetime.now().date()
        if last_date <= today < (last_date + timedelta(days=user_menses_len)): p_key = "menstrual"
        elif (ovu - timedelta(days=5)) <= today <= (ovu + timedelta(days=1)): p_key = "ovulation"
        elif (last_date + timedelta(days=user_menses_len)) <= today < (ovu - timedelta(days=5)): p_key = "follicular"
        else: p_key = "luteal"
        
        advice = doctor_advice[p_key][st.session_state.lang]
        st.subheader(f"🌿 {t('adv_title')} - {t('phase_'+p_key)}")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            with st.expander(t('adv_diet'), True):
                for i in advice['diet']: st.write(f"• {i}")
        with ac2:
            with st.expander(t('adv_exe'), True):
                for i in advice['exe']: st.write(f"• {i}")
        with ac3:
            with st.expander(t('adv_med'), True):
                for i in advice['med']: st.write(f"• {i}")

    st.subheader(t('log_title'))
    with st.form("log"):
        l_date = st.date_input(t('log_date'), datetime.now())
        l_mood = st.select_slider(t('log_mood'), options=t('moods'))
        l_sym = st.multiselect(t('log_sym'), t('syms'))
        l_note = st.text_area(t('log_note'))
        if st.form_submit_button(t('btn_save_log')):
            new_log = pd.DataFrame({"username": [st.session_state.current_user], "type": ["daily_log"], "date": [l_date.strftime("%Y-%m-%d")], "menses_length": [0], "mood": [l_mood], "symptoms": [", ".join(l_sym)], "notes": [l_note]})
            pd.concat([df, new_log], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    with st.expander(t('hist_title')):
        st.dataframe(user_data[['date', 'type', 'mood', 'symptoms', 'notes']].sort_values('date', ascending=False), use_container_width=True, hide_index=True)