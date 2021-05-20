<a href="https://zerodha.tech"><img src="https://zerodha.tech/static/images/github-badge.svg" align="right" /></a>
# Option Chain Stream

Live streaming option chain for equity derivatives using [Kite connect Websocket](https://kite.trade/docs/connect/v3/websocket/). 

This package uses [Redis](https://redis.io/) as storage backend. Here Redis is used to store real time streaming websocket data and instruments detail i.e all option strike details for contracts. Combination of these data structure are used to create real-time option chain stream for any given instrument.

#### Installation
``` 
pip install optionchain_stream
```
#### Request parameters

| Field                | Type    | Detail                                                                 |
| -------------        |:-------:|:-------------:                                                         |
| api_key              | string  | Kite connect API key                                                   |
| secret_key           | string  | Kite connect API secret                                                |
| request_token        | string  | Kite connect one-time token obtained after the [login flow](https://kite.trade/docs/connect/v3/user/#login-flow)              |
| access_token         | string  | The authentication token obtained post the [login flow](https://kite.trade/docs/connect/v3/user/#login-flow) using request_token and secret_key
| option_symbol        | string  | Symbol of the instrument(eg: NIFTY, SBIN, ONGC, etc)                   |
| option_expiry_date   | string  | Option expiry date in yyyy-mm-dd format(eg: '2021-02-25', '2021-04-29')|

#### Usage
```
from optionchain_stream import OptionChain
OptionStream = OptionChain("option_symbol", "option_expiry_date in yyyy-mm-dd format", "api_key",
                    "api_secret=None", "request_token=None", "access_token=None")

# You can directly pass access_token from previous active session 
Eg: OptionStream = OptionChain("ONGC", "2021-02-25", "your_api_key", access_token="XXXXXX")

# Generate new session by passing api_secret and request_token
Eg: OptionStream = OptionChain("ONGC", "2021-02-25", "your_api_key", api_secret="XXXXX",
                    request_token="XXXXXX")

# Sync master instrument data to DB(redis)     
# This sync is required only once daily at initial run             
OptionStream.sync_instruments()

# Stream option chain data in real-time
StreamData = OptionStream.create_option_chain()
for data in StreamData:
    print(data)
```
#### Response
Responses are JSON messages.

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
#### Response attributes

| Field        | Type    | Detail                                                     |
| -------------|:-------:|:-------------:                                             |
| token        | string  | instrument_token for requested tradingsymbol               |
| symbol       | string  | tradingsymbol of the instrument                            |
| last_price   | float   | Current market price                                       |
| volume       | int     | Volume traded for the day                                  |
| change       | float   | Price change % w.r.t previous day close/LTP                |
| oi           | float   | Open Interest for a options contract                       |
