import json
import sys,os
from time import sleep
from threading import Thread
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from session.Session import Session
from request.RequestOpenTreasure import RequestOpenTreasure

def open_treasure(sess: Session):
    req_open_treasure = RequestOpenTreasure(sess)
    res_open_treasure = req_open_treasure.post()
    pass


def task(sess: Session):
    while True:
        open_treasure(sess)

        sleep(3600)

if __name__ == '__main__':
    sess = Session(sys.argv[1])

    if not sess.load_from_file():
        raise 'no session'

    thr_task = Thread(target=task, args=[sess])
    thr_task.daemon = True
    thr_task.start()
    thr_task.join()
