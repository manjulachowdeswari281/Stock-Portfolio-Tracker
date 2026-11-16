
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Stock Portfolio Tracker",
    page_icon="📈",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
[data-testid="stMetric"] {
    background-color: #1c2431;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #303b4d;
}
div.stButton > button {
    background-color: #16a085;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# App title
st.title("📈 Stock Portfolio Tracker")
st.caption("Track your investments | Monitor performance | Manage your portfolio")

# Sample portfolio
if "portfolio" not in st.session_state:
    st.session_state.portfolio = [
        {"Stock": "RELIANCE.NS", "Company": "Reliance Industries",
         "Quantity": 5, "Buy Price": 1200.0},
        {"Stock": "TCS.NS", "Company": "TCS",
         "Quantity": 3, "Buy Price": 3500.0},
        {"Stock": "INFY.NS", "Company": "Infosys",
         "Quantity": 4, "Buy Price": 1500.0},
        {"Stock": "HDFCBANK.NS", "Company": "HDFC Bank",
         "Quantity": 6, "Buy Price": 1600.0}
    ]

# Fetch stock price
def get_stock_price(symbol, buy_price):
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period="5d")
        if not history.empty:
            return float(history["Close"].dropna().iloc[-1])
    except Exception:
        pass
    return float(buy_price)

# Build portfolio dataframe
def get_portfolio_data():
    records = []

    for item in st.session_state.portfolio:
        current_price = get_stock_price(
            item["Stock"], item["Buy Price"]
        )

        investment = item["Quantity"] * item["Buy Price"]
        current_value = item["Quantity"] * current_price
        profit_loss = current_value - investment

        records.append({
            "Stock": item["Stock"],
            "Company": item["Company"],
            "Quantity": item["Quantity"],
            "Buy Price": item["Buy Price"],
            "Current Price": round(current_price, 2),
            "Investment": round(investment, 2),
            "Current Value": round(current_value, 2),
            "Profit / Loss": round(profit_loss, 2)
        })

    return pd.DataFrame(records)

# Sidebar
st.sidebar.title("⚙️ Portfolio Menu")
menu = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Add Stock", "Portfolio", "Stock Analysis"]
)

# Get data
df = get_portfolio_data()

# Dashboard
if menu == "Dashboard":

    st.subheader("Portfolio Overview")

    total_investment = df["Investment"].sum()
    total_value = df["Current Value"].sum()
    total_profit = total_value - total_investment

    profit_percentage = (
        (total_profit / total_investment) * 100
        if total_investment else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Investment",
        f"₹{total_investment:,.2f}"
    )

    col2.metric(
        "Current Value",
        f"₹{total_value:,.2f}"
    )

    col3.metric(
        "Total Profit / Loss",
        f"₹{total_profit:,.2f}",
        f"{profit_percentage:.2f}%"
    )

    col4.metric(
        "Total Stocks",
        len(df)
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Portfolio Allocation")

        if not df.empty:
            fig = px.pie(
                df,
                values="Current Value",
                names="Company",
                hole=0.55,
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="#0e1117",
                font_color="white"
            )
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Investment Performance")

        if not df.empty:
            chart_data = df[
                ["Company", "Investment", "Current Value"]
            ].melt(
                id_vars="Company",
                var_name="Type",
                value_name="Amount"
            )

            fig = px.bar(
                chart_data,
                x="Company",
                y="Amount",
                color="Type",
                barmode="group",
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="#0e1117",
                font_color="white"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("My Stock Holdings")
    st.dataframe(df, use_container_width=True, hide_index=True)

# Add stock
elif menu == "Add Stock":

    st.subheader("➕ Add New Stock")

    with st.form("add_stock_form"):

        company = st.text_input("Company Name")
        symbol = st.text_input(
            "Stock Symbol",
            placeholder="Example: WIPRO.NS"
        ).upper()

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1
        )

        buy_price = st.number_input(
            "Purchase Price (₹)",
            min_value=0.01,
            step=10.0
        )

        submitted = st.form_submit_button("Add to Portfolio")

        if submitted:
            if company.strip() and symbol.strip():
                st.session_state.portfolio.append({
                    "Stock": symbol,
                    "Company": company,
                    "Quantity": int(quantity),
                    "Buy Price": float(buy_price)
                })
                st.success("Stock added successfully!")
                st.rerun()
            else:
                st.error("Please enter company name and stock symbol.")

# Portfolio
elif menu == "Portfolio":

    st.subheader("📊 My Portfolio")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Remove a Stock")

    if not df.empty:
        selected_stock = st.selectbox(
            "Select stock to remove",
            df["Stock"].tolist()
        )

        if st.button("Delete Selected Stock"):
            st.session_state.portfolio = [
                item for item in st.session_state.portfolio
                if item["Stock"] != selected_stock
            ]
            st.success("Stock removed successfully!")
            st.rerun()

    # Download portfolio
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Portfolio CSV",
        data=csv,
        file_name="my_stock_portfolio.csv",
        mime="text/csv"
    )

# Stock analysis
elif menu == "Stock Analysis":

    st.subheader("📉 Stock Price Analysis")

    if not df.empty:
        selected = st.selectbox(
            "Choose a company",
            df["Company"].tolist()
        )

        selected_row = df[df["Company"] == selected].iloc[0]
        symbol = selected_row["Stock"]

        try:
            history = yf.Ticker(symbol).history(period="1mo")

            if not history.empty:
                fig = px.line(
                    history,
                    x=history.index,
                    y="Close",
                    title=f"{selected} - Last 1 Month",
                    template="plotly_dark"
                )

                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    paper_bgcolor="#0e1117",
                    font_color="white"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
            else:
                st.warning("Price history is currently unavailable.")

        except Exception:
            st.warning("Unable to fetch stock history. Please try again.")

        st.write("Company:", selected)
        st.write("Stock Symbol:", symbol)
        st.write("Current Price:", f"₹{selected_row['Current Price']:,.2f}")
        st.write("Quantity:", int(selected_row["Quantity"]))
    else:
        st.info("Add stocks to see analysis.")

# Footer
st.divider()
st.caption(
    "Stock Portfolio Tracker | Built with Python, Streamlit and Yahoo Finance"
)
st.caption(
    "Educational demo only. Stock prices depend on Yahoo Finance data availability."
)
