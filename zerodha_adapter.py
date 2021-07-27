from adapter import Adapter
import decimal
from order import ZerodhaOrder
from kiteconnect import KiteConnect
import parameters
import time
from datetime import datetime
from pytz import timezone
import logger
import csv

class ZerodhaAdapter(Adapter):
    def __init__(self, api_key, secret_key):
        self.relay_price_to_strategy = None
        self.kite = None
        print('Initializing create client')
        while self.kite == None:
            try:
                self.kite = self.create_client(api_key, secret_key)
            except Exception:
                logger.write(logger.CONNECTION,"Re-trying connection to client")
                time.sleep(20)

        #from_date   = "2015-03-01"
        #to_date     = "2015-08-30"
        interval    =  "30minute"
        instrument_token = "779521"#"500112"# SBIN
        dates= ['2019-04-01','2019-09-30','2019-10-01','2020-03-30']
        #dates= ['2015-03-01','2015-05-30','2015-06-01','2015-08-30','2015-09-01','2015-11-30','2015-12-01','2016-02-29']
        for  from_date,to_date  in zip(dates[0::2], dates[1::2]):
            print (f'downloading Klines from { from_date} To {to_date}')
            self.get_historical_candle_stick(from_date, to_date, interval, instrument_token)
    

    def set_price_callback(self, price_callback_func):
        self.relay_price_to_strategy = price_callback_func


    def get_current_indian_time(self):
        india_time_zone = timezone('Asia/Kolkata')
        india_time = datetime.now(india_time_zone)
        date_time = f'{india_time}'
        current_time = date_time.split()[1].split('.')[0]
        hour = int(current_time.split(':')[0])
        minute = int(current_time.split(':')[1])
        print (f'time = {current_time}')
        return [hour, minute]


    def publish_LTP(self):
        # MAIN loop
        while True:
            hour, minute = self.get_current_indian_time()
            if  hour >= 9 and hour <= 15 :
                if hour == 9 and minute < 15:
                    print ('Out of Trading hours')
                    time.sleep(30)
                elif hour == 15 and minute > 30:
                    print('Out of Trading hours')
                    time.sleep(30)
                else:
                    price = self.get_LTP()
                    self.relay_price_to_strategy(price)
                    time.sleep(900) #publish price in 15 min interval
            else:
                print ('Out of Tradinf hours')
                time.sleep(30)
                

    def get_LTP(self):
        return self.get_current_margin_price()


    def create_client(self, api_key, secret_key):
        kite = None
        kite = KiteConnect(api_key = api_key)
        url = kite.login_url()
        print ('-------------Request url----------------------------------------')
        print (url)
        print ('------------------------------------------------------') 
        data = kite.generate_session(parameters.request_token, api_secret =  secret_key)
        print (data)
        print('Setting access token')
        kite.set_access_token(data["access_token"])
        return kite
    


    def create_order(self):
        return ZerodhaOrder()

    def get_klines(self):
        pass

    def round(self, value, round_off):
        i = 0
        multiply = 1
        divisor = 10.0
        while i < round_off:
            divisor = divisor * multiply
            multiply = 10
            i += 1
        return math.floor(value * divisor) / divisor

    def verify_tick_lot_size(self, price, quantity):
        if quantity < 1:
            quantity = 1
        d_price = decimal.Decimal(price)
        last_digit = d_price.as_tuple().digits[-1]
        if last_digit % 5 != 0: #5 paisa tick
            logger.write(logger.ERROR,f'verify_tick_lot_size: Price not in tick size, last digit = {last_digit} need to adjust price')
            price = price - (last_digit / 100)
            logger.write(logger.ERROR,f'verify_tick_lot_size: Adjusted price = {price}')
        #No need of testing lot size for most of stocks as its 1
        return price, quantity


    def correct_quantity(self, quanitiy, mode):
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
        return quantity
        

    def place_buy_limit_order(self, quantity, price, mode = 'Margin'):#ignore mode
        price = self.round(price, 2)
        quantity = int(quantity)
        #verify tick size of price, normally 5 paisa, get tick size and lot size normally 1
        price , quantity = self.verify_tick_lot_size(price, quantity)
        logger.write(logger.ERROR,"order_limit_buy:Symbol = {} quantity = {}, price = {}".format(parameters.trading_symbol, quantity,price))
        try:
            return  self.kite.place_order(variety = kite.VARIETY_REGULAR,
                                tradingsymbol = parameters.trading_symbol,
                                exchange = self.kite.EXCHANGE_NSE,
                                transaction_type = self.kite.TRANSACTION_TYPE_BUY,
                                quantity = quantity,
                                order_type = self.kite.ORDER_TYPE_LIMIT,
                                price = price,
                                product = self.kite.PRODUCT_CNC)

        except Exception as e:
            logger.write(logger.EXCEPTION,"order_limit_buy: Buy order placement failed. Reason =  {}".format(e.message))        
            return None




    def place_sell_limit_order(self, quantity, price,  mode = 'Margin'):
        price = self.round(price, 2)
        quantity = int(quantity)
        #verify tick size of price, normally 5 paisa, get tick size and lot size normally 1
        price , quantity = self.verify_tick_lot_size(price, quantity)
        logger.write(logger.ERROR,"order_limit_sell:Symbol = {} quantity = {}, price = {}".format(parameters.trading_symbol,quantity,price))        
        try:
            return  self.kite.place_order(variety = kite.VARIETY_REGULAR,
                                tradingsymbol = parameters.trading_symbol,
                                exchange = self.kite.EXCHANGE_NSE,
                                transaction_type = self.kite.TRANSACTION_TYPE_SELL,
                                quantity = quantity,
                                order_type = self.kite.ORDER_TYPE_LIMIT,
                                price = price,
                                product = self.kite.PRODUCT_CNC)
        except Exception as e:
                logger.write(logger.EXCEPTION,"order_limit_sell: Sell order placement failed. Reason = {}".format(e.message))
                return None


    def get_order(self,order_ID, type = 'Margin'):
        try:
            return self.kite.order_trades(order_id = '{}'.format(order_ID))
        except  Exception as e:
            logger.write(logger.EXCEPTION,"get_order: call failed. Reason = {}".format(e.message))


    def cancel_open_order(self,order_ID, type = 'Margin'):
        try:
            return  self.kite.cancel_order(variety = self.kite.VARIETY_REGULAR, order_id = '{}'.format(order_ID))
        except Exception as e:
            logger.write(logger.EXCEPTION,"cancel_order: call failed. Reason =  {}".format(e.message))


    def update_account_info(self, type = 'Margin'):
        cash = 0
        try:
            info =   self.kite.margins()
        except Exception as e:
            logger.write(logger.EXCEPTION,"update_account_info: margins() call failed.Reason =  {}".format(e.message))
            return [0, 0]
        cash = info["equity"]["net"]
        #First get short term positions quantity
        try:
            info =   self.kite.positions()
        except Exception as e:
            logger.write(logger.EXCEPTION,"update_account_info:positions() call failed.Reason =  {}".format(e.message))
            return [0, 0]
        asset_quantity = 0
        for asset in info:
            if asset["tradingsymbol"] == parameters.trading_symbol:
                asset_quantity = asset["quantity"]
                break
        #Get portfolio quantity
        try:
            info =   self.kite.holdings()
        except Exception as e:
            logger.write(logger.EXCEPTION,"update_account_info:holdings() call failed.Reason =  {}".format(e.message))
            return [0, 0]
        for asset in info:
            if asset["tradingsymbol"] == parameters.trading_symbol:
                asset_quantity += asset["quantity"]
                break

        return [asset_quantity, cash]
       
    def adjust_price_for_sell(self, price):
        return price - 0.05


    def adjust_price_for_buy(self, price):
        return price + 0.05

    def get_margin_health(self):
        pass

    def cancel_all_open_margin_orders(self):
        pass

    def get_current_margin_price(self):
        arg =  self.kite.EXCHANGE_NSE + ':' + parameters.trading_symbol
        try:
            response =   self.kite.ltp(arg)
        except Exception as e:
            logger.write(logger.EXCEPTION,"get_current_margin_price(: call failed. Reason =  {}".format(e.message))
            return None
        return response[arg]["last_price"]

    def get_minimum_quote_balance_required_for_trade(self):
        return 100

    def get_minimum_base_trade_quantity(self):
        return 1
  
    def get_historical_candle_stick(self, from_date, to_date, interval, instrument_token):
        logger.write(logger.OUTPUT,f' get_historical_candle_stick: Started downloading Candle sticks')
        historical_data = self.kite.historical_data(instrument_token, from_date, to_date, interval) 
        logger.write(logger.OUTPUT,f' get_historical_candle_stick: Done getting candle sticks of Instrument = {instrument_token} from {from_date} to {to_date} in Interval = {interval}')
        
        for kline in historical_data:
            self. save_klines_in_csv([kline['close'], kline['volume']]) 

    def save_klines_in_csv(self,kline):
        #logger.write(logger.OUTPUT,f' save_klines_in_csv: Saving Klines in CSV')
        file = open("klines_MA.csv", "at")
        cw = csv.writer(file,delimiter=',',quoting=csv.QUOTE_ALL)
        if cw is not None:
            cw.writerow(kline)

 
    def spot_to_margin_transfer(self,asset, amount):
        pass

    def margin_to_spot_transfer(self,asset,amount):
        pass

    def get_max_transfer_amount(self,asset):
        pass

    def create_loan(self,asset, amount):
        pass

    def repay_loan(self,asset, amount):
        pass

    def get_loan_request_status(self,asset, tx):
        pass

    def get_loan_repay_status(self,asset, tx):
        pass

    def get_max_loan_amount(self, asset):
        pass

    def get_quote_asset_balance(self):
        pass

    def get_base_asset_balance(self):
        pass


    













  























