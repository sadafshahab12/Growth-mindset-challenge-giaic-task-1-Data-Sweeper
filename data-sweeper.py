import streamlit as st
import pandas as pd
import os
from io import (
    BytesIO,
)  # convert data into binary and store into memory just for short time

st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("Data Sweeper")
st.write(
    "Transform your files between CSV and Excel formats with built-in data cleaning and visualization"
)

uploaded_files = st.file_uploader(
    "Upload your file (CSV or Excel): ",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[
            -1
        ]  # file ext csv and xlsx or something else

        if file_ext == ".csv":
            df = pd.read_csv(file, encoding="ISO-8859-1")
        elif file_ext == ".xlsx":
            df = pd.read_excel(file , engine="openpyxl")
        else:
            st.error(f"Unsupported file type : {file_ext}")
            continue
        # display file info
        st.write(f"File Name: {file.name}")
        st.write(f"File Size : {file.size/1024}")

        # show 5 rows of our data frame
        st.write("Preview the Head of the Data Frame")
        st.dataframe(df.head())

        # options for data cleaning
        st.subheader("Data Cleaning option:")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:  # context manager automatically open and close what we do
                if st.button(f"Remove Duplicate from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicated Removed!")
            with col2:
                if st.button(f"Fill Missing values for {file.name} "):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(
                        df[numeric_cols].mean()
                    )  # fillna is use replace any missing values
                    st.write("Missing Values have been filled")
            # choose specific column to keep and convert
            st.subheader("Select columns to convert")
            columns = st.multiselect(
                f"Choose column for {file.name}", df.columns, default=df.columns
            )
            df = df[columns]

            # create some visualization
            st.subheader("Data Visualization")
            if st.checkbox(f"Show Visualization for {file.name}"):
                st.bar_chart(df.select_dtypes(include="number").iloc[:,:2])
            # convert file CSV to excel
            st.subheader("Conversion")
            conversion_type = st.radio(
                f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name
            )
            if st.button(f"Convert {file.name}"):
                if not conversion_type:
                    st.warning("Please select a conversion type before converting.")
                    st.stop()

                buffer = BytesIO()

                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False , engine="openpyxl")
                    file_name = file.name.replace(file_ext, ".xlsx" ,)
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)

                # download
                st.download_button(
                    label=f"⬇ Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name= file_name,
                    mime=mime_type,
                )
st.success("All Files Processed!")
