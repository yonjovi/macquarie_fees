import csv
import pandas as pd
from PyPDF2 import PdfReader
import streamlit as st
import re
from io import BytesIO

app_header = st.header("Macquarie Fee Extractor")
app_info = st.info("Upload the Macquarie Reports to extract fees")
macquarie_reports = st.file_uploader("Please upload your Macquarie Report here...")

if macquarie_reports is not None:
    file_name = macquarie_reports.name

    reader = PdfReader(macquarie_reports)
    number_of_pages = len(reader.pages)
    pages = reader.pages

    # Create a list to store extracted data
    extracted_data = []

    for i in range(number_of_pages):
        page = pages[i]
        text = page.extract_text()

        # Use regex to find matches for various fee types followed by a number and a date (case-insensitive)
        matches = re.findall(
            r'(ADMIN FEE|Administration Fee|ADVISER FEE|Adviser Fee Tax Credit|Administration Fee Tax Credit)\s+([+-]?\d+\.\d+)\s+(\d{2}/\d{2}/\d{4})',
            text, re.IGNORECASE)

        # Extract and store the data from each match
        for match in matches:
            fee_type, fee_amount, date = match
            # Convert fee_amount to float
            fee_amount = float(fee_amount)
            # If it's a credit, convert to a negative number
            if "Credit" in fee_type:
                fee_amount = -fee_amount
            extracted_data.append({"Date": date, "FeeType": fee_type, "FeeAmount": fee_amount})

    # Create DataFrame
    df = pd.DataFrame(extracted_data)

    # Create a pivot table to arrange data by date and fee type
    pivot_table = df.pivot_table(values='FeeAmount', index='Date', columns='FeeType', aggfunc='sum', fill_value=0)

    # Add a row for totals
    pivot_table.loc['Total'] = pivot_table.sum()

    # Add a column for the total of each date
    pivot_table['Total Date'] = pivot_table.sum(axis=1)

    # Print the resulting DataFrame
    print(pivot_table)

    # Export DataFrame to Excel
    excel_buffer = BytesIO()
    pivot_table.to_excel(excel_buffer)
    excel_buffer.seek(0)  # Reset the buffer position to the beginning

    download_file = st.download_button(
        label="Download",
        data=excel_buffer,
        file_name=f"{file_name}_FEES.xlsx",  # Ensure the file extension is .xlsx
    )

    # Print extracted data for verification
    for entry in extracted_data:
        print(entry)
