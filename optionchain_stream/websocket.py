"""
@author: rakeshr
"""
"""
Websocket client that streams data of all strikes contract 
for requested option symbol 
"""

import json, logging, asyncio, time
from multiprocessing import Process, Queue
from kiteconnect import KiteConnect, KiteTicker
from optionchain_stream.instrument_file import InstrumentMaster


class WebsocketClient:
    def __init__(self, api_key, api_secret, request_token, symbol, expiry):
        # Create kite connect instance
        self.kite = KiteConnect(api_key=api_key)
        self.data = self.kite.generate_session(request_token, api_secret=api_secret)
        self.kws = KiteTicker(api_key, self.data["access_token"], debug=True)
        self.symbol = symbol
        self.expiry = expiry
        self.instrumentClass = InstrumentMaster(api_key)
        self.token_list = self.instrumentClass.fetch_contract(self.symbol, str(self.expiry))
        self.q = Queue()

    def form_option_chain(self, q):
        """
        Wrapper method around fetch and create option chain
        """
        while 1:
            complete_option_data = self.instrumentClass.generate_optionChain(self.token_list)
            # Store queue data 
            q.put(complete_option_data)

    def on_ticks(self, ws, ticks):
        """
        Push each tick to DB
        """   
        for tick in ticks:
            contract_detail = self.instrumentClass.fetch_token_detail(tick['instrument_token'])
            optionData = {'token':tick['instrument_token'], 'symbol':contract_detail['symbol'], 
                                'last_price':tick['last_price'], 'volume':tick['volume'], 'change':tick['change'],
                                'oi':tick['oi']}
            # Store each tick to redis with symbol and token as key pair
            self.instrumentClass.store_option_data(contract_detail['symbol'], tick['instrument_token'], optionData)

    def on_connect(self, ws, response):
        ws.subscribe(self.token_list)
        ws.set_mode(ws.MODE_FULL, self.token_list)

    def on_close(self, ws, code, reason):
        logging.error("closed connection on close: {} {}".format(code, reason))

    def on_error(self, ws, code, reason):
        logging.error("closed connection on error: {} {}".format(code, reason))

    def on_noreconnect(self, ws):
        logging.error("Reconnecting the websocket failed")

    def on_reconnect(self, ws, attempt_count):
        logging.debug("Reconnecting the websocket: {}".format(attempt_count))
    
    def assign_callBacks(self):
        # Assign all the callbacks
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_error = self.on_error
        self.kws.on_noreconnect = self.on_noreconnect
        self.kws.on_reconnect = self.on_reconnect
        self.kws.connect()

    def queue_callBacks(self):
        """
        Wrapper around ticker callbacks with multiprocess Queue
        """
        # Process to keep updating real time tick to DB
        Process(target=self.assign_callBacks,).start()
        # Delay to let intial instrument DB sync
        # For option chain to fetch value
        # Required only during initial run
        time.sleep(2)
        # Process to fetch option chain in real time from Redis
        Process(target=self.form_option_chain,args=(self.q, )).start()