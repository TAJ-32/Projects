import requests
from bs4 import BeautifulSoup
import smtplib
import re

def get_price(max_price, business, url):
    #url = 'https://www.barnesandnoble.com/w/red-white-royal-blue-casey-mcquiston/1141346152?ean=9781250856036'

    #business = ""
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    #print(soup.prettify())

    HTML_list = soup.find_all('meta', {'property': lambda x: x
                                                  and 'price' in x})

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
    else:
       converted_price = float(price)

    print("Converted: " + str(converted_price))
    print("Max: " + str(max_price))

    if (converted_price < max_price):
        send_mail(url)
    
    return {"business": business, "price": price}

def send_mail(url):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    UserInput = input("Enter email: ")

    server.login('developercopyemail@gmail.com', 'ixboyksrkmwadrmy')

    Subject = 'Price drop!'

    body = 'The price on your desired item has fallen. Click ' + url

    msg = f"Subject: {Subject}\n\n{body}"

    server.sendmail(
        'developercopyemail@gmail.com',
        UserInput,
        msg
    )
    print("EMAIL SENT")
    #https://www.barnesandnoble.com/w/red-white-royal-blue-casey-mcquiston/1141346152?ean=9781250856036

    server.quit()

def main():
    url = input("Enter Link You Want to Scrape: ")
   
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
    get_price(max_price, business, url),
    #get_price(max_price, business2, url2, "")
    ]

    print(results)    

if __name__ == "__main__":
    main()


   # if (YesOrNo.upper() == "Y" or YesOrNo.upper() == "YES"):
    #    get_price(WhatPrice, UserInput)
    #else:
     #   main()

#main()