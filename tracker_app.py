import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib
import extra_streamlit_components as stx

# ==========================================
# 🌸 1. 极致响应式 UI & 手机端优化
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
    
    .stMarkdown, p, label, span, h1, h2, h3 { color: inherit !important; }

    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
        color: #B71C1C !important; 
        border-radius: 20px !important;
        border: none !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 10px rgba(255, 154, 158, 0.3);
    }
    
    .stExpander {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 107, 129, 0.4) !important;
        background-color: transparent !important; 
    }
    
    [data-testid="stMetricValue"] { color: #FF6B81 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🍪 2. Cookie 管理器 (实现 30 天免登录)
# ==========================================
# 初始化 Cookie 管理器
cookie_manager = stx.CookieManager()

# ==========================================
# 🌐 3. 纯净双语系统 (100% 覆盖)
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = 'zh'

lang_dict = {
    'zh': {
        'app_title': "🌸 Glow Pro 智能助手",
        'tab_login': "🔑 登录", 'tab_reg': "📝 注册",
        'l_user': "用户名", 'l_pwd': "密码", 'btn_in': "登录系统",
        'r_user': "新用户名", 'r_pwd': "新密码", 'btn_up': "立即注册",
        'login_err': "用户名或密码错误！", 'reg_ok': "注册成功！请登录。",
        'tab_dash': "📈 看板", 'tab_cal': "📅 日历", 'tab_log': "📝 记录", 'tab_set': "⚙️ 数据",
        'sidebar_len': "设置默认经期天数", 'btn_logout': "👋 退出登录",
        'pred_next': "下次月经预计", 'pred_ovu': "预计排卵日",
        'alert_late': "⚠️ 智能提醒：您的经期已迟到 {days} 天。",
        'adv_title': "👨‍⚕️ 阶段建议", 'adv_diet': "🍽️ 饮食", 'adv_exe': "🏃‍♀️ 运动", 'adv_med': "💡 贴士",
        'record_title': "🩸 记录经期开始", 'start_date': "开始日期", 'btn_save_date': "💾 保存日期",
        'log_habits': "📝 每日健康数据", 'flow_label': "🩸 今日出血量",
        'flow_levels': ["无 (None)", "极少量 (Spotting)", "少量 (Light)", "中量 (Medium)", "大量 (Heavy)"],
        'habit_water': "喝够 2L 水", 'habit_vit': "已吃保健品",
        'mood_label': "今日心情", 'sym_label': "身体症状", 'note_label': "备注", 'btn_save_log': "💾 保存记录",
        'cal_title': "🗓️ 未来三月预测", 'export_btn': "📥 导出就医报告 (CSV)", 'hist_title': "📖 历史日志",
        'phase_menstrual': "月经期", 'phase_follicular': "滤泡期", 'phase_ovulation': "排卵期", 'phase_luteal': "黄体期",
        'moods': ["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"],
        'syms': ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"]
    },
    'en': {
        'app_title': "🌸 Glow Pro Tracker",
        'tab_login': "🔑 Login", 'tab_reg': "📝 Register",
        'l_user': "Username", 'l_pwd': "Password", 'btn_in': "Sign In",
        'r_user': "New Username", 'r_pwd': "New Password", 'btn_up': "Sign Up",
        'login_err': "Invalid credentials!", 'reg_ok': "Registered! Please login.",
        'tab_dash': "📈 Dash", 'tab_cal': "📅 Calendar", 'tab_log': "📝 Log", 'tab_set': "⚙️ Data",
        'sidebar_len': "Default period days", 'btn_logout': "👋 Logout",
        'pred_next': "Next Period", 'pred_ovu': "Est. Ovulation",
        'alert_late': "⚠️ Alert: Your period is {days} days late.",
        'adv_title': "👨‍⚕️ Daily Advice", 'adv_diet': "🍽️ Diet", 'adv_exe': "🏃‍♀️ Exercise", 'adv_med': "💡 Tips",
        'record_title': "🩸 Log Period Start", 'start_date': "Start Date", 'btn_save_date': "💾 Save Date",
        'log_habits': "📝 Daily Health Data", 'flow_label': "🩸 Flow Intensity",
        'flow_levels': ["None", "Spotting", "Light", "Medium", "Heavy"],
        'habit_water': "2L Water Done", 'habit_vit': "Vitamins Taken",
        'mood_label': "Mood", 'sym_label': "Symptoms", 'note_label': "Notes", 'btn_save_log': "💾 Save Log",
        'cal_title': "🗓️ Future Outlook", 'export_btn': "📥 Export CSV Report", 'hist_title': "📖 History Logs",
        'phase_menstrual': "Menstrual", 'phase_follicular': "Follicular", 'phase_ovulation': "Ovulation", 'phase_luteal': "Luteal",
        'moods': ["😭 Awful", "😔 Sad", "😐 Okay", "🙂 Good", "😄 Great"],
        'syms': ["Cramps", "Headache", "Tender", "Fatigue", "Acne", "Backache", "None"]
    }
}
def t(key): return lang_dict[st.session_state.lang].get(key, key)

doctor_advice = {
    "menstrual": {"zh": {"d": ["补铁：红肉", "温水"], "e": ["慢走"], "m": ["注意保暖"]}, "en": {"d": ["Iron", "Warm water"], "e": ["Walk"], "m": ["Stay warm"]}},
    "follicular": {"zh": {"d": ["高蛋白：鱼"], "e": ["慢跑"], "m": ["精力充沛"]}, "en": {"d": ["Protein"], "e": ["Jogging"], "m": ["High energy"]}},
    "ovulation": {"zh": {"d": ["备孕叶酸"], "e": ["HIIT训练"], "m": ["黄金期"]}, "en": {"d": ["Folic acid"], "e": ["HIIT"], "m": ["Prime time"]}},
    "luteal": {"zh": {"d": ["复合碳水"], "e": ["瑜伽"], "m": ["预防PMS"]}, "en": {"d": ["Complex carbs"], "e": ["Yoga"], "m": ["PMS alert"]}}
}

# ==========================================
# 📂 4. 数据初始化
# ==========================================
USERS_FILE = "users.csv"
DATA_FILE = "health_log.csv"
def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def init_files():
    if not os.path.exists(USERS_FILE): pd.DataFrame(columns=["username", "password_hash"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(DATA_FILE): pd.DataFrame(columns=["username", "type", "date", "mood", "symptoms", "notes", "water", "vit", "flow"]).to_csv(DATA_FILE, index=False)
init_files()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""

# --- 🚀 自动登录拦截器 (读取 Cookie) ---
# 给组件一点时间加载 cookie
if not st.session_state.logged_in:
    cached_user = cookie_manager.get(cookie="glow_pro_user")
    if cached_user:
        st.session_state.logged_in = True
        st.session_state.current_user = cached_user
        st.rerun()

# ==========================================
# 📱 5. 页面逻辑
# ==========================================
if not st.session_state.logged_in:
    st.title(t('app_title'))
    lang_choice = st.radio("Language / 语言", ["中文", "English"], horizontal=True)
    st.session_state.lang = 'zh' if lang_choice == "中文" else 'en'
    t1, t2 = st.tabs([t('tab_login'), t('tab_reg')])
    with t1:
        u = st.text_input(t('l_user'), key="l_u").strip()
        p = st.text_input(t('l_pwd'), type="password", key="l_p")
        if st.button(t('btn_in')):
            udf = pd.read_csv(USERS_FILE)
            if u in udf['username'].values and make_hash(p) == udf.loc[udf['username']==u, 'password_hash'].values[0]:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                # 设置 30 天有效期的 Cookie
                cookie_manager.set("glow_pro_user", u, expires_at=datetime.now() + timedelta(days=30))
                st.rerun()
            else: st.error(t('login_err'))
    with t2:
        ru = st.text_input(t('r_user'), key="r_u").strip()
        rp = st.text_input(t('r_pwd'), type="password", key="r_p")
        if st.button(t('btn_up')):
            udf = pd.read_csv(USERS_FILE)
            if ru and ru not in udf['username'].values:
                pd.concat([udf, pd.DataFrame({"username":[ru], "password_hash":[make_hash(rp)]})]).to_csv(USERS_FILE, index=False)
                st.success(t('reg_ok'))
else:
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    m_len = st.sidebar.number_input(t('sidebar_len'), 2, 10, 5)
    st.sidebar.divider()
    if st.sidebar.button(t('btn_logout')):
        # 退出时删除 Cookie
        cookie_manager.delete("glow_pro_user")
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    tab_dash, tab_cal, tab_log, tab_set = st.tabs([t('tab_dash'), t('tab_cal'), t('tab_log'), t('tab_set')])
    df = pd.read_csv(DATA_FILE)
    u_data = df[df['username'] == st.session_state.current_user].copy()
    u_data['date'] = pd.to_datetime(u_data['date'])
    p_recs = u_data[u_data['type'] == 'period_start'].sort_values('date')
    today = datetime.now().date()
    avg = int(p_recs['date'].diff().dt.days.dropna().mean()) if len(p_recs)>=2 else 28

    # --- 看板 ---
    with tab_dash:
        if len(p_recs) > 0:
            last = p_recs['date'].iloc[-1].date()
            nxt = last + timedelta(days=avg)
            ovu = nxt - timedelta(days=14)
            if (today - last).days > avg + 3: st.error(t('alert_late').format(days=(today - last).days - avg))
            c1, c2 = st.columns(2)
            c1.metric(t('pred_next'), str(nxt))
            c2.metric(t('pred_ovu'), str(ovu))
            
            # 阶段判定
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

    # --- 日历 ---
    with tab_cal:
        st.subheader(t('cal_title'))
        if len(p_recs) > 0:
            last = p_recs['date'].iloc[-1].date()
            preds = []
            for i in range(1, 4):
                p_s = last + timedelta(days=avg * i)
                preds.append({t('pred_next'): p_s.strftime("%Y-%m-%d"), t('pred_ovu'): (p_s - timedelta(days=14)).strftime("%Y-%m-%d")})
            st.table(pd.DataFrame(preds))
        else: st.write("No data.")

    # --- 记录与流量打卡 ---
    with tab_log:
        with st.expander(t('record_title'), True):
            d_in = st.date_input(t('start_date'), datetime.now())
            if st.button(t('btn_save_date')):
                nr = pd.DataFrame({"username":[st.session_state.current_user], "type":["period_start"], "date":[d_in.strftime("%Y-%m-%d")], "flow":[t('flow_levels')[3]]})
                pd.concat([df, nr], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.rerun()
            
        st.divider()
        st.subheader(t('log_habits'))
        with st.form("daily"):
            ld = st.date_input("Date", datetime.now())
            flow_val = st.select_slider(t('flow_label'), options=t('flow_levels'), value=t('flow_levels')[0])
            w, v = st.toggle(t('habit_water')), st.toggle(t('habit_vit'))
            m = st.select_slider(t('mood_label'), t('moods'), value=t('moods')[2])
            s = st.multiselect(t('sym_label'), t('syms'))
            n = st.text_area(t('note_label'))
            if st.form_submit_button(t('btn_save_log')):
                nl = pd.DataFrame({"username":[st.session_state.current_user], "type":["daily_log"], "date":[ld.strftime("%Y-%m-%d")], "mood":[m], "symptoms":[", ".join(s)], "notes":[n], "water":[w], "vit":[v], "flow":[flow_val]})
                pd.concat([df, nl], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.rerun()

    # --- 数据 ---
    with tab_set:
        st.subheader(t('hist_title'))
        csv = u_data.to_csv(index=False).encode('utf-8-sig')
        st.download_button(t('export_btn'), csv, f"Report_{st.session_state.current_user}.csv", "text/csv")
        st.dataframe(u_data.sort_values('date', ascending=False), use_container_width=True, hide_index=True)