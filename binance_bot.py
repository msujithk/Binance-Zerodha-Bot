from bot import Bot
from binance_adapter import BinanceAdapter
from binance_mocker import  BinanceMocker
class BinanceBot(Bot):
    def __init__(self,api_key, secret_key, mock):
        if mock:
            self.adapter =  BinanceMocker(api_key, secret_key)
        else:
            self.adapter = BinanceAdapter(api_key, secret_key)
        Bot.__init__(self, self.adapter)
        self.adapter.set_price_callback(self.break_out_strategy.process_message)

    def start_publish(self):
        self.adapter.publish_LTP()







