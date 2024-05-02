import pandas as pd

def save_high_ratings(file_name="contest_details(staters 132).xlsx", new_sheet_name="2 star and above", min_rating=1400):
    # Read the existing Excel file
    df = pd.read_excel(file_name, sheet_name="Latest Ratings")
    # Colors to stars dict
    colors_to_stars = {"#FFBF00": 5, "#684273": 4, "#3366CC": 3, "#1E7D22": 2}
    
    # Filter users with ratings higher than the minimum rating
    high_ratings_df = df[df['rating'] > min_rating].copy()

    # Add a column for stars based on the color of the user
    high_ratings_df['stars'] = high_ratings_df['color'].map(colors_to_stars)
    
    # Drop the 'colors' column
    high_ratings_df.drop(columns=['color'], inplace=True)
    
    # Move the 'stars' column to the desired position (column 7)
    cols = high_ratings_df.columns.tolist()
    cols.insert(6, cols.pop(cols.index('stars')))
    high_ratings_df = high_ratings_df[cols]
    
    # Use ExcelWriter to write this DataFrame to a new sheet in the same Excel file
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # Check if the 'High Ratings' sheet already exists, and if so, remove it
        if new_sheet_name in writer.book.sheetnames:
            del writer.book[new_sheet_name]
        
        high_ratings_df_sorted = high_ratings_df.sort_values(by="rating", ascending=True)
        # Save the high ratings DataFrame to a new sheet named 'High Ratings'
        high_ratings_df_sorted.to_excel(writer, sheet_name=new_sheet_name, index=False)
        print(f"High ratings (more than {min_rating}) saved to sheet: '{new_sheet_name}' in the file '{file_name}'.")

# Example usage
if __name__ == "__main__":
    save_high_ratings()
