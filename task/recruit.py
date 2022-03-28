import json
import sys,os
from time import sleep
from threading import Thread
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from session.Session import Session
from request.RequestGetProductionQueue import RequestGetProductionQueue
from request.RequestStartProduction import RequestStartProduction
from request.RequestPickupProduction import RequestPickupProduction

def auto_train(sess, barrack_name: str, barrack_id: int, train_item: List[int]):
    item_len = len(train_item)
    count = 0
    while True:
        req_get_production_queue = RequestGetProductionQueue(sess, barrack_name)
        res_military_production = req_get_production_queue.post()
        li = json.loads(res_military_production.text)

        unlocked_slots_num = 0
        producing_slots_num = 0
        remaining_time = 0

        for item in li:
            if item['requestMethod'] == 'getProductionQueue':
                res_data = item['responseData']
                unlocked_slots_num = res_data['unlockedSlots']
                if 'slots' in res_data:
                    slots = res_data['slots']
                    producing_slots_num = len(slots)
                    producing_item = slots[0]
                    remaining_time = producing_item['remainingTime']

        idle_slots_num = unlocked_slots_num - producing_slots_num
        if idle_slots_num > 0:
            req_pickup = RequestPickupProduction(sess, [barrack_id])
            res_pickup = req_pickup.post()
            sleep(2)
            remaining_time -= 2

            for _ in range(idle_slots_num):
                train_item_index = count % item_len
                count += 1
                req_start_production = RequestStartProduction(sess, [barrack_id], train_item[train_item_index], 1)
                res_start_production = req_start_production.post()
                sleep(2)
                remaining_time -= 2

        if remaining_time <= 0:
            sleep(10)
        else:
            sleep(remaining_time + 0.2)



if __name__ == '__main__':
    sess = Session(sys.argv[1])

    if not sess.load_from_file():
        raise 'no session'

    thr_military = Thread(target=auto_train, args=[sess, 'military_production', 15, [3,4,5]])
    thr_military.daemon = True
    thr_military.start()

    thr_training_grounds = Thread(target=auto_train, args=[sess, 'training_grounds_production', 261, [1,2,3]])
    thr_training_grounds.daemon = True
    thr_training_grounds.start()

    thr_military.join()
    thr_training_grounds.join()