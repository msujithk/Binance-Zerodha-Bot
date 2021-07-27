from kiteconnect import KiteConnect
import requests,json
from kiteconnect import KiteTicker
from datetime import datetime
from pytz import timezone
import time
#import urllib2

buf = [1,2,3,4,5,6,7,8,9]
remove = [2,4,8,1,3,5,6,7,9]
buf = [x for x in buf if x not in remove]
print(buf)


api_key = 'z2eq7chglmfkhy4k' 
s_key = 'viazgyt22cbluetute5727kyy908lyx5'
kite = KiteConnect(api_key=api_key)
url = kite.login_url()
print(url)
#response = requests.get(url)
#print(response.history)
#req = requests.request('GET', url)
#print (f'REQUEST = {req.content}')
with requests.Session() as s:
    p = s.post(url)
    print(p.text)


request_token = ''
#if request_token == '':
#    print('Request Token is empty')
data = kite.generate_session(request_token, api_secret=s_key)
print(data)
kite.set_access_token(data["access_token"])



arg =  kite.EXCHANGE_NSE + ':' + 'VEDL'
try:
    response =  kite.ltp(arg)
except Exception as e:
    print("get_current_margin_price(: call failed. Reason =  {}".format(e.message))

print(" kite.ltp Response")
print(response)


try:
    order = kite.place_order(variety = kite.VARIETY_REGULAR,
                                tradingsymbol = 'VEDL',
                                exchange = kite.EXCHANGE_NSE,
                                transaction_type = kite.TRANSACTION_TYPE_BUY,
                                quantity = 1,
                                order_type = kite.ORDER_TYPE_LIMIT,
                                price = 97,
                                product = kite.PRODUCT_CNC)
except Exception as e:
        print("order_limit_buy: Buy order placement failed. Reason =  {}".format(e.message))   

print(' kite.place_order BUY Response')
print (order)
'''
order = None

try:
    order = kite.place_order(variety = kite.VARIETY_REGULAR,
                                tradingsymbol = 'VEDL',
                                exchange = kite.EXCHANGE_NSE,
                                transaction_type = kite.TRANSACTION_TYPE_SELL,
                                quantity = 1,
                                order_type = kite.ORDER_TYPE_LIMIT,
                                price = 101.25,
                                product = kite.PRODUCT_CNC)
except Exception as e:
        print("order_limit_sell: Sell order placement failed. Reason = {}".format(e.message)) 
print('kite.place_order SELL Response')
print (order)



try:
    trades = kite.order_trades(order_id = '{}'.format(order))

except  Exception as e:
        print("get_order: call failed. Reason = {}".format(e.message))
print(' kite.order_trades Response')
print(trades)
'''
try:
    res  = kite.cancel_order(variety = kite.VARIETY_REGULAR, order_id ='{}'.format(order))
except Exception as e:
        print("cancel_order: call failed. Reason =  {}".format(e.message))
print(' kite.cancel_order Response')
print(res)
'''
try:

    info =   kite.margins()

except Exception as e:
    print("get_account_info: call failed. Reason =  {}".format(e.message))

print(' kite.margins Response')
print(info)
'''
