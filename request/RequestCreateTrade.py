from enum import Enum
import json
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session

class GoodType(Enum):
    Marble = 0
    Steel = 1
    Planks = 2

    Crystal = 3
    Scrolls = 4
    Silk = 5

    Elixir = 6
    MagicDust = 7
    Gems = 8

GoodId = [
    'marble',   # 0
    'steel',    # 1
    'planks',   # 2
    'crystal',  # 3
    'scrolls',  # 4
    'silk',     # 5
    'elixir',   # 6
    'magic_dust', # 7
    'gems'      # 8
]

class RequestCreateTrade(RequestPostJson):
    def __init__(self, session: Session, sell: GoodType, sell_count: int, buy: GoodType, buy_count: int) -> None:
        super().__init__(session)
        self.buy_index = buy.value
        self.sell_index = sell.value
        self.buy_count = buy_count
        self.sell_count = sell_count

    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'TradeService',
            'requestData': [
                {
                    '__clazz__': 'CityGoodVO',
                    'good_id': GoodId[self.sell_index],
                    'value': self.sell_count,
                },
                {
                    '__clazz__': 'CityGoodVO',
                    'good_id': GoodId[self.buy_index],
                    'value': self.buy_count,
                }
            ],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'createTrade'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestCreateTrade(sess, GoodType.Gems, 5, GoodType.Elixir, 5)
        response = request.post()
        di = json.loads(response.text)
        print(json.dumps(di, indent=4))
