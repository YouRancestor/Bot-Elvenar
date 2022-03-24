import json
import sys,os
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestPickupProduction(RequestPostJson):
    def __init__(self, session: Session, entities: List[int]) -> None:
        super().__init__(session)
        self.entities = entities

    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'CityProductionService',
            'requestData': [
                self.entities
            ],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'pickupProduction'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestPickupProduction(sess, [12, 32, 77, 10, 30, 41, 51, 187, 188])
        print(request.get_body())
        response = request.post()
        li = json.loads(response.text)
        print(json.dumps(li, indent=4))
