import json
from typing import List
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestStartProduction(RequestPostJson):
    def __init__(self, session: Session, entities_id: List[int], production_index: int, amount: int) -> None:
        super().__init__(session)
        self.entities = entities_id
        self.production_index = production_index
        self.amount = amount

    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'CityProductionService',
            'requestData': [
                self.entities,
                self.production_index,
                self.amount
            ],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'startProductions'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestStartProduction(sess, [], 1, 1)
        response = request.post()
        li = json.loads(response.text)
        print(json.dumps(li, indent=4))


