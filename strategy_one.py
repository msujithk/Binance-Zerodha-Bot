from os import path
import logger
import json
import time
import sys
import parameters
import math
POSITIONS_JASON = 'positions.json'
LOOK_FOR_BREAKOUTS = 1
FLUSH_BREAK_OUT  = 3
MONITOR_PL = 4
LONG = 5
SHORT = 6
MONITOR_MARKET = 7
PRICE_ABOVE_BOUNCE_LEVEL = 8
PRICE_BELOW_REJECTION_LEVEL = 9
DOWNTREND = 10
UPTREND = 11
POP = 12
PUSH = 13    


class Position:
    def __init__(self, update_account_info, sell_asset, buy_asset, write_to_file):
        self.trade_quantity  = 25000
        self.negative_stop_loss = 0.0
        self.negative_stop_loss_percentage = 1
        self.final_stop_loss = 0.0
        self.rejection_price = 0.0
        self.bounce_price = 0.0
        self.margin_multiplier = 1
        self.volume = 10 #strength
        self.take_loan = 'NO'
        self.repeat = 'YES'
        self.state = 0
        self.bounced_already = False
        self.rejected_already = False
        self.loan_trans_ID = 0.0
        self.STOP_JASON_WRITE = 0#below this parameters wont be written to Jason
        self.order = None
        self.sell = sell_asset
        self.buy = buy_asset
        self.write_to_file = write_to_file
        self.update_account_info = update_account_info
        self.quantity = 0.0
        self.stop_loss = 0.0
        self.gain = 0.0

    def reset_params(self):
        self.bounced_already = False
        self.rejected_already = False
        self.loan_trans_ID = 0.0
        self.quantity = 0.0
        self.order = None
        self.state = 0
        self.stop_loss = 0.0
        self.gain = 0.0

    def borrow_loan(self):
        if self.take_loan == 'NO':
            return False
        elif self.take_loan == 'YES':
            return True

    def check_break_out(self, current_price, volume):
         raise NotImplementedError("check_break_out method not implemented")
    
    def get_trade_quantity(self, available_quantity):
        self.quantity =  self.trade_quantity
        '''
        if self.quantity == 0:
            self.quantity = available_quantity
            return self.quantity
        if available_quantity > self.quantity:
            return self.quantity
        else:
        '''
        return self.quantity

    

    def get_trade_type(self):
         raise NotImplementedError("get_trade_type method not implemented")


    def open_position(self, quantity):
        raise NotImplementedError("open_position method not implemented")

    def close_position(self):
        self.order = None

    def log_PE(self, placed_order, type):
        if placed_order != None:
            exc_quantity = placed_order.executed_quantity
            logger.write(logger.OUTPUT, f'log_PE: ExecutedQuantity = {exc_quantity}')
            sell_closing_pice = placed_order.price
            if type == LONG:
                self.write_to_file(self.order.price, sell_closing_pice , exc_quantity, type)
            else:
                self.write_to_file(sell_closing_pice, self.order.price, exc_quantity, type)
            self.order = None
        else:
            logger.write(logger.OUTPUT, f'log_PE: placed_order  is None')


    def get_gains(self, current_price):
        raise NotImplementedError("get_gains method not implemented")

    def check_negative_stoploss(self, current_price):
        raise NotImplementedError("check_negative_stoploss method not implemented")

    def break_even_price(self, current_price, trail):
        raise NotImplementedError("break_even_price method not implemented")

    def trailing_stoploss_price(self, current_price, percentage):
        raise NotImplementedError("trailing_stoploss_price method not implemented")

    def check_final_stoploss(self, current_price):
        raise NotImplementedError("check_final_stoploss method not implemeneted")

    def get_rejection_bounce_status(self, current_price):
        raise NotImplementedError("get_rejection_bounce_status  method not implemeneted")

    def get_USDT_equvivalent(self, quantity, current_price):
        raise NotImplementedError("get_rejection_bounce_status  method not implemeneted")

    def check_stop_loss_breach(self, stop_loss_price, current_price):
        raise NotImplementedError("check_stop_loss_breach  method not implemeneted")

    def good_to_open_position(self, current_price):
        raise NotImplementedError("good_to_open_position  method not implemeneted")

    def initial_trade_level(self, current_price):
        raise NotImplementedError("initial_trade_level  method not implemeneted")

    def check_price_gap(self , trade_level, current_price):
        raise NotImplementedError("check_price_gap  method not implemeneted")

    def update_trade_level(self, trade_level , current_price):
        raise NotImplementedError("update_trade_level  method not implemeneted")

    def check_trade_level(self,current_price,trade_level):
        raise NotImplementedError("check_trade_level  method not implemeneted")

class Long_Position(Position):
    def __init__(self,price, update_account_info, sell_asset, buy_asset, write_to_file, get_minimum_base_trade_quantity):
        self.price = price
        self.get_minimum_base_trade_quantity = get_minimum_base_trade_quantity
        super().__init__( update_account_info, sell_asset, buy_asset, write_to_file)

    def check_break_out(self, current_price,current_volume):
        status = False
        if self.price == 0:
            return status
        logger.write(logger.OUTPUT,f'check_break_out: Checking current_price = {current_price } < {self.price} self.price')
        if (((current_price - self.price) / self.price) * 100) > 2:#2
            self.price = current_price -  (0.002 * current_price)#current_price * 1.008#1.008#0.002
            logger.write(logger.OUTPUT,f'check_break_out: Market in uptrend, Setting self.price = {self.price}')
        if current_price < self.price:
            status = True
        return status

    def good_to_open_position(self, current_price):
        status = True
        if self.price == 0:
            status =  False
        if (self.price * 1.008) < current_price:
            logger.write(logger.OUTPUT, f'good_to_open_position: DONT OPEN POSITION :current price = {current_price} is way more [0.8 %] than self.price = {self.price}')
            status = False
        return status

    def check_negative_stoploss(self, current_price):
        status = False
        logger.write(logger.OUTPUT,f'check_negative_stoploss: stop loss price = {self.negative_stop_loss}')
        if current_price < self.negative_stop_loss:
            logger.write(logger.OUTPUT,f'check_negative_stoploss: STOPPED: current_price = {current_price} < {self.negative_stop_loss}: negative_stop_loss')
            status = True
        return status

    def trailing_stoploss_price(self, current_price, trail):
        return current_price - trail


    def check_final_stoploss(self, current_price):
        if self.final_stop_loss == 0.0:
            return 0
        if current_price >= self.final_stop_loss:
            logger.write(logger.OUTPUT,f'check_final_stoploss: Triggered: current_price >= {current_price} >= {self.final_stop_loss} final_stop_loss:: == STOP LOSS == {current_price - (current_price * 0.005)}')
            return current_price - (current_price * 0.008)
        else:
            return 0


    def did_price_bounce_back(self, current_price):
        status = False
        if current_price > self.bounce_price and self.state == 0:
            self.state = PRICE_ABOVE_BOUNCE_LEVEL
            logger.write(logger.OUTPUT, f'did_price_bounce_back: price went above bounce level = {self.bounce_price}')
        if self.state == PRICE_ABOVE_BOUNCE_LEVEL:
            if current_price <= self.bounce_price:
                self.state = 0
                status = True
        return status


    def get_trade_quantity(self):
        quote_quantity = self.update_account_info()[1]
        return  super().get_trade_quantity(quote_quantity)

    @staticmethod
    def get_available_amount_stat():
        return self.update_account_info()[1]

    def get_available_amount(self):
        return self.update_account_info()[1]

    def get_trade_type(self):
        return LONG

    def get_asset(self):
        return parameters.QUOTE

    def open_position(self, quantity, order):
        self.order = order
        placed_order = self.buy(quantity, self.order)
        if self.order.executed_quantity <  self.get_minimum_base_trade_quantity():
            logger.write(logger.OUTPUT,f'open_position: executed quantity = { self.order.executed_quantity} is less than < Minimum base traded quantity = { self.get_minimum_base_trade_quantity()}')
            return False
        buy_price =  self.order.price
        if self.negative_stop_loss_percentage != 0:
             self.negative_stop_loss =  buy_price - ((self.negative_stop_loss_percentage)/100 * buy_price)
        return True

    
    def close_position(self, order):
        if self.sell(self.order.executed_quantity,order,self.order.price) == False:
            logger.write(logger.OUTPUT,f'close_position: Sell not successful')
            #super().close_position()
            return False
        else:
            self.log_PE(order, LONG)
            super().close_position()
            logger.write(logger.OUTPUT,f'close_position: Successfully sold asset')
            return True

    def break_even_price(self,current_price, trail):
        return current_price - trail

    def get_rejection_bounce_status(self, current_price):
        status = False
        if self.bounce_price != 0:
            if self.bounced_already:
                status = True
            elif self.did_price_bounce_back(current_price):
                self.bounced_already = True
                status = True
        else:
                status = True
        return status


    def get_USDT_equvivalent(self,quantity,current_price):
        return quantity

    def get_gains(self, current_price):
        return (((current_price - self.order.price) / self.order.price) * 100) - 0.2

    def check_stop_loss_breach(self, stop_loss_price, current_price):
        status = False
        if current_price < stop_loss_price:
            status = True
        return status

    def initial_trade_level(self, current_price):
        return current_price + (0.005 * current_price)#0.005


    def check_trade_level(self,current_price,trade_level):
        status = False
        if current_price > trade_level:
            status= True
        return status

    def check_price_gap(self, trade_level, current_price):
        status = False
        logger.write(logger.OUTPUT,f' check_price_gap = { (trade_level - current_price) }')
        if (trade_level - current_price) > (0.005 * current_price):#0.005
            status = True
        return status

    def update_trade_level(self, trade_level , current_price):
        trade_level -= (trade_level - current_price) - (0.005 * current_price) #0.005
        return trade_level
        



class Short_Position(Position):
    def __init__(self,price, update_account_info, sell_asset, buy_asset, write_to_file):
        self.price = price
        super().__init__( update_account_info, sell_asset, buy_asset, write_to_file)


        def check_break_out(self,current_price,current_volume):
            status = False
            if self.price == 0:
                return status
            logger.write(logger.OUTPUT,f'check_break_out: Checking current_price = {current_price } > {self.price} self.price')
            if current_price > self.price:
                status = True
            return status

        def good_to_open_position(self, current_price):
            status = True
            if self.price == 0:
                status = False
            if (self.price * 1.008) > current_price:
                logger.write(logger.OUTPUT,f'good_to_open_position: DONT OPEN POSITION current price = {current_price} is way less [0.8 %] than self.price = {self.price}')
                status = False
            return status

        def check_negative_stoploss(self, current_price):
            status = False
            if current_price > self.negative_stop_loss:
                logger.write(logger.OUTPUT,f'check_negative_stoploss: STOPPED: current_price = {current_price} > {self.negative_stop_loss}: negative_stop_loss')
                status = True
            return status


        def trailing_stoploss_price(self, current_price, trail):
            return current_price + trail


        def check_final_stoploss(self, current_price):
            if self.final_stop_loss == 0.0:
                return 0
            if current_price <= self.final_stop_loss:
                logger.write(logger.OUTPUT,f'check_final_stoploss: Triggered: current_price <= {current_price} >= {self.final_stop_loss} final_stop_loss: == STOP LOSS == {current_price+(current_price*0.005)}')
                return current_price + (current_price * 0.008)
            else:
                return 0


        def did_price_reach_rejection_level(self, current_price):
            status = False
            if current_price < self.rejection_price and self.state == 0:
                self.state = PRICE_BELOW_REJECTION_LEVEL
                logger.write(logger.OUTPUT, f'did_price_reach_rejection_level: price went below rejection level = {self.rejection_price}')

            if self.state == PRICE_BELOW_REJECTION_LEVEL:
                if current_price >= self.rejection_price:
                    self.state = 0
                    status = True
            return status



        def get_trade_quantity(self):
            base_quantity = self.update_account_info()[0]
            return  super().get_trade_quantity(base_quantity)

        @staticmethod
        def get_available_amount_stat():
            return self.update_account_info()[0]

        def get_available_amount(self):
            return self.update_account_info()[0]

        def get_trade_type(self):
            return SHORT

        def get_asset(self):
            return parameters.BASE

        def open_position(self, quantity, order):
            self.order = order
            self.sell(quantity, self.order,0)
            if self.order.executed_quantity == 0:
                return False
            sell_price =  self.order.price
            if self.negative_stop_loss_percentage != 0:
                self.negative_stop_loss =  sell_price + ((self.negative_stop_loss_percentage)/100 * sell_price)

            logger.write(logger.OUTPUT,f'Open position Self.order = {self.order}')
            return True


        def close_position(self, order):
            placed_order = self.buy(self.order.executed_quantity, order)
            if order.executed_quantity == 0:
                super().close_position()
                return False
            else:
                self.log_PE(order, SHORT)
                super().close_position()
                return True


        def break_even_price(self, current_price, trail):
            return current_price + trail


        def get_rejection_bounce_status(self, current_price):
            status = False
            if self.rejection_price != 0:
                if self.rejected_already:
                    status = True
                elif self.did_price_reach_rejection_level(current_price):
                        self.rejected_already = True
                        status = True
            else:
                status = True
            return status


        def get_USDT_equvivalent(self,quantity,current_price):
            return quantity * current_price


        def get_gains(self, current_price):
            return (((self.order.price - current_price) / current_price) * 100) - 0.2


        def check_stop_loss_breach(self, stop_loss_price, current_price):
            status = False
            if current_price > stop_loss_price:
                status = True
            return status

        def initial_trade_level(self, current_price):
            return current_price - (0.003 * current_price)

        def check_trade_level(self,current_price, trade_level):
            status = False
            if current_price < trade_level:
                status = True
            return status

        def check_price_gap(self, trade_level, current_price):
            status = False
            logger.write(logger.OUTPUT,f' check_price_gap = { (current_price - trade_level) }')
            if (current_price - trade_level) > (0.003 * current_price):
                status = True
            return status


        def update_trade_level(self, trade_level , current_price):
            trade_level += (current_price - trade_level) - (0.003 * current_price)
            return trade_level




class BreakOutStrategy:
    def __init__(self,  adapter):
            self.adapter = adapter
            self.asset_info = [0,0]
            self.current_price = 0.0
            self.current_volume = 0.0
            self.positions = []
            self.pending_positions = []
            self.trade_level = 0.0
            self.position = None
            self.uptrend_count = 0
            self.downtrend_count = 0
            self.deduction = 0.008
            self.state_machine  = {
                MONITOR_MARKET: self.monitor_market,
                LOOK_FOR_BREAKOUTS:  self.look_for_breakouts,
                FLUSH_BREAK_OUT: self.flush_break_out,
                MONITOR_PL: self.monitor_PL
            }
            self.positions = self.create_positions()
            self.read_pending_orders()
            self.state = MONITOR_MARKET
            #self.sell_percentage = 2#1
            self.sell_zone = 1
            self.initial_burst = 2#2
            self.burst_price = 0
            self.stash = 400000


    def create_positions(self, consider_balance = True):
        long_price, short_price = self.get_next_long_short_price()
        positions = []
        position = self.create_long_position(long_price, consider_balance)
        if position == None:
            logger.write(logger.OUTPUT,f'POSITION = NONE')
        if position != None:
            positions.append(position)
        #position = self.create_short_position(short_price)
        #if position != None:
        #    positions.append(position)
        return positions


    def get_last_position(self, type):
        pos = None
        logger.write(logger.OUTPUT,f'get_last_position: Position = {self.pending_positions}')
        for position in self.pending_positions:
            if position.get_trade_type() == type:
                pos = position
        return pos           

    def get_next_long_short_price(self):
        long_price = 0
        short_price = 0
        long_price = self.current_price - (self.current_price *  self.deduction )#0.008
        short_price = 1.008 * self.current_price
        return self.round(long_price,7), self.round(short_price,7)


    def update_price_breach_level(self, trend):
        logger.write(logger.CONNECTION,f'Current Price = {self.current_price}') 
        count = self.get_order_count()
        if trend == DOWNTREND:
            self.deduction = self.round(self.deduction * 2, 3)#2
            if  self.deduction > 0.20:#0.20
                self.deduction  = 0.008
                if count > 6:
                    self.deduction  = 0.03#0.03  
            
            logger.write(logger.CONNECTION,f'@@@  DOWNTREND  -- Dedution = {self.deduction} pending len = {count} self.uptrend_count = {self.uptrend_count} self.downtrend_count = {self.downtrend_count}')
        elif trend == UPTREND:
            self.deduction = self.round((self.deduction - (self.deduction * 0.4)), 3)#0.4
            if self.deduction < 0.008:
                self.deduction = 0.008
            logger.write(logger.CONNECTION,f'@@@  UPTREND ++ Dedution = {self.deduction} Pendng len = {count}  self.uptrend_count = {self.uptrend_count} self.downtrend_count = {self.downtrend_count}') 
        else:
            logger.write(logger.CONNECTION,f'@@@  Trend = -1  -- Dedution = {self.deduction} pending len = {count}  self.uptrend_count = {self.uptrend_count} self.downtrend_ount = {self.downtrend_count}')



    def create_long_position(self, price, consider_balance):
        if consider_balance == True:
            if self.check_minimum_balance(LONG) == False:
                logger.write(logger.OUTPUT,f'MINIMUM BALANCE NONE')
                return None
        return Long_Position(price,  self.adapter.update_account_info, self.sell_asset, self.buy_asset,self.write_to_file,self.adapter.get_minimum_base_trade_quantity)

    def create_short_position(self, price):
        #if self. check_minimum_balance(LONG) == False:
        #    return None
        return Short_Position(price,  self.adapter.update_account_info, self.sell_asset, self.buy_asset,self.write_to_file)

    def process_message(self, price):
        self.current_price = float(price)
        logger.write(logger.OUTPUT,f'CURRENT_PRICE = {self.current_price}')
        self.state_machine.get(self.state, self.default)()
        self.check_pending_orders()
        self.monitor_margin_health()
        self.save_pending_orders()
        if self.burst_price > 0 and self.current_price > (self.burst_price * 1.008):
            logger.write(logger.OUTPUT,f'process_message: current price = { self.current_price } > {(self.burst_price * 1.008)} (self.burst_price * 1.008)')
            if self.initial_burst != 2:
                self.initial_burst = 2 - self.initial_burst 
                logger.write(logger.OUTPUT,f'process_message:  Initial Burst  = { self.initial_burst }')
            else:
                self.burst_price = 0
    

    def save_pending_orders(self):
        data_dict = dict()
        if len(self.pending_positions) > 0:
            dict_array_long = []
            dict_array_short = []
            for item in self.pending_positions:
                if item.order != None:
                    if item.get_trade_type() == LONG:
                        dict_array_long.append(item.order.__dict__)
                    else:
                        dict_array_short.append(item.order.__dict__)
            data_dict['LONG'] = dict_array_long
            data_dict['SHORT'] = dict_array_short
    
        with open('pending_orders.json', 'w') as fp:
            json.dump(data_dict, fp)
    



    def read_pending_orders(self):
        if path.exists('pending_orders.json') is False:
            return
        logger.write(logger.OUTPUT,"read_pending_orders: Reading Pending orders from Json")
        data_dict = dict()
        try:
            with open('pending_orders.json') as f:
                data_dict = json.load(f)
        except Exception as e:
            logger.write(logger.OUTPUT,"read_pending_orders: Exception occured while reading file")
            return
        if 'LONG' in data_dict.keys():
            dict_array_long = data_dict['LONG']
        else:
            dict_array_long =[]
        if 'SHORT' in data_dict.keys():
            dict_array_short = data_dict['SHORT']
        else:
             dict_array_short = []
        for item in dict_array_long:
            order = self.adapter.create_order()
            for attr in item:
                order.__setattr__(attr,item[attr])
            positions = self.create_positions()
            pos = positions[0]
            pos.order = order
            logger.write(logger.OUTPUT,f'read_pending_orders: ORDER price = {pos.order.price }')
            self.pending_positions.append(pos)
            for index in range(pos.order.count):
                self.update_trend(PUSH, 1)
        for item in dict_array_short:
            order = self.adapter.create_order()
            for attr in item:
                order.__setattr__(attr,item[attr])
            positions = self.create_positions()
            pos = positions[1]
            pos.order = order
            self.pending_positions.append(pos)
                



    def validate_inputs(self):
        for position in self.positions:
            if position.margin_multiplier < 1:
                 position.margin_multiplier = 1
            if position.margin_multiplier > 3:
                position.margin_multiplier = 1
            if position.volume < 50:
                position.volume = 100
            if position.take_loan != 'YES' and position.take_loan != 'NO':
                logger.write(logger.OUTPUT, f'validate_inputs: INVALID TAKE_LOAN PARAMETER in {position}')
                sys.exit()
            if position.repeat != 'YES' and position.repeat != 'NO':
                logger.write(logger.OUTPUT, f'validate_inputs: INVALID REPEAT  PARAMETER in {position}')
                sys.exit()

    def check_minimum_balance(self, type):
        status = True
        if type == LONG:
            available_amount =  self.adapter.update_account_info()[1]
        else:
            available_amount =  self.adapter.update_account_info()[0]
        if available_amount < self.adapter.get_minimum_quote_balance_required_for_trade():
            status = False
            logger.write(logger.OUTPUT, f'check_minimum_balance: gains : Out of balance to open new position available_amount = {available_amount}')
        return status


    def monitor_market(self):
        ###################################################################
        logger.write(logger.OUTPUT,f'monitor_markt: STASH = {self.stash}')
        if self.stash  <= 0:
            logger.write(logger.OUTPUT,f'monitor_markt: OUT OF BALANCE')
            return
        ###################################################################
        logger.write(logger.OUTPUT,f'monitor_market: Monitoring Market....current price = {self.current_price}')
        for position in self.positions:
            if position.price == 0.0:
                position.price = self.current_price
            self.position = position
            logger.write(logger.OUTPUT,f'monitor_market: Monitoring Market: Position = {position}')
            position.stop_loss = 0.0
            position.gain = 0.0
            if self.look_for_breakouts():
                self.state = LOOK_FOR_BREAKOUTS
                break


    def look_for_breakouts(self):
        position = self.position 
        if self.trade_level == 0:
            if position.check_break_out(self.current_price, self.current_volume):
                logger.write(logger.OUTPUT, f'look_for_breakouts: Broke First price level = : {position}')
                self.trade_level = self.round(position.initial_trade_level(self.current_price), 7)
                logger.write(logger.OUTPUT, f'look_for_breakouts: ## Trade_Level = {self.trade_level}')
                return True
        else:
            if  position.check_trade_level(self.current_price, self.trade_level):
                self.state = FLUSH_BREAK_OUT
                self.flush_break_out()
            elif position.check_price_gap(self.trade_level, self.current_price):
                self.trade_level = self.round(position.update_trade_level(self.trade_level , self.current_price), 7)
                logger.write(logger.OUTPUT, f'look_for_breakouts: ## Trade_Level = {self.trade_level}')
        return False

    def flush_break_out(self):
        self.trade_level = 0.0
        position = self.position
        logger.write(logger.OUTPUT, f'flush_break_out: Position = {position}')
        quantity = self.get_quantity(position)
        if quantity == 0:
            logger.write(logger.OUTPUT, f'flush_break_out: quantity == 0, setting state =  MONITOR_MARKET')
            self.closing_activities(position)
            self.positions = self.create_positions()
            self.state = MONITOR_MARKET
            return
        if self.good_to_buy() == False:
            logger.write(logger.OUTPUT, f'flush_break_out: Setting state =  MONITOR_MARKET and creating new positions')
            self.closing_activities(position)
            self.positions = self.create_positions()
            self.state = MONITOR_MARKET
            return
        if position.open_position(quantity,  self.adapter.create_order()):
            self.state = MONITOR_PL
            self.monitor_PL()      
        else:
            logger.write(logger.OUTPUT,f'flush_break_out: position could not be opened due to low or no buying, self.state = MONITORMARKET')
            if position.borrow_loan():
                self.settle_loan(position)
            self.positions.clear()            
            self.positions = self.create_positions()
            #self.reset_position(position)
            self.state = MONITOR_MARKET


    def get_quantity(self, position):
        #quantity = position.get_trade_quantity()
        count = self.get_order_count()
        if count <= 3 and self.initial_burst > 0:#2
            quantity = 50000
        elif count >= 13:#13
            quantity = 50000
        else:
            quantity = 500
        
        logger.write(logger.OUTPUT, f'get_quantity: Quantity = {quantity} Pending order count = {count}')
        available_amount = position.get_available_amount()
        logger.write(logger.OUTPUT, f'get_quantity: Available Amount = {available_amount}')
        if position.borrow_loan():
            status, loan_amount = self.take_loan(quantity * position.margin_multiplier, position)
            if status == True:
                quantity = loan_amount
                logger.write(logger.OUTPUT, f'get_quantity: Loan amount taken = {quantity}')
                quantity +=  position.trade_quantity
                logger.write(logger.OUTPUT, f'get_quantity: Loan + Available Amount  = {quantity}')
            else:
                logger.write(logger.OUTPUT, f'get_quantity: Loan borrow failed')
        return quantity



    def monitor_PL(self):
            position = self.position
            if position.order == None:
                return
            logger.write(logger.OUTPUT,f'monitor_PL:Gains: Position = { position} order.price = {position.order.price}')
            gains = position.get_gains(self.current_price)
            logger.write(logger.OUTPUT,f'monitor_PL:Gains = {gains}')
            if gains > 0.0: #positive gains
                if position.stop_loss != 0.0:
                    if position.check_stop_loss_breach(position.stop_loss, self.current_price):
                        logger.write(logger.OUTPUT,f'monitor_PL:Gains: Stop loss breached closing position')
                        count = self.get_order_count()
                        go_ahead_and_sell = True
                        if count >  self.sell_zone:
                            logger.write(logger.OUTPUT,f'monitor_PL:Gains: order count = {count} > {self.sell_zone} Sell Zone')
                            order_count = 0
                            for pos in self.pending_positions:
                                order_count += pos.order.count
                                if len(self.pending_positions) == 1:
                                    logger.write(logger.OUTPUT,f'monitor_PL:Gains: Pending pos length == 1')
                                    go_ahead_and_sell = True
                                    break
                                if order_count >= self.sell_zone: 
                                    logger.write(logger.OUTPUT,f'monitor_PL:Gains: order count = {order_count} >= {self.sell_zone} Sell Zone')
                                    if self.pending_positions[len(self.pending_positions) - 1].order.price ==  pos.order.price: #last pos = sell zone, so make sell_zone = last pos -1
                                        self.sell_zone = order_count - pos.order.count - 1
                                        if self.sell_zone < 0:
                                            self.sell_zone = 1
                                        logger.write(logger.OUTPUT,f'monitor_PL:Gains: Sell Zone = {self.sell_zone}')
                                        go_ahead_and_sell = False
                                        break
                                    if position.order.price >= pos.order.price:
                                        logger.write(logger.OUTPUT,f'monitor_PL:Gains: Aggregatd price =  { position.order.price } >= { pos.order.price} Sell Zone pos {self.sell_zone} price, GO AHEAD AND SELL')
                                        go_ahead_and_sell = True
                                        break
                                    else:
                                        logger.write(logger.OUTPUT,f'monitor_PL:Gains: Aggregatd price =  { position.order.price } < { pos.order.price} Sell Zone pos {self.sell_zone} price, DO NOT SELL')
                                        go_ahead_and_sell = False
                                        break
                        if go_ahead_and_sell != True:
                            return 
                        position.stop_loss = 0.0
                        position.gain = 0.0
                        logger.write(logger.CONNECTION,f'POP Order_count = {position.order.count} Sell Zone = {self.sell_zone}')
                        count = position.order.count
                        if position.close_position(self.adapter.create_order()):
                            #for index in range(count):
                            self.update_trend(POP, 1)
                            self.closing_activities(position)
                            self.positions = self.create_positions()
                            
                            self.state = MONITOR_MARKET
                        else:
                            logger.write(logger.OUTPUT, f'monitor_PL: gains : Sell was not successful , Pushing Position = {position.order.price} into pendng list')
                            self.pending_positions.append(position)
                            logger.write(logger.CONNECTION,f'PUSH Order_count = {position.order.count}')
                            for index in range(count):
                                self.update_trend(PUSH, 1)
                            self.positions = self.create_positions()
                            self.state = MONITOR_MARKET

                        return

                if position.gain < gains:  # set trailing stop loss
                    position.stop_loss = position.trailing_stoploss_price(self.current_price,(0.02 * self.current_price))#0.02
                    logger.write(logger.OUTPUT, f'monitor_PL: ###### Stop Loss = {position.stop_loss} ########## ')
                    position.gain = gains
                    count = self.get_order_count()
                    if gains > 3.6 and position.order.count == 1 and count < 4:#3.6,4
                        logger.write(logger.OUTPUT, f'monitor_PL: gains : {gains} > 3.6 and order count == 1 and count < 4, Add position')
                        self.add_new_position()
                    
            else: #negative gains
                position.stop_loss = 0.0
                position.gain = 0.0
                if position.check_negative_stoploss(self.current_price):
                    logger.write(logger.OUTPUT, f'monitor_PL: gains : {gains} < negatve stoploss, Pushing Position = {position.order.price} into pendng list')
                    self.pending_positions.append(position)
                    logger.write(logger.CONNECTION,f'PUSH Order_count = {position.order.count}')
                    for index in range(position.order.count):
                        self.update_trend(PUSH, 1)
                    self.positions = self.create_positions()
                    self.state = MONITOR_MARKET
                    return                    


    def check_pending_orders(self):
        index = 0
        pop = False
        logger.write(logger.OUTPUT, f'check_pending_orders: Length of pending list = {len(self.pending_positions)}')
        for index in range(len(self.pending_positions)- 1,-1,-1):
            position = self.pending_positions[index]
            gains = position.get_gains(self.current_price)
            if gains > 0.0: #positive gains
                logger.write(logger.OUTPUT, f' check_pending_orders: Positive gains = {gains} price = {position.order.price}')
                if self.state != MONITOR_PL:
                    #count = self.get_order_count()
                    #if count < 4:
                    #    logger.write(logger.OUTPUT, f' check_pending_orders: self.state != MONITOR_PL an pending order count = {count} < 4, ignorin fthe pending order')
                    #    break
                    logger.write(logger.OUTPUT, f' check_pending_orders: Positive gains = {gains} setting self.position = {position.order.price} and setting  self.state = MONITOR_PL')
                    self.position =  position
                    self.state = MONITOR_PL
                    pop = True
                    logger.write(logger.OUTPUT, f' check_pending_orders: Popping position price = {position.order.price} and quantity  = {position.order.executed_quantity}')
                elif self.state  ==  MONITOR_PL and self.position.get_trade_type() == position.get_trade_type():
                    logger.write(logger.OUTPUT, f' check_pending_orders: self.price  = {self.position.order.price}')
                    logger.write(logger.OUTPUT, f' check_pending_orders: pos.price = { position.order.price}') 
                    #average
                    self.position.order.price, self.position.order.executed_quantity, self.position.order.count =  self.average_position(self.position.order.price, self.position.order.executed_quantity, position.order.price,  position.order.executed_quantity, self.position.order.count, position.order.count)
                    pop = True
                    logger.write(logger.OUTPUT, f' check_pending_orders: Popping position price = {position.order.price} and quantity  = {position.order.executed_quantity}')
                    if self.position.order.count >= 2 and self.position.order.count < 7:#7
                        logger.write(logger.OUTPUT,f'check_pending_orders: order count = { self.position.order.count} which is >=2 and <5, market may be in uptrend.Start buying and aggregating asset')
                        self.add_new_position()
                break

        if pop is True:
            self.pending_positions.pop(index)
            self.update_trend(POP, 1)#0.3
        
        count = self.get_order_count() 
        '''
        if count <= 3 and self.state !=  MONITOR_PL:
            self.sell_zone = 1
        elif count > 6 and count <= 13  and self.state !=  MONITOR_PL:
            self.sell_zone = 3
        elif count > 13 and count <= 17  and self.state !=  MONITOR_PL:
            self.sell_zone = 6
        elif count > 17 and  self.state !=  MONITOR_PL:
            self.sell_zone = 12
        '''
        logger.write(logger.OUTPUT,f'check_pending_orders: Sell Zone = {self.sell_zone}')
        pos = []
        deduct_burst =  False
        if count > 6  and len(self.pending_positions) > 2:#6
            logger.write(logger.OUTPUT,f'check_pending_orders: Order Count = {count} > 6')
            for num in range (3):
                if num < len(self.pending_positions):
                    sell_quantity = 0
                    order_count = self.pending_positions[num].order.count
                    exc_quantity = self.pending_positions[num].order.executed_quantity# / order_count
                    quote = exc_quantity * self.pending_positions[num].order.price
                    if quote > 40000:
                        logger.write(logger.OUTPUT, f' check_pending_orders: quote = {quote} > 40000')
                        if self.burst_price == 0:
                            self.burst_price =  self.pending_positions[num].order.price
                            logger.write(logger.OUTPUT, f' check_pending_orders: Burst Price = {self.burst_price}')
                        deduct_burst =  True
                        position =  self.pending_positions[num]   
                        #if self.sell_percentage < 1:#!=
                        #    logger.write(logger.OUTPUT, f' check_pending_orders: Sell percentage = {self.sell_percentage}')
                        #    sell_quantity = int(self.pending_positions[num].order.executed_quantity * self.sell_percentage)
                        #    self.pending_positions[num].order.executed_quantity = self.pending_positions[num].order.executed_quantity -  sell_quantity
                        #    if self.pending_positions[num].order.count > 1:
                        #        self.pending_positions[num].order.count = int(self.pending_positions[num].order.count * (1 - self.sell_percentage))
                        #        if self.pending_positions[num].order.count < 1:
                        #                self.pending_positions[num].order.count = 1
                        #    logger.write(logger.OUTPUT, f' check_pending_orders: Quantity to be left unsold = {self.pending_positions[num].order.executed_quantity}, Quantity to be sold = { sell_quantity}')
                        #    self.positions = self.create_positions(False)
                        #    if len(self.positions) == 0:
                        #        logger.write(logger.OUTPUT, f' check_pending_orders: couldnt not create new position')
                        #        return
                        #    position = self.positions[0]
                        #    position.order = self.adapter.create_order()
                        #    position.order.price = self.pending_positions[num].order.price
                        #    position.order.executed_quantity = sell_quantity
                        #    if self.pending_positions[num].order.count > 1:
                        #        position.order.count = int(self.pending_positions[num].order.count * self.sell_percentage)
                        #        if position.order.count < 1:
                        #            position.order.count = 1
                            
                        order_count = position.order.count
                        price = position.order.price
                        executed_quantity = position.order.executed_quantity
                        if position.close_position(self.adapter.create_order()):
                            self.closing_activities(position)
                            self.positions = self.create_positions()
                            #if self.sell_percentage >= 1:#==1
                            logger.write(logger.OUTPUT, f' check_pending_orders: Popping position price = {price} and quantity  = {executed_quantity}')
                            self.pending_positions.pop(num)
                            for index in range(order_count):
                                self.update_trend(POP, 1)
                            #self.sell_percentage =  self.sell_percentage - 0.25#0.25
                            #if self.sell_percentage < 0.50:#0.25
                            #    self.sell_percentage = 2#1
                            #logger.write(logger.OUTPUT, f' check_pending_orders: sell percentage = {self.sell_percentage}')
                        else:
                            logger.write(logger.OUTPUT, f' check_pending_orders: Sell order Failed,')
                            #self.pending_positions[num].order.executed_quantity = self.pending_positions[num].order.executed_quantity +  sell_quantity
                else:
                     logger.write(logger.OUTPUT, f' check_pending_orders: index  = { num} < {len(self.pending_positions)} Pending list length, ignoring  rest or orders')
            if deduct_burst:
                if self.initial_burst > 0:
                    self.initial_burst -= 1
                    logger.write(logger.OUTPUT, f' check_pending_orders: Initial Burst = {self.initial_burst}')                 
        if count > 13 and self.initial_burst == 0:
            self.initial_burst = 2
            self.burst_price = 0
            logger.write(logger.OUTPUT, f' check_pending_orders: order count > 13 and initial_burst == 0, Setting Initial Burst = {self.initial_burst} and Burst Price = {self.burst_price}')

   
    def get_order_count (self):
        count = 0
        for pos in self.pending_positions:
            count = count + pos.order.count
        #logger.write(logger.OUTPUT, f'get_order_count: Order count = {count}')
        return count

    def add_new_position(self):
            #if self.good_to_buy() == False:
            #    return
            logger.write(logger.OUTPUT,f' add_new_position: Adding new position')
            ###################################################################
            logger.write(logger.OUTPUT,f'monitor_markt: STASH = {self.stash}')
            if self.stash  <= 0:
                logger.write(logger.OUTPUT,f'monitor_markt: OUT OF BALANCE')
                return
            ###################################################################
            self.positions = self.create_positions()
            if len(self.positions) == 0:
                logger.write(logger.OUTPUT,f'add_new_position: OUT OF BALANCE') 
                return

            position = self.positions[0]
            quantity = self.get_quantity(position)
            if quantity == 0:
                logger.write(logger.OUTPUT, f'add_new_position: quantity == 0')
                return
            if position.open_position(quantity, self.adapter.create_order()):
                #average
                self.position.order.price, self.position.order.executed_quantity, self.position.order.count =  self.average_position(self.position.order.price, self.position.order.executed_quantity, position.order.price,  position.order.executed_quantity, self.position.order.count, position.order.count)
            else:
                logger.write(logger.OUTPUT,f'add_new_position: position could not be opened')
                if position.borrow_loan():
                    self.settle_loan(position)


    def average_position(self,price1, quantity1, price2, quantity2, count1, count2):
        logger.write(logger.OUTPUT, f'average_position: MERGING self.position.order.price = {price1}  self.position.order.executed_quantity = {quantity1} (position.order.price = {price2} position.order.executed_quantity = {quantity2}')
        price =  ((price1 * quantity1) + (price2 * quantity2)) /(quantity1 + quantity2)
        quantity = quantity1 +  quantity2
        count = count1 + count2
        logger.write(logger.OUTPUT, f' average_position: Aggregated price = {price} Quantity  = {quantity} count = {count}')
        return [price, quantity, count]


    def update_trend(self, type, delta):
        trend = -1
        if type == POP:
            self.downtrend_count -= 0.3
            if self.downtrend_count < 0:
                self.downtrend_count = 0
            self.uptrend_count += delta
            if self.uptrend_count > 2.0:
                logger.write(logger.OUTPUT, f' check_uprend_count = {self.uptrend_count} > 2') 
                self.uptrend_count = 0
                self.downtrend_count = 0
                trend = UPTREND
                logger.write(logger.OUTPUT, f' check_pending_orders: TREND = UPTREND')
        elif type == PUSH:
            self.uptrend_count -= 1
            if self.uptrend_count < 0:
                self.uptrend_count = 0
            self.downtrend_count += delta
            if self.downtrend_count > 2.0:
                logger.write(logger.OUTPUT, f' check_pending_orders:downtrend_count = {self.downtrend_count} > 2')
                self.downtrend_count = 0
                self.uptrend_count = 0 
                trend = DOWNTREND
                logger.write(logger.OUTPUT, f' check_pending_orders: TREND = DOWNTREND')
        self.downtrend_count = self.round(self.downtrend_count,2)
        self.uptrend_count = self.round(self.uptrend_count,2)
        self.update_price_breach_level(trend)    


    def good_to_buy(self):
        if self.current_price == 0:
            return False
        if len(self.pending_positions) == 0:
            return True
        if (self.current_price * 1.008) >= self.pending_positions[len(self.pending_positions) - 1].order.price:
            logger.write(logger.OUTPUT, f' NOT good to buy, self,current_price * 1.008 = {(self.current_price * 1.008)} >= {self.pending_positions[len(self.pending_positions) - 1].order.price} Last bough position price')
            return False
        else:
            return True


    def closing_activities(self, position):
        if position.borrow_loan(): #keep in same order
            self.settle_loan(position)
        # if position.repeat == 'NO':
        #     self.remove_position(position)
        # elif position.repeat == 'YES':
        #     self.reset_position(position)
    


    def remove_position(self, position):
        logger.write(logger.OUTPUT,f'remove_position: Removing position = {position}')
        for index, pos in enumerate(self.positions):
            if pos.price == position.price:
                self.positions.pop(index)
                break


    def reset_position(self, position):
        logger.write(logger.OUTPUT,f'reset_position: Resetting position')
        #OR SIMPLY CLEAR THE LIST AND Re-READ IT
        self.remove_position(position)
        position.reset_params()
        self.positions.append(position)
        


    def sell_asset(self, quantity, order, original_price):
        # sell asset
        result = False
        original_qty = self.adapter.correct_quantity(quantity, 'SELL')
        quantity_sell = original_qty
        price = self.current_price
        sell_price = self.adapter.adjust_price_for_sell(price)  # place a sell order below 0.01%
        if quantity_sell != 0:
            attempt = 0
            while True:
                result = False
                available_quantity =  self.adapter.update_account_info()[0]
                if quantity_sell > available_quantity:
                    quantity_sell = available_quantity
                    logger.write(logger.OUTPUT, f'sell_asset: Sell quantity  = {quantity_sell} > Available Quantity {available_quantity}, Setting quantity_sell = {available_quantity}')
                if quantity_sell < self.adapter.get_minimum_base_trade_quantity():
                    logger.write(logger.OUTPUT, f'sell_asset: Sell qantity = {quantity_sell} is  less than 15 USD')
                    result = True  
                    break
                logger.write(logger.OUTPUT, "sell_asset: selling asset quantity_sell = {}  at price = {}".format(quantity_sell, sell_price))
                logger.write(logger.ERROR, "sell_asset: selling asset quantity_sell = {}  at price = {}".format(quantity_sell, sell_price))
                exc_order = None
                exc_order =  self.adapter.place_sell_limit_order(quantity_sell, sell_price)
                if exc_order == None:
                    logger.write(logger.ERROR, 'sell_asset: exc_order == None, Breaking while loop')
                    break
                #time.sleep(15)
                status = self.adapter.get_order(order.get_order_id(exc_order))
                exc_order =  order.update_executed_quantity(exc_order, status)
                order.update_order(exc_order)
                pending_quantity = self.get_pending_quantity(order, original_qty, order.get_order_id(exc_order))
                ###################################################################
                self.stash = self.stash + (quantity_sell *  sell_price)
                logger.write(logger.TEST,f'self.stash = {self.stash}')
                logger.write(logger.OUTPUT,f'sell_asset: STASH = {self.stash}')
                ##################################################################
                if pending_quantity != 0:
                    quantity_sell = pending_quantity
                    attempt += 1
                    logger.write(logger.OUTPUT,f'sell_asset: Partially Filled or Sell was not successful, trying again attempt = {attempt}') 
                    if attempt > 15:
                        logger.write(logger.OUTPUT,f'sell_asset:Attempt = {attemp} > 15, breaking while loop') 
                        break
                    price =  self.adapter.get_current_margin_price()
                    logger.write(logger.OUTPUT,f'sell_asset: current price = {price}')
                    if attempt < 10:
                        sell_price = price
                    elif attempt > 10:
                        sell_price = self.adapter.adjust_price_for_sell(price)
                        if  original_price != 0 and sell_price < original_price:
                            logger.write(logger.OUTPUT, f'sell_asset: sell_price = {sell_price} is less than the original buy  price = {original_price}, Abandoning sell')
                            break

                else:
                    result = True
                    break
        return result    


    def get_pending_quantity(self, order, org_quantity, orderID):
        logger.write(logger.ERROR, "get_pending_quantity: Sell ORDER = {}".format(order))
        exc_quantity = order.executed_quantity 
        logger.write(logger.ERROR, "get_pending_quantity: Excuted quantity = {}".format(exc_quantity))
        if exc_quantity < (org_quantity * 0.98):
            logger.write(logger.OUTPUT, "get_pending_quantity: Partially filled, Cancelling Order")
            self.cancel_order(orderID)
            #time.sleep(10)
            logger.write(logger.OUTPUT, f'get_pending_quantity: Getting Pending quantity')
            quantity = org_quantity  - exc_quantity
            logger.write(logger.OUTPUT,f'get_pending_quantity: pending quantity = {quantity}')
            return quantity
        return 0


    def buy_asset(self, quantity, order):
        ######################################3
        if quantity > self.stash:
            quantity = self.stash
            self.stash = 0
        else:
            self.stash = self.stash - quantity
            if self.stash < 0:
                self.stash = 0
        logger.write(logger.TEST,f'self.stash = {self.stash}')
        logger.write(logger.OUTPUT,f'buy_asset: STASH  = {self.stash}')
        ######################################
        # buy the asset
        buy_price = self.adapter.adjust_price_for_buy(self.current_price) # place a sell order below 0.01%
        buy_quantity =  quantity / buy_price
        original_price = buy_price
        buy_quantity = self.adapter.correct_quantity(buy_quantity, 'BUY') 
        original_qty  = buy_quantity
        attempt = 0
        logger.write(logger.OUTPUT, "buy_asset:Buy asset  quantity_buy = {} at  price = {}".format(buy_quantity, buy_price))
        
        while True:
            exc_order = None
            logger.write(logger.ERROR, "buy_asset:Buy asset  quantity_buy = {} at  price = {}".format(buy_quantity, buy_price))
            exc_order =   self.adapter.place_buy_limit_order(buy_quantity, buy_price)
            if exc_order == None:
                logger.write(logger.ERROR, 'buy_asset: exc_order == None, Breaking while loop')
                break
            #time.sleep(15)
            status = self.adapter.get_order(order.get_order_id(exc_order))
            exc_order =  order.update_executed_quantity(exc_order, status)
            order.update_order(exc_order)
            pending_quantity = self.get_pending_quantity(order, original_qty , order.get_order_id(exc_order))
            
            if pending_quantity != 0:
                buy_quantity = pending_quantity
                if buy_quantity < self.adapter.get_minimum_base_trade_quantity():
                    logger.write(logger.OUTPUT,f'buy_asset: PARTIALLY FILLED.  quantity less than 15 USD quantity = {buy_quantity}')
                    break
                attempt += 1
                logger.write(logger.OUTPUT,f'buy_asset: Buy not successful, trying again attempt = {attempt}')
                if attempt > 15:
                    break
                price =  self.adapter.get_current_margin_price()#self.current_price 
                if attempt < 10:
                    buy_price = price
                elif attempt > 10:
                    buy_price =  self.adapter.adjust_price_for_buy(price)
                    if buy_price < original_price +  (original_price * 0.008):
                        logger.write(logger.OUTPUT,f'buy_asset: buy_price = {buy_price} is far less than the original price = {original_price}, Abandoning Buy')
                        break
            else:
                break

        return order


    def default(self):
        pass

    
    def cancel_order(self,order_ID):
        if order_ID != 0:
            logger.write(logger.OUTPUT, "cancel_order: Cancelling order = {}".format(order_ID))
            self.adapter.cancel_open_order(order_ID)
             


    def check(self, price1, price2):
        return (((price1 - price2) / price2) * 100) - 0.2 # 0.2% is the exchange fee, both side\


    def monitor_margin_health(self):
        health_meter =  self.adapter.get_margin_health()
        if health_meter == None: #not implemented in the adapater
            return True
        logger.write(logger.OUTPUT,f'Health Meter = {health_meter}')
        if health_meter < 1.15:
            logger.write(logger.OUTPUT,f' ALEART ALEART HEalth meter: {health_meter} < 1.15, Settling loan')
            self.adapter.cancel_all_open_margin_orders()
            self.arrange_principal_amount()
            sys.exit('ALEART ALEART HEalth meter: {health_meter} < 1.15')
        return True


    def arrange_principal_amount(self):
        if self.position is None:
            return
        asset = self.position.get_asset()
        loan_amount = self.get_principle_amount(asset, self.position.loan_trans_ID)
        if self.state ==  MONITOR_PL:
            if self.position.close_position(self.adapter.create_order()):
                self.closing_activities(self.position)
                self.state = MONITOR_MARKET
                return

    
    def get_principle_amount(self, asset,loan_trans_ID):
        resp = self.adapter.get_loan_request_status(asset, loan_trans_ID)
        return self.round(float(resp['rows'][0]['principal']),4)



    def settle_loan(self, position):
        asset = position.get_asset()
        while True:    
            if position.loan_trans_ID == 0:
                logger.write(logger.OUTPUT,f'settle_loan: LOAN ID == 0') 
                break      
            loan_amount = self.get_principle_amount(asset, position.loan_trans_ID)
            available_amount = position.get_available_amount()
            if loan_amount > available_amount:
                loan_amount = available_amount
            resp = self.adapter.repay_loan(asset, loan_amount)
            trans_id =  f'{resp["tranId"]}'
            #time.sleep(10)
            resp = self.adapter.get_loan_repay_status(asset, trans_id)
            if len(resp['rows']) != 0:
                if resp['rows'][0]['status'] == 'CONFIRMED':
                    logger.write(logger.OUTPUT,'settle_loan: Loan successfully settled')
                    position.loan_trans_ID = 0
                    break
                else:
                    logger.write(logger.OUTPUT,'settle_loan:Lone Repay Failed, Trying again')
                    #time.sleep(10)


    def take_loan(self, loan_amount, position):
        asset_type  = position.get_asset()
        status = False
        max_amount =  self.adapter.get_max_loan_amount(asset_type)
        if max_amount == 0:
            position.loan_trans_ID
            logger.write(logger.OUTPUT, f'take_loan: max_amount Loan amount = {max_amount}')
            return True
        loan_amount = self.round(loan_amount, 4)
        if loan_amount > max_amount:
            logger.write(logger.OUTPUT,f'take_loan: Loan amount = {loan_amount}  is greator than max amount = {max_amount}')
            loan_amount = (max_amount - (max_amount * 0.005))
        resp = self.adapter.create_loan(asset_type, loan_amount)
        position.loan_trans_ID = f'{resp["tranId"]}'
        #time.sleep(10)
        resp = self.adapter.get_loan_request_status(asset_type, position.loan_trans_ID)
        if len(resp['rows']) != 0:
            if resp['rows'][0]['status'] == 'CONFIRMED':
                loan_amount = float(resp['rows'][0]['principal'])
                logger.write(logger.OUTPUT, f'take_loan: Loan amount = {loan_amount}')
                status = True
        if self.monitor_margin_health() != True:
            status = False
            return status, 0
        return status, loan_amount

    def round(self, value, round_off):
        i = 0
        multiply = 1
        divisor = 10.0
        while i < round_off:
            divisor = divisor * multiply
            multiply = 10
            i += 1
        return math.floor(value * divisor) / divisor

    def write_to_file(self, buy_price, sell_price, quantity, type):
        file = open("Trade_Results.txt","at")
        profit = 0.0
        if type == LONG:
            logger.write(logger.OUTPUT, f'write_to_file : buy_price = {buy_price}  sell_price = {sell_price} quantity = {quantity}')
            sellside = (sell_price * quantity) - (0.002 * (sell_price * quantity))
            profit = sellside - (buy_price *  quantity)
            rowstr = "{}".format(time.time())+ ',' + "{}".format(buy_price) + ',' + "{}".format(sell_price)+ ',' + "{}".format(profit)  + "\n"
        elif type == SHORT:
            sellside = (sell_price * quantity) - (0.002 * (sell_price * quantity))
            profit = sellside - (buy_price *  quantity)
            rowstr = "{}".format(time.time())+ ',' + "{}".format(sell_price) + ',' + "{}".format(buy_price)+ ',' + "SHORT PROFIT" + ',' +  "{}".format(profit) + "\n"
        file.write(rowstr)
        file.close()


