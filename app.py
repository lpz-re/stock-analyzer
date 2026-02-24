import streamlit as st
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from langchain.agents import tool
import openai

# 页面配置
st.set_page_config(
    page_title="智能股票助手",
    page_icon="📈",
    layout="wide"
)

# 标题和说明
st.title("📈 智能股票信息助手")
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;'>
    <strong>⚠️ 免责声明</strong>：本工具仅提供信息整理，不构成任何投资建议。投资有风险，入市需谨慎。
    </div>
    """, unsafe_allow_html=True)

# 侧边栏 - 使用说明
with st.sidebar:
    st.header("📖 使用说明")
    st.markdown("""
    1. 输入A股股票代码（如：000858）
    2. 点击"开始分析"
    3. 查看实时数据和分析结果
    
    **支持的功能**：
    - 实时股价查询
    - 财务指标分析
    - 新闻情绪速览
    - 技术指标展示
    
    **数据来源**：Akshare（东方财富、新浪财经等）
    """)
    
    st.divider()
    st.caption("© 2024 智能股票助手 | 版本 1.0")

# 主界面 - 输入区域
col1, col2 = st.columns([3, 1])
with col1:
    symbol = st.text_input(
        "请输入股票代码",
        value="000858",
        placeholder="例如：000858（五粮液）、600519（贵州茅台）",
        help="输入6位A股股票代码"
    )
with col2:
    analyze_button = st.button("🔍 开始分析", type="primary", use_container_width=True)

# 当用户点击分析按钮
if analyze_button:
    if not symbol:
        st.error("请输入股票代码")
    else:
        # 显示加载状态
        with st.spinner(f"正在获取 {symbol} 的数据..."):
            try:
                # 创建标签页
                tab1, tab2, tab3, tab4 = st.tabs(["📊 实时行情", "📈 财务指标", "📰 新闻情绪", "📉 技术分析"])
                
                # Tab 1: 实时行情
                with tab1:
                    # 获取实时数据
                    stock_df = ak.stock_zh_a_spot()
                    stock_info = stock_df[stock_df['代码'] == symbol]
                    
                    if not stock_info.empty:
                        stock = stock_info.iloc[0]
                        
                        # 显示主要数据卡片
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("当前价格", f"¥{stock['最新价']}", f"{stock['涨跌幅']}%")
                        with col2:
                            st.metric("今开", f"¥{stock['今开']}")
                        with col3:
                            st.metric("最高", f"¥{stock['最高']}")
                        with col4:
                            st.metric("最低", f"¥{stock['最低']}")
                        
                        # 显示详细数据表
                        st.subheader("详细行情数据")
                        detail_data = {
                            "指标": ["成交量", "成交额", "振幅", "换手率", "市盈率(动态)", "市净率"],
                            "数值": [
                                f"{stock['成交量']}手",
                                f"{stock['成交额']}万",
                                f"{stock['振幅']}%",
                                f"{stock['换手率']}%",
                                stock['市盈率-动态'],
                                stock['市净率']
                            ]
                        }
                        st.dataframe(pd.DataFrame(detail_data), use_container_width=True)
                    else:
                        st.warning("未找到该股票数据，请检查代码是否正确")
                
                # Tab 2: 财务指标
                with tab2:
                    st.subheader("主要财务指标")
                    # 获取财务数据
                    try:
                        financial_df = ak.stock_financial_analysis_indicator(symbol=symbol)
                        if not financial_df.empty:
                            st.dataframe(financial_df.head(5), use_container_width=True)
                            
                            # 简单解读
                            latest = financial_df.iloc[0]
                            st.info(f"**ROE（净资产收益率）**: {latest.get('净资产收益率', 'N/A')}% - 反映公司盈利能力")
                        else:
                            st.write("暂无财务数据")
                    except:
                        st.write("财务数据获取失败")
                
                # Tab 3: 新闻情绪
                with tab3:
                    st.subheader("最新相关新闻")
                    # 获取新闻数据
                    try:
                        news_df = ak.stock_news_em(symbol=symbol)
                        if not news_df.empty:
                            for idx, row in news_df.head(5).iterrows():
                                with st.expander(f"{row['发布时间']} - {row['标题']}"):
                                    st.write(f"来源：{row.get('来源', '未知')}")
                                    st.write(f"[阅读原文]({row.get('链接', '#')})")
                        else:
                            st.write("暂无新闻数据")
                    except:
                        st.write("新闻获取失败，请稍后重试")
                
                # Tab 4: 技术分析
                with tab4:
                    st.subheader("K线图（最近30天）")
                    # 获取历史数据
                    try:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=30)
                        hist_data = ak.stock_zh_a_hist(
                            symbol=symbol,
                            period="daily",
                            start_date=start_date.strftime("%Y%m%d"),
                            end_date=end_date.strftime("%Y%m%d"),
                            adjust="qfq"
                        )
                        
                        if not hist_data.empty:
                            # 用plotly画K线图
                            fig = go.Figure(data=[go.Candlestick(
                                x=hist_data['日期'],
                                open=hist_data['开盘'],
                                high=hist_data['最高'],
                                low=hist_data['最低'],
                                close=hist_data['收盘']
                            )])
                            fig.update_layout(
                                title=f"{symbol} K线图",
                                xaxis_title="日期",
                                yaxis_title="价格",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # 显示简单技术指标
                            ma5 = hist_data['收盘'].rolling(5).mean().iloc[-1]
                            ma10 = hist_data['收盘'].rolling(10).mean().iloc[-1]
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("MA5", f"¥{ma5:.2f}")
                            with col2:
                                st.metric("MA10", f"¥{ma10:.2f}")
                        else:
                            st.write("暂无历史数据")
                    except Exception as e:
                        st.error(f"数据获取失败: {str(e)}")
            
            except Exception as e:
                st.error(f"分析过程中出现错误: {str(e)}")
                st.info("请稍后重试，或检查股票代码是否正确")

# 底部信息
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("数据更新：实时")
with col2:
    st.caption("数据来源：东方财富、新浪财经")
with col3:
    st.caption("更新时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))