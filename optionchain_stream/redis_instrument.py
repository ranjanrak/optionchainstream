"""
@author: rakeshr
"""

"""
Dump all exchange instruments/contract data to Redis
Retrive strike and instrument token detail from redis for each symbol search
"""

import redis
import json

class InstrumentDumpFetch():

    __conn = None

    @staticmethod
    def __init__():
        # Default redis port connection
        # Port no and host be edited by user or will make both as acceptable argument in later release
        print('This is init')
        if InstrumentDumpFetch.__conn != None:
            raise Exception("This class is a singleton!")
        else:
            InstrumentDumpFetch.__conn = redis.Redis(host='localhost', port=6379)


    @staticmethod
    def get_conn():
        if InstrumentDumpFetch.__conn == None:
            InstrumentDumpFetch()
        return InstrumentDumpFetch

    @staticmethod
    def data_dump(symbol, instrument_data):
        """
        Dump specific exchange complete instrument data
        Param symbol:(string) - Option contract symbol
        Param instrument_data:(dictionary) - List of dict for specific option contract containing all strike, etc
        """

        InstrumentDumpFetch.__conn.set(symbol, json.dumps(instrument_data))


    @staticmethod
    def symbol_data(symbol):
        """
        Return instrument detail for required symbol
        Param symbol:(string) - Option contract symbol to be searched
        """
        try:
            contract_detail = json.loads(InstrumentDumpFetch.__conn.get(symbol))
        except TypeError:
            raise Exception('Key not found - {}'.format(symbol))
        return contract_detail

    @staticmethod
    def fetch_token(token):
        """
        Fetch contract name for requested instrument token
        Param token:(integer) - Instrument token
        """
        try:
            token_instrument = json.loads(InstrumentDumpFetch.__conn.get(token))
        except Exception as e:
            raise Exception('Error {}'.format(e))
        return token_instrument

    @staticmethod
    def store_optiondata(tradingsymbol, token, optionData):
        """
        Store option chain data for requested symbol
        Param symbol:(string) - Option contract symbol
        Param token:(integer) - Instrument token
        Param optionData:(dict) - Complete data dump for specific option symbol
        """
        optionChainKey = '{}:{}'.format(tradingsymbol, token)
        try:
            InstrumentDumpFetch.__conn.set(optionChainKey, json.dumps(optionData))
        except Exception as e:
            raise Exception('Error - {}'.format(e))

    @staticmethod
    def fetch_option_data(tradingsymbol, token):
        """
        Fetch stored option data
        Param symbol:(string) - Option contract symbol
        Param token:(integer) - Instrument token
        """
        optionContractKey = '{}:{}'.format(tradingsymbol, token)
        try:
            token_data = json.loads(InstrumentDumpFetch.__conn.get(optionContractKey))
        except Exception as e:
            raise Exception('Error - {}'.format(e))
        return token_data