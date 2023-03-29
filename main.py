from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import csv

DRIVER_URL = "./chromedriver/chromedriver"
NAVER_URL = "https://map.naver.com/v5/search"
SEARCH_TEXT = "아동미술학원"

driver = webdriver.Chrome(DRIVER_URL)
driver.get(NAVER_URL)

time.sleep(3)

# for initalize
driver.switch_to.default_content()

with open('result.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["이름", "주소(우편번호)", "전화번호"])

# search keyword
search_box = driver.find_element_by_css_selector("#container > shrinkable-layout > div > app-base > search-input-box > div > div > div.input_box > input")
search_box.send_keys(SEARCH_TEXT)

time.sleep(1)

search_box.send_keys(Keys.ENTER)

time.sleep(1.5)

with open('result.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    
    while True:
        # scroll to load lazyload element
        try:
            driver.switch_to.frame("searchIframe")

            scroll_container = driver.find_element_by_id("_pcmap_list_scroll_container")
            for i in range(10):
                driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scroll_container)
                time.sleep(0.2)

        finally:
            driver.switch_to.default_content()

        # Get Data and write
        try:
            driver.switch_to.frame("searchIframe")
            boxes = driver.find_elements_by_class_name("VLTHu")

            for i in range(len(boxes)):
                driver.find_element_by_css_selector("#_pcmap_list_scroll_container > ul > li:nth-child(" + str(i + 1) + ") > div.qbGlu > div > a.P7gyV").click()
                driver.switch_to.default_content()

                time.sleep(2)

                try:
                    driver.switch_to.frame("entryIframe")
                    address_opener = driver.find_element_by_css_selector("#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.tQY7D > div > a > span._UCia")
                    address_opener.click()

                    time.sleep(0.5)

                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")
                    place_name = soup.select("#_title > span.Fc1rA")[0].string
                    place_address = soup.select("#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.tQY7D > div > a > span.LDgIH")[0].string
                    place_post_text = soup.select("#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.tQY7D > div > div.Y31Sf")[0].get_text()
                    post_index = place_post_text.find('우편번호')+4
                    place_post = place_post_text[post_index:-2] if post_index != 3 else '우편번호 없음'
                    place_phone = soup.select("#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.nbXkr > div > span.xlx7Q")[0].string

                    print([place_name, place_address + '(' + place_post + ')', place_phone])
                    writer.writerow([place_name, place_address + '(' + place_post + ')', place_phone])
                except Exception as err:
                    print(f'Unexpected {err=}, {type(err)=}')

                finally:
                    driver.switch_to.default_content()
                    driver.switch_to.frame("searchIframe")

            next_page_button_svg = driver.find_elements_by_css_selector('#app-root > div > div.XUrfU > div.zRM9F > a.eUTV2 > svg')[1]    
            is_page_end = driver.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('opacity') === '0.4'", next_page_button_svg)

            if is_page_end == True:
                break
                    
        finally:
            driver.switch_to.default_content()
        
        # goto next page
        try:
            driver.switch_to.frame("searchIframe")
            driver.find_elements_by_css_selector('#app-root > div > div.XUrfU > div.zRM9F > a.eUTV2')[1].click()
        finally:
            driver.switch_to.default_content()

