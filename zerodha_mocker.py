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
import os

class ZerodhaMocker(Adapter):
    def __init__(self, api_key, secret_key):
        self.relay_price_to_strategy = None
        self.LTP = 0.0
        self.order_quantity = 0
        self.order_price  = 0.0


    def set_price_callback(self, price_callback_func):
        self.relay_price_to_strategy = price_callback_func


    def get_current_indian_time(self):
        pass


    def publish_LTP(self):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
            for file in files:
                if file.endswith(".csv"):
                    path = ROOT_DIR + '/' + file
                    #print(f'CSV Path = {path}')

                    with open(path, 'rt') as csvfile:
                        csv_reader = csv.reader(csvfile,delimiter=',',quoting=csv.QUOTE_ALL)
                        count = 0
                        for row in csv_reader:
                            if len(row) > 1:
                                count += 1
                                self.LTP = float(row[0])
                                self.relay_price_to_strategy(self.LTP)
                        print(f'###########################################  PUBLISH ENDED= {count} ###################################')
                

    def get_LTP(self):
        return self.get_current_margin_price()


    def create_client(self, api_key, secret_key):
        pass
    


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
        d_price = decimal.Decimal(price)
        last_digit = d_price.as_tuple().digits[-1]
        if last_digit % 5 != 0: #5 paisa tick
            logger.write(logger.ERROR,f'verify_tick_lot_size: Price not in tick size, last digit = {last_digit} need to adjust price')
            price = price - (last_digit / 100)
            logger.write(logger.ERROR,f'verify_tick_lot_size: Adjusted price = {price}')
        #No need of testing lot size for most of stocks as its 1
        return price, quantity
        

    def place_buy_limit_order(self, quantity, price, mode = 'Margin'):#ignore mode
        self.order_quantity = int(quantity)
        self.order_price = round(price, 2)
        self.order_price , self.order_quantity = self.verify_tick_lot_size(self.order_price, self.order_quantity)
        logger.write(logger.ERROR,"order_limit_buy:Symbol = {} quantity = {}, price = {}".format(parameters.trading_symbol, self.order_quantity,self.order_price))
        return 11111


    def correct_quantity(self, quantity, mode): 
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
        return quantity

    def place_sell_limit_order(self, quantity, price,  mode = 'Margin'):
        self.order_quantity = int(quantity)
        self.order_price = round(price,2)
        self.order_price , self.order_quantity = self.verify_tick_lot_size(self.order_price, self.order_quantity)   
        logger.write(logger.ERROR,"order_limit_buy:Symbol = {} quantity = {}, price = {}".format(parameters.trading_symbol, self.order_quantity,self.order_price))
        return 11111


    def get_order(self,order_ID, type = 'Margin'):
        data = [{'average_price': self.order_price, 'quantity': self.order_quantity}]
        return data


    def cancel_open_order(self,order_ID, type = 'Margin'):
        return 11111

    def update_account_info(self, type = 'Margin'):
        return [90000, 9000000]
       
    def adjust_price_for_sell(self, price):
        return price - 0.05


    def adjust_price_for_buy(self, price):
        return price + 0.05

    def get_margin_health(self):
        pass

    def cancel_all_open_margin_orders(self):
        pass

    def get_current_margin_price(self):
        return self.LTP

    def get_minimum_quote_balance_required_for_trade(self):
        return 100

    def get_minimum_base_trade_quantity(self):
        return 1
  
    def get_historical_candle_stick(self):
        from_date   = "2020-01-01"
        to_date     = "2020-02-01"
        interval    = "15minute"
        instrument_token = "779521"#"500112"# SBIN
        logger.write(logger.OUTPUT,f' get_historical_candle_stick: Started downloading Candle sticks')
        historical_data = self.kite.historical_data(instrument_token, from_date, to_date, interval) 
        logger.write(logger.OUTPUT,f' get_historical_candle_stick: Done getting candle sticks of Instrument = {instrument_token} from {from_date} to {to_date} in Interval = {interval}')
        
        for kline in historical_data:
            self. save_klines_in_csv([kline['close'], kline['volume']]) 

    def save_klines_in_csv(self,kline):
        logger.write(logger.OUTPUT,f' save_klines_in_csv: Saving Klines in CSV')
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


    













  























