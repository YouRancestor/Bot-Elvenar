import json
import sys,os
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestCancelTrade(RequestPostJson):
    def __init__(self, session: Session, trades: List[int]) -> None:
        super().__init__(session)
        self.trades = trades

    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'TradeService',
            'requestData': self.trades,
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'cancelTrade'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        from request.RequestGetOwnPlayerTrades import RequestGetOwnPlayerTrades

        # query exsisting trades
        request = RequestGetOwnPlayerTrades(sess)
        response = request.post()
        li_responses = json.loads(response.text)

        li_trades = []
        for res in li_responses:
            if res['requestMethod'] == 'getOwnPlayerTrades':
                li_trades = res['responseData']

        # cancel all trades
        for trade in li_trades:
            request = RequestCancelTrade(sess, trade['id'])
            response = request.post()
            li = json.loads(response.text)
            print(json.dumps(li, indent=4))
