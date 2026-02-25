import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="股票助手",
    page_icon="📈",
    layout="wide"
)

st.title("📈 股票信息助手（演示版）")

st.info("""
    **系统正在升级中...**
    
    由于技术调整，暂时使用演示数据。
    输入股票代码查看示例效果。
""")

# 输入框
col1, col2 = st.columns([3, 1])
with col1:
    symbol = st.text_input("股票代码", value="000858")
with col2:
    market = st.selectbox("市场", ["A股", "港股", "美股"])

if st.button("查询", type="primary"):
    with st.spinner("正在获取数据..."):
        # 模拟数据 - 不依赖任何复杂库
        st.success(f"查询成功：{symbol}")
        
        # 显示模拟数据卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("当前价格", "¥158.30", "+2.5%")
        with col2:
            st.metric("今开", "¥155.20")
        with col3:
            st.metric("最高", "¥159.80")
        with col4:
            st.metric("最低", "¥154.60")
        
        # 简单表格
        st.subheader("📊 详细数据")
        data = {
            "指标": ["成交量", "成交额", "市盈率", "换手率"],
            "数值": ["15.2万手", "24.1亿", "25.8倍", "1.2%"]
        }
        
        # 用纯 HTML 显示表格，避免用 pandas
        html_table = """
        <table style="width:100%; border-collapse: collapse;">
            <tr style="background-color: #f0f2f6;">
                <th style="padding: 10px; text-align: left;">指标</th>
                <th style="padding: 10px; text-align: left;">数值</th>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">成交量</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">15.2万手</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">成交额</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">24.1亿</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">市盈率</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">25.8倍</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">换手率</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">1.2%</td>
            </tr>
        </table>
        """
        st.markdown(html_table, unsafe_allow_html=True)
        
        st.caption(f"⏱ 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("⚠️ 注：当前为演示数据，非实时行情")

st.divider()
st.caption("© 2024 股票助手 | 数据仅供参考")
