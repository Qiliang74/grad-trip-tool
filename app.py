import streamlit as st
import pandas as pd
import plotly.express as px
import uuid
from typing import List, Dict

# 初始化全局状态
def init_session():
    if 'teams' not in st.session_state:
        st.session_state.teams = {}
    if 'current_team' not in st.session_state:
        st.session_state.current_team = None

# 创建团队，生成6位团队邀请码
def create_team(team_name: str) -> str:
    team_code = str(uuid.uuid4())[:6].upper()
    st.session_state.teams[team_code] = {
        'name': team_name,
        'members': [],
        'itinerary': [],
        'expenses': []
    }
    return team_code

# 加入团队
def join_team(team_code: str) -> bool:
    team_code = team_code.upper()
    if team_code in st.session_state.teams:
        st.session_state.current_team = team_code
        return True
    return False

# 添加成员信息
def add_member(name: str, budget: float, destinations: List[str], days: int):
    team = st.session_state.teams[st.session_state.current_team]
    member = {
        'name': name,
        'budget': budget,
        'destinations': destinations,
        'days': days
    }
    team['members'].append(member)

# 统计目的地投票
def get_destination_votes() -> Dict[str, int]:
    team = st.session_state.teams[st.session_state.current_team]
    vote_count = {}
    for member in team['members']:
        for dest in member['destinations']:
            vote_count[dest] = vote_count.get(dest, 0) + 1
    return dict(sorted(vote_count.items(), key=lambda x: x[1], reverse=True))

# 生成推荐行程模板
def generate_itinerary(destination: str, days: int) -> List[str]:
    templates = {
        "成都": [
            "Day1: 抵达成都 - 宽窄巷子 - 锦里古街 - 宿市区",
            "Day2: 大熊猫繁育研究基地 - 春熙路 - 太古里 - 宿市区",
            "Day3: 都江堰 - 青城山一日游 - 宿市区",
            "Day4: 武侯祠 - 杜甫草堂 - 人民公园喝茶 - 返程"
        ],
        "西安": [
            "Day1: 抵达西安 - 钟楼鼓楼 - 回民街 - 宿市区",
            "Day2: 秦始皇兵马俑 - 华清宫 - 宿市区",
            "Day3: 西安城墙 - 陕西历史博物馆 - 大唐不夜城 - 宿市区",
            "Day4: 华山一日游 - 返程"
        ],
        "厦门": [
            "Day1: 抵达厦门 - 中山路步行街 - 宿厦门岛",
            "Day2: 鼓浪屿一日游 - 宿厦门岛",
            "Day3: 厦门大学 - 南普陀寺 - 曾厝垵 - 宿厦门岛",
            "Day4: 集美学村 - 返程"
        ],
        "大理": [
            "Day1: 抵达大理 - 大理古城 - 宿古城",
            "Day2: 环洱海骑行 - 双廊古镇 - 宿双廊",
            "Day3: 苍山索道 - 喜洲古镇 - 宿古城",
            "Day4: 崇圣寺三塔 - 返程"
        ],
        "重庆": [
            "Day1: 抵达重庆 - 解放碑 - 洪崖洞 - 宿市区",
            "Day2: 磁器口古镇 - 长江索道 - 南山一棵树 - 宿市区",
            "Day3: 武隆天坑一日游 - 宿市区",
            "Day4: 鹅岭二厂 - 李子坝轻轨 - 返程"
        ],
        "青岛": [
            "Day1: 抵达青岛 - 栈桥 - 中山路 - 宿市南区",
            "Day2: 八大关 - 第二海水浴场 - 五四广场 - 宿市南区",
            "Day3: 崂山一日游 - 宿市区",
            "Day4: 啤酒博物馆 - 台东步行街 - 返程"
        ],
        "长沙": [
            "Day1: 抵达长沙 - 五一广场 - 太平老街 - 宿市区",
            "Day2: 橘子洲 - 岳麓山 - 湖南大学 - 宿市区",
            "Day3: 湖南省博物馆 - 文和友 - 宿市区",
            "Day4: 谢子龙影像馆 - 返程"
        ]
    }
    default = [f"Day{i+1}: 自由活动 - 探索{destination}当地特色" for i in range(days)]
    schedule = templates.get(destination, default)
    return schedule[:days]

# 添加消费记录
def add_expense(item: str, amount: float, payer: str, participants: List[str]):
    team = st.session_state.teams[st.session_state.current_team]
    expense = {
        'item': item,
        'amount': amount,
        'payer': payer,
        'participants': participants
    }
    team['expenses'].append(expense)

# 计算费用分摊与最优转账方案
def calculate_split():
    team = st.session_state.teams[st.session_state.current_team]
    members = [m['name'] for m in team['members']]
    balance = {name: 0.0 for name in members}
    
    for exp in team['expenses']:
        per_person = exp['amount'] / len(exp['participants'])
        balance[exp['payer']] += exp['amount']
        for p in exp['participants']:
            balance[p] -= per_person
    
    debtors = [(name, -amt) for name, amt in balance.items() if amt < -0.01]
    creditors = [(name, amt) for name, amt in balance.items() if amt > 0.01]
    
    transfers = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        d_name, d_amt = debtors[i]
        c_name, c_amt = creditors[j]
        transfer = min(d_amt, c_amt)
        transfers.append({
            '付款人': d_name,
            '收款人': c_name,
            '金额(元)': round(transfer, 2)
        })
        debtors[i] = (d_name, d_amt - transfer)
        creditors[j] = (c_name, c_amt - transfer)
        if debtors[i][1] < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1
    
    return balance, transfers

# 首页
def show_home():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("👥 快速组队")
        st.write("创建团队生成邀请码，同学输入即可加入，一键收集所有人的预算和目的地偏好。")
    with col2:
        st.subheader("🗺️ 统一行程")
        st.write("自动统计目的地投票，生成推荐行程模板，支持自定义调整，所有人同步最新安排。")
    with col3:
        st.subheader("💰 智能AA")
        st.write("记录每一笔消费，自动计算每人分摊金额，生成最优转账方案，告别算账烦恼。")
    
    st.divider()
    st.subheader("使用指南")
    steps = [
        "第一步：创建团队，分享团队码给小伙伴",
        "第二步：所有人加入团队，填写预算和意向目的地",
        "第三步：投票选出目的地，生成统一行程",
        "第四步：旅行中记录消费，自动计算分摊账单"
    ]
    for i, step in enumerate(steps, 1):
        st.write(f"{i}. {step}")

# 组队页面
def show_team():
    if not st.session_state.current_team:
        tab1, tab2 = st.tabs(["创建新团队", "加入已有团队"])
        with tab1:
            st.subheader("创建你的旅行团")
            team_name = st.text_input("团队名称", placeholder="比如：2024届毕业旅行团")
            if st.button("创建团队", type="primary"):
                if team_name.strip():
                    code = create_team(team_name.strip())
                    st.session_state.current_team = code
                    st.success(f"团队创建成功！团队码：{code}")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("请输入团队名称")
        
        with tab2:
            st.subheader("加入朋友的团队")
            team_code = st.text_input("输入团队码", placeholder="6位大写字母数字")
            if st.button("加入团队", type="primary"):
                if join_team(team_code):
                    st.success("加入成功！")
                    st.rerun()
                else:
                    st.error("团队码不存在，请检查后重试")
    else:
        team = st.session_state.teams[st.session_state.current_team]
        st.subheader(f"📋 {team['name']} - 成员列表")
        
        with st.expander("➕ 添加成员信息", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("姓名")
                budget = st.number_input("预算（元）", min_value=0, value=2000, step=100)
            with col2:
                days = st.slider("计划出行天数", 1, 7, 3)
                dest_options = ["成都", "西安", "厦门", "大理", "重庆", "青岛", "长沙", "武汉"]
                destinations = st.multiselect("意向目的地（可多选）", dest_options)
            
            if st.button("提交信息", type="primary"):
                if name.strip() and destinations:
                    add_member(name.strip(), budget, destinations, days)
                    st.success(f"{name} 加入成功！")
                    st.rerun()
                else:
                    st.warning("请填写姓名并选择至少一个目的地")
        
        if team['members']:
            df = pd.DataFrame(team['members'])
            df = df.rename(columns={
                'name': '姓名', 'budget': '预算(元)',
                'destinations': '意向目的地', 'days': '计划天数'
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.subheader("📊 预算统计")
            col1, col2, col3 = st.columns(3)
            budgets = [m['budget'] for m in team['members']]
            with col1:
                st.metric("团队人数", len(team['members']))
            with col2:
                st.metric("平均预算", f"¥{int(sum(budgets)/len(budgets))}")
            with col3:
                st.metric("总预算池", f"¥{sum(budgets)}")
        else:
            st.info("暂无成员，快添加第一个成员吧~")

# 行程规划页面
def show_itinerary():
    if not st.session_state.current_team:
        st.warning("请先创建或加入团队")
        return
    team = st.session_state.teams[st.session_state.current_team]
    if not team['members']:
        st.warning("请先添加团队成员")
        return
    
    st.subheader("🗳️ 目的地投票统计")
    votes = get_destination_votes()
    if votes:
        vote_df = pd.DataFrame({
            '目的地': list(votes.keys()),
            '票数': list(votes.values())
        })
        fig = px.bar(vote_df, x='目的地', y='票数', color='目的地', 
                     title='目的地投票结果', text='票数')
        st.plotly_chart(fig, use_container_width=True)
        top_dest = list(votes.keys())[0]
        st.info(f"最高票目的地：**{top_dest}**（{votes[top_dest]}票）")
    else:
        st.info("暂无投票数据")
    
    st.divider()
    st.subheader("📅 行程安排")
    col1, col2 = st.columns(2)
    with col1:
        selected_dest = st.selectbox("选择目的地", list(votes.keys()) if votes else ["成都"])
    with col2:
        avg_days = int(sum([m['days'] for m in team['members']]) / len(team['members']))
        travel_days = st.slider("出行天数", 1, 7, avg_days)
    
    if st.button("生成推荐行程", type="primary"):
        itinerary = generate_itinerary(selected_dest, travel_days)
        team['itinerary'] = itinerary
        st.success("行程生成成功！")
    
    if team['itinerary']:
        st.write("### 最终行程单")
        for i, day in enumerate(team['itinerary'], 1):
            with st.expander(f"📌 {day.split(':')[0]}", expanded=True):
                st.write(day.split(':')[1].strip())
        
        itinerary_text = "\n".join(team['itinerary'])
        st.download_button(
            "下载行程单",
            data=itinerary_text,
            file_name=f"{selected_dest}_毕业旅行行程.txt",
            mime="text/plain"
        )
    else:
        st.info("点击上方按钮生成推荐行程")

# 费用分摊页面
def show_expense():
    if not st.session_state.current_team:
        st.warning("请先创建或加入团队")
        return
    team = st.session_state.teams[st.session_state.current_team]
    member_names = [m['name'] for m in team['members']]
    
    if not member_names:
        st.warning("请先添加团队成员")
        return
    
    st.subheader("💸 添加消费记录")
    with st.expander("➕ 新增一笔消费", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            item = st.text_input("消费项目", placeholder="比如：聚餐、门票、打车")
            amount = st.number_input("总金额（元）", min_value=0.0, value=0.0, step=10.0)
        with col2:
            payer = st.selectbox("付款人", member_names)
            participants = st.multiselect("参与分摊的人", member_names, default=member_names)
        
        if st.button("记录消费", type="primary"):
            if item.strip() and amount > 0 and participants:
                add_expense(item.strip(), amount, payer, participants)
                st.success("消费记录已添加！")
                st.rerun()
            else:
                st.warning("请填写完整信息")
    
    st.divider()
    if team['expenses']:
        st.subheader("📋 所有消费记录")
        exp_df = pd.DataFrame(team['expenses'])
        exp_df = exp_df.rename(columns={
            'item': '消费项目', 'amount': '金额(元)',
            'payer': '付款人', 'participants': '参与人'
        })
        st.dataframe(exp_df, use_container_width=True, hide_index=True)
        
        total_exp = sum([e['amount'] for e in team['expenses']])
        st.metric("总消费金额", f"¥{total_exp:.2f}")
        
        st.subheader("🧮 分摊结算")
        balance, transfers = calculate_split()
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**个人余额**")
            balance_df = pd.DataFrame({
                '成员': list(balance.keys()),
                '余额(元)': [round(v, 2) for v in balance.values()]
            })
            balance_df['状态'] = balance_df['余额(元)'].apply(
                lambda x: '应收' if x > 0 else '应付' if x < 0 else '已结清'
            )
            st.dataframe(balance_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.write("**转账方案**")
            if transfers:
                trans_df = pd.DataFrame(transfers)
                st.dataframe(trans_df, use_container_width=True, hide_index=True)
            else:
                st.success("所有账目已结清！")
        
        st.subheader("📊 消费分布")
        fig = px.pie(exp_df, values='金额(元)', names='消费项目', title='消费项目占比')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无消费记录，开始记录第一笔消费吧~")

# 主程序
def main():
    st.set_page_config(page_title="毕业旅行拼团规划工具", page_icon="🎒", layout="wide")
    init_session()
    
    st.title("🎒 毕业旅行拼团规划工具")
    st.caption("毕业季轻松组队 · 统一行程 · 智能AA算账")
    
    with st.sidebar:
        st.header("导航菜单")
        page = st.radio("选择功能", ["🏠 首页", "👥 团队组队", "🗺️ 行程规划", "💰 费用分摊"])
        
        st.divider()
        if st.session_state.current_team:
            team = st.session_state.teams[st.session_state.current_team]
            st.success(f"当前团队：{team['name']}")
            st.code(f"团队码：{st.session_state.current_team}", language=None)
            if st.button("退出当前团队"):
                st.session_state.current_team = None
                st.rerun()
        else:
            st.info("请先创建或加入一个团队")
    
    if page == "🏠 首页":
        show_home()
    elif page == "👥 团队组队":
        show_team()
    elif page == "🗺️ 行程规划":
        show_itinerary()
    elif page == "💰 费用分摊":
        show_expense()

if __name__ == "__main__":
    main()