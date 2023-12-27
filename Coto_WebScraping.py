from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas
import re

def cotoMainPage(content = True):
    """"
    This function will open the coto's main page. Then if content is True will return the page content, 
    will return the page driver.
    """
    # Config chrome options. The window will open in full screen.
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')  

    #Chromedriver's path, if you dont have it, you can download it in chromedriver page.
    chrome_driver_path = 'chromedriver.exe'
    chrome_service = ChromeService(executable_path=chrome_driver_path)

    # Initialize chrome
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    # Load Coto's main page and wait until is load,
    driver.get("https://www.cotodigital3.com.ar/sitios/cdigi")
    driver.implicitly_wait(15)
    time.sleep(5)
    
    # if content return the page content, else, return page's driver
    if content:
        page_content = driver.page_source
        driver.quit()
        return page_content
    else:
        return driver

# the 3 ids from the categories that will be use in the study
ids_to_found = ['catv00001254','catv00001256', 'catv00001255' , 'catv00001296']

page_content = cotoMainPage()
soup = BeautifulSoup(page_content, 'html.parser')


# Iterar sobre los IDs y encontrar los elementos <a>
categories = []
sub_categories = []
dict_items = {}

#iter over the id of ids and make a dict with the formath {category:[sub_categories]}
for id_ in ids_to_found:
    # find the id in the page, and then find it's subcategories
    elemento = soup.find("li", id=id_)
    sub_categories_elements = elemento.find_all("ul", class_ ="sub_category")
    #Find the category name.
    category_elements = elemento.find('a', href='#')
    category = category_elements.get_text(strip=True) if category_elements else None
    categories.append(category)
    # iter over the sub_categories and add them to the dict.
    for sub in sub_categories_elements:
        if category not in dict_items.keys():
            dict_items[category] = []
        sub_category = sub.get_text().split("\n")[2]
        dict_items[category].append(sub_category)

#Patter to find the porducts in the html.
pattern = re.compile(r"li_prod00\d+")
items_data = []

# Iter over the range of the dict's keys.
for i in range( len( dict_items.keys() ) ) :
    #Find the id of the key
    id = ids_to_found[i]
    j = 0
    # iter over the category's sub categories.
    for sub_category_name in dict_items[ categories[i] ]:

        # Open Coto's main page.
        driver = cotoMainPage(content=False)

        # Move the mouse on the category to display its content.
        try:
            element = driver.find_element(By.ID, id)
            ActionChains(driver).move_to_element(element).perform()
            driver.implicitly_wait(15)
            time.sleep(2)
        except:
            driver.refresh()
            driver.implicitly_wait(15)
            time.sleep(2)

            element = driver.find_element(By.ID, id)
            ActionChains(driver).move_to_element(element).perform()
            driver.implicitly_wait(15)
            time.sleep(2)

        # Find all the sub_categories in order to be clicked and click the nro j
        sub_category = element.find_elements(By.TAG_NAME, 'h2')[j]
        sub_category.click()
        driver.implicitly_wait(15)
        time.sleep(2)

        # Find all the numer of pages of the sub category
        even_list_items = driver.find_elements(By.CSS_SELECTOR, 'li.even')
        odd_list_items = driver.find_elements(By.CSS_SELECTOR, 'li.odd')
        driver.implicitly_wait(15)
        time.sleep(2)
        num_of_pages = len(even_list_items) + len(odd_list_items)

        # iter over all the number of pages.
        number = 0
        print(number)
        for page in range(0, num_of_pages):
            print(number)
            if number > num_of_pages + 1:
                break
            number = page + 2
            # get the page content.
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            #Obtein all the product data from the page.
            productos = soup.find_all("li", id =pattern)
            if num_of_pages > 1 and number < num_of_pages:
                try:
                    element_next_page = driver.find_element(By.XPATH, '//a[@title="Ir a página {}"]'.format(number))
                except:
                    driver.refresh()
                    driver.implicitly_wait(15)
                    time.sleep(2)
                    element_next_page = driver.find_element(By.XPATH, '//a[@title="Ir a página {}"]'.format(number))

            #Iter over all the page'product and sabe its name and price in items_data
            
            for producto in productos:
                name = producto.find("div", class_ = "descrip_full").get_text(strip=True)
                price = producto.find("span", class_ = "atg_store_newPrice")
                print(name)
                if price:
                    price = price.get_text(strip=True).replace("$","")
                    sub_category_name_txt = sub_category_name.strip().replace(" ", "-",).replace(",","")
                    items_data.append([name, sub_category_name_txt, price])
            #Go to the next page.
            if num_of_pages > 1 and number < num_of_pages:
                element_next_page.click()
                driver.implicitly_wait(15)
                time.sleep(2)

        driver.quit()
        # j increment
        j += 1


# Save the data in a .csv file.

import pandas as pd
from datetime import datetime

column_names = ["Product", "Category", "Price"]
df = pd.DataFrame(items_data)
df.columns = column_names

date_today = datetime.now()
date_today = date_today.strftime("%d-%m-%Y")
save_file_name = f"Coto_Prices-{date_today}.csv"

df.to_csv(save_file_name, index = False, sep = ";")
