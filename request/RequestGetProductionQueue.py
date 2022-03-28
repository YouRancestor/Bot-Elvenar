import json
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestGetProductionQueue(RequestPostJson):
    def __init__(self, session: Session, entity_id: str) -> None:
        super().__init__(session)
        self.entity_id = entity_id

    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'CityProductionService',
            'requestData': [
                self.entity_id
            ],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'getProductionQueue'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestGetProductionQueue(sess, "training_grounds_production")
        response = request.post()
        li = json.loads(response.text)
        print(json.dumps(li, indent=4))

