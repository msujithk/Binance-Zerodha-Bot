import logger
import uuid
class Order(dict):
    def __init__(self):
        self._order_ID = self.generate_order_ID()
        self.price = 0.0
        self.executed_quantity = 0.0
        self.pending_quantity = 0.0
        self.transactiontime = 0
        self.count = 1
        self.aggregated_orders = []

    @property
    def order_ID(self):
        return self._order_ID

    @order_ID.setter
    def order_ID(self, value):
        self._order_ID = value


    def generate_order_ID(self):
        return uuid.uuid4().int
        
    def add_order_to_aggregated_list(self, order_id):
        self.aggregated_orders.append(order_id)
        logger.write(logger.OUTPUT,f'add_order_to_aggregated_list: Order ID = {order_id} added to Aggregated order list')

    def remove_order_ID(self, order_id):
        if order_id in self.aggregated_orders:
            self.aggregated_orders.remove(order_id)
            logger.write(logger.OUTPUT,f'remove_ordeR_ID: Order ID = {order_id} removed from Aggregated order list')


    def update_order(self, order):
        raise NotImplementedError("update_order  method not implemented")

    def get_order_id(self, order):
        raise NotImplementedError("get_order_id  method not implemented")

    def update_executed_quantity(self, order, status):
        raise NotImplementedError("update_executed_quantity  method not implemented")

class BinanceOrder(Order):
    def get_order_id(self, order):
        return order["orderId"] 

    def update_executed_quantity(self, order, status):
        executed_quantity = status["executedQty"]
        order["executedQty"] = executed_quantity
        logger.write(logger.OUTPUT,f' update_order_status: executedQty = {executed_quantity}')
        return order
    
    def update_order(self, info):
        side = info["side"]
        self.price = ((self.price * self.executed_quantity) + (float(info["price"]) *  float(info['executedQty']))) / (self.executed_quantity +  float(info['executedQty']))
        ex_quantity = float(info['executedQty'])
        self.executed_quantity += ex_quantity
        logger.write(logger.OUTPUT, f'Update_order: self.executed_quantity = {self.executed_quantity}')
        if len(info['fills']) != 0:
            if side == "BUY":
                if info['fills'][0]['commissionAsset'] == 'BNB':
                    pass
                else:
                    commission = float(info['fills'][0]['commission'])
                    logger.write(logger.OUTPUT, f'Commission = {commission}')
                    self.executed_quantity = self.executed_quantity - commission
        else:
            if side == 'BUY':
                self.executed_quantity = self.executed_quantity - (self.executed_quantity * 0.001)
                logger.write(logger.OUTPUT, f'After deducting commision (0.1%): executed_quantity ={self.executed_quantity} ')


#def order_history( self, order_id) to get the order goins to various stages. get the status of the order from this
#def order_trades(  self, order_id)
class ZerodhaOrder(Order):
    def get_order_id(self, order):
        return order

    def update_executed_quantity(self, order, status):
        return status

    def update_order(self, order):
        info = order[0]
        self.price = ((self.price * self.executed_quantity) + (float(info["average_price"]) *  float(info["quantity"]))) / (self.executed_quantity +  float(info["quantity"]))
        self.executed_quantity = self.executed_quantity + float(info["quantity"])
        logger.write(logger.OUTPUT, f'Update_order: self.executed_quantity = {self.executed_quantity}')






