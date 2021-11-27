"""
@author: rakeshr
"""

"""
Segregate all option contract along with all strike detail 
and store it in Redis
"""

from kiteconnect import KiteConnect
import requests, os
import pandas as pd
from optionchain_stream.redis_instrument import InstrumentDumpFetch

class InstrumentMaster:
    def __init__(self, api_key):
        self.fno_file = 'https://archives.nseindia.com/content/fo/fo_mktlots.csv'
        self.kite = KiteConnect(api_key=api_key)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.redis_db = InstrumentDumpFetch.get_conn()
        self.counter = 0


    def filter_redis_dump(self):
        """
        Filter only option contract from master instrument and
        dump it to redis
        """
        contractToken = {}
        # Fetch instrument file
        # Filter only F&O contracts
        instruments = self.kite.instruments()
        # Dump token:{symbol,strike} data to redis
        for contract in instruments:
            token_detail = {'symbol':contract['tradingsymbol'], 'strike':contract['strike'],
                            'type':contract['instrument_type']}
            self.redis_db.data_dump(contract['instrument_token'], token_detail)

        # Download and read F&O enabled list of contract
        response = requests.get(self.fno_file, headers=self.headers)
        with open(os.path.join('fo_mktlots.csv'), 'wb') as f:
            f.write(response.content)
        # Filter only contract symbol from marketlot file
        fno_contract = pd.read_csv('fo_mktlots.csv')
        optionInstrument = []
        underInstrument = []
        for index, row in fno_contract.iterrows():
            underlying_name = row['UNDERLYING                          '].rstrip()
            # Remove these suffix to match with kite instrument master
            if 'LTD' in underlying_name:
                underlying_name = underlying_name.replace('LTD', '')
            elif 'LIMITED' in underlying_name:
                underlying_name = underlying_name.replace('LIMITED', '')

            optionInstrument.append({'symbol':row['SYMBOL    '].rstrip(),
                            'underlying':underlying_name.rstrip()})

        for optContract in optionInstrument:
            # Create list of strike price for specific symbol
            contractToken[optContract['symbol']] = []
            for contract in instruments:
                if ((contract['name'] == optContract['symbol'] or \
                    contract['tradingsymbol'] == optContract['symbol'] or \
                    contract['name'] == optContract['underlying']) and \
                    (contract['segment'] == 'NFO-OPT' or
                    (contract['instrument_type'] == 'EQ' and contract['exchange'] == 'NSE'))):
                        contractToken[optContract['symbol']].append({'strike':contract['strike'],
                        'type':contract['instrument_type'], 'expiry':str(contract['expiry']),
                        'token':contract['instrument_token']})
            self.redis_db = InstrumentDumpFetch.get_conn()
            self.redis_db.data_dump(optContract['symbol'], contractToken[optContract['symbol']])

    def fetch_contract(self, symbol, expiry, underlying):
        """
        Fetch strike and token detail for requested symbol
        Param symbol:(string) - Option contract symbol
        """
        token_list = []
        # Fetch all active opt and EQ contracts for requested symbol
        self.redis_db = InstrumentDumpFetch.get_conn()
        optionData = self.redis_db.symbol_data(symbol)
        for strike_detail in optionData:
            # For underlying request fetch both EQ and option contracts
            if underlying:
                if strike_detail['expiry'] == str(expiry) or \
                                strike_detail['type'] == 'EQ':
                    token_list.append(strike_detail['token'])
            else:
                # Only fetch opt contracts
                if strike_detail['expiry'] == str(expiry):
                    token_list.append(strike_detail['token'])
        return token_list

    def fetch_token_detail(self, token):
        """
        Fetch contract name for requested instrument token
        Param token:(integer) - Instrument token
        """
        self.redis_db = InstrumentDumpFetch.get_conn()
        return self.redis_db.fetch_token(token)

    def store_option_data(self, tradingsymbol, token, optionData):
        """
        Store option chain data for requested symbol
        Param tradingsymbol:(string) - Option contract symbol
        Param token:(string) - Expiry date of the requested symbol
        Param optionData:(string) - Complete data dump for required option symbol
        """

        self.redis_db = InstrumentDumpFetch.get_conn()
        return self.redis_db.store_optiondata(tradingsymbol, token, optionData)

    def generate_optionChain(self, token_list):
        """
        Fetch all option contracts for requested symbol
        Param token:(List of string) - List of token
        """
        optionChain = []
        # Iterate though list of tokens for respective symbol and fetch respective strike data
        for instrumentToken in token_list:
            self.counter += 1
            # print("counter = ",(self.counter))
            # print('parent process id:', os.getppid())
            # print('Internal process id:', os.getpid())
            # Fetch market depth data for respective strike
            optionInstrument = self.fetch_token_detail(instrumentToken)
            self.redis_db = InstrumentDumpFetch.get_conn()
            optionData = self.redis_db.fetch_option_data(optionInstrument['symbol'], instrumentToken)
            optionChain.append(optionData)
        return optionChain