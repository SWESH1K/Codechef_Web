import pandas as pd

def save_latest_ratings(file_name="contest_details.xlsx", new_sheet_name="Latest Ratings"):
    # Read the existing Excel file
    df = pd.read_excel(file_name)
    
    df_sorted = df.sort_values(by='code', ascending=True)
    
    # Drop duplicates, keeping the last occurrence, which is the latest rating per user
    latest_ratings_df = df_sorted.drop_duplicates(subset=['user_id'], keep='last')
    
    # Use ExcelWriter to write this DataFrame to a new sheet in the same Excel file
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # Check if the 'Latest Ratings' sheet already exists, and if so, remove it
        if new_sheet_name in writer.book.sheetnames:
            del writer.book[new_sheet_name]
        
        latest_ratings_df_sorted = latest_ratings_df.sort_values(by="roll_no", ascending=True)
        # Save the latest ratings DataFrame to a new sheet named 'Latest Ratings'
        latest_ratings_df_sorted.to_excel(writer, sheet_name=new_sheet_name, index=False)
        print(f"Latest ratings saved to sheet: '{new_sheet_name}' in the file '{file_name}'.")

# Example usage
if __name__ == "__main__":
    save_latest_ratings()
