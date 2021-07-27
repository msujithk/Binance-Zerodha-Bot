import os
import re
import glob
import parameters
import time
import csv
from decimal import Decimal
import datetime
import threading
import logger
from adapter import Adapter
from order import BinanceOrder


class BinanceMocker(Adapter):
    def __init__(self, api_key, secret_key):
        self.relay_price_to_strategy = None
        self.account_balance = 0
        self.quote_asset = 0
        self.base_asset = 0
        self.base = parameters.base
        self.quote = parameters.quote
        self.exchange_pair = self.base + self.quote
        self.trade_type = parameters.trade_type
        self.quantity_round_off = 0
        self.LTP = 0
        self.order_status = dict()
        self.Total_quote  = 0

    def set_price_callback(self, price_callback_func):
        self.relay_price_to_strategy = price_callback_func


    def create_client(self):
        pass


    def get_symbol_info(self):
        if self.exchange_pair == 'BTCUSDT':
           value = Decimal(0.01).normalize()
           self.price_round_off = abs(value.as_tuple().exponent)
           value = Decimal(0.000001).normalize()
           self.quantity_round_off = abs(value.as_tuple().exponent)


    def create_socket(self):
        pass

    def update_account_info(self, type = 'Margin'):
        self.account_balance = 50000
        self.quote_asset = 2000
        self.base_asset = 2000
        return [self.base_asset, self.quote_asset]

    def adjust_price_for_sell(self, price):
        return  (price - (price * 0.0001))

    
    def adjust_price_for_buy(self, price):
        return (price + (price * 0.0001))

    def create_order(self):
        return BinanceOrder()

    def get_quote_asset_PE(self):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        pth = ROOT_DIR + '/Trade_Results.txt'
        if os.path.exists(pth) is False:
            return 0
        fd = open(pth, 'r')
        PE = 0
        for row in fd:
            if 'SHORT' in row:
                pass
            else:
                values = row.split(",")
                if len(values) >= 4:
                        num = round(float(values[3]), 2)
                        PE += num
        return PE


    def place_buy_limit_order(self, quantity, price):
        if self.exchange_pair == 'BTCUSDT':
            price = round(float(price), 4)
            quantity = round(float(quantity), 6)
            buy_order = {'symbol': 'BTCUSDT', 'orderId': 829841939, 'orderListId': -1, 'clientOrderId': 'U0xOf49xK3jg9wsfArUuKP', 'transactTime': 1574642340217,
            'price': '6877.88000000', 'origQty': '0.07269700', 'executedQty': '0.07269700', 'cummulativeQuoteQty': '500', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'fills': []}
            buy_order['price'] = price
            buy_order['origQty'] = quantity
            buy_order['executedQty'] = quantity
            self.order_status['executedQty'] = quantity
            self.order_status['cummulativeQuoteQty'] = quantity
            self.Total_quote += (price * quantity)
            exe = buy_order['executedQty']
            logger.write(logger.EXCEPTION, f'order_limit_buy: EXECUTED QTY = {exe}')
        return buy_order


    def place_sell_limit_order(self, quantity, price):
        if self.exchange_pair == 'BTCUSDT':
            price = round(float(price), 4)
            quantity = round(float(quantity), 6)
            sell_order = {'symbol': 'BTCUSDT', 'orderId': 828506556, 'orderListId': -1, 'clientOrderId': 'ldmttlWEFUT9HEdMtCwuV9', 'transactTime': 1574610840425
            , 'price': '7001.92000000', 'origQty': '0.06821400', 'executedQty': '0.06821400', 'cummulativeQuoteQty': '500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT',
            'side': 'SELL', 'fills': []}
            sell_order['price'] = price
            sell_order['origQty'] = quantity
            sell_order['executedQty'] = quantity
            self.order_status['executedQty'] = quantity
            self.order_status['cummulativeQuoteQty'] = quantity
            self.Total_quote += (price * quantity)
            exe =   sell_order['executedQty']
            logger.write(logger.EXCEPTION, f'order_limit_sell: EXECUTED QTY = {exe}')
        return sell_order

    def get_order(self, order_ID):
        exe = self.order_status['executedQty']
        logger.write(logger.EXCEPTION, f'Get Order Status : EXECUTED QTY = {exe}')
        return self.order_status


    def get_minimum_quote_balance_required_for_trade(self):
        return 12


    def get_minimum_base_trade_quantity(self):
        return 0.00015

    def cancel_open_order(self, order_ID,type = 'Margin'):
        pass

    def get_quote_asset_balance(self):
        return self.quote_asset

    def get_base_asset_balance(self):
        return self.base_asset

    def verify_quantity(self, quantity):
        return round(float(quantity), 6)

    def get_current_margin_price(self):
        return  self.LTP

    def correct_quantity(self, quantity, mode):
        return round(float(quantity), 6)

    def spot_to_margin_transfer(self, asset, amount):
        pass

    def margin_to_spot_transfer(self, asset, amount):
        pass

    def get_max_transfer_amount(self, asset):
        pass

    def create_loan(self, asset, amount):
        self.loan_amount = amount
        return {"tranId": 10001}

    def repay_loan(self, asset, amount):
        return {"tranId": 10001}

    def get_loan_request_status(self, asset, tx):
        resp = {"rows": [{"asset": "BNB", "principal": self.loan_amount, "timestamp": 1555056425000, "status": "CONFIRMED"}], "total": 1}
        return resp

    def get_loan_repay_status(self, asset, tx):
        resp = {"rows": [{"asset": "BNB", "principal": self.loan_amount, "timestamp": 1555056425000, "status": "CONFIRMED"}], "total": 1}
        return resp

    def get_max_loan_amount(self, asset):
        self.max_loan = "40000.0"
        return float(self.max_loan)

    def get_margin_health(self):
        return 1.9



    def cancel_all_open_margin_orders(self):
        pass


    def calculate_initial_MA(self):
        closing_price = []
        self.get_price_from_csv(closing_price, True)
        self.starting_price = closing_price[0]
        self.kline_processor.calculate_SMA(closing_price)
        


    def get_support_resistance_points(self):
        closing_price  = []
        self.get_price_from_csv(closing_price, False)
        #maxtab, mintab = peak_drop_detect.peakdet(closing_price,20)
        maxpoints  = peak_drop_detect.peakdetmax(maxtab,20)
        minpoints  = peak_drop_detect.peakdetmin(mintab,20)
        #maxtab.sort()
        #mintab.sort()
        print (maxtab)
        print (mintab)




    def get_price_from_csv(self, closing_price, sma):
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
                                if count < 100:
                                    closing_price.append(float(row[4]))
                                    count +=1
                                else:
                                    if sma is True:
                                        break
                                    else:
                                        closing_price.append(float(row[4]))
                                        


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
                                self.LTP = float(row[4])
                                self.relay_price_to_strategy(self.LTP)
                                
                        print(f'###########################################  PUBLISH ENDED = {count} ###################################')
            
