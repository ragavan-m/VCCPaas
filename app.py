import streamlit as st
from pytrends.request import TrendReq
import matplotlib.pyplot as plt

def plot_trend_over_time(interest_over_time_df, trend_name):
    """Generates a plot for trend interest over time."""
    plt.figure(figsize=(10, 6))
    plt.plot(interest_over_time_df.index, interest_over_time_df[trend_name], marker='o', linestyle='-', color='skyblue')
    plt.fill_between(interest_over_time_df.index, interest_over_time_df[trend_name], color='skyblue', alpha=0.3)
    plt.title(f'Interest Over Time: {trend_name}')
    plt.xlabel('Time')
    plt.ylabel('Interest')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

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

trends_data = []

# Fetch interest over time for the top trends
for trend in top_trends:
    pytrends.build_payload([trend], timeframe='now 1-d')
    interest_over_time_df = pytrends.interest_over_time()

    if not interest_over_time_df.empty:
        # Plot trend over time
        plt = plot_trend_over_time(interest_over_time_df, trend)

        # Gather data for display
        trends_data.append({
            'name': trend,
            'search_volume': interest_over_time_df[trend].max(),
            'started': interest_over_time_df.index[0].strftime('%Y-%m-%d %H:%M:%S'),
            'breakdown': interest_over_time_df[trend].tolist(),
            'plot': plt
        })

# Display trend data
for data in trends_data:
    st.subheader(data['name'])
    st.write(f"Search Volume: {data['search_volume']}")
    st.write(f"Started At: {data['started']}")
    
    # Display the plot for each trend
    st.pyplot(data['plot'])

    # Breakdown of interest over time
    st.write("Interest Breakdown:")
    st.line_chart(data['breakdown'])
