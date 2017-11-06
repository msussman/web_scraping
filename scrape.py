from requests import get
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urljoin

main_page = "https://www.stickyguide.com"

# url for product list of all flowers
url = urljoin(main_page, '/dispensaries/capital-city-care/menu.html')
print(url)


response = get(url)

# parse the html
html_soup = BeautifulSoup(response.text, 'html.parser')
print(type(html_soup))

prod_containers = html_soup.find_all('div', class_='flower-details')
print(type(prod_containers))
print(len(prod_containers))

# loop through each container and pull out relevant information
for prod_container in prod_containers[:2]:
    # product name
    prod_name = prod_container.h5.a.text.strip()
    # product link
    prod_link = urljoin(main_page, prod_container.h5.a['href'])
    print(prod_link)
    prod_response = get(prod_link)
    prod_html = BeautifulSoup(prod_response.text, 'html.parser')
    # pull description from individual page
    prod_sum_container = prod_html.find('div', class_='product-bio')
    prod_summary = prod_sum_container.p.text.strip()
    # pull type from individual page
    prod_type_containers = prod_html.find_all('a')
    for prod_type_container in prod_type_containers:
        if "product_category" in prod_type_container['href']:
            prod_category = prod_type_container.text
            print("product_category {}".format(prod_category))
        elif "type_name" in prod_type_container['href']:
            prod_type = prod_type_container.text
            print("product_type {}".format(prod_type))
    # output product html to file
    '''with open(prod_name + '.html', 'w') as f:
        f.write(str(prod_html))'''
    # grower
    prod_grower = prod_container.div.text.strip()
    # navigate to product page and parse HTML
    # loop through attributes in the stats clearfix...div
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
        prod_price = prod_price_value.text
        prod_size = prod_price_sizes[i].text
        #print(prod_name, prod_link, prod_grower, prod_summary, prod_price, prod_size)