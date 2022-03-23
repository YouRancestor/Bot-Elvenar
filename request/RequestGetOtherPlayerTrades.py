import hashlib
import json
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestGetOtherPlayerTrades(RequestPostJson):
    def __init__(self, session: Session) -> None:
        super().__init__(session)


    def post(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'TradeService',
            'requestData': [],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'getOtherPlayersTrades'
        }]
        request_json_str = json.dumps(di_request, separators=(',', ':'))
        str_to_hash = (self.session.json_h + self.session.hash_key + request_json_str).encode()
        body = hashlib.md5(str_to_hash).hexdigest()[0:10] + request_json_str

        super().set_url(self.session.get_json_gateway_url())
        super().set_cookies(self.session.get_cookie(self.session.world_id+'.elvenar.com'))
        super().set_headers({'Content-Type': 'application/json'})
        super().set_body(body)

        return super().post()


if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestGetOtherPlayerTrades(sess)
        response = request.post()
        print(response.text)
