import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import numpy as np
from trust_score import calculate_trust_score

class Contestant:
    def __init__(self, user_id=None, roll_no=None, df=None):
        self.user_id = user_id
        self.roll_no = roll_no
        self.df = df
        self.user_data = None
        self.additional_info = {}
        self.find_user_data()

    def find_user_data(self):
        if self.user_id is not None:
            self.user_data = self.df[self.df.user_id == self.user_id]
        elif self.roll_no is not None:
            self.user_data = self.df[self.df.roll_no == int(self.roll_no)]
            self.user_id = min(self.user_data.user_id) if not self.user_data.empty else None
        self.calculate_additional_info()

    def calculate_additional_info(self):
        if self.user_data is not None and not self.user_data.empty:
            ratings_list = list(self.user_data.rating)
            contest_inc = [ratings_list[0]-1000] + [ratings_list[i]-ratings_list[i-1] for i in range(1, len(ratings_list))]
            self.additional_info = {
                "Highest rating": max(self.user_data.rating),
                "Contests Participated": len(self.user_data.code),
                "Plagarisms": len(self.user_data[self.user_data['reason'].notna()]),
                "Average Increase in Rating": int(sum(contest_inc) / len(contest_inc)),
                "Average Rating": int(self.user_data.rating.mean()),
                "Average Rank": int(self.user_data["rank"].mean())
            }
            self.credentials = {
                "N": len(ratings_list), # Number of contests
                "P": len(self.user_data[self.user_data['reason'].notna()]), # Number of plagarisms
                "OA": int(sum(contest_inc) / len(contest_inc)), # Overall Average Increment
                "PA": sum(contest_inc[-5:])/5 if len(contest_inc) >= 5 else sum(contest_inc)/len(contest_inc), # Past 3 Average Increment
                "C": ratings_list[-1], # Current rating
                "A": int(self.user_data.rating.mean()), # Average rating
            }

class AnalysisTools:

    @staticmethod
    def generate_short_analysis(user_id, additional_info):
        # Load the specific sheet from the Excel file
        latest_df = pd.read_excel("contest_details.xlsx", sheet_name="Latest Ratings")
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
                st.metric(label="Current Rating", value=rating)
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

    @staticmethod
    def generate_line_chart(user_data, df):
        code_unique = user_data['code'].unique()
        average_ratings = {code: df[df['code'] == code]['rating'].mean() for code in code_unique}

        fig = go.Figure()

        # Normal user rating trace
        fig.add_trace(go.Scatter(x=user_data['code'], y=user_data['rating'], mode='lines+markers', name=f'{max(user_data.user_id)} Rating'))

        # Highlight penalized contests
        penalized_data = user_data[user_data['penalised_in'].notna()]
        # print(penalized_data)
        if not penalized_data.empty:
            fig.add_trace(go.Scatter(x=penalized_data['code'], y=penalized_data['rating'],
                                    mode='markers', name='Penalized',
                                    marker=dict(color='red', size=10, symbol='x-dot')))

        # Average rating trace
        avg_rating_data = pd.DataFrame({'code': list(average_ratings.keys()), 'average_rating': list(average_ratings.values())})
        fig.add_trace(go.Scatter(x=avg_rating_data['code'], y=avg_rating_data['average_rating'], mode='lines+markers', name='Average Rating', line=dict(color='firebrick', width=2)))

        # Background rating bands
        fig.add_hrect(y0=min(min(user_data['rating']), min(average_ratings.values())), y1=1399, line_width=0, fillcolor="gray", opacity=0.2)
        fig.add_hrect(y0=1400, y1=1600, line_width=0, fillcolor="green", opacity=0.2)
        fig.add_hrect(y0=1600, y1=1800, line_width=0, fillcolor="blue", opacity=0.2)

        # Chart layout settings
        fig.update_layout(title='Rating Analysis', xaxis_title='Code', yaxis_title='Rating', height=800)
        st.plotly_chart(fig, use_container_width=True)


    @staticmethod
    def generate_pie_chart(user_data):
        colors_dict = {"#666666": "Division-4 (1Star)", "#1E7D22": "Division-3 (2Star)", "#3366CC": "Division-2 (3Star)"}
        colors_list = {}
        for color in set(user_data.color):
            colors_list[colors_dict[color]] = list(user_data.color).count(color)
        labels = list(colors_list.keys())
        values = list(colors_list.values())

        pie_colors = ["#272727", "#FF652F", "#747474", "#FFE400", "#14A76C"]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=pie_colors)])
        fig.update_layout(title="Division Analysis")
        return fig

    @staticmethod
    def generate_bar_chart(user_data, df):
        average_ranks = df.groupby('code')['rank'].mean().reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=user_data['code'], y=user_data['rank'], name=f'{max(user_data.user_id)} Rank', marker_color="#FF652F"))
        fig.add_trace(go.Bar(x=user_data['code'], y=average_ranks['rank'], name='Average Rank', marker_color="lightblue"))

        fig.update_layout(title='Rank Analysis', xaxis_title='Code', yaxis_title='Rank')
        return fig
    
    @staticmethod
    def generate_trust_text(credentials):

        scores_dict = calculate_trust_score(credentials)
        total = scores_dict['total_score']

        # Define the color based on the score range
        if total >= 90:
            color = 'green'
        elif total >= 70:
            color = 'orange'
        else:
            color = 'red'
        
        # Generate the highlighted text
        trust_text = f"<p style='font-size: 28px; font-weight: bold; color: #1a1a1d; background-color: {color}; padding: 10px;'>Trust Score: {total}%</p>"
        st.markdown(trust_text,unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="Based on number of contests(20%):", value=f"{scores_dict['score1']}%")
        col2.metric(label="Based on number of plagarisms(50%):", value=f"{scores_dict['score2']}%")
        col3.metric(label="Based on sudden increase in average increment(15%):", value=f"{scores_dict['score3']}%")
        col4.metric(label="Based on difference between Current & Average rating(15%):", value=f"{scores_dict['score4']}%")
        st.subheader("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")


class Dashboard:
    def __init__(self, df):
        self.df = df
        self.colors_dict = {"#666666": "Division-4 (1Star)", "#1E7D22": "Division-3 (2Star)", "#3366CC": "Division-2 (3Star)"}

    def run(self):
        st.set_page_config(page_title="Codechef-Dashboard", layout="wide", page_icon="codechef_icon.png")
        col1, col2 = st.columns([2,9])
        col2.header("Student Dashboard")
        col2.subheader("Analyze yourself?")
        logo = Image.open("codechef_logo.png")
        col1.image(logo, width=230)
        
        user_input = st.text_input(label="Codechef id or Roll No", placeholder="user_id", key="Key")
        if user_input:
            self.display_user_analysis(user_input)

    def display_user_analysis(self, user_input):
        user_id = None
        roll_no = None
        
        if user_input.isnumeric():
            roll_no = user_input
        else:
            user_id = user_input

        contestant = Contestant(user_id=user_id, roll_no=roll_no, df=self.df)
        contestant.calculate_additional_info()
        if contestant.user_data is None or contestant.user_data.empty:
            st.error("User not found!")
            return
        
        # Display additional info, such as highest rating, average increase in rating, etc.
        AnalysisTools.generate_short_analysis(contestant.user_id, contestant.additional_info)
        AnalysisTools.generate_trust_text(contestant.credentials)
        # Display the user data.
        st.subheader("All contests details")
        st.dataframe(contestant.user_data, use_container_width=True, hide_index=True)
        # Generate and display charts
        AnalysisTools.generate_line_chart(contestant.user_data, self.df)
        pie_chart = AnalysisTools.generate_pie_chart(contestant.user_data)
        bar_chart = AnalysisTools.generate_bar_chart(contestant.user_data, self.df)
        col1,col2 = st.columns(2)
        col1.plotly_chart(bar_chart, use_container_width=True)
        col2.plotly_chart(pie_chart)
        

if __name__ == "__main__":
    df = pd.read_excel("contest_details.xlsx")
    dashboard = Dashboard(df)
    dashboard.run()
