import json
from math import floor
import signal
import threading
import websocket
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from session.Session import Session
from request.RequestPostJson import RequestPostJson
from request.RequestCancelTrade import clear_all_trades
from request.RequestGetOtherPlayerTrades import RequestGetOtherPlayerTrades
from request.RequestGetResources import RequestGetResources
from request.RequestCreateTrade import GoodId, RequestCreateTrade
from request.RequestAcceptPlayerTrade import RequestAcceptPlayerTrade

t = None

class Schedule:
    def __init__(self) -> None:
        self.timer = None
        
def post_request(request: RequestPostJson):
    request.post()

def place_unfair_trades(sess: Session):
    req_get_resource = RequestGetResources(sess)
    res_get_resource = req_get_resource.post()
    resouces = json.loads(res_get_resource.text)[0]['responseData']['resources']

    threads = []
    for i, good_id in enumerate(GoodId):
        tier = floor(i / 3)
        offer_index = i % 3
        need_indices = [0, 1, 2]
        need_indices.remove(offer_index)
        need_indices = [j + tier * 3 for j in need_indices]
        amount = resouces[good_id]
        offer_value = floor(amount / 10)
        need_value = offer_value * 8
        for need_index in need_indices:
            need_good_id = GoodId[need_index]

            req_create_trade = RequestCreateTrade(sess, good_id, offer_value, need_good_id, need_value)
            thr = threading.Thread(target=post_request, args=[req_create_trade])
            thr.daemon = True
            thr.start()
            threads.append(thr)

    for thr in threads:
        thr.join()

def accept_fellow_trades(sess: Session, guild_id: int):
    req_other_trades = RequestGetOtherPlayerTrades(sess)
    res_other_trades = req_other_trades.post()
    trades = json.loads(res_other_trades.text)[0]['responseData']

    req_get_resource = RequestGetResources(sess)
    res_get_resource = req_get_resource.post()
    res_data = json.loads(res_get_resource.text)
    resouces = res_data[0]['responseData']['resources']

    for trade in trades:
        if trade['trader']['guild_info']['id'] != guild_id:
            continue

        need_good_id = trade['need']['good_id']
        need_good_value = trade['need']['value']
        inventory = resouces[need_good_id]

        if (inventory / 8 * 10 - need_good_value <= 50):
            # not enough stock
            continue
        offer_good_id = trade['offer']['good_id']
        offer_good_value = trade['offer']['value']

        need_good_index = GoodId.index(need_good_id)
        need_tier = floor(need_good_index / 3)
        offer_good_index = GoodId.index(offer_good_id)
        offer_tier = floor(offer_good_index / 3)

        ratio = offer_good_value / need_good_value
        tier_diff = need_tier - offer_tier
        reference_ratio = 1.5 ** tier_diff

        if ratio >= reference_ratio:
            # fair trade, accept
            clear_all_trades(sess)
            req_accept_trade = RequestAcceptPlayerTrade(sess, trade['id'])
            req_accept_trade.post()
            place_unfair_trades(sess)
            break

    t = threading.Timer(5, accept_fellow_trades, args=[sess, guild_id])
    t.daemon = True
    t.start()

def on_open(wsapp):
    passcode = sess.get_ws_passcode()
    msg = 'CONNECT\n'
    msg+= 'login:channel\n'
    msg+= 'passcode:{}\r\n'.format(passcode)
    msg+= 'accept-version:1.1,1.0\n'
    msg+= 'heart-beat:10000,10000\n'
    msg+= '\n\0'
    print(msg)
    wsapp.send(msg)

def on_message(wsapp, message: str):
    lines = message.split('\n')
    command = lines[0]

    if command == 'CONNECTED':
        msg = 'SUBSCRIBE\n'
        msg+= 'id:sub-0\n'
        msg+= 'destination:/queue\n'
        msg+= '\n\0'
        wsapp.send(msg)
        print('connected')
        def heart_beat(wsapp, event):
            while not event.wait(5):
                try:
                    wsapp.send('\n')
                except:
                    print('error: connection closed')
        event = threading.Event()
        thread = threading.Thread(target=heart_beat, args=(wsapp, event))
        thread.daemon = True
        thread.start()

    elif command == 'MESSAGE':
        content_start = message.find('\n\n') + 2
        content = message[content_start:-1]
        o = json.loads(content) # List[Dict]

        if isinstance(o, list):
            for item in o:
                if 'requestClass' in item:
                    request_class = item['requestClass']
                    if request_class == 'CallbackService':
                        data = item['responseData']
                        service = data['service']
                        method = data['method']
                        if method == 'updateTrades' and service == 'TradeService':
                            global t
                            t.cancel()
                            clear_all_trades(wsapp.sess)
                            place_unfair_trades(wsapp.sess)
                            t = threading.Timer(5, accept_fellow_trades, args=[wsapp.sess, wsapp.guild_id])
                            t.daemon = True
                            t.start()
        elif isinstance(o, dict):
            if 'channels' in o:
                for key, value in o['channels'].items():
                    if key.find('guild.') >= 0:
                        wsapp.guild_id = int(key[6:])
                        # global t
                        t = threading.Timer(5, accept_fellow_trades, args=[wsapp.sess, wsapp.guild_id])
                        t.daemon = True
                        t.start()
                        break
                    
                    
        else:
            print('Received message: ' + content)

    else:
        print('Unhandled message: \n' + message)

def on_error(wsapp, error):

    print('Error: {}'.format(error))


def on_close(wsapp, status_code, message):
    print("### closed ###")

# old_sig_handler = signal.getsignal(signal.SIGINT)
# def _handler(signum, frame):
#     global t
#     if signum == signal.SIGINT:
#         t.cancel()
#         old_sig_handler(signum, frame)
# signal.signal(signal.SIGINT, _handler)

if __name__ == '__main__':
    sess = Session(sys.argv[1], sys.argv[2])
    # login
    while True:
        if not sess.load_from_file():
            sess.login_account()
        if sess.login_game():
            break

    clear_all_trades(sess)
    place_unfair_trades(sess)

    wsapp = websocket.WebSocketApp(sess.get_ws_gateway_url(),
        on_open = on_open,
        on_message = on_message,
        on_error = on_error,
        on_close = on_close
    )
    wsapp.sess = sess
    print('enter main event loop')
    wsapp.run_forever(ping_interval=5, ping_payload='\n')
