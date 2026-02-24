import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(
    page_title="智能股票助手",
    page_icon="📈",
    layout="wide"
)

st.title("📈 智能股票信息助手")
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;'>
    <strong>⚠️ 免责声明</strong>：本工具仅提供信息整理，不构成任何投资建议。投资有风险，入市需谨慎。
    </div>
    """, unsafe_allow_html=True)

# 侧边栏说明
with st.sidebar:
    st.header("📖 使用说明")
    st.markdown("""
    1. 输入股票代码
       - A股：6位代码，如 000858（五粮液）
       - 港股：5位代码，如 00700（腾讯）
       - 美股：字母代码，如 AAPL（苹果）
    
    2. 点击"开始分析"
    
    3. 查看实时数据
    
    **数据来源**：新浪财经
    """)
    
    st.divider()
    st.caption("© 2024 智能股票助手")

# 主界面
col1, col2 = st.columns([3, 1])
with col1:
    symbol = st.text_input(
        "请输入股票代码",
        value="000858",
        placeholder="例如：000858（五粮液）、00700（腾讯）、AAPL（苹果）"
    )
with col2:
    market = st.selectbox(
        "市场",
        options=["A股", "港股", "美股"],
        index=0
    )
    
analyze_button = st.button("🔍 开始分析", type="primary", use_container_width=True)

# 根据市场转换代码格式
def format_symbol(symbol, market):
    if market == "A股":
        return f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}"
    elif market == "港股":
        return f"hk{symbol}"
    else:  # 美股
        return symbol

if analyze_button:
    if not symbol:
        st.error("请输入股票代码")
    else:
        with st.spinner(f"正在获取 {symbol} 的数据..."):
            try:
                # 调用新浪财经API
                formatted_symbol = format_symbol(symbol, market)
                url = f"https://hq.sinajs.cn/list={formatted_symbol}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://finance.sina.com.cn'
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    # 解析新浪返回的数据
                    data = response.text.split('="')
                    if len(data) > 1:
                        stock_data = data[1].split(',')
                        
                        # 创建标签页
                        tab1, tab2 = st.tabs(["📊 实时行情", "📈 技术分析"])
                        
                        with tab1:
                            # 显示主要数据（根据市场调整索引）
                            if market == "A股":
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("当前价格", f"¥{float(stock_data[3]):.2f}")
                                with col2:
                                    st.metric("涨跌幅", f"{((float(stock_data[3])-float(stock_data[2]))/float(stock_data[2])*100):.2f}%")
                                with col3:
                                    st.metric("今开", f"¥{float(stock_data[1]):.2f}")
                                with col4:
                                    st.metric("昨收", f"¥{float(stock_data[2]):.2f}")
                                
                                # 详细数据
                                st.subheader("📊 详细行情")
                                detail_df = pd.DataFrame({
                                    "指标": ["最高", "最低", "成交量(手)", "成交额(万)"],
                                    "数值": [
                                        f"¥{float(stock_data[4]):.2f}",
                                        f"¥{float(stock_data[5]):.2f}",
                                        f"{int(float(stock_data[8])):,}",
                                        f"{int(float(stock_data[9])/10000):,}"
                                    ]
                                })
                                st.dataframe(detail_df, use_container_width=True)
                            
                            elif market == "港股":
                                st.metric("当前价格", f"HK${float(stock_data[6]):.2f}")
                                st.info("港股数据加载中...")
                            
                            else:  # 美股
                                st.metric("当前价格", f"${float(stock_data[1]):.2f}")
                                st.info("美股数据加载中...")
                        
                        with tab2:
                            st.subheader("📈 历史走势（模拟数据）")
                            # 生成模拟K线数据用于展示
                            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                            mock_data = pd.DataFrame({
                                '日期': dates,
                                '开盘': [float(stock_data[1]) * (1 + i*0.01) for i in range(30)],
                                '收盘': [float(stock_data[3]) * (1 + i*0.01) for i in range(30)],
                                '最高': [float(stock_data[4]) * (1 + i*0.01) for i in range(30)],
                                '最低': [float(stock_data[5]) * (1 + i*0.01) for i in range(30)]
                            })
                            
                            fig = go.Figure(data=[go.Candlestick(
                                x=mock_data['日期'],
                                open=mock_data['开盘'],
                                high=mock_data['最高'],
                                low=mock_data['最低'],
                                close=mock_data['收盘']
                            )])
                            fig.update_layout(
                                title=f"{symbol} 近期走势",
                                xaxis_title="日期",
                                yaxis_title="价格",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                    else:
                        st.error("未找到该股票数据，请检查代码是否正确")
                else:
                    st.error("数据源暂时无法访问，请稍后重试")
                    
            except Exception as e:
                st.error(f"数据获取失败: {str(e)}")
                st.info("提示：可以尝试切换市场选项，或检查股票代码格式")

# 底部信息
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("数据更新：实时")
with col2:
    st.caption("数据来源：新浪财经")
with col3:
    st.caption("更新时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
