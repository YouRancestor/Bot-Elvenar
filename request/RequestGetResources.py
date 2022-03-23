import json
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session



class RequestGetResources(RequestPostJson):
    def __init__(self, session: Session) -> None:
        super().__init__(session)


    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'CityResourcesService',
            'requestData': [],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'getResources'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestGetResources(sess)
        response = request.post()
        li = json.loads(response.text)
        print(json.dumps(li, indent=4))



        print(li[0]['responseData']['resources'])
