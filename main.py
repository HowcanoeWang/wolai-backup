# -*- encoding: utf-8 -*-
import os
import json
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from data_process import get_root_index, get_pages_from_chunks


class Wolai():

    def __init__(self, info_file, save_folder='.', close_tab=False):

        with open(info_file, 'r') as f:
            info = json.loads(f.readlines()[0])
            self.username = info['username']
            self.password = info['password']
            self.namespace = info['namespace']
            self.token = info['token']

        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        self.close_tab = close_tab
        self.folder = os.path.abspath(save_folder)
        self.cookie= os.path.join(self.folder, 'cookie.json')

        # no header mode please refer: https://www.cnblogs.com/lsdb/p/10515759.html
        # browser_options = webdriver.FirefoxOptions()
        # browser_options.add_argument('--headless')
        # browser_options.add_argument('--disable-gpu')
        # self.browser = webdriver.Firefox(firefox_options=browser_options)
        self.driver = webdriver.Edge("msedgedriver.exe")

        self.header = {
            "Content-Type": "application/json;charset=UTF-8",
            "Cookie": "token=" + self.token,
            "Connection": "close",
            "User-Agent": self.driver.execute_script("return navigator.userAgent;")
        }


    def element_exist(self, tag='div', element={'id': 'pre-loading-mask'}):
        soup = self.get_soup()

        exist = len(soup.find_all(tag, element))

        print(f"waitting for <{tag}> {element}")

        if exist > 0:
            return True
        else:
            return False


    def get_soup(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        return soup


    def login(self):
        if os.path.exists(self.cookie):
            self.driver.get('https://www.wolai.com')

            while self.element_exist(tag='div', element={'id': 'pre-loading-mask'}):
                time.sleep(5)

            self.load_cookie(self.cookie)

            time.sleep(3)

            self.driver.refresh()

        else:
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

            while not self.element_exist(tag='div', element={'id': 'private-tree'}):
                time.sleep(5)


            self.save_cookie(self.cookie)

            print(self.token)


    def save_cookie(self, path):
        with open(path, 'w') as filehandler:
            json.dump(self.driver.get_cookies(), filehandler)


    def load_cookie(self, path):
        with open(path, 'r') as cookiesfile:
            cookies = json.load(cookiesfile)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.add_cookie({'domain': 'api.wolai.com', 
                                'expiry': cookie['expiry'], 
                                'httpOnly': False, 
                                'secure': False, 
                                'path': '/', 
                                'name': 'token', 
                                'value': self.token})

        print(f"The cookie will expire at {datetime.utcfromtimestamp(cookie['expiry']).strftime('%Y-%m-%d %H:%M:%S')}")

    ###########################
    # Fetch data by html.post #
    ###########################
    def get_user_data(self):
        url = "https://api.wolai.com/v1/transaction/getUserData"

        r = requests.post(url, headers=self.header)

        if r.status_code == 200:
            return json.loads(r.text)
        else:
            return False

    def get_page_chunks(self, page_id):
        url = 'https://api.wolai.com/v1/transaction/getPageChunks'

        post_data = {
            "pageId": page_id,
            "chunkNumber": 0,
            "limit": 300,
            "position": {"stack": []}
        }

        time.sleep(1)

        r = requests.post(url, data=json.dumps(post_data), headers=self.header)
        # 跑多了之后，会出来这样的错误
        """  
        File "main.py", line 178, in iter_page
            self.iter_page(pid, level=level+4)
        File "main.py", line 170, in iter_page
            getPageChunks = self.get_page_chunks(page_id)
        File "main.py", line 152, in get_page_chunks
            r = requests.post(url, data=json.dumps(post_data), headers=self.header)
        File "C:\ProgramData\Anaconda3\envs\lab\lib\site-packages\requests\api.py", line 119, in post
            return request('post', url, data=data, json=json, **kwargs)
        File "C:\ProgramData\Anaconda3\envs\lab\lib\site-packages\requests\api.py", line 61, in request
            return session.request(method=method, url=url, **kwargs)
        File "C:\ProgramData\Anaconda3\envs\lab\lib\site-packages\requests\sessions.py", line 542, in request
            resp = self.send(prep, **send_kwargs)
        File "C:\ProgramData\Anaconda3\envs\lab\lib\site-packages\requests\sessions.py", line 655, in send
            r = adapter.send(request, **kwargs)
        File "C:\ProgramData\Anaconda3\envs\lab\lib\site-packages\requests\adapters.py", line 498, in send
            raise ConnectionError(err, request=request)
        requests.exceptions.ConnectionError: ('Connection aborted.', OSError(0, 'Error'))
        """

        if r.status_code == 200:
            return json.loads(r.text)
        else:
            return False


    def get_all_page_info(self):
        getUserData = self.get_user_data()
        self.workspace, self.pages = get_root_index(getUserData)

        for pid in self.pages.id.values:
            print(f"-> {pid}-{self.pages[self.pages.id == pid].name.values[0]}")
            self.iter_page(pid)


    def iter_page(self, page_id, level=0):
        getPageChunks = self.get_page_chunks(page_id)
        child_pages = get_pages_from_chunks(getPageChunks, self.workspace)
        
        for pid in child_pages.id.values:
            current_record = child_pages[child_pages.id == pid]
            if pid not in self.pages.id.values:
                self.pages = pd.concat([self.pages, current_record])
                print(f"{' '*(level+4)}-> {pid}-{child_pages[child_pages.id == pid].name.values[0]}")
                self.iter_page(pid, level=level+4)
            else:
                #print(f"{' '*(level+4)}[] {pid}-{child_pages[child_pages.id == pid].name.values[0]}")
                continue


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

    def __del__(self):
        # 退出程序时关闭浏览器
        if self.close_tab:
            self.driver.close()

if __name__ == '__main__':

    wolai = Wolai('userinfo.txt', 'backup', close_tab=True)

    #wolai.login()
    wolai.get_all_page_info()

    print(wolai.pages)

    wolai.pages.to_csv('backup/pages.csv')

    #pages = wolai.get_menu_tree_page()

    #print(pages)