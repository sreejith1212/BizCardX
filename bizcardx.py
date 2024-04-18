import streamlit as st 
from streamlit_option_menu import option_menu
import pandas as pd
import time
import pymysql
from streamlit_modal import Modal
import base64
from PIL import Image
import io
import easyocr
import re

# create required table in sql database if they don't exist
def create_mysql_tables(cursor):

    cursor.execute("SHOW TABLES")
    tables_sql = []
    for table in cursor:
        tables_sql.append(table[0])

    if "business_card_info" not in tables_sql:
        cursor.execute("CREATE TABLE business_card_info ( "
                        "image LONGBLOB,"
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

 # clean the extracted data       
def preprocess_extracted_data(data_string_list):
    
    data_extract = {}
    data_string = " ".join(data_string_list).strip()
    regex_email = re.compile(r'''(
                                    [a-zA-Z0-9]+
                                    @
                                    [a-zA-Z0-9]+
                                    \.[a-zA-Z]{2,10}
                                    )''', re.VERBOSE)
    email_address = ''
    for email in regex_email.findall(data_string):
        email_address += email
        data_string = data_string.replace(email, '')

    regex_website = re.compile(r'www.?[\w.]+', re.IGNORECASE)
    website = ''
    for url in regex_website.findall(data_string):
        website += url
        data_string = data_string.replace(url, '')
    website = website.strip()
    website = "www." + website[3:-3].replace(".","").replace(" ","") + ".com"

    regex_mobile_number = re.compile(r'\+*\d{2,3}\s*\-*\d{3,10}\-*\d{3,10}')
    mobile_number = ''
    for number in regex_mobile_number.findall(data_string):
        mobile_number += ' ' + number
        data_string = data_string.replace(number, '')
    mobile_number = mobile_number.strip()
    mobile_number = mobile_number.strip()
    mobile_number = mobile_number.replace(" ",",")

    regex_address = re.compile(r'\d{2,4}.+\d{6}')
    address = ''
    for i in regex_address.findall(data_string):
        address += i
        data_string = data_string.replace(i, '')
    address = address.replace(";",",")

    pincode_regex = re.compile(r'\b\d{6,7}\b')
    pincode = ''
    for pin in pincode_regex.findall(address):
        pincode += pin
        address = address.replace(pin,"")

    address = address.split(",")

    area = address[0].strip()
    
    city = address[1].strip()
    
    state = address[2].strip()

    designations = ['DATA MANAGER', 'CEO & FOUNDER', 'General Manager', 'Marketing Executive', 'Technical Manager']
    designation = ''
    card_holdername = ''
    for des in designations:
        if re.search(des, data_string, flags=re.IGNORECASE):
            designation += des
            data_string = data_string.replace(des, '')
            card_holdername = (data_string_list[0]).replace(des,"").strip()
            data_string = data_string.replace(card_holdername, '')

    company_name = data_string.strip()
            
    data_extract["company_name"] = company_name
    data_extract["card_holdername"] = card_holdername
    data_extract["designation"] = designation
    data_extract["mobile_number"] = mobile_number
    data_extract["email_address"] = email_address
    data_extract["website_url"] = website
    data_extract["area"] = area
    data_extract["city"] = city
    data_extract["state"] = state
    data_extract["pincode"] = pincode
 
    return data_extract


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
        
        st.header(':green[BizCardX: Your tool for managing business card information efficiently] :scroll:')
        st.write("")
        col_home1, col_home2 = st.columns(2)
        # col_home1.subheader(":orange[Application Properties :]")
        for i in range(3):
            col_home1.subheader("")
        col_home1.subheader(":one: :grey[_Allows users to upload the business card image and extract its information._]")
        for i in range(4):
            col_home1.subheader("")
        col_home1.subheader(":two: :grey[_Allows users to save the extracted information into a database along with the uploaded business card image._]")
        for i in range(4):
            col_home1.subheader("")
        col_home1.subheader(":three: :grey[_Also, allows the users to read, update and delete the business card data from the database._]")
        col_home2.image("business_cards.png")

    if page == "Upload":

        st.header(':green[_BizCardX: Your tool for managing business card information efficiently_] :books:')
        st.header("")
        col1, col2 = st.columns(2)
        # image uploader
        image_upload = col1.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'], key="selected_file")

        if image_upload is not None:
            
            col1.image(image_upload)
           
            file = image_upload.read()
            image_stream = io.BytesIO(file)
            img_bytes = image_stream.getvalue()
            reader = easyocr.Reader(["en"])
             # extract data from image
            extracted_data = reader.readtext(img_bytes, paragraph=True, decoder="wordbeamsearch")
            data_string_list = []
            for data in extracted_data:
                # appending the extracted text only
                data_string_list.append(data[1])

            data_extracted = preprocess_extracted_data(data_string_list)

            # encode the uploaded image to insert it to the sql database
            file_encoded = base64.b64encode(file)

            channel_data_df = pd.DataFrame([data_extracted])
            channel_data_df_transpose = channel_data_df.T
            channel_data_df = channel_data_df.rename(columns={0:""})
            container_upload = col2.container(height=600, border=False)
            for i in range(6):
                container_upload.write("")
            with container_upload.form(key = "ddd"):
                col14, col15 = st.columns(2)
                company_name = col15.text_input(label="Company Name 🏟️", value=channel_data_df.iloc[0]["company_name"])
                card_holder_name = col14.text_input(label="Card Holder Name 👨‍🏭", value=channel_data_df.iloc[0]["card_holdername"])
                designation = col14.text_input(label="Designation 💼", value=channel_data_df.iloc[0]["designation"])
                email = col14.text_input(label="Email Address 📧", value=channel_data_df.iloc[0]["email_address"])
                phone = col14.text_input(label="Mobile Number 📱", value=channel_data_df.iloc[0]["mobile_number"])
                website_url = col15.text_input(label="Website Url 🌐", value=channel_data_df.iloc[0]["website_url"])
                area = col15.text_input(label="Area 🌃", value=channel_data_df.iloc[0]["area"])
                city = col15.text_input(label="City 🌇", value=channel_data_df.iloc[0]["city"])
                state = col15.text_input(label="State 🌆", value=channel_data_df.iloc[0]["state"])
                pincode = col14.text_input(label="Pincode 🏣", value=channel_data_df.iloc[0]["pincode"])

                upload_data = col14.form_submit_button(label="Upload", help="Click to Upload Info!", type = "primary")

            # upload to database if not already exists
            if upload_data:
                query = ("SELECT * FROM business_card_info WHERE email_address = %s")
                val = email
                cursor.execute(query, val)
                connection.commit()
                result = cursor.fetchall()
                if len(result) == 0:
                    if not company_name or not card_holder_name or not designation or not email or not phone or not website_url or not area or not city or not state or not pincode:
                        col2.error(f"All fields are mandatory", icon="🚨")
                    else:
                        sql = ("INSERT INTO business_card_info (company_name, card_holdername, designation, mobile_number, email_address, website_url, area, city, state," 
                                " pincode, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                        val = (company_name, card_holder_name, designation, phone, email, website_url, area, city, state, pincode, file_encoded)
                        cursor.execute(sql, val)
                        connection.commit()
                        col2.success("Business Card Successfully Uploaded")
                else:
                    col2.warning("Business Card Already Uploaded")       
    
    if page == "View":

        sql = "SELECT * FROM business_card_info"
        cursor.execute(sql)
        connection.commit()
        # fetch data from database
        result = cursor.fetchall()
        # decode a base64 encoded image and open it as an image
        def decode_image(image):
            binary_data = base64.b64decode(image)
            fin_image = Image.open(io.BytesIO(binary_data))
            return fin_image
        
        result_df = pd.DataFrame(result, columns=["Business Card", "Company Name", "Card Holder Name", "Designation", "Mobile Number", 
                                                    "Email Address", "Website Url", "Area", "City", "State", "Pincode"])
        result_df[""] = range(1, len(result_df) + 1) 
        result_df.set_index("", inplace=True)
        result_df["Business Card"] = result_df["Business Card"].apply(decode_image)
        business_card_exp = st.expander(":orange[_Business Card Info_]", expanded=True)
        business_card_exp.dataframe(result_df.drop(columns=["Business Card"]), use_container_width=True)

        st.write("")

        business_cards = []
        for i, row in result_df.iterrows():
            card_holder_name = row["Card Holder Name"]
            email_address = row["Email Address"]
            business_cards.append(card_holder_name + " - " + email_address)
        col1, col2, col3 = st.columns(3)
        # Dropdown displays all business cards available in the database 
        option = col1.selectbox("Select Required Business Card Data To Modify/Delete", business_cards, index=None, placeholder="Select Business Card Data", key="selectbox")

        if option is not None:
            email_selected = option.split("-")[1].strip()
            result = result_df[result_df["Email Address"] == email_selected]
            col4, col5 = st.columns([4,2])
            # form to update/delete business card data
            with col4.form(key = 'Business_Card_Info'):     
                st.write('Business Card Information')
                col7, col8 = st.columns(2)
                company_name = col8.text_input(label="Company Name 🏟️", value=result.iloc[0]["Company Name"])
                card_holder_name = col7.text_input(label="Card Holder Name 👨‍🏭", value=result.iloc[0]["Card Holder Name"])
                designation = col7.text_input(label="Designation 💼", value=result.iloc[0]["Designation"])
                email = col7.text_input(label="Email Address 📧", value=result.iloc[0]["Email Address"])
                phone = col7.text_input(label="Mobile Number 📱", value=result.iloc[0]["Mobile Number"])
                website_url = col8.text_input(label="Website Url 🌐", value=result.iloc[0]["Website Url"])
                area = col8.text_input(label="Area 🌃", value=result.iloc[0]["Area"])
                city = col8.text_input(label="City 🌇", value=result.iloc[0]["City"])
                state = col8.text_input(label="State 🌆", value=result.iloc[0]["State"])
                pincode = col7.text_input(label="Pincode 🏣", value=result.iloc[0]["Pincode"])

                col9, col10, col11 = st.columns([1,1,7])
                submit_form = col9.form_submit_button(label="Update", help="Click to Update Info!", type = "primary")
                delete_data = col10.form_submit_button("Delete", type = "primary") 

            col5.image(result.iloc[0]["Business Card"], use_column_width=True, caption= "Business Card")

            if submit_form:
                if not company_name or not card_holder_name or not designation or not email or not phone or not website_url or not area or not city or not state or not pincode:
                    col1.error(f"All fields are mandatory", icon="🚨")
                else:
                    query = ("UPDATE business_card_info SET company_name = %s, card_holdername = %s, designation = %s, mobile_number = %s, email_address = %s, website_url = %s, "
                            "area = %s, city = %s, state = %s, pincode = %s WHERE email_address = %s")
                    val = (company_name, card_holder_name, designation, phone, email, website_url, area, city, state, pincode, result.iloc[0]["Email Address"])
                    cursor.execute(query, val)
                    connection.commit()
                    col1.success(f"Business Card Data successfully updated", icon="✅")
                    time.sleep(1)
                    st.rerun()


            if "delete_confirmation" not in st.session_state:
                st.session_state["delete_confirmation"] = False

            if delete_data:
                st.session_state["delete_confirmation"] = True

            if st.session_state["delete_confirmation"]:    
                modal = Modal(key="Key",title="Confirm To Delete")
                with modal.container():
                    col12, col13, col14 = st.columns(3)
                    if col12.button("Yes", type="primary"):
                        query = "DELETE FROM business_card_info WHERE email_address = %s"
                        val = (result.iloc[0]["Email Address"], )
                        cursor.execute(query, val)
                        connection.commit()
                        col12.success(f":violet[_Business Card Data successfully deleted_]", icon="✅")
                        st.session_state["delete_confirmation"] = False
                        time.sleep(1)
                        st.rerun()
                    if col13.button("No", type="primary"):
                        st.session_state["delete_confirmation"] = False
                        st.rerun()


