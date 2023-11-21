import requests
import pandas as pd
import datetime
import logging
import os
class FMP:

    def __init__(self) -> None:
        self.api_key = 'c6b648e71a9debf6bb7dac776e6cb205'
        self.end_point = 'https://financialmodelingprep.com/api/'
        self.session = requests.Session()

    def recent_stock_info(self,tickers, start: str =None, end: str =None):
        """
        Return stockdata for tickers from start and end date.
        Default start is 7 days ago until today.
        
        
        Parameters
        ----------
        
        tickers: Iterable[str]. Tickers should be in their official format.
        See https://stockanalysis.com/stocks/ for more info.
        
        start: str|datetime.datetime. Start date of stock data. If in str format, should be in YYYY-MM-DD format.
        Default is 7 days ago.
        
        end: str|datetime.datetime. End date of stock data. If in str format, should be in YYYY-MM-DD format.
        Default is today | datetime.datetime.now().
        
        
        Return type
        ----------
        
        A pd.DataFrame with stock data for tickers from start until end.
        Columns are: 
        date: str
        open:               .2f     | > 0.00
        high:               .2f     | > 0.00
        low:                .2f     | > 0.00
        close:              .2f     | > 0.00
        adjClose:           .2f     | > 0.00
        volume:             int     | >= 0
        unadjustedVolume:   int     | >= 0
        change:             float   | >= 0.00
        changePercent:      float   | >= 0.00
        vwap:               .2f     | >= 0.00
        changeOverTime:     float   | >= 0.00
        ticker:             str     | ticker of stock
        
        Examples
        --------
        
        >>> fmp = FMP()
        >>> ticker = 'AAPL'
        >>> start = '2023-01-01'
        >>> end = '2023-01-31'
        >>> df = fmp.recent_stock_info(tickers=[ticker],start=start,end=end)
        # returns a dataframe with stock data for ticker AAPL from 2023-01-01 until 2023-01-31
        # when a list of n>=2 tickers is given, the dataframe will contain stock data for all tickers create N dataframes by doing 
        df1 = df[df['ticker'] == ticker1]
        df2 = df[df['ticker'] == ticker2]
        """
        
        
        
        if not start:
            start = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        if not end:
            end = datetime.datetime.now().strftime("%Y-%m-%d")
        
        
        logging.info(f"Getting recent stock info for {tickers}")
        try:
            if len(tickers) >=2:
            
                    tickers_request = ",".join(tickers)
                    url = f"{self.end_point}v3/historical-price-full/{tickers_request}?apikey={self.api_key}&from={start}&to={end}"
                    logging.info(url)
                    print(url)
                    data = self.session.get(url).json()
                    data = data["historicalStockList"]
                    data_per_ticker = [data_ticker['historical'] for data_ticker in data]

                    df = pd.DataFrame()
                    for symbol, ticker_data in zip(tickers, data_per_ticker) :
                        df_ticker = pd.DataFrame(ticker_data)
                        # remove label, adjClose and unadjustedVolume
                        df_ticker = df_ticker.drop(['label', 'adjClose', 'unadjustedVolume'], axis=1)
                        df_ticker['ticker'] = symbol
                        df = pd.concat([df, df_ticker])
                    return df
            if len(tickers) == 1:
                url = f"{self.end_point}v3/historical-price-full/{tickers[0]}?apikey={self.api_key}&from={start}&to={end}"
                logging.info(url)
                print(url)
                df = pd.DataFrame()
                data = self.session.get(url).json()
                data_per_ticker = [data_per_day for data_per_day in data['historical']]
                df = pd.DataFrame(data_per_ticker)
                df['ticker']= tickers[0]
                # keep every column except label
                df = df[[i for i in df.columns if i != 'label']]
                return df
        
        except Exception as e: 
            logging.error(f"Could not get recent stock info for {tickers}")
            print(e)
            return None

    def yearly_financial_report(self, symbol: str, year: int) -> pd.DataFrame:
        url = f"{self.end_point}v4/financial-reports-json?symbol={symbol}&year={year}&period=FY&apikey={self.api_key}"
        print(url)
        data = self.session.get(url).json()
        return data
    
    def quarterly_financial_report(self, symbol: str, year: int, quarter: int) -> pd.DataFrame:
        url = f"{self.end_point}v4/financial-reports-json?symbol={symbol}&year={year}&period=Q{quarter}&apikey={self.api_key}"
        print(url)
        data = self.session.get(url).json()
        return data
    
    def earning_call_transcript(self,symbol:str,year :int,quarter: int) -> pd.DataFrame:
        url = f"{self.end_point}v3/earning_call_transcript/{symbol}?quarter={quarter}&year={year}&apikey={self.api_key}"
        data = self.session.get(url).json()
        print(url)
        return data
    
    
    def stock_exchange_days(self,start: str ,end: str,ticker: str) -> pd.DataFrame:
        """ returns a dataframe with all stock exchange days between start and end for ticker"""
        path = 'data/price full/'
        # check if file exists
        for file in os.listdir(path):
            if file.startswith(f"{ticker} price 1970-01-01"):
                filename = file
                df = pd.read_csv(f"{path}{filename}")
                return df
        
        url = f"{self.end_point}v3/historical-price-full/{ticker}?apikey={self.api_key}&from={start}&to={end}"
        logging.info(url)
        print(url)
        data = self.session.get(url).json()
        data = data["historical"]
        days = [info['date'] for info in data][::-1]
        df = pd.DataFrame(columns=['date'],data=(days))
        df['date'] = pd.to_datetime(df['date'])
        return df