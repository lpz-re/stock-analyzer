import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

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

# 侧边栏
with st.sidebar:
    st.header("📖 使用说明")
    st.markdown("""
    1. 输入股票代码（如：000858）
    2. 点击"开始分析"
    3. 查看实时行情
    
    **数据来源**：新浪财经
    """)
    
    st.divider()
    st.caption("© 2024 智能股票助手")

# 主界面
col1, col2 = st.columns([3, 1])
with col1:
    symbol = st.text_input("请输入股票代码", value="000858")
with col2:
    analyze_button = st.button("🔍 开始分析", type="primary", use_container_width=True)

if analyze_button:
    if not symbol:
        st.error("请输入股票代码")
    else:
        with st.spinner(f"正在获取 {symbol} 的数据..."):
            try:
                # 格式化代码（A股）
                if symbol.startswith('6'):
                    formatted = f"sh{symbol}"
                else:
                    formatted = f"sz{symbol}"
                
                # 调用新浪财经API
                url = f"https://hq.sinajs.cn/list={formatted}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://finance.sina.com.cn'
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.text.split('="')
                    if len(data) > 1:
                        stock_data = data[1].split(',')
                        
                        # 显示主要数据
                        st.subheader(f"📊 {symbol} 实时行情")
                        
                        # 指标卡片
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            current_price = float(stock_data[3])
                            st.metric("当前价格", f"¥{current_price:.2f}")
                        with col2:
                            prev_close = float(stock_data[2])
                            change = ((current_price - prev_close) / prev_close) * 100
                            st.metric("涨跌幅", f"{change:.2f}%", delta=f"{change:.2f}%")
                        with col3:
                            st.metric("今开", f"¥{float(stock_data[1]):.2f}")
                        with col4:
                            st.metric("昨收", f"¥{prev_close:.2f}")
                        
                        # 详细数据表格
                        st.subheader("📋 详细行情")
                        detail_df = pd.DataFrame({
                            "指标": ["最高", "最低", "成交量(手)", "成交额(万元)", "日期", "时间"],
                            "数值": [
                                f"¥{float(stock_data[4]):.2f}",
                                f"¥{float(stock_data[5]):.2f}",
                                f"{int(float(stock_data[8])):,}",
                                f"{int(float(stock_data[9])/10000):,}",
                                stock_data[30] if len(stock_data) > 30 else "N/A",
                                stock_data[31] if len(stock_data) > 31 else "N/A"
                            ]
                        })
                        st.dataframe(detail_df, use_container_width=True, hide_index=True)
                        
                        # 简单的K线图（模拟数据用于演示）
                        st.subheader("📈 近期走势示意")
                        
                        # 生成30天的模拟数据
                        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                        base_price = current_price
                        
                        mock_data = pd.DataFrame({
                            '日期': dates,
                            '收盘': [base_price * (1 + 0.01 * i) for i in range(30)]
                        })
                        
                        fig = px.line(mock_data, x='日期', y='收盘', title=f"{symbol} 收盘价走势")
                        fig.update_layout(
                            xaxis_title="日期",
                            yaxis_title="价格 (元)",
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    else:
                        st.error("未找到该股票数据")
                else:
                    st.error("无法连接到数据源")
                    
            except Exception as e:
                st.error(f"数据获取失败: {str(e)}")
                st.info("提示：请检查股票代码是否正确，或稍后重试")

# 底部
st.divider()
st.caption(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
