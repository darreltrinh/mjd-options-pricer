import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Get the stock object for SPY
spy = yf.Ticker("SPY")

def pull_underlying(ticker):
    
    # pull 3-months worth of data to calculate the standard deviation and +/- to the most recent close
    asset = yf.Ticker(ticker)
    price_rn = asset.history(period='1d')
    recent_close = price_rn["Close"].iloc[-1]

    hist_pricing = pd.DataFrame(asset.history(period="3mo"))
    stdev_close = hist_pricing['Close'].std()
    info = {"SYMBOL": ticker, "PRICE": recent_close, "-STDEV": recent_close - stdev_close, "+STDEV": recent_close + stdev_close, "STDEV" : stdev_close}
   
    return info

def get_option_data(days : int) -> pd.DataFrame:

    # Get the options data for SPY
    options = spy.options

    # Convert the options data to a pandas DataFrame
    options_df = pd.DataFrame(options, columns=['expiration'])
    options_df['expiration'] = pd.to_datetime(options_df['expiration'], format = '%Y-%m-%d')
    options_df['exp_date'] = options_df['expiration'].dt.strftime('%Y-%m-%d')

    # Filter the options data to include only expiries within the next 30 days
    thirty_days_from_now = datetime.now() + timedelta(days=days)
    options_df = options_df[options_df['expiration'].dt.date <= thirty_days_from_now.date()]

    opt_list = []

    for exp in options_df['exp_date']:
        opt = spy.option_chain(date = exp)
        calls = opt.calls
        calls = calls.assign(expiry=exp)
        puts = opt.puts
        puts = puts.assign(expiry=exp)
        opt_list.append(calls)
        opt_list.append(puts)
        opt_chains = pd.concat(opt_list)
    #opt_chains = pd.DataFrame(opt_list, columns=['contractSymbol', 'lastTradeDate', 'strike', 'lastPrice', 'bid', 'ask', 'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility', 'inTheMoney', 'contractSize', 'currency', 'expiry'])
    # Return the filtered options data
    return opt_chains

def identify_strikes(ticker, days : int):
    mrkt_price = pull_underlying(ticker)
    chains = get_option_data(days)

    adj_chains = chains[(chains['strike'] > mrkt_price["-STDEV"]) & (chains['strike'] < mrkt_price["+STDEV"])]
    
    return adj_chains

print(identify_strikes("SPY", 30))

#print(get_option_data(30))


