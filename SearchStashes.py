import requests
import time
import os
import sys
import re
from plyer import notification


class Sniper:
    def __init__(self):
        self.DEBUG = False
        self.League = "Legion"
        self.ex_price = 150

    def normalize_price(self, price):
        price_list = price.split(' ')
        if price_list[1] == 'exa':
            return float(price_list[0]) * self.ex_price
        elif price_list[1] == 'chaos':
            return float(price_list[0])
        else:
            return 99999999.0

    def check_if_good_deal(self, item):
        wanted_items = {"Inspired Learning": {"price": 15*self.ex_price},
                        "The Pariah": {"price": 1*self.ex_price, "sockets": "W"},
                        "The Taming": {"price": 2.3*self.ex_price},
                        "Berek's Respite": {"price": 2.3*self.ex_price}}

        price = item.get('note', None)
        name = re.sub(r'<<.*>>', '', item.get('name', None))
        if price and name:
            price = price.replace("~b/o ", "").replace("~price ", "")
            if str(item.get('league')) == self.League:
                if name in wanted_items:
                    norm_price = self.normalize_price(price)
                    if self.DEBUG:
                        print(name)
                        print(price)
                        print(norm_price)

                    if norm_price > wanted_items[name]['price']:
                        return False

                    # Check sockets
                    if "sockets" in wanted_items[name]:
                        sockets = item.get('sockets', None)
                        if sockets:
                            color = sockets[0]['sColour']
                            if color != "W":
                                return False
                        else:
                            return False

                    return True

    def run(self):

        url_api = "http://www.pathofexile.com/api/public-stash-tabs?id="
        r = requests.get("http://poe.ninja/api/Data/GetStats")
        next_change_id = r.json().get('next_change_id')
        print(next_change_id)

        while True:
            params = {'id': next_change_id}
            try:
                params = {'id': next_change_id}
                r = requests.get(url_api, params=params)

                ## parsing structure
                data = r.json()

                ## setting next change id
                next_change_id = data['next_change_id']

                ## attempt to find items...
                for stash in data['stashes']:
                    lastCharacterName = stash['lastCharacterName']
                    items = stash['items']
                    stashName = stash.get('stash')

                    # scan items
                    for item in items:
                        price = item.get('note', None)
                        name = re.sub(r'<<.*>>', '', item.get('name', None))
                        if price and name:
                            price = price.replace("~b/o ", "").replace("~price ", "")
                            if str(item.get('league')) == self.League:
                                if self.check_if_good_deal(item):
                                    msg = "@{} Hi, I would like to buy your {} listed for {} in {} (stash tab \"{}\"; position: left {}, top {})".format(
                                        lastCharacterName, name, price, self.League, stashName, item.get('x'),
                                        item.get('y'))
                                    print(msg)
                                    notification.notify(
                                        title='Sniper',
                                        message='Item Found',
                                        app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
                                        timeout=10,  # seconds
                                    )

                # wait 5 seconds until parsing next structure
                time.sleep(0)
            except KeyboardInterrupt:
                print("Closing sniper.py")
                sys.exit(1)
            except BaseException as e:
                exc_type, esc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('Error in main:')
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                # sys.exit(1)


LegionSniper = Sniper()
LegionSniper.run()