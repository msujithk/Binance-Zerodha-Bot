from binance_bot import BinanceBot 
from zerodha_bot import ZerodhaBot 
import sys
import parameters


ZERODHA     =               'zerodha'
BINANCE     =               'binance'
trade_bot   =               None #main global object


def main():
    mock = False
    if len(sys.argv) < 2:
        message='Please insert '+ZERODHA+' or '+BINANCE+' as second argument'
        sys.exit(message)    
    mode = sys.argv[1]
    if len(sys.argv) == 3:
        if sys.argv[2] == 'mocker':
            mock = True
        else:
            sys.exit('Thrid argument should be = mocker')
    print (f'Mode = {mode}, Initializing bot...')
    if mode == BINANCE :
        if parameters.binance_api_key != '' and parameters.binance_secret_key != '':
            pass
        else:
            sys.exit('Api key or Secret key is empty, Exiting ...')
        trade_bot = BinanceBot(parameters.binance_api_key, parameters.binance_secret_key, mock)
    elif mode == ZERODHA :
        if parameters.zerodha_api_key != '' and parameters.zerodha_secret_key != '':
            pass
        else:
            sys.exit('Api key or Secret key is empty, Exiting ...')
        trade_bot = ZerodhaBot(parameters.zerodha_api_key, parameters.zerodha_secret_key, mock)
    else:
        message = 'Please insert ' + ZERODHA + ' or ' + BINANCE + ' as second argument' 
        sys.exit(messsage)
    if trade_bot == None:
        sys.exit('Failed to Initilize Bot. Exiting .... ')
    print ('Starting main publish loop  ....')
    trade_bot.start_publish()
    #none of the statements will get executed below this while zerodha  bot is running



if __name__== "__main__":
    print ('Calling Main()')
    main()


