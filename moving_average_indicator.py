import numpy
import logger

class MovingAverage:
    '''''
    def __init__(self):
        #self.SMA = None
        #self.EMA = None
    '''''


    def get_SMA(self, price, period, SMA, slow_to_fast_sma):

        length = len(price)
        index = 0
        for interval in period:
          n = length -  interval
          cumsum = numpy.cumsum(price[int(n):], dtype= float)
          cumsum[interval:] = cumsum[interval:] - cumsum[:-interval]
          SMA[index] =  round((cumsum[interval - 1:] / float(interval))[0], 8)
          slow_to_fast_sma[index] = SMA[index]
          index += 1













    def get_EMA(self, price, period):
        '''''
        for interval in period:
            #[ avg' * (n-1) + x ] / n
            price = round(price,4)
            print("price = {}".format(price))
            weight = 1 / (interval)
            self.EMA = (self.SMA * (interval - 0.95361) + price) / interval #0.964
            self.EMA = round(self.EMA, 8)
            print("SMA = {}".format(self.EMA))
        '''''
        '''''
            weight = 1 / (day)

            if self.EMA is None:
              self.EMA = float(price) * weight + self.SMA * (1 - weight)
              print("self.EMA = {} :({} * {}) + ({}* {})".format(self.EMA,float(price), weight, self.SMA, (1 - weight)))
            
            else:
                self.EMA = float(price) * weight + self.EMA * (1 - weight)
                print ("self.EMA = {} : ({} * {}) + ({}* {})".format(self.EMA, float(price),weight,self.EMA,  (1 - weight)))
            
        '''''








