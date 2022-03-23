import json
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestGetOwnPlayerTrades(RequestPostJson):
    def __init__(self, session: Session) -> None:
        super().__init__(session)


    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'TradeService',
            'requestData': [],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'getOwnPlayerTrades'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestGetOwnPlayerTrades(sess)
        response = request.post()
        di = json.loads(response.text)
        print(json.dumps(di, indent=4))