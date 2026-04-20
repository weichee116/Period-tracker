import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# ==========================================
# 🌸 1. 极致响应式 UI (彻底解决暗色模式看不见字)
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
    
    /* 按钮：固定渐变色 + 纯白文字，保证任何模式下都清晰 */
    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
        color: #FFFFFF !important; 
        text-shadow: 0px 1px 2px rgba(0,0,0,0.1);
        border-radius: 20px !important;
        border: none !important;
        font-weight: 800 !important;
        width: 100%;
        box-shadow: 0 4px 10px rgba(255, 154, 158, 0.3);
    }
    
    /* 卡片容器：透明底色 + 柔和粉色边框，完美适配深/浅模式 */
    .stExpander {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 107, 129, 0.5) !important;
        background-color: transparent !important; 
    }
    
    /* 数字指标颜色固定为强调色 */
    [data-testid="stMetricValue"] {
        color: #FF6B81 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 2. 纯粹的多语言系统 (100% 覆盖)
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
        'sidebar_len': "平均经期天数", 'btn_logout': "👋 退出登录",
        'pred_next': "下次月经预计", 'pred_ovu': "排卵日预计",
        
        'alert_late': "⚠️ 智能提醒：您的经期似乎迟到了 {days} 天，请注意休息，必要时可使用验孕棒或咨询医生。",
        'alert_short': "⚠️ 智能提醒：您上一次的周期短于 21 天，若频繁发生请留意内分泌健康。",
        'alert_long': "⚠️ 智能提醒：您上一次的周期长于 35 天，近期可能压力过大或作息不规律。",
        
        'adv_title': "👨‍⚕️ 阶段建议", 'adv_diet': "🍽️ 饮食", 'adv_exe': "🏃‍♀️ 运动", 'adv_med': "💡 贴士",
        'record_title': "🩸 记录新周期", 'start_date': "月经第一天", 'btn_save_date': "💾 保存日期",
        'log_habits': "💊 习惯打卡与症状", 'habit_water': "今日喝够 2L 水", 'habit_vit': "今日已吃保健品",
        'mood_label': "今日心情", 'sym_label': "身体症状", 'note_label': "其他备注", 'btn_save_log': "💾 保存日记",
        
        'cal_title': "🗓️ 未来三月预测", 'cal_tip': "💡 贴士：利用这些日期提前规划您的旅行或重要会议！", 'cal_none': "暂无足够数据生成日历。",
        'export_btn': "📥 导出就医报告 (CSV)", 'hist_title': "📖 历史日志",
        
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
        'sidebar_len': "Avg Period Days", 'btn_logout': "👋 Logout",
        'pred_next': "Next Period", 'pred_ovu': "Est. Ovulation",
        
        'alert_late': "⚠️ Alert: Your period seems to be {days} days late. Please rest well, and consult a doctor if necessary.",
        'alert_short': "⚠️ Alert: Your last cycle was shorter than 21 days. Monitor for hormonal changes.",
        'alert_long': "⚠️ Alert: Your last cycle was longer than 35 days. Stress or poor sleep might be the cause.",
        
        'adv_title': "👨‍⚕️ Daily Advice", 'adv_diet': "🍽️ Diet", 'adv_exe': "🏃‍♀️ Exercise", 'adv_med': "💡 Tips",
        'record_title': "🩸 Log New Cycle", 'start_date': "First day of period", 'btn_save_date': "💾 Save Date",
        'log_habits': "💊 Habits & Symptoms", 'habit_water': "Drank 2L Water", 'habit_vit': "Took Vitamins",
        'mood_label': "Mood", 'sym_label': "Symptoms", 'note_label': "Notes", 'btn_save_log': "💾 Save Log",
        
        'cal_title': "🗓️ Future Outlook", 'cal_tip': "💡 Tip: Use these dates to plan trips or events!", 'cal_none': "Not enough data to predict.",
        'export_btn': "📥 Export Medical Report (CSV)", 'hist_title': "📖 History Logs",
        
        'phase_menstrual': "Menstrual", 'phase_follicular': "Follicular", 'phase_ovulation': "Ovulation", 'phase_luteal': "Luteal",
        'moods': ["😭 Awful", "😔 Sad", "😐 Okay", "🙂 Good", "😄 Great"],
        'syms': ["Cramps", "Headache", "Tender", "Fatigue", "Acne", "Backache", "None"]
    }
}
def t(key): return lang_dict[st.session_state.lang].get(key, key)

doctor_advice = {
    "menstrual": {"zh": {"d": ["补铁：红肉", "温水"], "e": ["慢走"], "m": ["注意保暖"]}, "en": {"d": ["Iron: Red meat", "Warm water"], "e": ["Walk"], "m": ["Stay warm"]}},
    "follicular": {"zh": {"d": ["高蛋白：鱼"], "e": ["慢跑"], "m": ["精力充沛"]}, "en": {"d": ["Protein: Fish"], "e": ["Jogging"], "m": ["High energy"]}},
    "ovulation": {"zh": {"d": ["备孕叶酸"], "e": ["HIIT训练"], "m": ["黄金期"]}, "en": {"d": ["Folic acid"], "e": ["HIIT"], "m": ["Prime time"]}},
    "luteal": {"zh": {"d": ["复合碳水"], "e": ["瑜伽"], "m": ["预防PMS"]}, "en": {"d": ["Complex carbs"], "e": ["Yoga"], "m": ["PMS alert"]}}
}

# ==========================================
# 📂 3. 数据持久化
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
# 🔑 登录页面
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

# ==========================================
# 📱 主界面 (含隐式预警)
# ==========================================
else:
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    m_len = st.sidebar.number_input(t('sidebar_len'), 2, 10, 5)
    st.sidebar.divider()
    if st.sidebar.button(t('btn_logout')):
        st.session_state.logged_in = False
        st.rerun()

    tab_dash, tab_cal, tab_log, tab_set = st.tabs([t('tab_dash'), t('tab_cal'), t('tab_log'), t('tab_set')])
    
    df = pd.read_csv(DATA_FILE)
    u_data = df[df['username'] == st.session_state.current_user].copy()
    u_data['date'] = pd.to_datetime(u_data['date'])
    p_recs = u_data[u_data['type'] == 'period_start'].sort_values('date')
    today = datetime.now().date()
    avg = int(p_recs['date'].diff().dt.days.dropna().mean()) if len(p_recs)>=2 else 28

    # --- Tab 1: 看板 (预测、隐式预警与建议) ---
    with tab_dash:
        if len(p_recs) > 0:
            last = p_recs['date'].iloc[-1].date()
            nxt = last + timedelta(days=avg)
            ovu = nxt - timedelta(days=14)
            
            # 🚨 隐形式健康预警逻辑 (Smart Health Alerts)
            if len(p_recs) >= 2:
                days_since_last = (today - last).days
                last_cycle_len = int(p_recs['date'].diff().dt.days.dropna().iloc[-1])
                
                if days_since_last > avg + 3:
                    st.error(t('alert_late').format(days=days_since_last - avg))
                if last_cycle_len < 21:
                    st.warning(t('alert_short'))
                elif last_cycle_len > 35:
                    st.warning(t('alert_long'))
            
            c1, c2 = st.columns(2)
            c1.metric(t('pred_next'), str(nxt))
            c2.metric(t('pred_ovu'), str(ovu))
            
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
            st.warning("Please record your data first!")

    # --- Tab 2: 日历 ---
    with tab_cal:
        st.subheader(t('cal_title'))
        if len(p_recs) > 0:
            last = p_recs['date'].iloc[-1].date()
            preds = []
            for i in range(1, 4):
                p_start = last + timedelta(days=avg * i)
                o_day = p_start - timedelta(days=14)
                preds.append({t('pred_next'): p_start.strftime("%Y-%m-%d"), t('pred_ovu'): o_day.strftime("%Y-%m-%d")})
            st.table(pd.DataFrame(preds))
            st.caption(t('cal_tip'))
        else:
            st.write(t('cal_none'))

    # --- Tab 3: 记录与打卡 ---
    with tab_log:
        with st.expander(t('record_title'), expanded=(len(p_recs)==0)):
            d_in = st.date_input(t('start_date'), datetime.now())
            if st.button(t('btn_save_date')):
                nr = pd.DataFrame({"username":[st.session_state.current_user], "type":["period_start"], "date":[d_in.strftime("%Y-%m-%d")], "mood":[""], "symptoms":[""], "notes":[""], "water":[False], "vit":[False]})
                pd.concat([df, nr], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.rerun()
            
        st.subheader(t('log_habits'))
        with st.form("daily_form"):
            ld = st.date_input("Date", datetime.now())
            w = st.toggle(t('habit_water'))
            v = st.toggle(t('habit_vit'))
            m = st.select_slider(t('mood_label'), t('moods'), value=t('moods')[2])
            s = st.multiselect(t('sym_label'), t('syms'))
            n = st.text_area(t('note_label'))
            if st.form_submit_button(t('btn_save_log')):
                nl = pd.DataFrame({"username":[st.session_state.current_user], "type":["daily_log"], "date":[ld.strftime("%Y-%m-%d")], "mood":[m], "symptoms":[", ".join(s)], "notes":[n], "water":[w], "vit":[v]})
                pd.concat([df, nl], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.success("Saved!")

    # --- Tab 4: 设置与导出 ---
    with tab_set:
        st.subheader(t('hist_title'))
        if not u_data.empty:
            csv = u_data.to_csv(index=False).encode('utf-8-sig') # 修复中文字符导出乱码
            st.download_button(t('export_btn'), data=csv, file_name=f"Glow_Report_{st.session_state.current_user}.csv", mime="text/csv")
        st.dataframe(u_data.sort_values('date', ascending=False), use_container_width=True, hide_index=True)