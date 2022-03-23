import json
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestAcceptPlayerTrade(RequestPostJson):
    def __init__(self, session: Session, trade_id: int) -> None:
        super().__init__(session)
        self.trade_id = trade_id

    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'TradeService',
            'requestData': [
                self.trade_id
            ],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'acceptPlayerTrade'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestAcceptPlayerTrade(sess, 79621780)
        response = request.post()
        li = json.loads(response.text)
        print(json.dumps(li, indent=4))


