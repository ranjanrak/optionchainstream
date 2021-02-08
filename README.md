# Option Chain Stream

Live streaming option chain for equity derivatives using Kite connect Websocket. 

# Installation
``` 
git clone https://github.com/ranjanrak/OptionChainStream.git
```
# Usage
```
from option_chain import OptionChain
OptionStream = OptionChain("connect_api_key", "connect_secret_key", "connect_request_token",
                    "option_trading_symbol", "option_expiry_date in yyyy-mm-dd format")
# Eg: OptionChain('XXXXXX', 'XXXXXXX', 'XXXXXX', 
                    'ONGC', '2021-02-25')
# Sync master instrument data to DB(redis)     
# This sync is required only once daily at initial run             
OptionStream.sync_instruments()
# Stream option chain data in real-time
StreamData = OptionStream.create_option_chain()
for data in StreamData:
    print(data)
```
#### Response
```
...., 'change': 54.09090909090908, 'oi': 7700},{'token': 24268034, 'symbol': 'ONGC21FEB87PE', 'last_price': 1.5, 'volume': 61600, 'change': 0.0, 'oi': 400400}, 
{'token': 24268290, 'symbol': 'ONGC21FEB88CE', 'last_price': 10.6, 'volume': 0, 'change': -12.033195020746897, 'oi': 15400}, {'token': 24268546, 'symbol': 
'ONGC21FEB88PE', 'last_price': 1.75, 'volume': 53900, 'change': 25.000000000000007, 'oi': 261800}, {'token': 24268802, 'symbol': 'ONGC21FEB89CE', 
'last_price':10.6, 'volume': 15400, 'change': -5.77777777777778, 'oi': 107800}, 
{'token': 24269058, 'symbol': 'ONGC21FEB89PE', 'last_price': 1.85, 'volume': 184800, 'change': -11.904761904761905, 'oi': 338800}, {'token': 24269314, 'symbol': 
'ONGC21FEB90CE', 'last_price': 10.0, 'volume': 654500, 'change': 2.5641025641025643, 'oi': 1632400}, {'token': 24269570, 'symbol': 'ONGC21FEB90PE', 'last_price': 
2.2, 'volume': 1925000, 'change': -2.2222222222222143, 'oi': 3326400}, {'token': 24269826, 'symbol': 'ONGC21FEB91CE', 'last_price': 9.3, 'volume': 15400, 
'change': -6.999999999999993, 'oi': 308000}, {'token': 24270082, 'symbol': 'ONGC21FEB91PE', 'last_price': 2.55, 'volume': 61600, 'change': -5.555555555555569, 
'oi': 323400}, {'token': 24270338, 'symbol': 'ONGC21FEB92CE', 'last_price': 8.7, 'volume': 30800,....
```
