import math
from builtins import print
from itertools import count
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.exceptions import BinanceAPIException
import parameters
from adapter import Adapter
import time
import csv
from decimal import Decimal
import datetime
import threading
import logger
from order import BinanceOrder


Relay_Price_To_Strategy = None

''''   
def process_trade_message(msg):

    if not validate_msg(msg):
        trade_bot.event.set()
        return

    if msg['e'] == 'error':
        logger.write(logger.CONNECTION, "Restarting trade socket, Received error msg in process_trade_message : " + msg['m'])
        trade_bot.restart_socket(parameters.TRADE_CHANNEL)
    elif msg['e'] == 'trade':
        trade_bot.trade_data_procerror.process_message(msg)
    trade_bot.event.set()
    #global trade_message_timestamp = msg['E']
'''

def process_kline_message(msg):

    if not validate_msg(msg):
        return

    if msg['e'] == 'error':
        logger.write(logger.CONNECTION, "Restarting Kline socket,Received error msg in process_kline_message: " + msg['m'])
        #trade_bot.restart_socket(parameters.KLINE_CHANNEL)
    elif msg['e'] == 'kline':
        price = round(float(msg['k']['c']), price_round_off)
        if(msg['k']['x'] == True):
            #Relay only closing price
            Relay_Price_To_Strategy(price)

    #kline_message_timestamp = msg['E']


def validate_msg(msg):
    if ((int(time.time() * 1000)) - msg['E']) > 500 :  # make it 2000 ms if there is no time issue
        logger.write(logger.CONNECTION,"Dropping msg: Time Difference = {}  msg = ".format(((int(time.time() * 1000)) - msg['E'])) + msg['e'])
        if msg['e'] == 'trade':
           pass
        elif msg['e'] == 'kline':
           pass
        return False
    return True



class BinanceAdapter(Adapter):
   def __init__(self, api_key, secret_key):
      self.event = threading.Event()
      self.client = None
      self.socket_manager = None
      self.trade_conn_keys = list()
      self.kline_conn_keys = list()
      self.price_round_off  = 0
      self.quantity_round_off = 0
      self.account_balance = []
      self.quote_asset = 0.0
      self.base_asset = 0.0
      self.base = parameters.base
      self.quote = parameters.quote
      self.exchange_pair = self.base + self.quote
      self.trade_type = parameters.trade_type 
      logger.todays_date = datetime.date.today()

      while self.client is None:
        try:
          self.client = self.create_client(api_key,secret_key)
        except Exception:
          logger.write(logger.CONNECTION,"Re-trying connection to client")
          time.sleep(20)

      try:
        self.get_symbol_info()
      except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "EXCEPTION Code = {}  ".format(e.code) + e.message)

      try:
        self.update_account_info('Margin')
      except BinanceAPIException as e:
          logger.write(logger.EXCEPTION, "EXCEPTION Code = {}  ".format(e.code) + e.message)

      print (f'Base asset balance = {self.get_base_asset_balance()}  Quote asset balance = {self.get_quote_asset_balance()}')

      self.create_socket()
      self.get_klines()

      #self.connection_check_thread = threading.Thread(target=self.poll)
      #self.connection_check_thread.start()
      #self.read_klinefile()

   def set_price_callback(self, price_callback_func):
        global Relay_Price_To_Strategy
        Relay_Price_To_Strategy = price_callback_func

   def create_order(self):
        return BinanceOrder()

   def publish_LTP(self): 
        pass

   def adjust_price_for_sell(self, price):
        return (price - (price * 0.0001))

   def adjust_price_for_buy(self, price):
        return (price + (price * 0.0001))

   def create_client(self, api_key, secret_key):
       print("Connecting to server")
       # {"verify": False, "timeout": 20} will be internally added to every request. To override the values explictly add this in other statements
       return Client(api_key, secret_key, {"verify": False, "timeout": 20})

   def get_symbol_info(self):
       symbol_info = self.client.get_symbol_info(self.exchange_pair)
       print(symbol_info)
       value = Decimal(symbol_info['filters'][0]['minPrice']).normalize()
       self.price_round_off = abs(value.as_tuple().exponent)
       global price_round_off
       price_round_off  = self.price_round_off
       value = Decimal(symbol_info['filters'][2]['stepSize']).normalize()
       self.quantity_round_off = abs(value.as_tuple().exponent)
       logger.write(logger.CONNECTION,f'self.quantity_round_off = {self.quantity_round_off} self.exchange_pair = {self.exchange_pair}')


   def server_time_sync_check(self):
      # time check
      for i in range(1, 10):
         local_time1 = int(time.time() * 1000)
         server_time = self.client.get_server_time()
         diff1 = server_time['serverTime'] - local_time1
         local_time2 = int(time.time() * 1000)
         diff2 = local_time2 - server_time['serverTime']
         print("local1: %s server:%s local2: %s diff1:%s diff2:%s" % (
         local_time1, server_time['serverTime'], local_time2, diff1, diff2))
         time.sleep(2)



   def create_socket(self):
      while self.socket_manager is  None:
          self.socket_manager = BinanceSocketManager(self.client, user_timeout = 60)
          if(self.socket_manager is None):
             logger.write(logger.CONNECTION,"BinanceSocketManager() returned None")
             time.sleep(20)
      #if atleast one thred is not started here websocket will not work in Linux
      self.open_data_channels()
      self.socket_manager.start()


   # this is to check the network disconnection
   def poll(self):
       while(True):
           if  self.event.wait(timeout= 60) == False: # wait returms False if it times out
               logger.write(logger.CONNECTION,"Poll Time Out, Restarting connection")
               #self.restart_socket(parameters.KLINE_CHANNEL)
               #self.restart_socket(parameters.TRADE_CHANNEL)
           time.sleep(20)
           self.event.clear()  # reset the event flag

   def open_trade_socket(self):
      pass
      '''
      conn = False
      while conn is False:
           conn = self.socket_manager.start_trade_socket(self.exchange_pair, process_trade_message)
           if conn is not False:
             self.trade_conn_keys.append(conn)
           else:
             logger.write(logger.CONNECTION,"start_trade_socket returned False for " + self.exchange_pair)
             time.sleep(10)

      print(self.trade_conn_keys)
      '''

   def open_kline_socket(self):
       conn = False
       while conn is False:
               conn = self.socket_manager.start_kline_socket(self.exchange_pair, process_kline_message, interval = parameters.KLINE_INTERVAL_MINUTE) #kline  of 15 minute interval
               if conn is not False:
                   self.kline_conn_keys.append(conn)
               else:
                   logger.write(logger.CONNECTION,"start_kline_socket returned False for " + self.exchange_pair)
                   time.sleep(10)

       print(self.kline_conn_keys)

   '''
   def restart_socket(self, connection_type):

       #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2
       #CLOSE ALL OPEN ORDERS FIRST
       #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       logger.write(logger.CONNECTION,"Re-starting " + connection_type)

       if connection_type == parameters.TRADE_CHANNEL:
           for conn in self.trade_conn_keys:
              self.socket_manager.stop_socket(conn)
              self.trade_conn_keys.remove(conn)
           try:
               self.open_trade_socket()
           except Exception as e:
               logger.write(logger.CONNECTION,"start_trade_socket() Exception raised: " + e.status_code + "" + e.message)
       elif connection_type == parameters.KLINE_CHANNEL:
           self.get_klines()
           for conn in self.kline_conn_keys:
              self.socket_manager.stop_socket(conn)
              self.kline_conn_keys.remove(conn)
           try:
               self.open_kline_socket()
           except Exception as e:
               logger.write(logger.CONNECTION,"start_kline_socket() Exception raised: " + e.status_code + "" + e.message)
   '''


   def get_klines(self):
       while not self.download_klines():
           time.sleep(10)  # get fresh klines after re-connection



   def download_klines(self):
         try:
           closing_price = []
           for kline in self.client.get_historical_klines_generator(self.exchange_pair, parameters.KLINE_INTERVAL_MINUTE, parameters.KLINE_PERIOD):
              closing_price.append(self.round(float(kline[4]),self.price_round_off))
              self.save_klines_in_csv(kline)
              print("Downloading klines ...")
         except BinanceAPIException as e:
              logger.write(logger.EXCEPTION, "EXCEPTION Code = {}  ".format(e.code) + e.message)
              return False
         print("For {} Done getting {} worth of {} candle sticks".format(self.exchange_pair, parameters.KLINE_PERIOD, parameters.KLINE_INTERVAL_MINUTE))
         return True


   def open_data_channels(self):
       try:
           self.open_kline_socket()
       except Exception as e:
           logger.write(logger.CONNECTION,"start_kline_socket() Exception raised: ")
       '''''
       try:
           self.open_trade_socket()
       except Exception as e:
           logger.write(logger.CONNECTION,"start_trade_socket() Exception raised: ")
       '''''

   def save_klines_in_csv(self,kline):
       file = open("klines_MA.csv", "at")
       cw = csv.writer(file,delimiter=',',quoting=csv.QUOTE_ALL)
       if cw is not None:
           cw.writerow(kline)



   def correct_quantity(self, quanitiy, mode):
        if mode == 'BUY':
           return  self.round(float(quantity),self.quantity_round_off) 
        elif mode == 'SELL':
            return  self.verify_quantity(quantity)
        


   def place_buy_limit_order(self, quantity, price, mode = 'Margin'):
        price = self.round(price,self.price_round_off)
        quantity = self.round(float(quantity),self.quantity_round_off)
        logger.write(logger.ERROR,"order_limit_buy: symbol = {}, quantity = {}, price = {}".format(self.exchange_pair,quantity,price))
        try:
            if mode == 'Margin':
                return self.client.create_margin_order(
                                            symbol = self.exchange_pair,
                                            side = self.client.SIDE_BUY,
                                            type = self.client.ORDER_TYPE_LIMIT,
                                            timeInForce = self.client.TIME_IN_FORCE_GTC,
                                            quantity = quantity,
                                            price = '{}'.format(price)
                                        )
            else:
                return self.client.order_limit_buy(
                                           symbol = self.exchange_pair,
                                           quantity = quantity,
                                           price = '{}'.format(price)
                                         )
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code) + e.message)
            return None
            


   def place_sell_limit_order(self, quantity, price, mode = 'Margin'):
        price = self.round(price, self.price_round_off)
        quantity = self.verify_quantity(quantity)#self.correction(quantity)
        logger.write(logger.ERROR,"order_limit_sell: symbol = {}, quantity = {}, price = {}".format(self.exchange_pair, quantity,price))
        try:
            if mode == 'Margin':
                return self.client.create_margin_order(
                                            symbol = self.exchange_pair,
                                            side = self.client.SIDE_SELL,
                                            type = self.client.ORDER_TYPE_LIMIT,
                                            timeInForce = self.client.TIME_IN_FORCE_GTC,
                                            quantity = quantity,
                                            price = '{}'.format(price)
                                        )
            else:
                return self.client.order_limit_sell(
                                            symbol = self.exchange_pair,
                                            quantity = quantity,
                                            price = '{}'.format(price)
                                          )
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code) + e.message)
            return None


   def get_order(self,order_ID, type = 'Margin'):
        logger.write(logger.OUTPUT, "get_order:  symbol = {}, orderID = {}".format(self.exchange_pair, order_ID))    
        try:
            if type == 'Margin':
                return self.client.get_margin_order(
                                    symbol = self.exchange_pair,
                                    orderId = '{}'.format(order_ID)
                                   )
            else:
                return self.client.get_order(
                                     symbol = self.exchange_pair,
                                     orderId = '{}'.format(order_ID)
                                   )
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)



   def cancel_open_order(self,order_ID, type = 'Margin'):
        logger.write(logger.ERROR, "cancel_order:  Cancelling symbol = {}, orderID = {}".format(self.exchange_pair, order_ID))
        try:
            if type == 'Margin':
                return self.client.cancel_margin_order(
                                        symbol = self.exchange_pair,
                                        orderId = '{}'.format(order_ID)
                                      )
            else:
                return self.client.cancel_order(
                                        symbol = self.exchange_pair,
                                        orderId = '{}'.format(order_ID)
                                      )
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def update_account_info(self, type = 'Margin'):
        try:
            if type == 'Margin':
                info = self.client.get_margin_account()
                self.account_balance = info["userAssets"]
                #logger.write(logger.OUTPUT, f'get_account_info: BALANCE = {self.account_balance}')
            else:
                info = self.client.get_account()
                self.account_balance = info["balances"]
            self.quote_asset = self.get_quote_asset_balance()
            self.base_asset = self.get_base_asset_balance()
            logger.write(logger.OUTPUT, f'update_account_info: Base = {self.base_asset} Quote = {self.quote_asset}')
            return [self.base_asset, self.quote_asset]
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def get_margin_health(self):
        try:
            info = self.client.get_margin_account()
            #'marginLevel': '1.96592799' The meter
            # 'totalAssetOfBtc': '0.00348556' Total balance in BTC
            #'totalLiabilityOfBtc': '0.0017' Loan amount in BTC
            #'totalNetAssetOfBtc': '0.00171257' Original quantity (my amount)
            #price = self.get_current_margin_price()
            #liquidity_buffer = (price * float(info['totalLiabilityOfBtc'])) - (price * float(info['totalNetAssetOfBtc']))
            return float(info['marginLevel'])
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def cancel_all_open_margin_orders(self):
        try:
            orders =  self.client.get_open_margin_orders()
            if len(orders) is 0:
                return
            for order in orders:
                self.cancel_order(order['orderId'], 'Margin')
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)
       

   def get_current_margin_price(self):
        try:
            info =  self.client.get_margin_price_index(symbol = self.exchange_pair)
            price = Decimal(info['price'])
            logger.write(logger.OUTPUT, f'get_current_margin_price: Current price = {price}') 
            return price
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def spot_to_margin_transfer(self,asset, amount):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            return self.client.transfer_spot_to_margin(asset = asset,  amount = amount)
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def margin_to_spot_transfer(self,asset,amount):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            amount  = self.round(float(amount),self.quantity_round_off)
            return self.client.transfer_margin_to_spot(asset = asset,  amount = amount)
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def get_max_transfer_amount(self,asset):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            return self.client.get_max_margin_transfer(asset = asset)
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def create_loan(self,asset, amount):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            amount = self.round(float(amount), self.quantity_round_off)
            logger.write(logger.OUTPUT, f'create_loan: Amount = {amount} asset = {asset}')
            return self.client.create_margin_loan(asset = asset, amount = amount)
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def repay_loan(self,asset, amount):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            amount = self.round(float(amount), self.quantity_round_off)
            return self.client.repay_margin_loan(asset = asset, amount = amount)
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def get_loan_request_status(self,asset, tx):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            return self.client.get_margin_loan_details(asset = asset, txId = tx)
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def get_loan_repay_status(self,asset, tx):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            return self.client.get_margin_repay_details(asset = asset, txId = tx)
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def get_max_loan_amount(self, asset):
        try:
            if  parameters.BASE == asset:
                asset = self.base
            elif parameters.QUOTE == asset:
                asset = self.quote
            max_amount = self.client.get_max_margin_loan(asset = asset)
            return float(max_amount['amount'])
        except BinanceAPIException as e:
            logger.write(logger.EXCEPTION, "buy_asset: EXCEPTION Code = {}".format(e.code)+ e.message)


   def get_quote_asset_balance(self):
       for balance in self.account_balance:
           if balance["asset"] in self.exchange_pair:
              if self.exchange_pair[len(self.exchange_pair) - len(balance["asset"]):] == balance["asset"]:
                   return float(balance["free"])


   def get_base_asset_balance(self):
       for balance in self.account_balance:
           if balance["asset"] in self.exchange_pair:
               if self.exchange_pair[:len(balance["asset"])] == balance["asset"]:
                   return float(balance["free"])


   def verify_quantity(self, quantity):
       self.update_account_info('Margin')
       logger.write(logger.OUTPUT, f'verify_quantity:  self.base_asset = {self.base_asset} quantity = {quantity} self.quantity_round_off = {self.quantity_round_off}')
       if quantity > self.base_asset:
           return self.round(self.base_asset,self.quantity_round_off)
       return self.round(quantity, self.quantity_round_off)

   def round(self, value, round_off):
       i = 0
       multiply = 1
       divisor = 10.0
       while i < round_off:
           divisor = divisor * multiply
           multiply = 10
           i += 1
       return math.floor(value * divisor) / divisor


   def get_minimum_quote_balance_required_for_trade(self):
        min_balance = 0
        quote =  parameters.quote
        if quote == 'USDT':
            min_balance = 15
        elif quote == 'BTC':
            min_balance = 0.0023
        elif quote == 'ETH':
            min_balance = 0.098
        elif quote == 'BNB':
            min_balance = 1.08
        return min_balance


   def get_minimum_base_trade_quantity(self):
        min_quantity = 0
        base =  parameters.base
        if base == 'BTC':
            min_quantity =  0.0023
        elif base ==  'ETH':
            min_quantity = 0.098
        elif base == 'BNB':
            min_quantity = 1.08
        return min_quantity
















