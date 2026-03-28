import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# ==========================================
# 🌸 1. UI & Dark Mode 深度适配 (解决 UI 消失问题)
# ==========================================
st.set_page_config(
    page_title="Glow Cycle Tracker", 
    page_icon="🌸", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 核心 CSS：确保在 Dark Mode 和 Light Mode 下建议板块都清晰可见
st.markdown("""
<head>
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3667/3667231.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
</head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', 'PingFang SC', sans-serif !important;
    }

    /* 建议板块卡片样式优化 */
    .stExpander {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 107, 129, 0.3) !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        margin-bottom: 1rem;
    }

    /* 按钮样式：确保在深色模式下文字也清晰 */
    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
        color: #721c24 !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: 800 !important;
        width: 100%;
        padding: 0.5rem 1rem !important;
    }

    /* Metric 数值颜色，适配深色模式 */
    [data-testid="stMetricValue"] {
        color: #FF6B81 !important;
    }

    /* 强力修复暗色模式文字不可见问题 */
    @media (prefers-color-scheme: dark) {
        .stMarkdown, p, label, span { color: #F0F0F0 !important; }
        .stExpander { background-color: #1E1E1E !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 2. 多语言翻译字典
# ==========================================
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

lang_dict = {
    'zh': {
        'app_title': "🌸 Glow 周期助手",
        'welcome': "欢迎回来！请登录以查看您的健康建议。",
        'tab_login': "🔑 登录", 'tab_reg': "📝 注册",
        'username': "用户名", 'pwd': "密码",
        'btn_login': "进入系统", 'btn_reg': "立即注册",
        'login_ok': "登录成功！", 'login_fail': "密码错误！", 'user_none': "用户名不存在，请先注册！",
        'reg_ok': "注册成功！请切换到登录标签页。", 'reg_err_exists': "该用户名已存在！", 'reg_err_short': "名字太短啦！",
        'sidebar_hi': "👤 您好", 'sidebar_len': "平均经期天数", 'btn_logout': "👋 退出登录",
        'dash_title': "📊 健康数据看板", 'chart_title': "📊 周期趋势 (天)",
        'record_title': "🩸 记录月经第一天", 'record_date': "选择日期", 'btn_save_date': "💾 保存日期",
        'pred_title': "🔮 智能预测", 'pred_last': "最后一次", 'pred_avg': "平均周期", 'pred_next': "✨ 排卵日",
        'pred_result': "预测下次月经日",
        'adv_title': "👨‍⚕️ 专业建议", 'adv_diet': "🍽️ 饮食建议", 'adv_exe': "🏃🏻‍♀️ 运动建议", 'adv_med': "💡 医学贴士",
        'log_title': "📝 每日日记", 'btn_save_log': "💾 保存日记", 'hist_title': "📖 历史记录",
        'phase_menstrual': "月经期", 'phase_follicular': "滤泡期", 'phase_ovulation': "排卵期", 'phase_luteal': "黄体期",
        'moods': ["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"],
        'syms': ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"]
    },
    'en': {
        'app_title': "🌸 Glow Tracker",
        'welcome': "Welcome! Login to see your advice.",
        'tab_login': "🔑 Login", 'tab_reg': "📝 Register",
        'username': "Username", 'pwd': "Password",
        'btn_login': "Sign In", 'btn_reg': "Sign Up",
        'login_ok': "Success!", 'login_fail': "Incorrect password!", 'user_none': "User not found, please register!",
        'reg_ok': "Success! Now please login.", 'reg_err_exists': "Username already exists!", 'reg_err_short': "Username too short!",
        'sidebar_hi': "👤 Hi", 'sidebar_len': "Avg Period Days", 'btn_logout': "👋 Logout",
        'dash_title': "📊 Health Dashboard", 'chart_title': "📊 Cycle Trends (Days)",
        'record_title': "🩸 Log Period Start", 'record_date': "Select Date", 'btn_save_date': "💾 Save Date",
        'pred_title': "🔮 Predictions", 'pred_last': "Last Log", 'pred_avg': "Avg Cycle", 'pred_next': "✨ Ovulation",
        'pred_result': "Next Period Date",
        'adv_title': "👨‍⚕️ Advice", 'adv_diet': "🍽️ Diet", 'adv_exe': "🏃🏻‍♀️ Exercise", 'adv_med': "💡 Health Tips",
        'log_title': "📝 Daily Journal", 'btn_save_log': "💾 Save Log", 'hist_title': "📖 History Logs",
        'phase_menstrual': "Menstrual", 'phase_follicular': "Follicular", 'phase_ovulation': "Ovulation", 'phase_luteal': "Luteal",
        'moods': ["😭 Awful", "😔 Sad", "😐 Okay", "🙂 Good", "😄 Great"],
        'syms': ["Cramps", "Headache", "Tender", "Fatigue", "Acne", "Backache", "None"]
    }
}

def t(key): return lang_dict[st.session_state.lang].get(key, key)

# --- 专业建议数据库 ---
doctor_advice = {
    "menstrual": {
        "zh": {"diet": ["补铁：红肉、菠菜", "喝生姜红糖水"], "exe": ["慢走", "轻度拉伸"], "med": ["注意腹部保暖", "多休息"]},
        "en": {"diet": ["Iron: Red meat, Spinach", "Ginger tea"], "exe": ["Walking", "Stretching"], "med": ["Stay warm", "More rest"]}
    },
    "follicular": {
        "zh": {"diet": ["优质蛋白：鱼、鸡肉", "多吃西兰花"], "exe": ["慢跑", "游泳"], "med": ["精力充沛期", "适合工作挑战"]},
        "en": {"diet": ["Protein: Fish, Chicken", "Broccoli"], "exe": ["Jogging", "Swimming"], "med": ["High energy", "Work hard!"]}
    },
    "ovulation": {
        "zh": {"diet": ["补充叶酸：鸡蛋", "多喝水 2L+"], "exe": ["HIIT 训练", "力量练习"], "med": ["黄金受孕期", "保持心情愉快"]},
        "en": {"diet": ["Folic acid: Eggs", "Water 2L+"], "exe": ["HIIT", "Strength"], "med": ["Peak fertility", "Stay happy"]}
    },
    "luteal": {
        "zh": {"diet": ["复合碳水：燕麦", "富含镁：香蕉"], "exe": ["瑜伽", "普拉提"], "med": ["预防 PMS", "减少咖啡因"]},
        "en": {"diet": ["Carbs: Oats", "Magnesium: Bananas"], "exe": ["Yoga", "Pilates"], "med": ["Watch for PMS", "Less caffeine"]}
    }
}

# --- 3. 核心数据存储逻辑 (修正注册/登录 Bug) ---
USERS_FILE = "users.csv"
DATA_FILE = "health_log.csv"

def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()

def init_files():
    if not os.path.exists(USERS_FILE): pd.DataFrame(columns=["username", "password_hash"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(DATA_FILE): pd.DataFrame(columns=["username", "type", "date", "menses_length", "mood", "symptoms", "notes"]).to_csv(DATA_FILE, index=False)

init_files()

# 初始化登录状态
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 4. 侧边栏 ---
st.sidebar.markdown("### 🌐 Language")
lang_choice = st.sidebar.radio(" ", ["中文", "English"], index=0 if st.session_state.lang == 'zh' else 1, label_visibility="collapsed")
st.session_state.lang = 'zh' if lang_choice == "中文" else 'en'

# ==========================================
# 5. 页面路由 (注册与登录修复版)
# ==========================================
if not st.session_state.logged_in:
    st.title(t('app_title'))
    tab1, tab2 = st.tabs([t('tab_login'), t('tab_reg')])
    
    with tab1:
        # 登录逻辑修复：增加 strip() 防止空格错误
        u_login = st.text_input(t('username'), key="login_user_input").strip()
        p_login = st.text_input(t('pwd'), type="password", key="login_pwd_input")
        if st.button(t('btn_login')):
            udf = pd.read_csv(USERS_FILE)
            if u_login in udf['username'].values:
                stored_hash = udf.loc[udf['username'] == u_login, 'password_hash'].values[0]
                if make_hash(p_login) == stored_hash:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u_login
                    st.rerun()
                else: st.error(t('login_fail'))
            else: st.error(t('user_none'))
            
    with tab2:
        # 注册逻辑修复：增加重复性检查
        u_reg = st.text_input(t('username'), key="reg_user_input").strip()
        p_reg = st.text_input(t('pwd'), type="password", key="reg_pwd_input")
        if st.button(t('btn_reg')):
            udf = pd.read_csv(USERS_FILE)
            if u_reg in udf['username'].values:
                st.error(t('reg_err_exists'))
            elif len(u_reg) < 3:
                st.warning(t('reg_err_short'))
            else:
                new_u = pd.DataFrame({"username": [u_reg], "password_hash": [make_hash(p_reg)]})
                pd.concat([udf, new_u], ignore_index=True).to_csv(USERS_FILE, index=False)
                st.success(t('reg_ok'))

else:
    # 登录后的面板
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

    # 2. 记录月经
    with st.expander(t('record_title'), expanded=(len(p_recs)==0)):
        d_input = st.date_input(t('record_date'), datetime.now())
        if st.button(t('btn_save_date')):
            nr = pd.DataFrame({"username":[st.session_state.current_user], "type":["period_start"], "date":[d_input.strftime("%Y-%m-%d")], "menses_length":[0], "mood":[""], "symptoms":[""], "notes":[""]})
            pd.concat([df, nr], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    # 3. 建议与预测 (强制显示逻辑修复)
    if len(p_recs) > 0:
        st.divider()
        st.subheader(t('pred_title'))
        # 计算平均周期，没有两次记录则默认 28
        avg = int(p_recs['date'].diff().dt.days.dropna().mean()) if len(p_recs)>=2 else 28
        last = p_recs['date'].iloc[-1].date()
        nxt = last + timedelta(days=avg)
        ovu = nxt - timedelta(days=14)
        
        c1, c2, c3 = st.columns(3)
        c1.metric(t('pred_last'), str(last))
        c2.metric(t('pred_avg'), f"{avg} d")
        c3.metric(t('pred_next'), str(ovu))
        st.success(f"**{t('pred_result')}: {nxt}**")

        # 生理阶段判定
        today = datetime.now().date()
        if last <= today < (last + timedelta(days=m_len)): pk = "menstrual"
        elif (ovu - timedelta(days=5)) <= today <= (ovu + timedelta(days=1)): pk = "ovulation"
        elif (last + timedelta(days=m_len)) <= today < (ovu - timedelta(days=5)): pk = "follicular"
        else: pk = "luteal"
        
        # 建议板块回归：强制刷新显示
        st.markdown(f"### {t('adv_title')} - <span style='color:#FF6B81'>{t('phase_'+pk)}</span>", unsafe_allow_html=True)
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

    # 4. 每日日记
    st.divider()
    st.subheader(t('log_title'))
    with st.form("daily_log"):
        ld = st.date_input("Date", datetime.now())
        lm = st.select_slider(t('moods')[2], options=t('moods'))
        ls = st.multiselect("Symptoms", t('syms'))
        ln = st.text_area("Notes")
        if st.form_submit_button(t('btn_save_log')):
            nl = pd.DataFrame({"username":[st.session_state.current_user], "type":["daily_log"], "date":[ld.strftime("%Y-%m-%d")], "menses_length":[0], "mood":[lm], "symptoms":[", ".join(ls)], "notes":[ln]})
            pd.concat([df, nl], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()

    # 5. 历史记录
    with st.expander(t('hist_title')):
        st.dataframe(u_data[['date', 'type', 'mood', 'symptoms', 'notes']].sort_values('date', ascending=False), use_container_width=True, hide_index=True)