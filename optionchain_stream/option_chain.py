"""
@author: rakeshr
"""
import time
from optionchain_stream.websocket import WebsocketClient
from optionchain_stream.instrument_file import InstrumentMaster

class OptionChain():
    """
    Wrapper class to fetch option chain steaming data
    """
    def __init__(self, api_key, api_secret, request_token, symbol, expiry):
        self.api_key = api_key
        self.api_secret = api_secret
        self.request_token = request_token
        self.symbol = symbol
        self.expiry = expiry
        self.instrumentClass = InstrumentMaster(self.api_key)

    def sync_instruments(self):
        """
        Sync master instrument to redis
        """
        self.instrumentClass.filter_redis_dump()
    
    def create_option_chain(self):
        """
        Wrapper method to fetch sreaming option chain for requested symbol/expiry
        """
        self.socketClient = WebsocketClient(self.api_key, self.api_secret, self.request_token, self.symbol, self.expiry)
        # create streaming websocket data
        self.socketClient.queue_callBacks()
        # Keep fetching streaming Queue
        while 1:
            yield self.socketClient.q.get()