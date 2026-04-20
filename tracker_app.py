import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib
import calendar

# ==========================================
# 🌸 1. 现代质感 UI & 手机适配
# ==========================================
st.set_page_config(page_title="Glow Pro", page_icon="🌸", layout="centered")

st.markdown("""
<head>
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3667/3667231.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
</head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', 'PingFang SC', sans-serif !important; }
    .stApp { background-color: #FFFDFD !important; }
    
    /* 侧边栏及按钮 */
    [data-testid="stSidebar"] { background-color: #FFF0F5 !important; }
    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
        color: #721c24 !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: 800 !important;
        width: 100%;
        box-shadow: 0 4px 10px rgba(255, 154, 158, 0.3);
    }
    
    /* 卡片美化 */
    .stExpander {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 107, 129, 0.2) !important;
        background-color: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
    }
    
    /* 标签页样式优化 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F8F9FA;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }
    
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #121212 !important; }
        .stMarkdown, p, label, span { color: #F0F0F0 !important; }
        .stExpander { background-color: #1E1E1E !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 2. 多语言系统
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = 'zh'

lang_dict = {
    'zh': {
        'app_title': "🌸 Glow Pro 智能助手",
        'tab_dash': "📈 看板", 'tab_cal': "📅 日历", 'tab_log': "📝 记录", 'tab_set': "⚙️ 数据",
        'sidebar_len': "平均经期天数", 'btn_logout': "👋 退出登录",
        'pred_next': "下次月经预计", 'pred_ovu': "排卵日预计",
        'adv_title': "👨‍⚕️ 阶段建议", 'adv_diet': "🍽️ 饮食", 'adv_exe': "🏃‍♀️ 运动", 'adv_med': "💡 贴士",
        'log_habits': "💊 习惯打卡", 'habit_water': "今日喝够 2L 水", 'habit_vit': "今日已吃保健品/叶酸",
        'export_btn': "📥 导出就医报告 (CSV)", 'hist_title': "📖 历史日志",
        'phase_menstrual': "月经期", 'phase_follicular': "滤泡期", 'phase_ovulation': "排卵期", 'phase_luteal': "黄体期"
    },
    'en': {
        'app_title': "🌸 Glow Pro Tracker",
        'tab_dash': "📈 Dash", 'tab_cal': "📅 Calendar", 'tab_log': "📝 Log", 'tab_set': "⚙️ Data",
        'sidebar_len': "Avg Period Days", 'btn_logout': "👋 Logout",
        'pred_next': "Next Period", 'pred_ovu': "Est. Ovulation",
        'adv_title': "👨‍⚕️ Daily Advice", 'adv_diet': "🍽️ Diet", 'adv_exe': "🏃‍♀️ Exercise", 'adv_med': "💡 Tips",
        'log_habits': "💊 Habit Tracker", 'habit_water': "2L Water Done", 'habit_vit': "Vitamins Taken",
        'export_btn': "📥 Export Medical Report (CSV)", 'hist_title': "📖 History Logs",
        'phase_menstrual': "Menstrual", 'phase_follicular': "Follicular", 'phase_ovulation': "Ovulation", 'phase_luteal': "Luteal"
    }
}
def t(key): return lang_dict[st.session_state.lang].get(key, key)

# --- 医生建议数据 ---
doctor_advice = {
    "menstrual": {"zh": {"d": ["补铁：红肉", "温水"], "e": ["慢走"], "m": ["注意保暖"]}, "en": {"d": ["Iron: Red meat", "Warm water"], "e": ["Walk"], "m": ["Stay warm"]}},
    "follicular": {"zh": {"d": ["高蛋白：鱼"], "e": ["慢跑"], "m": ["精力充沛"]}, "en": {"d": ["Protein: Fish"], "e": ["Jogging"], "m": ["High energy"]}},
    "ovulation": {"zh": {"d": ["备孕叶酸"], "e": ["HIIT训练"], "m": ["黄金期"]}, "en": {"d": ["Folic acid"], "e": ["HIIT"], "m": ["Prime time"]}},
    "luteal": {"zh": {"d": ["复合碳水"], "e": ["瑜伽"], "m": ["预防PMS"]}, "en": {"d": ["Complex carbs"], "e": ["Yoga"], "m": ["PMS alert"]}}
}

# ==========================================
# 📂 3. 数据持久化逻辑
# ==========================================
USERS_FILE = "users.csv"
DATA_FILE = "health_log.csv"
def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def init_files():
    if not os.path.exists(USERS_FILE): pd.DataFrame(columns=["username", "password_hash"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(DATA_FILE): pd.DataFrame(columns=["username", "type", "date", "mood", "symptoms", "notes", "water", "vit"]).to_csv(DATA_FILE, index=False)
init_files()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ==========================================
# 核心逻辑：登录页
# ==========================================
if not st.session_state.logged_in:
    st.title(t('app_title'))
    lang_choice = st.radio("Language", ["中文", "English"], horizontal=True)
    st.session_state.lang = 'zh' if lang_choice == "中文" else 'en'
    
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        u = st.text_input("User", key="l_u").strip()
        p = st.text_input("Pwd", type="password", key="l_p")
        if st.button("Sign In"):
            udf = pd.read_csv(USERS_FILE)
            if u in udf['username'].values and make_hash(p) == udf.loc[udf['username']==u, 'password_hash'].values[0]:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Login Error")
    with t2:
        ru = st.text_input("New User", key="r_u").strip()
        rp = st.text_input("New Pwd", type="password", key="r_p")
        if st.button("Register"):
            udf = pd.read_csv(USERS_FILE)
            if ru and ru not in udf['username'].values:
                pd.concat([udf, pd.DataFrame({"username":[ru], "password_hash":[make_hash(rp)]})]).to_csv(USERS_FILE, index=False)
                st.success("Registered!")
# ==========================================
# 核心逻辑：主界面 (Tab 布局)
# ==========================================
else:
    # 侧边栏控制
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    m_len = st.sidebar.number_input(t('sidebar_len'), 2, 10, 5)
    st.sidebar.divider()
    if st.sidebar.button(t('btn_logout')):
        st.session_state.logged_in = False
        st.rerun()

    # 主 Tab 切换
    tab_dash, tab_cal, tab_log, tab_set = st.tabs([t('tab_dash'), t('tab_cal'), t('tab_log'), t('tab_set')])
    
    df = pd.read_csv(DATA_FILE)
    u_data = df[df['username'] == st.session_state.current_user].copy()
    u_data['date'] = pd.to_datetime(u_data['date'])
    p_recs = u_data[u_data['type'] == 'period_start'].sort_values('date')
    avg = int(p_recs['date'].diff().dt.days.dropna().mean()) if len(p_recs)>=2 else 28

    # --- Tab 1: 看板 (预测与建议) ---
    with tab_dash:
        if len(p_recs) > 0:
            last = p_recs['date'].iloc[-1].date()
            nxt = last + timedelta(days=avg)
            ovu = nxt - timedelta(days=14)
            
            c1, c2 = st.columns(2)
            c1.metric(t('pred_next'), str(nxt))
            c2.metric(t('pred_ovu'), str(ovu))
            
            # 阶段判断
            today = datetime.now().date()
            if last <= today < (last + timedelta(days=m_len)): pk = "menstrual"
            elif (ovu - timedelta(days=5)) <= today <= (ovu + timedelta(days=1)): pk = "ovulation"
            elif (last + timedelta(days=m_len)) <= today < (ovu - timedelta(days=5)): pk = "follicular"
            else: pk = "luteal"
            
            st.info(f"✨ {t('adv_title')}: **{t('phase_'+pk)}**")
            adv = doctor_advice[pk][st.session_state.lang]
            ac1, ac2, ac3 = st.columns(3)
            with ac1: st.write(f"**{t('adv_diet')}**\n" + "\n".join([f"• {i}" for i in adv['d']]))
            with ac2: st.write(f"**{t('adv_exe')}**\n" + "\n".join([f"• {i}" for i in adv['e']]))
            with ac3: st.write(f"**{t('adv_med')}**\n" + "\n".join([f"• {i}" for i in adv['m']]))
        else:
            st.warning("Please log your first period in 'Log' tab!")

    # --- Tab 2: 视觉化预测日历 ---
    with tab_cal:
        st.subheader("🗓️ Future Outlook")
        if len(p_recs) > 0:
            last = p_recs['date'].iloc[-1].date()
            # 预测未来三轮
            predictions = []
            for i in range(1, 4):
                p_start = last + timedelta(days=avg * i)
                o_day = p_start - timedelta(days=14)
                predictions.append({"Month": p_start.strftime("%B"), "Period": p_start, "Ovulation": o_day})
            
            p_df = pd.DataFrame(predictions)
            st.table(p_df)
            st.caption("Tip: Use these dates to plan your trips or events! ✈️")
        else:
            st.write("No data to predict yet.")

    # --- Tab 3: 记录与打卡 ---
    with tab_log:
        st.subheader(t('record_title'))
        d_in = st.date_input("Start Date", datetime.now())
        if st.button(t('btn_save_date')):
            nr = pd.DataFrame({"username":[st.session_state.current_user], "type":["period_start"], "date":[d_in.strftime("%Y-%m-%d")], "mood":[""], "symptoms":[""], "notes":[""], "water":[False], "vit":[False]})
            pd.concat([df, nr], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.rerun()
            
        st.divider()
        st.subheader(t('log_habits'))
        with st.form("daily_form"):
            ld = st.date_input("Today", datetime.now())
            w = st.toggle(t('habit_water'))
            v = st.toggle(t('habit_vit'))
            m = st.select_slider("Mood", ["😭","😔","😐","🙂","😄"], value="😐")
            n = st.text_area("Notes")
            if st.form_submit_button(t('btn_save_log')):
                nl = pd.DataFrame({"username":[st.session_state.current_user], "type":["daily_log"], "date":[ld.strftime("%Y-%m-%d")], "mood":[m], "symptoms":[""], "notes":[n], "water":[w], "vit":[v]})
                pd.concat([df, nl], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.success("Saved!")

    # --- Tab 4: 设置与导出 ---
    with tab_set:
        st.subheader(t('hist_title'))
        # 导出报告
        if not u_data.empty:
            csv = u_data.to_csv(index=False).encode('utf-8')
            st.download_button(t('export_btn'), data=csv, file_name=f"Glow_Report_{st.session_state.current_user}.csv", mime="text/csv")
        
        st.dataframe(u_data.sort_values('date', ascending=False), use_container_width=True, hide_index=True)