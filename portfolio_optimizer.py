import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
import riskfolio as rp
import streamlit as st

def p_optimizer(tickers, start, end, returns_only=False):
    yf.pdr_override()
    pd.options.display.float_format = '{:.4%}'.format

    # Date range
    # start = '2017-01-01'
    # end = '2020-10-30'
    #
    # # Tickers of assets
    # my_etfs= ['AGG', 'SPY', 'VDE']

    if len(tickers) > 10:
        'Too many tickers selected, please reduce to <= 20.'
        return

    # Downloading data for stock portfolio
    data = yf.download(tickers, start = start, end = end)
    data = data.loc[:,('Adj Close', slice(None))]
    data.columns = tickers

    #Calculating and display returns for each asset
    asset_returns = data[tickers].pct_change().dropna()

    if returns_only:
        w = np.array([1 / len(tickers)] * len(tickers))
        return w, asset_returns


    # Building the portfolio object
    port = rp.Portfolio(returns=asset_returns)     ##using asset_returns we get from upper part

    # Calculating optimal portfolio

    # Select method and estimate input parameters:

    method_mu='hist' # Method to estimate expected returns based on historical data.
    method_cov='hist' # Method to estimate covariance matrix based on historical data.

    port.assets_stats(method_mu=method_mu, method_cov=method_cov, d=0.94)

    # Estimate optimal portfolio:

    model='Classic' # Could be Classic (historical), BL (Black Litterman) or FM (Factor Model)
    rm = 'MV' # Risk measure used, this time will be variance
    obj = 'Sharpe' # Objective function, could be MinRisk, MaxRet, Utility or Sharpe
    hist = True # Use historical scenarios for risk measures that depend on scenarios
    rf = 0 # Risk free rate
    l = 0 # Risk aversion factor, only useful when obj is 'Utility'

    w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

    fig, ax = plt.subplots()
    ax = rp.plot_pie(w, title='Sharpe Mean Variance', others=0.05, nrow=25, cmap='tab20', height=3, width=5, ax=None)
    c1, c2, c3 = st.columns([1, 1, 1])

    with c2:
        st.pyplot(fig)

    return w, asset_returns