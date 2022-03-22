import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from typing import Dict, List


class Request:
    def __init__(self) -> None:
        self.headers = dict()
        self.cookies = []
        self.body = None
    def set_url(self, url : str):
        self.url = url
    def set_headers(self, headers : Dict[str, str]):
        for key, value in headers.items():
            self.headers[key] = value
    def set_cookies(self, cookies : List[Dict[str, str]]):
        self.cookies = cookies
    def set_body(self, content : str):
        self.body = content
    def get_cookie_str(self):
        li = [cookie['name']+'='+cookie['value'] for cookie in self.cookies]
        return ';'.join(li)
    def get(self):
        headers = self.headers
        cookie_str = self.get_cookie_str()
        headers['Cookie'] = cookie_str
        return requests.get(self.url, headers=headers, data=self.body)
    def post(self):
        headers = self.headers
        cookie_str = self.get_cookie_str()
        headers['Cookie'] = cookie_str
        return requests.post(self.url, headers=headers, data=self.body)
