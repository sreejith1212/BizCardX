import streamlit as st 
from streamlit_option_menu import option_menu
import pandas as pd
import pymysql

# create required tables in sql database if they don't exist
def create_mysql_tables(cursor):

    cursor.execute("SHOW TABLES")
    tables_sql = []
    for table in cursor:
        tables_sql.append(table[0])

    if "business_card_info" not in tables_sql:
        cursor.execute("CREATE TABLE business_card_info ( "
                        "company_name VARCHAR(100),"
                        "card_holdername VARCHAR(100),"
                        "designation VARCHAR(100),"
                        "mobile_number VARCHAR(100),"
                        "email_address VARCHAR(100),"
                        "website_url VARCHAR(100),"
                        "area VARCHAR(100),"
                        "city VARCHAR(100),"
                        "state VARCHAR(100),"
                        "pincode VARCHAR(100),"
                        "PRIMARY KEY (email_address) ) ")
        
if __name__ == "__main__":

    host = 'localhost' 
    user = 'root' 
    password = '12121995' 
    dbname = 'bizcard_data'

    # connect to required sql database, if the database does not exist, create the database and connect to it
    try:
        connection = pymysql.connect(host=host, user=user, password=password, db=dbname)
        cursor = connection.cursor()
    except Exception as e:
        connection = pymysql.connect(host=host, user=user, password=password)
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE {}".format(dbname))
        connection = pymysql.connect(host=host, user=user, password=password, db=dbname)
        cursor = connection.cursor()
    
    create_mysql_tables(cursor)

    # set app page layout type
    st.set_page_config(layout="wide")

    # create sidebar
    with st.sidebar:        
        page = option_menu(
                            menu_title='BizCardX',
                            options=['Home', 'Upload', 'View'],
                            icons=['person-circle','trophy-fill'],
                            styles={"container": {"padding": "5!important"},
                                    "icon": {"color": "brown", "font-size": "23px"}, 
                                    "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "lightblue"},
                                    "nav-link-selected": {"background-color": "grey"},}  
                        )
   
    if page == "Home":

        st.header(':green[BizCardX: Extracting Business Card Data with OCR] :scroll:')
        st.write("")
        st.subheader(":orange[Application Properties :]")

    if page == "Upload":

        st.header(':green[_BizCardX: Extracting Business Card Data with OCR_] :books:')
        st.header("")
        col1, col2, col3 = st.columns(3)
        image_upload = col1.file_uploader("Upload an image")
        
        # extract
        data_extract = {}
        data_extract["company_name"] = "company_name"
        data_extract["card_holdername"] = "card_holdername"
        data_extract["designation"] = "designation"
        data_extract["mobile_number"] = "mobile_number"
        data_extract["email_address"] = "email_address"
        data_extract["website_url"] = "website_url"
        data_extract["area"] = "area"
        data_extract["city"] = "city"
        data_extract["state"] = "state"
        data_extract["pincode"] = "pincode"

        channel_data_df = pd.DataFrame([data_extract])
        channel_data_df_transpose = channel_data_df.T
        channel_data_df = channel_data_df.rename(columns={0:""})
        st.dataframe(channel_data_df_transpose)

        # add to database if not duplicate
        if col2.button("UPLOAD"):
            for i, row in channel_data_df.iterrows():
                query = ("SELECT * FROM business_card_info WHERE email_address = %s")
                val = row["email_address"]
                cursor.execute(query, val)
                connection.commit()
                result = cursor.fetchall()
                if len(result) == 0:
                    sql = ("INSERT IGNORE INTO business_card_info (company_name, card_holdername, designation, mobile_number, email_address, website_url, area, city, state," 
                            " pincode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    val = tuple(row)
                    cursor.execute(sql, val)
                    connection.commit()
                    st.success("inserted")
                else:
                    st.success("already existed")                   
    
    if page == "View":

        sql = "SELECT * FROM business_card_info"
        cursor.execute(sql)
        connection.commit()
        result = cursor.fetchall()
        result_df = pd.DataFrame(result, columns=["Company Name", "Card Holder Name", "Designation", "Mobile Number", 
                                                    "Email Address", "Website Url", "Area", "City", "State", "Pincode"])
        result_df[""] = range(1, len(result_df) + 1) 
        result_df.set_index("", inplace=True)
        result_df["Actions"] = ""

        st.write(result_df.loc[[1,]])

        st.dataframe(result_df, column_config={"Company Name": st.column_config.LinkColumn()},)
        
