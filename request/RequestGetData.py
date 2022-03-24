import json
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from request.RequestPostJson import RequestPostJson
from session.Session import Session


# get user data
class RequestGetData(RequestPostJson):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_body(self):
        di_request = [{
            '__clazz__': 'ServerRequestVO',
            'requestClass': 'StartupService',
            'requestData': [
                
            ],
            'requestId': self.session.get_post_request_id(),
            'requestMethod': 'getData'
        }]
        return self.build_body(di_request)

if __name__ == '__main__':
    sess = Session(sys.argv[1])
    if sess.load_from_file():
        request = RequestGetData(sess)
        response = request.post()
        li = json.loads(response.text)
        print(json.dumps(li, indent=4))
