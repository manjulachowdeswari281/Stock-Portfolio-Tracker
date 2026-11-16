
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Stock Portfolio Tracker",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #101820;
    color: white;
}
[data-testid="stMetric"] {
    background: #1c2b36;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #344955;
}
h1, h2, h3 {
    color: #00d09c;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 STOCK PORTFOLIO TRACKER")
st.caption("Manage your investments | Monitor your portfolio")

if "stocks" not in st.session_state:
    st.session_state.stocks = [
        {"Stock": "TCS", "Quantity": 10, "Buy Price": 3200, "Current Price": 3500},
        {"Stock": "INFY", "Quantity": 15, "Buy Price": 1400, "Current Price": 1550},
        {"Stock": "RELIANCE", "Quantity": 5, "Buy Price": 2500, "Current Price": 2400}
    ]

st.sidebar.title("📊 Portfolio Menu")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Stock", "My Holdings"]
)

if page == "Add Stock":
    st.header("➕ Add New Stock")

    with st.form("add_stock"):
        stock = st.text_input("Stock Name").upper()
        quantity = st.number_input("Quantity", min_value=1, step=1)
        buy = st.number_input("Purchase Price (₹)", min_value=0.01)
        current = st.number_input("Current Price (₹)", min_value=0.01)

        submit = st.form_submit_button("Add Stock")

        if submit:
            if stock:
                st.session_state.stocks.append({
                    "Stock": stock,
                    "Quantity": quantity,
                    "Buy Price": buy,
                    "Current Price": current
                })
                st.success("Stock added successfully!")
            else:
                st.warning("Enter a stock name.")

elif page == "Dashboard":
    st.header("📊 Portfolio Overview")

    df = pd.DataFrame(st.session_state.stocks)

    df["Investment"] = df["Quantity"] * df["Buy Price"]
    df["Current Value"] = df["Quantity"] * df["Current Price"]
    df["Profit/Loss"] = df["Current Value"] - df["Investment"]

    investment = df["Investment"].sum()
    current_value = df["Current Value"].sum()
    profit = current_value - investment

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Investment", f"₹{investment:,.2f}")
    col2.metric("Current Value", f"₹{current_value:,.2f}")
    col3.metric("Total Profit / Loss", f"₹{profit:,.2f}")

    st.divider()
    st.subheader("📈 Portfolio Distribution")

    fig = px.pie(
        df,
        values="Current Value",
        names="Stock",
        hole=0.5,
        title="Stock Allocation"
    )
    fig.update_layout(
        paper_bgcolor="#101820",
        plot_bgcolor="#101820",
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💰 Investment Performance")
    chart = px.bar(
        df,
        x="Stock",
        y=["Investment", "Current Value"],
        barmode="group",
        title="Investment vs Current Value"
    )
    chart.update_layout(
        paper_bgcolor="#101820",
        plot_bgcolor="#101820",
        font_color="white"
    )
    st.plotly_chart(chart, use_container_width=True)

elif page == "My Holdings":
    st.header("📋 My Stock Holdings")

    df = pd.DataFrame(st.session_state.stocks)

    df["Investment"] = df["Quantity"] * df["Buy Price"]
    df["Current Value"] = df["Quantity"] * df["Current Price"]
    df["Profit/Loss"] = df["Current Value"] - df["Investment"]

    st.dataframe(df, use_container_width=True)

    if not df.empty:
        selected = st.selectbox("Select stock to remove", df["Stock"].tolist())

        if st.button("Remove Stock"):
            index = next(
                i for i, item in enumerate(st.session_state.stocks)
                if item["Stock"] == selected
            )
            st.session_state.stocks.pop(index)
            st.success("Stock removed successfully!")
            st.rerun()

st.divider()
st.caption("Developed using Python | Streamlit | Pandas | Plotly")
