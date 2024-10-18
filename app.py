import streamlit as st
from pytrends.request import TrendReq

# Set up Streamlit
st.title("Trending Searches")

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Get trending searches
trending_searches_df = pytrends.trending_searches(pn='india')

# Display the top trending searches
st.subheader("Top Trending Searches in India")
top_trends = trending_searches_df.head(5)[0].tolist()  # Fetch the top 5 trends
for index, trend in enumerate(top_trends):
    st.write(f"{index + 1}. {trend}")  # Display each trend in a numbered list

# Fetch interest over time for the top trends
for trend in top_trends:
    pytrends.build_payload([trend], timeframe='now 1-d')
    interest_over_time_df = pytrends.interest_over_time()

    if not interest_over_time_df.empty:
        # Display trend data
        st.subheader(trend)
        st.write(f"Search Volume: {interest_over_time_df[trend].max()}")
        st.write(f"Started At: {interest_over_time_df.index[0].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Breakdown of interest over time
        st.write("Interest Breakdown:")
        st.line_chart(interest_over_time_df[trend])

