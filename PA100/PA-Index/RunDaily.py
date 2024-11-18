import pandas as pd
import paramiko
import zipfile
import os
from datetime import datetime, timedelta
import pickle
import numpy as np
import warnings
import streamlit as st

def _daily():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the 'data' directory relative to the script's location
    data_dir = os.path.join(script_dir, '..', 'data')

    def download_most_recent_zip(hostname, port, username, password, remote_folder, local_folder):
        # Create an SSH client
        ssh = paramiko.SSHClient()

        try:
            # Automatically add the server's host key
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the SSH server
            ssh.connect(hostname, port, username, password)

            # Open an SFTP session
            with ssh.open_sftp() as sftp:
                # Change to the remote folder
                sftp.chdir(remote_folder)

                # List files in the remote folder
                files = sftp.listdir()

                # Find the most recent ZIP file with "UnderlyingEOD" in the name
                most_recent_zip = None
                most_recent_date = datetime(1970, 1, 1)  # Initialize with a very old date

                for file in files:
                    if file.startswith("UnderlyingEOD") and not "Summaries" in file:
                        try:
                            file_date = datetime.strptime(file.split("_")[-1].split(".")[0], "%Y-%m-%d")
                            if file_date > most_recent_date:
                                most_recent_date = file_date
                                most_recent_zip = file
                        except ValueError:
                            pass  # Ignore files with date parsing issues

                if most_recent_zip:
                    # Replace backslashes with forward slashes in file paths
                    remote_path = os.path.join(remote_folder, most_recent_zip).replace("\\", "/")
                    local_path = os.path.join(local_folder, most_recent_zip).replace("\\", "/")

                    # Download the most recent ZIP file
                    sftp.get(remote_path, local_path)

                    # Extract files from the downloaded ZIP file
                    extract_zip(local_path, local_folder)

                    # Clean up: Remove downloaded ZIP file
                    os.remove(local_path)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Close the SSH connection
            ssh.close()

    def extract_zip(zip_filename, extraction_folder):
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            # Extract all files in the ZIP archive to the extraction folder
            zip_ref.extractall(extraction_folder)

    # SFTP server details
    sftp_hostname = "sftp.datashop.livevol.com"
    sftp_port = 22  # Change the port if your SFTP server uses a different port
    sftp_username = "nan2_lehigh_edu"
    sftp_password = "PAIndex2023!"
    sftp_remote_folder = "/subscriptions/order_000046197/item_000053507"  # Change to the actual path on the SFTP server
    local_download_folder = data_dir
    # local_download_folder = "/srv/paindex-test/data/"  # Set to "input" folder inside the current directory

    # Create the local download folder if it doesn't exist
    # os.makedirs(local_download_folder, exist_ok=True)

    # Download and extract the most recent ZIP file
    download_most_recent_zip(sftp_hostname, sftp_port, sftp_username, sftp_password, sftp_remote_folder, local_download_folder)

    # Define the file path where date_dataframes.pkl is saved
    input_file_path = os.path.join(data_dir, 'date_dataframes.pkl')
    # input_file_path = "/srv/paindex-test/data/date_dataframes.pkl"

    # Load the date_dataframes dictionary from the pickled file
    with open(input_file_path, 'rb') as input_file:
        date_dataframes = pickle.load(input_file)
    local_download_folder = data_dir
    # local_download_folder = "/srv/paindex-test/data/"  # Set to "input" folder inside the current directory

    # List all CSV files in the "input" folder
    csv_files = [file for file in os.listdir(local_download_folder) if file.startswith("UnderlyingEOD_") and file.endswith(".csv")]

    # Sort the CSV files by date, assuming the date is in the format "UnderlyingEOD_YYYY-MM-DD.csv"
    sorted_csv_files = sorted(csv_files, key=lambda x: datetime.strptime(x.split("_")[-1].split(".")[0], "%Y-%m-%d"), reverse=True)

    # Use the most recent CSV file
    if sorted_csv_files:
        most_recent_csv = sorted_csv_files[0]
        csv_file_path = os.path.join(local_download_folder, most_recent_csv)

        # Extract date from the filename
        date_format = most_recent_csv.split("_")[-1].split(".")[0]

        # Read the CSV file into a DataFrame
        eod_df = pd.read_csv(csv_file_path)

        # Store the DataFrame in the dictionary with the date as the key
        date_dataframes[date_format] = eod_df

        # After using the CSV file, optionally delete it
        try:
            os.remove(csv_file_path)
            print(f"Deleted: {csv_file_path}")
        except FileNotFoundError:
            print(f"File not found: {csv_file_path}")
        except Exception as e:
            print(f"Error deleting file: {e}")
    else:
        print("No CSV files found in the 'input' folder.")


    excel_file_path = os.path.join(data_dir, 'RAY as of Oct 23 20231_PA.xlsx')
    df = pd.read_excel(excel_file_path)
    #df = pd.read_excel("/srv/paindex-test/data/RAY as of Oct 23 20231_PA.xlsx")
    df.columns = df.columns.str.rstrip('\n')
    df['Ticker'] = df['Ticker'].str.split(' ', n=1, expand=True)[0]
    df['Ticker'] = df['Ticker'].str.replace(' ', '')  # Remove spaces
    # Create float_df by selecting the first 100 rows of "Ticker" and "Equity Float" columns
    float_df = df[['Ticker', 'Equity Float']].head(100)
    float_df
    # Create an empty DataFrame to store market cap DataFrames for each date
    eod_market_cap_pivot = pd.DataFrame()

    # Extract unique dates from date_dataframes dictionary
    unique_dates = list(date_dataframes.keys())

    # Iterate over unique dates
    for date_format in unique_dates[:]:
        # Access the corresponding DataFrame from date_dataframes
        eod_df = date_dataframes[date_format]

        # Merge dataframes on the common column 'Ticker' and 'underlying_symbol'
        merged_df = pd.merge(float_df, eod_df, left_on='Ticker', right_on='underlying_symbol')

        # Perform the multiplication and rename the column to 'Market Cap'
        merged_df['Market Cap'] = merged_df['Equity Float'] * merged_df['close']

        # Use pivot_table to create a multi-level DataFrame
        eod_market_cap_daily = merged_df.pivot_table(index='quote_date', columns='Ticker', values='Market Cap', aggfunc='sum')

        # Add a new column for the sum of market caps for each date
        #eod_market_cap_daily['close index market cap'] = eod_market_cap_daily.sum(axis=1)

        # Append the daily market cap DataFrame to the main DataFrame
        eod_market_cap_pivot = pd.concat([eod_market_cap_pivot, eod_market_cap_daily])

    # Rename the index to 'Date'
    eod_market_cap_pivot = eod_market_cap_pivot.rename_axis(index='Date')

    # Display the resulting pivot table
    eod_market_cap_pivot.index = pd.to_datetime(eod_market_cap_pivot.index, errors='coerce')
    #eod_market_cap_pivot.index.name = None  # Remove the index name

    # Display the resulting pivot table
    eod_market_cap_pivot


    # Ensure the index is in DateTime format
    eod_market_cap_pivot.index = pd.to_datetime(eod_market_cap_pivot.index)
    # Assuming eod_market_cap_pivot is your DataFrame and float_df["Ticker"] is the DataFrame with Ticker information

    # Step 1: Calculate the close market cap
    eod_market_cap_pivot["close_market_cap"] = eod_market_cap_pivot.sum(axis=1)

    # Step 2: Calculate the gross change mkt cap
    eod_market_cap_pivot["gross_change_mkt_cap"] = eod_market_cap_pivot["close_market_cap"].diff().fillna(0)

    # Step 3: Calculate the mkt_cap_deleted_stock

    # Precompute the most recent non-zero market cap for each ticker up to each date
    last_non_zero_caps = eod_market_cap_pivot.where(eod_market_cap_pivot != 0).ffill()

    mkt_cap_deleted_stock = {}
    for date in eod_market_cap_pivot.index:
        for ticker in float_df["Ticker"]:
            if pd.isna(eod_market_cap_pivot.at[date, ticker]) or eod_market_cap_pivot.at[date, ticker] == 0:
                if ticker not in mkt_cap_deleted_stock:
                    # Get the precomputed most recent non-zero market cap for the Ticker
                    mkt_cap_deleted_stock[ticker] = last_non_zero_caps.at[date, ticker]

    # Convert the dictionary to a Series
    mkt_cap_deleted_stock_series = pd.Series(mkt_cap_deleted_stock, name="mkt_cap_deleted_stock")

    # Map the Series to the DataFrame
    eod_market_cap_pivot["mkt_cap_deleted_stock"] = eod_market_cap_pivot.index.map(mkt_cap_deleted_stock_series)

    # Set mkt_cap_deleted_stock to 0 if it is NaN
    eod_market_cap_pivot["mkt_cap_deleted_stock"] = eod_market_cap_pivot["mkt_cap_deleted_stock"].fillna(0)

#    for date in eod_market_cap_pivot.index:
#        for ticker in float_df["Ticker"]:
#            if pd.isna(eod_market_cap_pivot.at[date, ticker]) or eod_market_cap_pivot.at[date, ticker] == 0:
#                if ticker not in mkt_cap_deleted_stock:
#                    # Get the most recent non-zero market cap for the Ticker
#                    non_zero_caps = eod_market_cap_pivot.loc[:date, ticker].replace({0: pd.NA}).dropna()
#                    if not non_zero_caps.empty:
#                        mkt_cap_deleted_stock[ticker] = non_zero_caps.iloc[-1]
#                    else:
#                        mkt_cap_deleted_stock[ticker] = 0

    # Set mkt_cap_deleted_stock to 0 if it is NaN
#    eod_market_cap_pivot["mkt_cap_deleted_stock"] = 0#-pd.Series(mkt_cap_deleted_stock, dtype=float)

    # Fill NaNs in mkt_cap_deleted_stock with 0
#    eod_market_cap_pivot["mkt_cap_deleted_stock"] = eod_market_cap_pivot["mkt_cap_deleted_stock"].fillna(0)
    # Step 4: Calculate adj_mkt_cap
    #eod_market_cap_pivot["mkt_cap_deleted_stock"][4] = -50000000000
    #eod_market_cap_pivot["mkt_cap_deleted_stock"][4] = 5000000000
    eod_market_cap_pivot["adj_mkt_cap"] = eod_market_cap_pivot["close_market_cap"] + eod_market_cap_pivot["mkt_cap_deleted_stock"]

    # Step 5: Create gross_index_level column and set the first row value to be 100
    eod_market_cap_pivot["close_divisor"] = 0
    eod_market_cap_pivot["adj_divisor"] = 0
    eod_market_cap_pivot["gross_index_level"] = 0
    eod_market_cap_pivot["Index Value"] = 0
    # Temporarily filter out FutureWarnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        eod_market_cap_pivot.at[eod_market_cap_pivot.index[0], "gross_index_level"] = 100
        eod_market_cap_pivot.at[eod_market_cap_pivot.index[0], "Index Value"] = 100
        eod_market_cap_pivot.at[eod_market_cap_pivot.index[0], "close_divisor"] = float(eod_market_cap_pivot["close_market_cap"][0]) / float(eod_market_cap_pivot["gross_index_level"][0])
        eod_market_cap_pivot.at[eod_market_cap_pivot.index[0], "adj_divisor"] = float(eod_market_cap_pivot["close_divisor"][0]) * float(eod_market_cap_pivot["close_market_cap"][0]) / float(eod_market_cap_pivot["adj_mkt_cap"][0])

    # Iterate through rows starting from the second row
    for i in range(1, len(eod_market_cap_pivot)):
            # Temporarily filter out FutureWarnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            # Calculate close_divisor based on the previous day's adj_divisor
            eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "close_divisor"] = float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i-1], "adj_divisor"])

            # Calculate gross_index_level
            eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "gross_index_level"] = float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "close_market_cap"]) / float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "close_divisor"])

            # Calculate adj_divisor
            eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "adj_divisor"] = float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "adj_mkt_cap"]) / float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "close_market_cap"]) * float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "close_divisor"])

            # Calculate Index Value
            eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "Index Value"] = float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "adj_mkt_cap"]) / float(eod_market_cap_pivot.at[eod_market_cap_pivot.index[i], "adj_divisor"])

    eod_market_cap_pivot

    # output_file_path = "/srv/paindex-test/data/date_dataframes.pkl"
    output_file_path = os.path.join(data_dir, 'date_dataframes.pkl')
    with open(output_file_path, 'wb') as output_file:
        pickle.dump(date_dataframes, output_file)

    print(f"Saved date_dataframes to: {output_file_path}")

    # Extract the "Date" and "Index Value" columns
    index_df = eod_market_cap_pivot[["Index Value"]].copy()

    # Save the DataFrame to a CSV file
    csv_output_path = os.path.join(data_dir, 'input.csv')
    # index_df.to_csv("/srv/paindex-test/data/input.csv")
    index_df.to_csv(csv_output_path)
    st.write(index_df)

def main():
    st.title("Daily Market Cap Analysis")
    if st.button("Run Analysis"):
        result = index_df
        st.write(result)

if __name__ == "__main__":
    main()
