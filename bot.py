from break_out_strategy import BreakOutStrategy
class Bot:
    def __init__(self, adapter):
        self.break_out_strategy = BreakOutStrategy(adapter)

    def start_publish(self):
        raise NotImplementedError("start_publish method not implemented")

