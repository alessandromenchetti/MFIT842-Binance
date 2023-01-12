import pandas as pd
import numpy as np
import streamlit as st
from portfolio_optimizer import p_optimizer
from mc_simulator import mc_opt

#streamlit
#yfinance
#riskfolio-lib





st.set_page_config(layout='wide')

st.markdown('<h1 styles={align: middle;}>Team Binance - MFIT 842 Assignment 1</h1>', unsafe_allow_html=True)

df = pd.read_excel('ETF Database Sample V2.0.xlsx', sheet_name='Database')

df = df[['Yahoo Ticker', 'Long Name', 'Fund Family', 'Inception Date', 'Structure', 'Index Weight', 'ESG', 'Leverage', 'Inverse Fund',
         'Derivatives', 'Management Style', 'Strategy', 'Asset Group', 'Geographical Focus', 'Industry', 'Market Cap',
         'Maturity', 'Ratings', 'Expense Ratio', 'Fund Mgr Stated Fee', 'beta (3Year)']]

df['Inception Date'] = df['Inception Date'].astype('str').str[:10]
df['Inception Date'] = pd.to_datetime(df['Inception Date'], infer_datetime_format=True, errors='coerce')
df = df[df['Inception Date'] < '2017-12-31']

df.rename(columns={'Ratings': 'Ratings (Fixed Income Only)', 'beta (3Year)': '3 Year Beta'}, inplace=True)

df['ESG'] = np.where(df['ESG'] == 'Y', 'Yes', 'No')
df['Leverage'] = np.where(df['Leverage'] == 'Y', 'Yes', 'No')
df['Inverse Fund'] = np.where(df['Inverse Fund'] == 'Y', 'Yes', 'No')
#f['Derivatives'] = np.where(df['Derivatives'] == 'Y', 'Yes', 'No')

filters = st.multiselect('Please select filters you would like to apply:', df.columns, default=['ESG', 'Leverage', 'Inverse Fund'])

# if filters:
#     with st.expander('Modify Selected Filters:'):
#         modify = st.selectbox('Please choose which filter you would like to modify:', filters)
#         #st.write(type(modify))
#         if type(modify) == str:
#             f = st.radio('Select Filter Type:', ('Text', 'Set'), horizontal=True)
#
#             if f == 'Text':
#                 operator = st.selectbox('', ('Equals', 'Not Equals', 'Starts With', 'Ends With', 'Contains', 'Not Contains'), label_visibility='collapsed')
#                 input = st.text_input('', placeholder='Filter...', label_visibility='collapsed')
#
#                 if operator == 'Equals' and input:
#                     df = df[df[modify] == input]
#
#                 elif operator == 'Not Equals' and input:
#                     df = df[~(df[modify] == input)]
#
#                 elif operator == 'Starts With' and input:
#                     df = df[df[modify].str.startswith(input, na=False)]
#
#                 elif operator == 'Ends With' and input:
#                     df = df[df[modify].str.endswith(input, na=False)]
#
#                 elif operator == 'Contains' and input:
#                     df = df[df[modify].str.contains(input)]
#
#                 elif operator == 'Not Contains' and input:
#                     df = df[~df[modify].str.contains(input)]
#
#             if f == 'Set':
#                 selection = st.multiselect('Values for ' + modify + ':', df[modify].unique())
#                 if selection:
#                     df = df[df[modify].isin(selection)]
#
#         st.write(type(modify))

for f in filters:
    if f in ('ESG', 'Leverage', 'Inverse Fund', 'Derivatives'):
        selection = st.radio('Value for ' + f + ':', np.append(['No Filter'], df[f].unique()), horizontal=True)

        if selection != 'No Filter':
            df = df[df[f] == selection]
    else:
        selection = st.multiselect('Values for ' + f + ':', df[f].unique())

        if selection:
            df = df[df[f].isin(selection)]

# df[['Yahoo Ticker', 'Long Name']]
df

tickers = df['Yahoo Ticker'].tolist()

start_dt = df['Inception Date'].max()
end_dt = start_dt + pd.DateOffset(years=3)

st.header('Test Portfolio Performance')

if len(tickers) > 10:
    st.error('Please reduce list to maximum 10 tickers.')

else:
    mv = st.number_input('Please enter how much you would like to invest:', value=1000)

    e_or_o = st.radio('Equal Weighted or Optimized Portfolio Weights', ('Equal Weighted', 'Optimize Weights'), horizontal=True)

    if e_or_o == 'Equal Weighted':
        weights, returns = p_optimizer(tickers, start_dt, end_dt, returns_only=True)

    else:
        weights, returns = p_optimizer(tickers, start_dt, end_dt)
        weights = weights.to_numpy()

    weights*mv

    if st.button('Simulate Portfolio Performance'):
        mc_opt(mv, returns, weights*mv)