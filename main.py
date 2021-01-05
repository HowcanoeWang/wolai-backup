# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import time
import urllib.request

class Wolai():

    def __init__(self, info_file):

        with open(info_file, 'r') as f:
            info = json.loads(f.readlines()[0])
            self.username = info['username']
            self.password = info['password']
            self.namespace = info['namespace']

        self.driver = webdriver.Edge("msedgedriver.exe")


    def element_exist(self, tag='div', element={'id': 'pre-loading-mask'}):
        soup = self.get_soup()

        exist = len(soup.find_all(tag, element))

        if exist > 0:
            return True
        else:
            return False


    def get_soup(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        return soup


    def login(self):
        self.driver.get('https://www.wolai.com/login')
        
        # 检查是否停留在加载页，不然就一直等
        while self.element_exist(tag='div', element={'id': 'pre-loading-mask'}):
            time.sleep(5)

        self.driver.find_element_by_id('inputMobile').send_keys(self.username)
        self.driver.find_element_by_xpath('//div[text()="继续"]').click()
        time.sleep(2)

        self.driver.find_element_by_id('inputPassword').send_keys(self.password)
        time.sleep(2)
        self.driver.find_element_by_xpath('//div[text()="进入"]').click()


    def get_menu_tree_page(self):
        soup = self.get_soup()

        # ensure the sidebar as been loaded
        while not self.element_exist(tag='div', element={'id': 'private-tree'}):
            time.sleep(7)
            soup = self.get_soup()

        menu_list = []
        for menu in soup.find_all('div', {'data-area': 'tree-menu'}):
            menu_list.append(menu['data-id'])

        return set(menu_list)


    def split_url(self, url):

        return url.split(f'{self.namespace}/')[-1]


    def make_url(self, page_id):

        return f"https://www.wolai.com/{self.namespace}/{page_id}"


    def get_one_page_html(self, page_id):
        url = self.make_url(page_id, info)
        home_id = f"id-{suffix}"

        self.driver.get(url)

        soup = self.get_soup()

        while not self.element_exist(driver, tag='div', element={'id': 'pageRoot'}):
            time.sleep(7)
            soup = self.get_soup()
        # pages = 

    def save_to_file(driver, url):
        pass


if __name__ == '__main__':

    wolai = Wolai('userinfo.txt')

    wolai.login()

    pages = wolai.get_menu_tree_page()

    print(pages)