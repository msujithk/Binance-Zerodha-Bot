class Adapter:
    def __int__(self):
        pass

    def publish_LTP(self):
        raise NotImplementedError("publish_LTP method not implemented")

    def set_price_callback(self):
        raise NotImplementedError("set_price_callback method not implemented")

    def create_order(self):
        raise NotImplementedError("create_order method not implemented")

    def adjust_price_for_sell(self, price) : 
        raise NotImplementedError("adjust_price_for_sell method not implemented")

    def adjust_price_for_buy(self, price):
        raise NotImplementedError("adjust_price_for_buy method not implemented")

    def get_klines(self):
        raise NotImplementedError("get_klines method not implemented")

    def correct_quantity(self, quanitiy, mode):
        raise NotImplementedError("correct_quantity method not implemented")    

    def place_buy_limit_order(self, quantity, price,mode = 'Margin'):
        raise  NotImplementedError("place_buy_limit_order  method not implemented")

    def place_sell_limit_order(self, quantity, price, mode = 'Margin'):
        raise NotImplementedError("place_sell_limit_order method not implemented")

    def get_order(self,order_ID, type = 'Margin'):
        raise NotImplementedError("get_order method not implemented")

    def cancel_open_order(self,order_ID, type = 'Margin'):
        raise NotImplementedError("cancel_open_order method not implemented")

    def update_account_info(self, type = 'Margin'):
        raise NotImplementedError("update_account_info method not implemented")

    def get_margin_health(self):
        raise NotImplementedError("get_margin_health method not implemented")

    def cancel_all_open_margin_orders(self):
        raise NotImplementedError("cancel_all_open_margin_orders method not implemented")

    def get_current_margin_price(self):
        raise NotImplementedError("get_current_margin_price method not implemented")
   
    def spot_to_margin_transfer(self,asset, amount):
        raise NotImplementedError("spot_to_margin_transfer method not implemented") 

    def margin_to_spot_transfer(self,asset,amount):
        raise NotImplementedError("margin_to_spot_transfer method not implemented")

    def get_max_transfer_amount(self,asset):
        raise NotImplementedError("get_max_transfer_amount method not implemented")

    def create_loan(self,asset, amount):
        raise NotImplementedError("create_loan method not implemented")

    def repay_loan(self,asset, amount):
        raise NotImplementedError("repay_loan method not implemented") 

    def get_loan_request_status(self,asset, tx):
        raise NotImplementedError(" get_loan_request_status method not implemented") 

    def get_loan_repay_status(self,asset, tx):
        raise NotImplementedError("get_loan_repay_status  method not implemented")

    def get_max_loan_amount(self, asset):
        raise NotImplementedError(" get_max_loan_amount method not implemented") 

    def get_quote_asset_balance(self):
        raise NotImplementedError(" get_quote_asset_balance method not implemented")

    def get_base_asset_balance(self):
        raise NotImplementedError("get_base_asset_balance method not implemented")

    def get_minimum_quote_balance_required_for_trade(self):
        raise NotImplementedError("get_minimum_quote_balance_required_for_trade method not implemented")

    def get_minimum_base_trade_quantity(self):
        raise NotImplementedError("get_minimum_base_trade_quantity method not  implemented")
    













  























