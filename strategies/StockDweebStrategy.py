import backtrader as bt
import pandas as pd

class StockDweebStrategy(bt.Strategy):
    # Configurable policy parameters
    params = (
        ('securities', pd.DataFrame()),
        ('period', 1)
    )

    def __init__(self):
        self.securities = self.params.securities
        self.current_buy_low = {}
        self.entry_prices = {}
        self.exited_positions = {}
        self.cut_losses = {}
        self.take_profit = {}
        self.current_take_profit = {}
        for index, row in self.securities.iterrows():
            self.current_buy_low[row['ticker']] = 0
            if isinstance(row['buy_zones'], float):
                self.entry_prices[row['ticker']] = [row['buy_zones']]
            elif isinstance(row['buy_zones'], str):
                self.entry_prices[row['ticker']] = [float(x) for x in row['buy_zones'].split('|')]
                self.entry_prices[row['ticker']].sort(reverse=True)
            self.exited_positions[row['ticker']] = False
            self.cut_losses[row['ticker']] = float(row['cut_losses'])
            self.current_take_profit[row['ticker']] = 0
            self.take_profit[row['ticker']] = [float(x) for x in row['take_profit'].split('|')]
            self.take_profit[row['ticker']].sort()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        for i, security in enumerate(self.datas):
            position_name = security.getwriterinfo()['Name']
            size = self.getposition(security).size
            #print(f'{self.datas[0].datetime.date(0)} {position_name} Close: {security.close[0]:.2f} - Entry: {self.entry_prices[position_name][self.current_buy_low[position_name]]:.2f}')
            if (self.exited_positions[position_name] is False) and self.cut_losses[position_name] < security.close[0] < \
                    self.entry_prices[position_name][self.current_buy_low[position_name]]:
                # A market order will be executed with the next available price.
                # In backtesting it will be the opening price of the next bar
                self.buy(data=security)
            elif size > 0 and self.exited_positions[position_name] is False and security.close[0] > self.take_profit[position_name][self.current_take_profit[position_name]]:
                if size != 0:
                    self.log(f'{self.datas[0].datetime.date(0)} {position_name}: Take Profit, closing position. Size: {size} {self.take_profit[position_name][self.current_take_profit[position_name]]:.2f}-{security.close[0]:.2f}')
                    self.close(security, size=size)
                self.exited_positions[position_name] = True
            elif size > 0 and self.exited_positions[position_name] is False and security.close[0] < self.cut_losses[position_name]:
                if size != 0:
                    self.log(f'{self.datas[0].datetime.date(0)} {position_name}: Stop Losses, closing position. Size: {size} {self.cut_losses[position_name]:.2f}-{security.close[0]:.2f}')
                    self.close(security, size=size)
                self.exited_positions[position_name] = True
            elif self.exited_positions[position_name]:
                continue
            else:
                continue
                #print(f'{self.datas[0].datetime.date(0)} {position_name} Entry: {self.entry_prices[position_name][self.current_buy_low[position_name]]} Current: {data.close[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{order.data._name} BUY EXECUTED, Price: {order.executed.price:.2f}  Cost: {order.executed.value:.2f}')
            else:
                self.log(f'{order.data._name} SELL EXECUTED, Price: {order.executed.price:.2f} Cost: {order.executed.value:.2f}')
        else:
            pass
            self.log(f'{order.data._name} Order: {order.Status[order.status]}')