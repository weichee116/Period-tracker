import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# --- 页面基础设置 ---
st.set_page_config(page_title="女性健康与周期助手", page_icon="🌸", layout="centered")

# --- 文件路径配置 ---
USERS_FILE = "users.csv"
DATA_FILE = "health_log.csv"

# --- 辅助函数：密码加密 ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 辅助函数：初始化数据文件 ---
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username", "password_hash"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["username", "type", "date", "cycle_length", "mood", "symptoms", "notes"]).to_csv(DATA_FILE, index=False)

init_files()

# --- 状态管理初始化 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ==========================================
# 模块 1：用户注册与登录系统
# ==========================================
def login_register_page():
    st.title("🌸 女性健康与周期助手")
    st.write("欢迎！请登录或注册以管理您的专属健康数据。")
    
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

    with tab2:
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
# 模块 2：主控面板 (登录后可见)
# ==========================================
def main_dashboard():
    # 侧边栏：用户信息与退出
    st.sidebar.title(f"👤 你好, {st.session_state.current_user}")
    if st.sidebar.button("退出登录"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    st.title("🌸 我的健康数据看板")
    
    # 加载当前用户的数据
    df = pd.read_csv(DATA_FILE)
    user_data = df[df['username'] == st.session_state.current_user].copy()
    user_data['date'] = pd.to_datetime(user_data['date'])
    
    # 筛选出所有的“月经开始日”记录，并按时间排序
    period_records = user_data[user_data['type'] == 'period_start'].sort_values('date')
    
    # --- 核心逻辑：动态计算平均周期 ---
    avg_cycle = 28 # 默认值
    if len(period_records) >= 2:
        # 计算相邻两次月经的间隔天数
        intervals = period_records['date'].diff().dt.days.dropna()
        avg_cycle = int(intervals.mean()) # 取平均值
    
    # --- 顶栏：记录新的月经开始日 ---
    with st.expander("🩸 记录新的月经开始日", expanded=(len(period_records)==0)):
        new_period_date = st.date_input("选择本次月经第一天的日期", datetime.now())
        if st.button("保存月经日期"):
            # 检查是否同一天已经记录过
            if not period_records.empty and pd.to_datetime(new_period_date) in period_records['date'].values:
                st.warning("这一天已经记录过啦！")
            else:
                new_record = pd.DataFrame({
                    "username": [st.session_state.current_user],
                    "type": ["period_start"],
                    "date": [new_period_date.strftime("%Y-%m-%d")],
                    "cycle_length": [0], "mood": [""], "symptoms": [""], "notes": [""]
                })
                pd.concat([df, new_record], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.success("记录成功！")
                st.rerun()

    st.divider()

    # --- 预测面板 ---
    st.subheader("🔮 周期预测")
    if len(period_records) == 0:
        st.info("💡 请先在上方记录至少一次您的月经开始日期，以启动预测功能。记录两次以上预测会更准确哦！")
    else:
        last_period_date = period_records['date'].iloc[-1].date()
        next_period = last_period_date + timedelta(days=avg_cycle)
        ovulation_day = next_period - timedelta(days=14)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("最后一次记录", str(last_period_date))
        col2.metric("当前个人平均周期", f"{avg_cycle} 天", "动态计算" if len(period_records)>=2 else "默认")
        col3.metric("✨ 预测下次排卵日", str(ovulation_day))
        
        st.success(f"**🩸 预测下次月经日：{next_period}**")

    # --- 每日日记功能 ---
    st.divider()
    st.subheader("📝 每日健康日记")
    with st.form("daily_log_form"):
        log_date = st.date_input("日记日期", datetime.now())
        mood = st.select_slider("今日心情", options=["😭 崩溃", "😔 低落", "😐 平静", "🙂 开心", "😄 极佳"], value="😐 平静")
        symptoms = st.multiselect("身体症状", ["腹痛", "头痛", "胸痛", "疲劳", "长痘", "腰酸", "无不适"])
        notes = st.text_area("其他备注")
        if st.form_submit_button("保存日记"):
            new_log = pd.DataFrame({
                "username": [st.session_state.current_user],
                "type": ["daily_log"],
                "date": [log_date.strftime("%Y-%m-%d")],
                "cycle_length": [0],
                "mood": [mood],
                "symptoms": [", ".join(symptoms)],
                "notes": [notes]
            })
            pd.concat([df, new_log], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("日记保存成功！")
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