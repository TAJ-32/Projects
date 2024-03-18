import requests
from bs4 import BeautifulSoup
import smtplib
import re
import mysql.connector
from mysql.connector import Error
import pandas as pd
import socket


socket.getaddrinfo('localhost', 3306)

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

connection = create_db_connection("localhost", "root", "BobbyB123(!)", "Products")


def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database Created Successfully")
    except Error as err:
        print(f"Error: '{err}'")

create_database_query = "CREATE DATABASE Products"
create_database(connection, create_database_query)

connection = create_db_connection("localhost", "root", "BobbyB123(!)", "Products")


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def execute_list_query(connection, sql, val):
    cursor = connection.cursor()
    try:
        cursor.executemany(sql, val)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

create_product_table = """
CREATE TABLE product (
    product_id INT PRIMARY KEY,
    url VARCHAR(1000) NOT NULL,
    price FLOAT(2) NOT NULL,
    max_price FLOAT(2) NOT NULL
);
"""

create_user_table = """
CREATE TABLE user (
    user_id INT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(40) NOT NULL
);
"""

create_userproduct_table = """
CREATE TABLE user_product (
    user_id INT,
    product_id INT,
    CONSTRAINT ID PRIMARY KEY (user_id, product_id),
    CONSTRAINT FK_user FOREIGN KEY (user_id) REFERENCES user (user_id),
    CONSTRAINT FK_product FOREIGN KEY (product_id) REFERENCES product (product_id)
);
"""
#


execute_query(connection, create_product_table)

execute_query(connection, create_user_table)

execute_query(connection, create_userproduct_table)

def get_price(max_price, business, url, user_email):
    #url = 'https://www.barnesandnoble.com/w/red-white-royal-blue-casey-mcquiston/1141346152?ean=9781250856036'

    #business = ""
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    #print(soup.prettify())

    HTML_list = soup.find_all('meta', {'property': lambda x: x
                                                  and 'price' in x})

    HTML_list.append(soup.find_all('span', {'data-test': lambda x: x
                                                and 'price' in x}))

    HTML_list.append(soup.find_all('span', {'class': lambda x: x
                                                and 'price' in x}))
    
    HTML_list.append(soup.find_all('span', {'id': lambda x: x
                                                and 'price' in x}))
    
    #HTML_list.append(soup.find_all('span', {lambda x: 'price' in x}))
    
    HTML_list.append(soup.find_all('div', {'id': lambda x: x
                                                and 'price' in x}))

    HTML_list.append(soup.find_all('div', {'class': lambda x: x
                                                and 'price' in x}))  

    #HTML_list.append(soup.find_all('div', {lambda x: 'price' in x}))                

    for i in HTML_list:
        print("ITEM: " + str(i))
        if ('meta' in str(i)):
            if str(i["content"]):
                HTML_list.remove(i)

    for i in HTML_list:
        print("ITEM: " + str(i))
        if ('meta' in str(i)):
            if float(i["content"]): #if the content of what is attached to the content is a number
                price = str(i["content"])
                print("META PRICE: " + price)
                break
        if ('id' in str(i)):
            print("IN ID")
            splitlist = re.split(' |=|<|>', str(i))

            if ("id" not in splitlist):
                print("Cannot find price")
                price = None
                break

            targetstring = splitlist[splitlist.index("id") + 1]
            targetstring = targetstring.replace('"', '')
            print("TARGET: " + targetstring)
            price = soup.find(id = targetstring).get_text().strip()
            print("PRICE: " + str(price))

            break
        elif ('class' in str(i)):
            print("IN CLASS")
            splitlist = re.split(' |=|<|>', str(i))
            targetstring = splitlist[splitlist.index("class") + 1]
            targetstring = targetstring.replace('"', '')
            print("TARGET: " + targetstring)
            price = soup.find("span", attrs={"class": targetstring}).get_text().strip()
            print("PRICE: " + str(price))

            break

    #print("ITEM: " + str(HTML_list[0]))

    # if ('current' or 'cur' or 'curr' or 'sale' in str(HTML_list[0])):
    #     print("HELLO")
    #     if ('id' in str(HTML_list[0])):
    #         print("HELLO2")
    #         splitlist = re.split(' |=|<|>', str(HTML_list[0]))
    #         targetstring = splitlist[splitlist.index("id") + 1]
    #         targetstring = targetstring.replace('"', '')
    #         print("TARGET: " + targetstring)
    #         price = soup.find(id = targetstring).get_text().strip()
    #         print("PRICE: " + str(price))

    #price = soup.find(id = selector).get_text().strip()

    if '$' in price:
       converted_price = float(price[1:]) #so that we can have it in number form
    elif 'USD' in price:
       converted_price = float(price[:3])
    else:
       converted_price = float(price)

    print("Converted: " + str(converted_price))
    print("Max: " + str(max_price))

    # if (converted_price < max_price):
    #     send_mail(url, converted_price, user_email)
    
    return {"business": business, "price": converted_price}

def send_mail(url, converted_price, user_email):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

#    user_email = input("Enter email: ")

    server.login('developercopyemail@gmail.com', 'ixboyksrkmwadrmy')

    Subject = 'Price match!'

    body = 'The price on your desired item is in your budget! It is only $' + str(converted_price) + '! Click ' + url

    msg = f"Subject: {Subject}\n\n{body}"

    server.sendmail(
        'developercopyemail@gmail.com',
        user_email,
        msg
    )
    print("EMAIL SENT")
    #https://www.barnesandnoble.com/w/red-white-royal-blue-casey-mcquiston/1141346152?ean=9781250856036

    server.quit()

def Login():
    cursor = connection.cursor()

    user_email = input("Enter email: ")

    # get_user_query = """
    # SELECT user_id FROM user WHERE email = %s 
    # """,
    # user_email

    cursor.execute("SELECT user_id FROM user WHERE email = %s", [user_email])
    user_id = cursor.fetchone()

    if user_id is None:
        password = input("You are a new user. Create a password: ")

        query = '''
        INSERT INTO user (user_id, email, password)
        VALUES (%s, %s, %s);
        '''

        cursor.execute("SELECT COUNT(*) FROM user")
        row_count = cursor.fetchone()[0]

        val = [(row_count + 1, user_email, password)]

        execute_list_query(connection, query, val)
        return [user_email, []]
    else:
        cursor.execute("SELECT password from user where email = %s", [user_email])

        user_password = str(cursor.fetchone())

        user_password = user_password.replace("(", "")

        user_password = user_password.replace(")", "")

        user_password = user_password.replace(",", "")

        user_password = user_password.replace("'", "")


        user_input = input("Enter Password: ")


        while (user_input != user_password):
            print("You entered: " + user_input)
            user_input = input("Wrong Password. Enter Password: ")
            
        cursor.executemany("SELECT product_id from user_product where user_id = %s", [user_id])
        products = cursor.fetchall()

        print("Products: " + str(products))
        return [user_email, products]
    

def main():
    cursor = connection.cursor()

    email_and_products = Login()

    user_email = email_and_products[0]

    print("IN MAIN: " + user_email) 

    products = email_and_products[1]

    print("IN MAIN: " + str(products))

    stop = False

    count = 1

    while (not stop):
        print("LOOP #"+str(count))
   
        url = input("Enter Link You Want to Scrape (type nothing if you are done): ")

        if (url == ""):
            break

        WhatPrice = input("Enter your maximum price cap: ")

        max_price = float(WhatPrice)

        business = ""
        #business2 = ""
        #print("At set: " + str(max_price))

        #get_price(max_price)

        #url = 'https://www.barnesandnoble.com/w/red-white-royal-blue-casey-mcquiston/1141346152?ean=9781250856036'
        #url2 = 'https://www.thriftbooks.com/w/red-white-and-royal-blue_casey-mcquiston/19855217/item/53086774/?utm_source=google&utm_medium=cpc&utm_campaign=shopping_new_condition_books_high&utm_adgroup=&utm_term=&utm_content=545756259058&gclid=CjwKCAjwrranBhAEEiwAzbhNtbi_74Fzj1V_JrDgST2HDUSsYJSSIKDlFD3DoyvC-tpJ0HFBmt9MKRoC5sEQAvD_BwE#idiq=53086774&edition=61217805'

        for i in url[12:]:
            #print(i)
            if i == '.':
                break
            else:
                business = business + i
                continue

        print(business)
        results = [
        get_price(max_price, business, url, user_email),
        #get_price(max_price, business2, url2, "")
        ]

        print(results)    

        cursor.execute("SELECT COUNT(*) FROM product")
        row_count = cursor.fetchone()[0]

        query = '''
                INSERT INTO product (product_id, url, price, max_price)
                VALUES (%s, %s, %s, %s);
        '''
        val = [(row_count + 1, url, results[0].get('price'), max_price)]
        count += 1
        execute_list_query(connection, query, val)

#  """
# CREATE TABLE user_product (
#     user_id INT,
#     product_id INT,
#     CONSTRAINT user_product_id PRIMARY KEY (user_id, product_id),
#     CONSTRAINT FK_user FOREIGN KEY (user_id) REFERENCES user (user_id),
#     CONSTRAINT FK_category FOREIGN KEY (product_id) REFERENCES product (product_id)
# );
# """
        cursor.execute("SELECT COUNT(*) FROM user_product")
        row_count2 = cursor.fetchone()[0]

        cursor.execute("SELECT user_id FROM user WHERE email = %s", [user_email])
        user_id, = cursor.fetchone()

        cursor.execute("SELECT product_id FROM product WHERE url = %s", [url])
        product_id, = cursor.fetchone()
        

        query2 = '''
                INSERT INTO user_product (user_id, product_id)
                VALUES (%s, %s);
        '''
        #((user_id,), (product_id,))

        val2 = [(user_id, product_id)]

        print("before query: " + str(query2), str(val2))
        execute_list_query(connection, query2, val2)
        #execute_query(connection, query2)
        print("after query")

    send_mail(user_email)

if __name__ == "__main__":
    main()


   # if (YesOrNo.upper() == "Y" or YesOrNo.upper() == "YES"):
    #    get_price(WhatPrice, UserInput)
    #else:
     #   main()

#main()