from bot import Bot
from zerodha_adapter import ZerodhaAdapter
from zerodha_mocker import  ZerodhaMocker
class ZerodhaBot(Bot):
    def __init__(self,api_key, secret_key, mock):
        if mock:
             self.adapter =  ZerodhaMocker(api_key, secret_key)
        else:
            self.adapter = ZerodhaAdapter(api_key, secret_key)
        Bot.__init__(self, self.adapter)
        self.adapter.set_price_callback( self.break_out_strategy.process_message)


    def start_publish(self):
        self.adapter.publish_LTP()


