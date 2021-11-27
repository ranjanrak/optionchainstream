"""
@author: rakeshr
"""
from kiteconnect import KiteConnect
from optionchain_stream.websocket import WebsocketClient
from optionchain_stream.instrument_file import InstrumentMaster


class OptionChain():
    """
    Wrapper class to fetch option chain steaming data
    """

    def __init__(self, symbol, expiry, api_key, api_secret=None, request_token=None, access_token=None,
                 underlying=False):
        self.symbol = symbol
        self.expiry = expiry
        self.api_key = api_key
        self.api_secret = api_secret
        self.request_token = request_token
        self.access_token = access_token
        self.underlying = underlying
        self.instrumentClass = InstrumentMaster(self.api_key)

    def sync_instruments(self):
        """
        Sync master instrument to redis
        """
        self.instrumentClass.filter_redis_dump()

    def create_option_chain(self):
        """
        Wrapper method to fetch streaming option chain for requested symbol/expiry
        """
        # Assign/generate access_token using request_token and api_secret
        if self.api_secret and self.request_token:
            self.kite = KiteConnect(api_key=self.api_key)
            self.data = self.kite.generate_session(self.request_token, api_secret=self.api_secret)
            self.access_token = self.data["access_token"]
        elif self.access_token:
            self.access_token = self.access_token
        try:
            self.socketClient = WebsocketClient(self.symbol, self.expiry, self.api_key, self.access_token, self.underlying)
        except Exception as e:
            print('%s Order modify to market failed: %s', self.socketClient, str(e))
            raise Exception(str(e))
        # create streaming websocket data
        self.socketClient.queue_callBacks()
        # Keep fetching streaming Queue
        while 1:
            yield self.socketClient.q.get()
