from requests import get
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urljoin
# to import html file already saved
import codecs
import pandas as pd
import time

pull_date = time.strftime("%Y%m%d")

main_page = "https://www.stickyguide.com"

DC_page = urljoin(main_page, "/washington-dc/dispensary-finder")

response = get(DC_page)

DC_soup = BeautifulSoup(response.text, 'html.parser')
print(type(DC_soup))


disp_details = DC_soup.find_all('div', class_='details')
disp_locations = DC_soup.find_all('div', class_='location')


print(len(disp_details))

disp_count = 0
columns = ["pull_date", "disp_name", "disp_address", "prod_name", "prod_link", "prod_grower",
           "prod_summary", "prod_category", "prod_subtype",
           "prod_type", "prod_price", "prod_size"]
prod_df = pd.DataFrame(columns=columns)

for disp_details in disp_details:
    # dispensary name
    disp_name = disp_details.h3.a.text.strip()
    print(disp_name)
    # dispensary page
    disp_link = urljoin(main_page, disp_details.h3.a['href'])
    print(disp_link)
    disp_address = disp_locations[disp_count].text
    print(disp_address)

    product_url_list = ["Flowers", "Pre_Rolls", "Concentrates",
                        "Edibles", "Topicals"]


    for product_url in product_url_list:
        # import html already scraped from site
        disp_folder = disp_name.replace(" ", "_")
        product_html = os.path.join(disp_folder, product_url + ".html")
        print(product_html)
        f = codecs.open(product_html, 'r', encoding="utf8")
        response = f.read()

        # parse the html
        html_soup = BeautifulSoup(response, 'html.parser')
        print(type(html_soup))

        prod_containers = html_soup.find_all('div', class_='flower-details')
        print(type(prod_containers))
        print(len(prod_containers))

        # loop through each container and pull out relevant information
        for prod_container in prod_containers:
            # product name
            prod_name = prod_container.h5.a.text.strip()
            print(prod_name)
            # product link
            prod_link = urljoin(main_page, prod_container.h5.a['href'])
            '''prod_response = get(prod_link)
            prod_html = BeautifulSoup(prod_response.text, 'html.parser')'''

            # import html already scraped from site
            html_name = prod_name.replace(
                "/", "_").replace("'", "_").replace(":", "_").replace("-","_") + ".html"
            html_path = os.path.join(disp_folder, product_url, html_name)
            f = codecs.open(html_path, 'r', encoding="utf8")
            prod_html = BeautifulSoup(f.read(), 'html.parser')
            try:
                # pull description from individual page
                prod_sum_container = prod_html.find('div', class_='product-bio')
                prod_summary = prod_sum_container.p.text.strip()
                # pull type from individual page
                prod_type_containers = prod_html.find_all('a')

                for prod_type_container in prod_type_containers:
                    if "product_category" in prod_type_container['href']:
                        if product_url in ["Concentrates", "Edibles", "Topicals"]:
                            prod_subtype = prod_type_container.text
                        else:
                            prod_subtype = ""
                    elif "type_name" in prod_type_container['href']:
                        prod_type = prod_type_container.text
                # pull the prod_category from div class stat id prod_type
                try:
                    prod_cat_container = prod_html.find(
                        'div', attrs={"class": "stat", "id": "product_type"})
                    prod_cat_subcontainer = prod_cat_container.find(
                        'div', class_="value")
                    prod_category = prod_cat_subcontainer.text.strip().replace(
                        "H", "Hybrid").replace("S", "Sativa").replace("I", "Indica")
                except:
                    prod_category = "Unknown"

                # grower
                prod_grower = prod_container.div.text.strip()
                # navigate to product page and parse HTML
                # loop through each div value container and pull price and size
                prod_price_div = prod_container.find(
                    'div', class_='parent_price_box')
                prod_price_values = prod_price_div.find_all('div', class_='value')
                prod_price_sizes = prod_price_div.find_all(
                    'div', class_='attribute')
                # loop through length of values list to get value and sizes
                for i in range(len(prod_price_values)):
                    prod_price_value = prod_price_values[i]
                    # remove denomination span
                    for match in prod_price_value.find_all('span'):
                        match.extract()
                    prod_price = int(prod_price_value.text)
                    if product_url == "Pre_Rolls":
                        prod_size = "Each"
                    else:
                        prod_size = prod_price_sizes[i].text
                    # append row to output dataframe
                    prod_df = prod_df.append(pd.Series([pull_date, disp_name, disp_address, prod_name, prod_link, prod_grower, prod_summary,
                                                        prod_category, prod_subtype, prod_type, prod_price, prod_size], index=columns), ignore_index=True)

                    print("prod_name: {} prod_link: {} prod_grower: {} prod_summary: {} prod_category: {} prod_subtype: {} prod_type: {} prod_price: {} prod_size: {}"
                          .format(prod_name, prod_link, prod_grower, prod_summary, prod_category, prod_subtype, prod_type, prod_price, prod_size))
            except:
                    print("Warning issue with {} for {}".
                          format(prod_html, disp_name))
    disp_count+=1

# output dataframe to CSV
outfile = "Daily_Pull_" + pull_date + ".csv"
prod_df.to_csv(outfile, index=False)
