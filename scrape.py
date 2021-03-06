from requests import get
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urljoin

# get list of all dispensaries in DC
main_page = "https://www.stickyguide.com"

DC_page = urljoin(main_page, "/washington-dc/dispensary-finder")

response = get(DC_page)

DC_soup = BeautifulSoup(response.text, 'html.parser')
print(type(DC_soup))


disp_details = DC_soup.find_all('div', class_='details')
disp_locations = DC_soup.find_all('div', class_='location')


print(len(disp_details))

disp_count = 0
for disp_details in disp_details:
    # dispensary name
    disp_name = disp_details.h3.a.text.strip()
    print(disp_name)
    # dispensary page
    disp_link = urljoin(main_page, disp_details.h3.a['href'])
    print(disp_link)
    disp_address = disp_locations[disp_count].text
    print(disp_address)

    # url for product lists
    product_url_list = ["Flowers", "Pre+Rolls", "Concentrates",
                        "Edibles", "Topicals"]

    for product_url in product_url_list:
        # get html for each dispensary's menu
        product_url_name = "menu.html?type_name=" + product_url
        url = os.path.join(disp_link, product_url_name)
        print(url)

        response = get(url)

        # parse the html
        html_soup = BeautifulSoup(response.text, 'html.parser')
        print(type(html_soup))
        disp_folder = disp_name.replace(" ", "_")
        if not os.path.exists(disp_folder):
            os.makedirs(disp_folder)
        output_name = product_url.replace("+", "_") + ".html"
        with open(os.path.join(disp_folder, output_name), 'w') as f:
            f.write(str(html_soup))

        prod_containers = html_soup.find_all('div', class_='flower-details')
        print(type(prod_containers))
        print(len(prod_containers))
        # loop through each container and pull out relevant information
        for prod_container in prod_containers:
            # product name
            prod_name = prod_container.h5.a.text.strip()
            # product link
            prod_link = urljoin(main_page, prod_container.h5.a['href'])
            print(prod_link)
            prod_response = get(prod_link)
            prod_html = BeautifulSoup(prod_response.text, 'html.parser')
            # pull description from individual page
            prod_sum_container = prod_html.find('div', class_='product-bio')
            # prod_summary = prod_sum_container.p.text.strip()
            # pull type from individual page
            '''prod_type_containers = prod_html.find_all('a')
            for prod_type_container in prod_type_containers:
                if "product_category" in prod_type_container['href']:
                    prod_category = prod_type_container.text
                    print("product_category {}".format(prod_category))
                elif "type_name" in prod_type_container['href']:
                    prod_type = prod_type_container.text
                    print("product_type {}".format(prod_type))'''
            # output product html to file
            output_name = prod_name.replace("/", "_").replace("'", "_")\
                                   .replace(":", "_").replace("-", "_")
            output_folder = os.path.join(disp_folder,
                                         product_url.replace("+", "_"))
            output_path = os.path.join(output_folder, output_name) + ".html"
            print(output_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            with open(output_path, 'w') as f:
                f.write(str(prod_html))
            '''
            # grower
            prod_grower = prod_container.div.text.strip()
            # navigate to product page and parse HTML
            # loop through attributes in the stats clearfix...div
            # loop through each div value container pull price & size
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
                prod_price = prod_price_value.text
                prod_size = prod_price_sizes[i].text
    disp_count += 1'''
