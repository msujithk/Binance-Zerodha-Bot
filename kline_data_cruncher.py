import logger
from moving_average_indicator import MovingAverage
import numpy as np

#import winsound

class KlineProcessor:

    def __init__(self,  round_off, period):
        self.crossover_price = 0.0
        self.dropped_packet_count = 0
        self.round_off = round_off
        self.moving_average = MovingAverage()
        self.closing_price = []
        self.period = period
        self.period.sort()
        self.SMA = []
        self.publish_klines = None
        self.fastest_sma_on_top = False
        self.slow_to_fast_sma = []
        for period in self.period:
            self.SMA.append(0.0)
            self.slow_to_fast_sma.append(0.0)

        self.cross_over =  [False, False]



    def process_message(self, msg):
        price = round(float(msg['k']['c']), self.round_off)
        if(msg['k']['x'] == True):
            #candle close
            self.publish_klines(price,msg['k'])
            self.closing_price[len(self.closing_price) - 1] = price
            self.closing_price.pop(0)
            self.closing_price.append(price)
        else:
            self.closing_price[len(self.closing_price) - 1] = price
            self.moving_average.get_SMA(self.closing_price, self.period, self.SMA, self.slow_to_fast_sma)
            self.SMA[0] -= (self.SMA[0] * 0.001)  #bring down the 0 SMA to be more aggressive
            self.SMA[2] += (self.SMA[2] * 0.001)
            self.SMA.sort()   #BUY = Ascending order
            self.fastest_sma_on_top = self.is_fastest_sma_on_top()

            index = 0
            for sma in self.SMA:
                print("SMA {}= {}".format(self.period[index], sma))
                index += 1


    def set_process_message_address(self, process_message):
        self.publish_klines = process_message



    def calculate_SMA(self,closing_price):
        self.closing_price = closing_price
        self.moving_average.get_SMA(self.closing_price, self.period, self.SMA, self.slow_to_fast_sma)
        self.SMA.sort()   #BUY = Ascending order


    def is_fastest_sma_on_top(self):
        if self.slow_to_fast_sma[0] == self.SMA[2]:
            return True
        else:
            return False

    def sma_crossed(self):
        if self.slow_to_fast_sma[0] < self.slow_to_fast_sma[2]: #if fastest crossed slowest
            return True
        else:
            return False




