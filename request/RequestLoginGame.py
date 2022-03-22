import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from request.Request import Request

class RequestLoginGame(Request):
    def __init__(self, world_id='en2') -> None:
        super().__init__()
        super().set_url('https://en0.elvenar.com/web/login/play')
        super().set_headers({'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        self.world_id = world_id
        super().set_body('world_id={}'.format(self.world_id))



if __name__ == '__main__':
    req = RequestLoginGame()