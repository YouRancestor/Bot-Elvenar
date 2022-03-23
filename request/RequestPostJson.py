import hashlib
import json
import sys,os
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
        super().set_cookies(self.session.get_cookie(self.session.world_id+'.elvenar.com'))
        super().set_headers({'Content-Type': 'application/json'})
        super().set_body(self.get_body())

        return super().post()

    def build_body(self, di_request: Dict) -> str:
        request_json_str = json.dumps(di_request, separators=(',', ':'))
        str_to_hash = (self.session.json_h + self.session.hash_key + request_json_str).encode()
        body = hashlib.md5(str_to_hash).hexdigest()[0:10] + request_json_str
        return body
    
    def get_body(self) -> str:
        return ''