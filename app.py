import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import numpy as np

def latest_analysis(user_id, additional_info):
    # Load the specific sheet from the Excel file
    latest_df = pd.read_excel("contest_details(new format).xlsx", sheet_name="Latest Ratings")

    colors_to_stars = {"#3366CC": "3⭐", "#1E7D22": "2⭐", "#666666": "1⭐"}
    
    # Find the row(s) where the user_id matches the given user_id
    matches = latest_df['user_id'] == user_id
    
    # Use np.where to find the indices of the matching row(s)
    matching_indices = np.where(matches)[0]
    
    # Check if we found any matches
    if len(matching_indices) > 0:
        index = matching_indices[0]
        user_row = latest_df.iloc[index]
        
        # Use columns to evenly distribute the content
        col1, col2, col3, col4 = st.columns(4)
        
        # Displaying rank and user details in the first column
        with col1:
            st.subheader(f"🏆 College Rank: {index+1}")
            st.metric(label="Roll Number", value=user_row['roll_no'])
            st.metric(label="User ID", value=user_id)
            st.metric(label="Last Contest Participated", value=user_row['name'])

        # Displaying rating and code details in the second column
        with col2:
            st.subheader("Contest Details")
            rating = user_row['rating']
            code = user_row['code']
            st.metric(label="Latest Rating", value=rating)
            st.metric(label="Average Rating", value=additional_info['Average Rating'])
            st.metric(label="Average Increment in Rating", value=additional_info['Average Increase in Rating'])

        # Displaying rank in the latest contest and division in the third column
        with col3:
            st.subheader("Performance")
            rank = user_row['rank']
            division_color = user_row.get('color', '#FFFFFF')  # Default to white if no color specified
            division_star = colors_to_stars.get(division_color, "")  # Convert division color to star rating
            st.metric(label="Stars", value=division_star)
            st.metric(label="Rank in Latest Contest", value=rank)
            st.metric(label="Average Rank", value=additional_info['Average Rank'])

        # Displaying Additional Info
        with col4:
            st.subheader("Additional Info")
            st.metric(label="Highest Rating", value=additional_info['Highest rating'])
            st.metric(label="Contests Participated", value=additional_info['Contests Participated'])
            st.metric(label="Num of Plagarisms", value=additional_info['Plagarisms'])
    else:
        st.error(f"User ID {user_id} not found in the 'Latest Ratings' sheet.")


def Analysis(user_id=None, roll_no=None):
    if user_id!=None:
        if user_id not in list(df.user_id):
            st.error("User id not found!")
            return
        user_data = df[df.user_id == user_id]
    else:
        if int(roll_no) not in list(df.roll_no):
            st.error("Roll No not found!")
            return
        user_data = df[df.roll_no == int(roll_no)]
        user_id = min(user_data.user_id)
    print(user_data)
    # Calculate average rating for each code in the entire DataFrame df
    code_unique = user_data['code'].unique()
    average_ratings = {code: df[df['code'] == code]['rating'].mean() for code in code_unique}

    ## Line Chart
    # Preparing the plot
    fig1 = go.Figure()

    # Add trace for user_data ratings
    fig1.add_trace(go.Scatter(x=user_data['code'], y=user_data['rating'], mode='lines', name=f'{user_name} Rating'))

    # Add trace for average ratings
    avg_rating_data = pd.DataFrame({'code': list(average_ratings.keys()), 'average_rating': list(average_ratings.values())})
    fig1.add_trace(go.Scatter(x=avg_rating_data['code'], y=avg_rating_data['average_rating'], mode='lines', name='Average Rating', line=dict(color='firebrick', width=2)))

    # Highlight area above 1400
    fig1.add_hrect(y0=min(min(user_data.rating), min(average_ratings.values())), y1=1399, line_width=0, fillcolor="gray", opacity=0.2)
    fig1.add_hrect(y0=1400, y1=1600, line_width=0, fillcolor="green", opacity=0.2)
    fig1.add_hrect(y0=1600, y1=1800, line_width=0, fillcolor="blue", opacity=0.2)

    fig1.update_layout(title='Rating Analysis', xaxis_title='Code', yaxis_title='Rating', height = 1000)

    ## Pie Chart
    colors_list = {}
    for color in set(user_data.color):
        colors_list[colors_dict[color]] = list(user_data.color).count(color)

    # Make sure the order of colors matches the labels order
    # The colors are mapped based on the division names derived from 'colors_list'
    pie_colors = ["#272727", "#FF652F","#747474", "#FFE400", "#14A76C"]

    fig2 = go.Figure(data=[go.Pie(labels=list(colors_list.keys()), values=list(colors_list.values()), marker_colors = pie_colors)])
    fig2.update_layout(title="Division Analysis")

    # Bar graph
    # Calculate average rank for each code in the entire DataFrame df
    average_ranks = df.groupby('code')['rank'].mean().reset_index()

    # Create the bar chart
    fig3 = go.Figure()

    # Add trace for user's rank
    fig3.add_trace(go.Bar(x=user_data['code'], y=user_data['rank'], name='User Rank', marker_color="#FF652F"))

    # Add trace for average rank
    fig3.add_trace(go.Bar(x=user_data['code'], y=average_ranks['rank'], name='Average Rank', marker_color = "light blue"))

    fig3.update_layout(title='Rank Analysis', xaxis_title='Code', yaxis_title='Rank')

    # Post-contest-Increments
    ratings_list = list(user_data.rating)
    contest_inc = [ratings_list[0]-1000]
    for i in range(1,len(ratings_list)):
        contest_inc.append(ratings_list[i]-ratings_list[i-1])
    print(ratings_list)
    print(contest_inc)

    additional_info = {
        "Highest rating": max(user_data.rating),
        "Contests Participated": len(user_data.code),
        "Plagarisms":len(user_data[user_data['reason'].notna()]),
        "Average Increase in Rating":int(sum(contest_inc)/len(contest_inc)),
        "Average Rating":int(user_data.rating.mean()),
        "Average Rank":int(user_data["rank"].mean())
    }

    #Ploting Graphs and Tables
    latest_analysis(user_id, additional_info)
    st.dataframe(user_data, use_container_width=True, hide_index=True)
    st.plotly_chart(fig1, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig3)
    col2.plotly_chart(fig2)

if __name__ == "__main__":
    st.set_page_config(page_title="Codechef-Dashboard", layout="wide")
    col1, col2 = st.columns([2,9])
    col2.header("Student Dashboard")
    col2.subheader("Analyze yourself?")
    logo = Image.open("codechef_logo.png")
    col1.image(logo, width=230)
    colors_dict = {"#666666": "Division-4 (1Star)", "#1E7D22": "Division-3 (2Star)", "#3366CC": "Division-2 (3Star)"}
    df = pd.read_excel("contest_details(new format).xlsx")


    user_name = st.text_input(label="Codechef id or Roll No", placeholder="user_id", key= "Key")
    if user_name.isnumeric():
        Analysis(roll_no=user_name)
    elif user_name:
        Analysis(user_id=user_name)