import os
import glob
import json
from decimal import Decimal
total_USDT_gain = 0.0
total_row_count = 0.0
class trade_result:
    def __init__(self):
        self.asset_gain = dict()








def get_pending_order_value():
    print("read_pending_orders: Reading Pending orders from Json")
    data_dict = dict()
    cwd = os.getcwd()
    #fileDir = os.path.dirname(os.path.realpath('__file__'))
    #filename = os.path.join(cwd, 'DATA/pending_orders.json ')
    #print(filename)
    try:
        with open('DATA/pending_orders.json') as f:
            data_dict = json.load(f)
    except IOError as e:
        #print(' pending_orders.Jason could not be opend' + e.message)
        return
    print ('++++++++++++++++++++++++++++++++++++++++   USDT++++++++++++++++++++++++++++++++++++++')
    if "LONG" in data_dict:
        dict_array = data_dict["LONG"]
        total_quantity = 0.0
        averaged_price = 0.0
        total_quote = 0.0
        #last_price = 0.0
        for item in dict_array:
            price = float(item["price"])
            quantity = float(item["executed_quantity"])
            #quote_qty = float(item["quote_quantity"])
            #total_quote += quote_qty
            if averaged_price == 0:
                averaged_price = price
            else:
                averaged_price = ((averaged_price * total_quantity) + (price * quantity)) / (total_quantity + quantity)
                total_quantity += quantity
        print(f'Total Quantity =  {total_quantity}')
        print(f'Average Price = {averaged_price}')
        #print(f'Total Quote = { total_quote}')










def calculate_gains(path):
    usd_gain = 0
    row_count = 0
    fd = open(path, 'r')
    for row in fd:
        if 'SHORT' in row:
            values = row.split(",")
            if len(values) >= 7:
                num = round(float(values[5]), 2)
                usd_gain += num
        else:
            values = row.split(",")
            if len(values) >= 5:
                num = round(float(values[4]), 2)
                usd_gain += num
        row_count += 1
    global  total_USDT_gain
    global total_row_count
    total_USDT_gain += usd_gain
    total_row_count = row_count

    fd.close()
    



ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

print ("Finding Directory")

path =  ROOT_DIR +  '/Trade_Results.txt'
print(path)
calculate_gains(path)
get_pending_order_value()

print(f'Total USD gained = {total_USDT_gain } USD')

#comission  = (((total_row_count * 2) *10000)* 0.0015) * 0.20
#print(f'commision as per 10000 USD per trade at 0.15% = {comission}')

#print(f'TOTAL PROFIT = {total_USDT_gain + comission}')
