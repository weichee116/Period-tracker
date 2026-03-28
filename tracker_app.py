import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# ==========================================
# 🌸 UI & Dark Mode 适配优化
# ==========================================
st.set_page_config(
    page_title="Glow Cycle Tracker", 
    page_icon="🌸", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 修复 Dark Mode 下的显示问题，并增加手机端适配
st.markdown("""
<head>
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3667/3667231.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
</head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: 'Nunito', 'PingFang SC', sans-serif !important;
    }

    /* 动态适配暗色模式的卡片样式 */
    .stExpander {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 107, 129, 0.2) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        margin-bottom: 1rem;
    }

    /* 统一按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
        color: #721c24 !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: 800 !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4) !important;
    }

    /* 指标数值颜色 */
    [data-testid="stMetricValue"] {
        color: #FF6B81 !important;
    }

    /* 针对暗色模式的微调 */
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #121212 !important; }
        .stMarkdown, p, label { color: #E0E0E0 !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 多语言词典 (i18n)
# ==========================================
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

lang_dict = {
    'zh': {
        'app_title': "🌸 Glow 周期助手",
        'welcome': "欢迎回来！请登录以查看您的健康建议。",
        'tab_login': "🔑 登录", 'tab_reg': "📝 注册",
        'username': "用户名", 'pwd': "密码", 'pwd_confirm': "确认密码",
        'btn_login': "进入系统", 'btn_reg': "立即注册",
        'login_ok': "登录成功！", 'login_fail': "密码错误！", 'user_none': "用户不存在！",
        'reg_ok': "注册成功！", 'reg_pwd_err': "密码不一致！",
        'sidebar_hi': "👤 您好", 'sidebar_len': "平均经期天数", 'btn_logout': "👋 退出登录",
        'dash_title': "📊 健康数据看板",
        'chart_title': "📊 周期趋势",
        'record_title': "🩸 记录经期开始日", 'record_date': "选择第一天日期", 'btn_save_date': "💾 保存日期",
        'pred_title': "🔮 智能预测", 'pred_last': "上次日期", 'pred_avg': "平均周期", 'pred_next': "✨ 排卵日",
        'pred_result': "预测下次月经日",
        'adv_title': "👨‍⚕️ 医生伴侣建议", 'adv_diet': "🍽️ 饮食建议", 'adv_exe': "🏃🏻‍♀️ 运动建议", 'adv_med': "💡 医学贴士",
        'log_title': "📝 每日日记", 'btn_save_log': "💾 保存日记",
        'hist_title': "📖 历史数据记录",
        'phase_menstrual': "月经期", 'phase_follicular': "滤泡期", 'phase_ovulation': "排卵期", 'phase_luteal': "黄体期",
        'moods': ["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"],
        'syms': ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"]
    },
    'en': {
        'app_title': "🌸 Glow Tracker",
        'welcome': "Welcome back! Login to see your advice.",
        'tab_login': "🔑 Login", 'tab_reg': "📝 Register",
        'username': "Username", 'pwd': "Password", 'pwd_confirm': "Confirm Pwd",
        'btn_login': "Sign In", 'btn_reg': "Sign Up",
        'login_ok': "Success!", 'login_fail': "Wrong password!", 'user_none': "No user!",
        'reg_ok': "Account created!", 'reg_pwd_err': "Mismatch!",
        'sidebar_hi': "👤 Hi", 'sidebar_len': "Avg period days", 'btn_logout': "👋 Logout",
        'dash_title': "📊 Health Dashboard",
        'chart_title': "📊 Cycle Trends",
        'record_title': "🩸 Log Period Start", 'record_date': "Select Start Date", 'btn_save_date': "💾 Save Date",
        'pred_title': "🔮 Predictions", 'pred_last': "Last Log", 'pred_avg': "Avg Cycle", 'pred_next': "✨ Ovulation",
        'pred_result': "Next Period",
        'adv_title': "👨‍⚕️ Professional Advice", 'adv_diet': "🍽️ Diet Tips", 'adv_exe': "🏃🏻‍♀️ Exercise", 'adv_med': "💡 Health Tips",
        'log_title': "📝 Daily Journal", 'btn_save_log': "💾 Save Log",
        'hist_title': "📖 History Logs",
        'phase_menstrual': "Menstrual", 'phase_follicular': "Follicular", 'phase_ovulation': "Ovulation", 'phase_luteal': "Luteal",
        'moods': ["😭 Awful", "😔 Sad", "😐 Okay", "🙂 Good", "😄 Great"],
        'syms': ["Cramps", "Headache", "Tender", "Fatigue", "Acne", "Backache", "None"]
    }
}

def t(key):
    return lang_dict[st.session_state.lang].get(key, key)

# --- 医生专业建议数据库 ---
doctor_advice = {
    "menstrual": {
        "zh": {"diet": ["补铁：红肉、菠菜", "喝生姜红糖水", "忌冷饮"], "exe": ["散步", "轻度拉伸", "避免剧烈运动"], "med": ["注意腹部保暖", "保证8小时睡眠"]},
        "en": {"diet": ["Iron: Red meat, Spinach", "Ginger tea", "Avoid cold drinks"], "exe": ["Walking", "Light stretching", "No heavy lifting"], "med": ["Keep belly warm", "8h sleep"]}
    },
    "follicular": {
        "zh": {"diet": ["高蛋白：鸡肉、鱼", "多吃西兰花"], "exe": ["慢跑", "游泳", "增加中强度训练"], "med": ["精力充沛期", "适合安排具挑战工作"]},
        "en": {"diet": ["Protein: Chicken, Fish", "Broccoli"], "exe": ["Jogging", "Swimming", "Moderate intensity"], "med": ["High energy phase", "Great for challenges"]}
    },
    "ovulation": {
        "zh": {"diet": ["补充叶酸：鸡蛋", "多喝水 2L+"], "exe": ["高强度间歇训练 (HIIT)", "力量训练"], "med": ["受孕黄金期", "保持心情愉快"]},
        "en": {"diet": ["Folic acid: Eggs", "Water 2L+"], "exe": ["HIIT Training", "Strength training"], "med": ["Peak fertility", "Stay positive"]}
    },
    "luteal": {
        "zh": {"diet": ["复合碳水：燕麦", "富含镁：香蕉", "低盐防浮肿"], "exe": ["瑜伽", "普拉提", "放松身心"], "med": ["留意经前综合征 (PMS)", "减少咖啡因摄入"]},
        "en": {"diet": ["Carbs: Oats", "Magnesium: Bananas", "Low sodium"], "exe": ["Yoga", "Pilates", "Relaxation"], "med": ["Watch for PMS", "Reduce caffeine"]}
    }
}

# --- 核心文件逻辑 ---
USERS_FILE = "users.csv"
DATA_FILE = "health_log.csv"

def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()

def init_files():
    if not os.path.exists(USERS_FILE): pd.DataFrame(columns=["username", "password_hash"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(DATA_FILE): pd.DataFrame(columns=["username", "type", "date", "menses_length", "mood", "symptoms", "notes"]).to_csv(DATA_FILE, index=False)

init_files()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ==========================================
# 侧边栏：语言 & 退出
# ==========================================
st.sidebar.markdown("### 🌐 Language")
lang_choice = st.sidebar.radio(" ", ["中文", "English"], index=0 if st.session_state.lang == 'zh' else 1, label_visibility="collapsed")
st.session_state.lang = 'zh' if lang_choice == "中文" else 'en'

# ==========================================
# 页面路由
# ==========================================
if not st.session_state.logged_in:
    st.title(t('app_title'))
    tab1, tab2 = st.tabs([t('tab_login'), t('tab_reg')])
    with tab1:
        u = st.text_input(t('username'), key="l_u")
        p = st.text_input(t('pwd'), type="password", key="l_p")
        if st.button(t('btn_login')):
            udf = pd.read_csv(USERS_FILE)
            if u in udf['username'].values:
                if make_hash(p) == udf.loc[udf['username']==u, 'password_hash'].values[0]:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else: st.error(t('login_fail'))
            else: st.error(t('user_none'))
    with tab2:
        ru = st.text_input(t('username'), key="r_u")
        rp = st.text_input(t('pwd'), type="password", key="r_p")
        if st.button(t('btn_reg')):
            udf = pd.read_csv(USERS_FILE)
            if len(ru) >=3:
                new_u = pd.DataFrame({"username": [ru], "password_hash": [make_hash(rp)]})
                pd.concat([udf, new_u], ignore_index=True).to_csv(USERS_FILE, index=False)
                st.success(t('reg_ok'))
else:
    # 登录后主界面
    st.sidebar.title(f"{t('sidebar_hi')}, {st.session_state.current_user}")
    m_len = st.sidebar.number_input(t('sidebar_len'), 2, 10, 5)
    if st.sidebar.button(t('btn_logout')):
        st.session_state.logged_in = False
        st.rerun()

    st.title(t('dash_title'))
    df = pd.read_csv(DATA_FILE)
    u_data = df[df['username'] == st.session_state.current_user].copy()
    u_data['date'] = pd.to_datetime(u_data['date'])
    p_recs = u_data[u_data['type'] == 'period_start'].sort_values('date')

    # 1. 趋势图
    if len(p_recs) >= 2:
        st.subheader(t('chart_title'))
        p_recs['cycle'] = p_recs['date'].diff().dt.days
        st.line_chart(p_recs.dropna().set_index('date')['cycle'])

    # 2. 记录功能
    with st.expander(t('record_title'), expanded=(len(p_recs)==0)):
        d = st.date_input(t('record_date'), datetime.now())
        if st.button(t('btn_save_date')):
            nr = pd.DataFrame({"username":[st.session_state.current_user], "type":["period_start"], "date":[d.strftime("%Y-%m-%d")], "menses_length":[0], "mood":[""], "symptoms":[""], "notes":[""]})
            pd.concat([df, nr], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    # 3. 预测与建议 (核心修复部分)
    if len(p_recs) > 0:
        st.divider()
        st.subheader(t('pred_title'))
        avg = int(p_recs['date'].diff().dt.days.dropna().mean()) if len(p_recs)>=2 else 28
        last = p_recs['date'].iloc[-1].date()
        nxt = last + timedelta(days=avg)
        ovu = nxt - timedelta(days=14)
        
        c1, c2, c3 = st.columns(3)
        c1.metric(t('pred_last'), str(last))
        c2.metric(t('pred_avg'), f"{avg} d")
        c3.metric(t('pred_next'), str(ovu))
        st.success(f"**{t('pred_result')}: {nxt}**")

        # 判断阶段
        today = datetime.now().date()
        if last <= today < (last + timedelta(days=m_len)): pk = "menstrual"
        elif (ovu - timedelta(days=5)) <= today <= (ovu + timedelta(days=1)): pk = "ovulation"
        elif (last + timedelta(days=m_len)) <= today < (ovu - timedelta(days=5)): pk = "follicular"
        else: pk = "luteal"
        
        # 显示建议板块
        st.subheader(f"{t('adv_title')} - {t('phase_'+pk)}")
        adv = doctor_advice[pk][st.session_state.lang]
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            with st.expander(t('adv_diet'), True):
                for i in adv['diet']: st.write(f"• {i}")
        with ac2:
            with st.expander(t('adv_exe'), True):
                for i in adv['exe']: st.write(f"• {i}")
        with ac3:
            with st.expander(t('adv_med'), True):
                for i in adv['med']: st.write(f"• {i}")

    # 4. 日记与历史
    st.divider()
    st.subheader(t('log_title'))
    with st.form("log"):
        ld = st.date_input("Date", datetime.now())
        lm = st.select_slider(t('moods')[2], options=t('moods'))
        ls = st.multiselect("Symptoms", t('syms'))
        ln = st.text_area("Notes")
        if st.form_submit_button(t('btn_save_log')):
            nl = pd.DataFrame({"username":[st.session_state.current_user], "type":["daily_log"], "date":[ld.strftime("%Y-%m-%d")], "menses_length":[0], "mood":[lm], "symptoms":[", ".join(ls)], "notes":[ln]})
            pd.concat([df, nl], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    with st.expander(t('hist_title')):
        st.dataframe(u_data[['date', 'type', 'mood', 'symptoms', 'notes']].sort_values('date', ascending=False), use_container_width=True, hide_index=True)