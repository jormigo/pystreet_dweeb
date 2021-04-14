import matplotlib
matplotlib.use('agg')

import sys
import backtrader as bt
import backtrader.feeds as btfeeds
import yfinance
import joblib
from strategies.StockDweebStrategy import StockDweebStrategy
from datetime import datetime as dt
import pandas as pd
import streamlit as st

cash = 25_000
MEMORY = joblib.Memory(location='cache/')

st.set_page_config(page_title='PyStreet Dweeb')


@MEMORY.cache
def get_data(ticker, start, end):
    data = yfinance.download(ticker, start, end)
    data.columns = [col.lower() for col in data.columns]
    return data


def main():
    dates = [
        '2021-04-05',
        '2021-04-10'
    ]
    for date in dates:
        starting_date = date
        df = pd.read_csv(f'./data/stockdweebs/weekly_10/{starting_date}.csv', index_col=['date'], parse_dates=True)

        start = starting_date
        end = dt.today().strftime('%Y-%m-%d')

        if df is None:
            print('Unable to retrieve weekly picks')
            sys.exit()

        for ticker in df['ticker']:
            with st.beta_expander(ticker, expanded=True):
                try:
                    data = get_data(ticker, start, end)
                    st.write(data.head())

                    if not df[['buy_zones', 'take_profit', 'cut_losses']].isna().values.any():
                        if not df[['buy_now']].isna().values.any():
                            entry_price = data.loc[starting_date, ['close']][0]
                            x = df['ticker'] == ticker
                            df.loc[x, ['buy_zones']] = df[x]['buy_zones'] + '|' + str(entry_price)

                        cerebro = bt.Cerebro()
                        cerebro.broker.setcash(cash)
                        datafeed = btfeeds.PandasData(dataname=data)
                        cerebro.adddata(datafeed, name=ticker)
                        cerebro.addstrategy(StockDweebStrategy, securities=df)
                        cer = cerebro.run()[0]
                        # Get final portfolio Value
                        portvalue = cerebro.broker.getvalue()
                        pnl = portvalue - cash
                        print(f'Final portfolio value: {portvalue}')
                        print('P/L: ${}'.format(pnl))

                        # Finally plot the end results
                        x = cerebro.plot(style ='bar', width=30, height=50, tight=False, volume=False)[0][0]
                        st.write(x)

                except:
                    e = sys.exc_info()[0]
                    print(f'Na data for: {ticker} : {e}')


if __name__ == '__main__':
    main()
