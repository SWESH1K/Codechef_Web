import requests
import json
import re
import os
import pandas as pd  # Import pandas for data manipulation
import csv
from latest_data_extractor import save_latest_ratings
from two_three_stars import save_high_ratings
global successfull,unsuccessfull
successfull=0
unsuccessfull=0

def print_details(ratings):
    if(len(ratings))==0: return
    for rating in ratings:
        print("Contest:", rating["code"])
        print("Rating:", rating["rating"])
        print("Rank:", rating["rank"])
        print("Date:", rating["end_date"])
        if rating["penalised_in"] is not None:
            print("Penalised in:", rating["penalised_in"])
            print("Reason:", rating["reason"])
        print("-"*30)  # Empty line for readability

class Codechef:
    def __init__(self, codechef_id: str, roll_no: str):
        self.codechef_id = codechef_id
        self.roll_no = roll_no
        self.url = f"https://www.codechef.com/users/{self.codechef_id}"  # Getting user's profile
        self.result = requests.get(self.url)  # Getting code from the url

        self.script_text = self.result.text
        # Use regular expression to find the JavaScript array containing ratings
        match = re.search(r"var all_rating = (\[.*?\]);", self.script_text, re.DOTALL)
        if match:
            # Extract the ratings data as a JSON array
            ratings_json = match.group(1)
            # Convert the JSON array to a Python list
            self.ratings = json.loads(ratings_json)
            global successfull
            successfull+=1
        else:
            print(f"User named {self.codechef_id} not found!!", end=" ")
            global unsuccessfull
            unsuccessfull+=1
            self.ratings = {}

    def print_all_ratings(self):
        print("-"*15, "All Contests", "-"*15)
        print("Number of Contests participated: ", len(self.ratings), "\n\n")
        print_details(self.ratings)

    def all_plagarized(self):
        print("-"*15, "Plagarised Contests", "-"*15)
        plagarised_list = [rating for rating in self.ratings if rating['penalised_in'] is not None]
        print("Number of Plagiarisms: ", len(plagarised_list), "\n\n")
        print_details(plagarised_list)

    def highest_rating(self):
        return print("Highest rating: ", max([int(rating["rating"]) for rating in self.ratings]))

    def save_to_excel(self, filename="contest_details(staters 132).xlsx"):
        if len(self.ratings) == 0:
            return

        # Extract only the required columns from the ratings
        selected_columns = ['code', 'rating', 'rank', 'name', 'color', 'penalised_in', 'reason']
        selected_data = [{key: rating[key] for key in selected_columns} for rating in self.ratings]

        # Convert selected data to a DataFrame
        new_data = pd.DataFrame(selected_data)

        # Add the 'user_id' column to the DataFrame and set its value to the user's CodeChef ID for all rows
        new_data.insert(0, 'roll_no', self.roll_no)
        new_data.insert(1, 'user_id', self.codechef_id)

        # Define a unique identifier for each row, assuming 'code' and 'user_id' can uniquely identify entries
        unique_columns = ['user_id', 'code']

        if os.path.exists(filename):
            # File exists, so read the existing data
            try:
                existing_data = pd.read_excel(filename)

                # Attempt to identify and exclude rows in new_data that already exist in existing_data
                # Create a boolean series that is True for rows in new_data that are already present in existing_data
                duplicates = new_data.apply(lambda row:
                                            (existing_data[unique_columns] == row[unique_columns]).all(axis=1).any(),
                                            axis=1)

                # Filter new_data to exclude these duplicates
                new_data_unique = new_data[~duplicates]

                # Append the new, unique data to the existing data
                combined_data = pd.concat([existing_data, new_data_unique], ignore_index=True)
            except Exception as e:
                print(f"Error reading the Excel file: {e}")
                # If there's an error reading, use new data only
                combined_data = new_data
        else:
            # File does not exist, use new data as the combined data
            combined_data = new_data

        # Save the combined DataFrame to an Excel file, overwriting the existing file
        try:
            combined_data.to_excel(filename, index=False)
            print(f"{self.codechef_id}, Contest details saved to {filename}", end=" ")
        except Exception as e:
            print(f"Failed to save Excel file: {e}")


def load_csv():
    # Open the CSV file for reading
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        
        # Skip the header if your CSV has one
        next(csvreader, None)  # Remove this line if your CSV doesn't have a header
        
        # Iterate through each row in the CSV
        for row in csvreader:
            # Check if the row has at least 2 columns
            if len(row) >= 2:
                # Append the element from the second column to the list
                if len(row[5])>0:
                    second_column_data[row[5]] = row[0]
        global total
        total = len(second_column_data)           
    for user, roll in second_column_data.items():
        cc = Codechef(user,roll)
        cc.save_to_excel()
        global counts
        counts+=1
        print(f"--> {counts} out of {total} done! --> {round(counts/total*100, 2)}%")



def main():
    import time
    start = time.time()

    global csv_file_path,second_column_data,counts,total

    # # Path to your CSV file
    csv_file_path = 'ranking.csv'

    # List to store the elements of the second column
    second_column_data = {}
    
    counts=0
    load_csv()
    save_latest_ratings() # Add an extra sheet that contains the latest rating of each student.
    save_high_ratings()
    end = time.time()
    print("Total username:",total)
    print("Correct users:",successfull)
    print("Wrong usernames:", unsuccessfull)
    print("Time taken:",round((end-start)/60,2),"minutes.")


if __name__ == '__main__':
    main()