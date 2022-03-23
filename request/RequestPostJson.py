import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session.Session import Session
from request.Request import Request

class RequestPostJson(Request):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
