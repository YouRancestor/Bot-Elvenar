from hashlib import new
import json
import sqlite3
from typing import List, Dict
import requests
import base64

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session.BrowserSimulationLogger import BrowerSimulationLogger
from request.RequestLoginGame import RequestLoginGame
from request.Request import Request

table_name = 'session_info'
db_file_name = 'sessions.db'

class Session:
    def __init__(self, username, password = '') -> None:
        self.username = username
        self.password = password
        self.cookies = dict()
        self.world_id = 'en2'
        self.json_h = ''
        self.hash_key = ''
        self.post_request_id = 0

    def get_cookie(self, domain) -> dict:
        return self.cookies[domain]

    def get_json_gateway_url(self) -> str:
        return 'https://{}.elvenar.com/game/json?h={}'.format(self.world_id, self.json_h)
    def get_ws_gateway_url(self) -> str:
        return 'wss://{}.elvenar.com/ws/stomp'.format(self.world_id)
    def get_ws_passcode(self) -> str:
        # get ws passcode
        index_page_url = 'https://{}.elvenar.com/game/index'.format(self.world_id, self.json_h)
        request_with_cookie = Request()
        request_with_cookie.set_url(index_page_url)
        cookie = self.get_cookie('{}.elvenar.com'.format(self.world_id))
        cookie.extend(self.get_cookie('en0.elvenar.com'))
        request_with_cookie.set_cookies(cookie)
        index_page = request_with_cookie.get() # /game/index
        new_socket_start = index_page.text.find('new Socket')
        first_comma = index_page.text.find(',', new_socket_start)
        ws_passcod_start = index_page.text.find('\'', first_comma) + 1
        ws_passcod_end = index_page.text.find('\'', ws_passcod_start)
        return index_page.text[ws_passcod_start:ws_passcod_end]


    def get_post_request_id(self) -> int:
        id = self.post_request_id
        self.post_request_id += 1
        return id

    def set_cookies(self, domain : str, cookies : List[Dict[str, str]]):
        self.cookies[domain] = cookies
        pass

    # the first step for existing session
    def load_from_file(self) -> bool:
        conn = sqlite3.connect(db_file_name)
        cur = conn.cursor()
        str_sql_select = "SELECT * FROM {} WHERE username='{}'".format(table_name, self.username)
        cur.execute(str_sql_select)
        result = cur.fetchall()
        conn.close()
        if len(result) == 0:
            return False
        else:
            self.password = result[0][1]
            self.cookies = json.loads(result[0][2])
            self.world_id = result[0][3]
            self.json_h = result[0][4]
            self.hash_key = result[0][5]
            return True

    def save_to_file(self):
        conn = sqlite3.connect(db_file_name)
        cur = conn.cursor()

        str_sql_select = "SELECT * FROM {} WHERE username='{}'".format(table_name, self.username)
        cur.execute(str_sql_select)
        result = cur.fetchall()

        str_cookies = self.cookie_to_str()
        if len(result) == 0:
            # insert
            str_sql = "INSERT INTO {} VALUES('{}', '{}', '{}', '{}', '{}', '{}')".format(table_name, self.username, self.password, str_cookies, self.world_id, self.json_h, self.hash_key)
        else:
            # update
            str_sql = "UPDATE {} SET cookies='{}', world_id='{}', json_h='{}', hash_key='{}' WHERE username='{}'".format(table_name, str_cookies, self.world_id, self.json_h, self.hash_key, self.username)
        c = cur.execute(str_sql)
        conn.commit()
        conn.close()

    def cookie_to_str(self) -> str:
        return json.dumps(self.cookies)

    # the first step for new session
    def login_account(self):
        if self.password is None:
            raise "no password"
        logger = BrowerSimulationLogger(self.username, self.password)
        self.cookies['en0.elvenar.com'] = logger.login_and_get_session_cookies()
        # self.save_to_file()

    # the second step
    # @param world_id 'en1' or 'en2' or 'en3'
    def login_game(self, world_id='en2'):
        self.world_id = world_id
        request = RequestLoginGame(self.world_id) # /play
        request.set_cookies(self.cookies['en0.elvenar.com'])
        response = request.post()
        # if response.status_code == 200:
        try:
            di = json.loads(response.text)
            next_request_url = di['redirect']
            next_response = requests.get(next_request_url) # /game
            if next_response.status_code == 200:
                self.cookies[self.world_id+'.elvenar.com'] = []
                for name, value in next_response.history[0].cookies.items():
                    self.cookies[self.world_id+'.elvenar.com'].append({'name': name, 'value': value})
                # self.cookies[self.world_id+'.elvenar.com'].append({'name': 'ig_conv_last_site', 'value': 'https://'+self.world_id+'.elvenar.com/game/index'})
                # for item in self.cookies['en0.elvenar.com']:
                #     if item['name'] == 'metricsUvId':
                #         metricsUvId = item
                # self.cookies[self.world_id+'.elvenar.com'].append(metricsUvId)

                # get json gateway
                json_gateway_url_index = next_response.text.find('json_gateway_url') # find json_gateway_url
                json_start = next_response.text.rfind('{', 0 ,json_gateway_url_index)
                json_end = next_response.text.find('}', json_gateway_url_index) + 1
                json_str = next_response.text[json_start:json_end] # json string including json_gateway_url
                json_str = json_str.replace('\'', '"')
                di = json.loads(json_str)
                b64_encoded_json_gateway_url = di['json_gateway_url']
                b64_encoded_ws_gateway_url = di['socket_gateway_url']
                self.json_gateway_url = 'https:'+base64.b64decode(b64_encoded_json_gateway_url).decode()
                self.ws_gateway_url = base64.b64decode(b64_encoded_ws_gateway_url).decode()

                def get_key(game_page) -> str:
                    # get hash key
                    script_key_word_index = game_page.find('elvenar-ax3-release')
                    if script_key_word_index < 0:
                        raise 'version changed'
                    script_url_start = game_page.rfind('http', 0 ,script_key_word_index)
                    if script_url_start < 0:
                        raise 'version changed'
                    script_url_end = game_page.find('.js', script_key_word_index) + 3
                    if script_url_end < 0:
                        raise 'version changed'
                    key_script_url = game_page[script_url_start:script_url_end]

                    script_src = requests.get(key_script_url).text
                    key_start = script_src.find('get_key:function(){return"') + len('get_key:function(){return"')
                    key_end = script_src.find('"', key_start)
                    key = script_src[key_start:key_end]
                    return key

                self.json_h = self.json_gateway_url[len('https:')+30:]
                self.hash_key = get_key(next_response.text)
                self.save_to_file()

                return True
        except Exception as e:
            conn = sqlite3.connect(db_file_name)
            cur = conn.cursor()

            str_sql = "DELETE FROM {} WHERE username='{}'".format(table_name, self.username)

            c = cur.execute(str_sql)
            conn.commit()
            conn.close()
            print('Exception:{}'.format(repr(e)))
            print('Login game faild. Cache cleared.')
            return False

# Relogin and cache all the required params
# After this, only need Session(username).load_from_file() before send POST request.
if __name__ == '__main__':
    import sys
    sess = Session(sys.argv[1], sys.argv[2])

    if not sess.load_from_file():
        sess.login_account()

    # for key, value in sess.cookies.items():
    #     print(key)
    #     for item in value:
    #         print(item)

    sess.login_game()



