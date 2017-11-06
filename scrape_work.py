from requests import get
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urljoin
#to import html file already saved
import codecs
import pandas as pd
import time

timestr = time.strftime("%Y%m%d")

main_page = "https://www.stickyguide.com"

# url for product list of all flowers
'''url = urljoin(main_page, '/dispensaries/capital-city-care/menu.html')
print(url)


response = get(url)'''

# import html already scraped from site

f = codecs.open("html_out.html", 'r')
response = f.read()

# parse the html
html_soup = BeautifulSoup(response, 'html.parser')
print(type(html_soup))

prod_containers = html_soup.find_all('div', class_='flower-details')
print(type(prod_containers))
print(len(prod_containers))


columns = ["prod_name", "prod_link", "prod_grower", "prod_summary", "prod_category", "prod_type", "prod_price", "prod_size"]
prod_df = pd.DataFrame(columns=columns)
# loop through each container and pull out relevant information
for prod_container in prod_containers[:2]:
    # product name
    prod_name = prod_container.h5.a.text.strip()
    # product link
    prod_link = urljoin(main_page, prod_container.h5.a['href'])
    '''prod_response = get(prod_link)
    prod_html = BeautifulSoup(prod_response.text, 'html.parser')'''
    
    # import html already scraped from site
    html_name = prod_name + ".html"
    f = codecs.open(html_name, 'r')
    prod_html = BeautifulSoup(f.read(), 'html.parser')

    # pull description from individual page
    prod_sum_container = prod_html.find('div', class_='product-bio')
    prod_summary = prod_sum_container.p.text.strip()
    # pull type from individual page
    prod_type_containers = prod_html.find_all('a')
    for prod_type_container in prod_type_containers:
        if "product_category" in prod_type_container['href']:
            prod_category = prod_type_container.text
        elif "type_name" in prod_type_container['href']:
            prod_type = prod_type_container.text
    # grower
    prod_grower = prod_container.div.text.strip()
    # navigate to product page and parse HTML
    # loop through each div value container and pull out the price and size
    prod_price_div = prod_container.find('div', class_='parent_price_box')
    prod_price_values = prod_price_div.find_all('div', class_='value')
    prod_price_sizes = prod_price_div.find_all('div', class_='attribute')
    # loop through length of values list to get value and sizes
    for i in range(len(prod_price_values)):
        prod_price_value = prod_price_values[i]
        '''remove denomination span'''
        for match in prod_price_value.find_all('span'):
            match.extract()
        prod_price = int(prod_price_value.text)
        prod_size = prod_price_sizes[i].text
        #append row to output dataframe
        prod_df = prod_df.append(pd.Series([prod_name, prod_link, prod_grower, prod_summary, prod_category, prod_type, prod_price, prod_size], index=columns), ignore_index=True)

        print("prod_name: {} prod_link: {} prod_grower: {} prod_summary: {} prod_category: {} prod_type: {} prod_price: {} prod_size: {}" \
              .format(prod_name, prod_link, prod_grower, prod_summary, prod_category, prod_type, prod_price, prod_size))

# output dataframe to CSV
outfile = "Daily_Pull_" + timestr + ".csv"
prod_df.to_csv(outfile, index=False)
