import sys,os
import threading
import websocket
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from session.Session import Session

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
                wsapp.send('\n')
        event = threading.Event()
        thread = threading.Thread(target=heart_beat, args=(wsapp, event))
        thread.daemon = True
        thread.start()

    elif command == 'MESSAGE':
        content_start = message.find('\n\n') + 2
        content = message[content_start:]
        print('Received message: ' + content)

    else:
        print('Unhandled message: \n' + message)

def on_error(wsapp, error):

    print('Error: {}'.format(error))


def on_close(wsapp, status_code, message):
    print("### closed ###")

if __name__ == '__main__':
    sess = Session(sys.argv[1], sys.argv[2])
    # login
    while True:
        if not sess.load_from_file():
            sess.login_account
        if sess.login_game():
            break
    wsapp = websocket.WebSocketApp(sess.get_ws_gateway_url(),
        on_open = on_open,
        on_message = on_message,
        on_error = on_error,
        on_close = on_close
    )
    wsapp.sess = sess
    print('enter main event loop')
    wsapp.run_forever(ping_interval=5, ping_payload='\n')
