import hashlib
import json
import sys,os
# import brotli
from typing import Dict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session.Session import Session
from request.Request import Request

class RequestPostJson(Request):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def post(self):
        super().set_url(self.session.get_json_gateway_url())
        super().set_headers({
            'Content-Type': 'application/json',
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': '{}.elvenar.com'.format(self.session.world_id),
            'Origin': 'https://{}.elvenar.com'.format(self.session.world_id),
            'Os-Type': 'browser',
            'Referer': 'https://{}.elvenar.com/game'.format(self.session.world_id),
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'X-Requested-With': 'ElvenarHaxeClient'
        })
        cookie_account = self.session.get_cookie('en0.elvenar.com')
        cookie_world = self.session.get_cookie(self.session.world_id+'.elvenar.com').copy()

        # for disguising, not necessary
        cookie_world.append({'name': 'ig_conv_last_site', 'value': 'https://{}.elvenar.com/game'.format(self.session.world_id)})
        for item in cookie_account:
            if item['name'] == 'metricsUvId':
                cookie_world.append(item)
                break

        super().set_cookies(cookie_world)
        super().set_body(self.get_body())

        return super().post()

    def build_body(self, di_request: Dict) -> str:
        request_json_str = json.dumps(di_request, separators=(',', ':'))
        str_to_hash = (self.session.json_h + self.session.hash_key + request_json_str).encode()
        body = hashlib.md5(str_to_hash).hexdigest()[0:10] + request_json_str
        return body
    
    def get_body(self) -> str:
        return ''