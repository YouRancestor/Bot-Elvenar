import json
import signal
import sys,os
from time import sleep
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from session.Session import Session
from request.RequestGetData import RequestGetData
from request.RequestPickupProduction import RequestPickupProduction
from request.RequestStartProduction import RequestStartProduction
from request.RequestGetNPCOffers import RequestGetNPCOffers
from request.RequestAcceptNpcOffer import RequestAcceptNpcOffer

from typing import Dict, List

def get_data(sess):
    req_get_data = RequestGetData(sess)
    res_get_data = req_get_data.post()
    li = json.loads(res_get_data.text)

    data = None
    for item in li:
        if item['requestMethod'] == 'getData' and item['requestClass'] == 'StartupService':
            data = item['responseData']
            break
    return data

def filter_entities(entities: List[Dict], type: str) -> List[Dict]:
    li = []
    for entity in entities:
        id = ''
        id = entity['cityentity_id']
        if id.find(type) > 0:
            li.append(entity)
    return li

def get_entities_with_state(entities: List[Dict], target_state: str):
    entitis_id = []
    for entity in entities:
        state = entity['state']
        if state['__class__'] == target_state:
            entitis_id.append(entity['id'])
    return entitis_id


def pickup(sess: Session, entity_type: str):

    data = get_data(sess)
    if data is not None:
        user_data = data['user_data']
        citi_map = data['city_map']
        all_entities = citi_map['entities']
        entities = filter_entities(all_entities, entity_type)
        entities_id = get_entities_with_state(entities, 'ProductionFinishedVO')
        req_pickup = RequestPickupProduction(sess, entities_id)
        res_pickup = req_pickup.post()
        return json.loads(res_pickup.text)
    else:
        return None

def start_production(sess, entity_type: str, production_index: int):

    data = get_data(sess)
    if data is not None:
        user_data = data['user_data']
        citi_map = data['city_map']
        all_entities = citi_map['entities']
        entities = filter_entities(all_entities, entity_type)
        entities_id = get_entities_with_state(entities, 'IdleVO')
        print('Idle {} num: {}'.format(entity_type, len(entities_id)))
        if len(entities_id) == 0:
            left_time = entities[0]['state']['next_state_transition_in']
            print('{}s left'.format(left_time))
        req_start = RequestStartProduction(sess, entities_id, production_index, 1)
        res_start = req_start.post()
        return json.loads(res_start.text)
    else:
        return None

# keep the amount of coins and supplies from reaching limit
def moniter_coin_and_supply(sess):
    # query status
    data = get_data(sess)
    def get_capacity(data, resource_name: str) -> int:
        return data['resources_cap']['resources'][resource_name]
    def get_amount(data, resource_name: str) -> int:
        return data['resources']['resources'][resource_name]
    coin_capacity = get_capacity(data, 'money')
    supply_capacity = get_capacity(data, 'supplies')
    coin_amount = get_amount(data, 'money')
    supply_amount = get_amount(data, 'supplies')

    def accept_cheapest_npc_offer(sess, money_or_supplies: str) -> int:
        req_get_npc_offers = RequestGetNPCOffers(sess)
        res_get_npc_offers = req_get_npc_offers.post()
        res_data = json.loads(res_get_npc_offers.text)
        offers = res_data[0]['responseData']['npcTrades'] # list
        target_offer_id = 0
        min_price = None
        for offer in offers:
            if money_or_supplies in offer:
                price = offer[money_or_supplies]
                if min_price is None:
                    min_price = price
                    target_offer_id = offer['id']
                else:
                    if price < min_price:
                        min_price = price
                        target_offer_id = offer['id']
        req_accept_npc_offer = RequestAcceptNpcOffer(sess, target_offer_id)
        res_accept_npc_offer = req_accept_npc_offer.post()
        return min_price


    while True:
        if (coin_amount > coin_capacity * 0.95):
            coin_amount -= accept_cheapest_npc_offer(sess, 'money')
        elif (supply_amount > supply_capacity * 0.95):
            supply_amount -= accept_cheapest_npc_offer(sess, 'supplies')
        else:
            break


    # restart timer
    global t
    t = threading.Timer(300, moniter_coin_and_supply, args=(sess,))
    t.start()



old_sig_handler = signal.getsignal(signal.SIGINT)
def _handler(signum, frame):
    global t
    if signum == signal.SIGINT:
        t.cancel()
        old_sig_handler(signum, frame)

import threading
t = None
if __name__ == '__main__':
    sess = Session(sys.argv[1])

    if not sess.load_from_file():
        raise 'no session'

    signal.signal(signal.SIGINT, _handler)

    t = threading.Timer(1, moniter_coin_and_supply, args=(sess,))
    t.start()
    while True:
        result = pickup(sess, 'Workshop')
        result = start_production(sess, 'Workshop', 1)
        sleep(300.5)



