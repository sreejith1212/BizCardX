# BizCardX: Extracting Business Card Data with OCR
The application is a useful tool for businesses and individuals who need to manage business card information efficiently.
Application contains a simple and intuitive user interface that guides users through the process of uploading the business card image and extracting its information. The extracted information is displayed in a clean and organized manner. The application also allows users to save the extracted information into a database along with the uploaded business card image. Also, the application allows users to read, update and delete the business card data from the database.

## Pre-Requisite
1) Python: Install Python
2) MySQL: Install MySQL database server and client on your system.

## Installation
1) Clone the repo, create and activate the environment for the project.
2) Install all required packages from requirements.txt file using command: "pip install -r requirements.txt".

## Usage
1) To start the app, run command: "streamlit run bizcardx.py".
2) The business card can be uploaded, extracted and saved to the database from "Upload" section.
3) From the "View" section, users can view, edit and delete the extracted business cards data.

## Features
1) Streamlit app: Used Streamlit application to create a simple UI where users can manage business card information efficiently.
2) Image text extraction: Used "Easyocr" to extract data from the Business card.
3) Preprocessing extracted data: Used Python to clean and preprocess extracted text to get required information.
4) Migrate data to a SQL data warehouse: Insert the transformed data into a MySQL database for efficient storage and retrieval.
5) Query the SQL data warehouse: Using SQL queries, retrieve the extracted data, so that the users can view, edit and delete the data as per requirement.



