import streamlit as st
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()


# Streamlit app title
st.title("Stock Price Trend and Volume Viewer")

# Alpaca API credentials
# Access API credentials from environment variables
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# Debugging: Check if API_KEY and API_SECRET are loaded
print(f"API_KEY: {API_KEY}")
print(f"API_SECRET: {API_SECRET}")

# Initialize the Alpaca SDK Historical Data Client
client = StockHistoricalDataClient(API_KEY, API_SECRET)

# User input for stock symbol
symbol = st.text_input("Enter the stock symbol:", "AAPL").upper()

# User selection for date range
range_options = ['1M', '3M', '6M', 'YTD', '1Y']
selected_range = st.selectbox("Select the time range for the trendline:", range_options)

# Determine the start date based on the selected range
end_date = datetime.now()
if selected_range == '1M':
    start_date = end_date - timedelta(days=30)
elif selected_range == '3M':
    start_date = end_date - timedelta(days=90)
elif selected_range == '6M':
    start_date = end_date - timedelta(days=180)
elif selected_range == 'YTD':
    start_date = datetime(end_date.year, 1, 1)
elif selected_range == '1Y':
    start_date = end_date - timedelta(days=365)

# Format dates as strings in the required format
start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

try:
    # Create a StockBarsRequest to fetch historical data
    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Day,
        start=start_date_str
        # end=end_date_str
    )

    # Fetch historical data
    bars = client.get_stock_bars(request_params)
    bars_df = bars.df
    st.write(bars_df)

    # Ensure the index is a DateTime type
    if isinstance(bars_df.index, pd.MultiIndex):
        # If the index is a MultiIndex (tuple), reset the index to make it a regular DataFrame
        bars_df = bars_df.reset_index()
        bars_df['timestamp'] = pd.to_datetime(bars_df['timestamp'])  # Convert timestamp to datetime
        bars_df.set_index('timestamp', inplace=True)  # Set it as the index

    # Check if the dataframe is empty
    if bars_df.empty:
        st.warning(f"No historical data available for {symbol} in the selected date range.")
    else:
        # Plot the closing prices with Streamlit's line_chart
        st.subheader(f"{symbol} Price Trend ({selected_range})")
        st.line_chart(bars_df[['close']])

        # Display volume data with Streamlit's bar_chart
        st.subheader(f"{symbol} Volume Data ({selected_range})")
        st.bar_chart(bars_df['volume'])

except Exception as e:
    st.error(f"An error occurred: {e}")