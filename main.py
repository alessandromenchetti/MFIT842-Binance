import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder
from portfolio_optimizer import p_optimizer
from mc_simulator import mc_opt

st.set_page_config(layout='wide')

st.markdown('<h1 styles={align: middle;}>Team Binance - MFIT 842 Assignment 1</h1>', unsafe_allow_html=True)

st.header('What type of investor are you?')

with st.expander('Take the questionaire!'):

    q1 = st.selectbox('1\. What is your primary goal for investing?',
                  ('',
                   'To preserve capital and generate income',
                   'To grow capital over a long term',
                   'To achieve a combination of income and growth'))

    q2 = st.selectbox('2\. What is your time horizon for investing?',
                  ('',
                   'Less than 3 years',
                   '3 to 5 years',
                   'More than 5 years'))

    q3 = st.selectbox('3\. How much risk are you willing to take?',
                  ('',
                   'Low',
                   'Moderate',
                   'High'))

    q4 = st.selectbox('4\. How much money do you have available to invest?',
                  ('',
                   'Less than $10,000',
                   '$10,000 - $50,000',
                   'More than $50,000'))

    q5 = st.selectbox('5\. How much experience do you have with investing?',
                  ('',
                   'None',
                   'Limited',
                   'Extensive'))

    q6 = st.selectbox('6\. How much time do you have to managing your investments?',
                  ('',
                   'None',
                   'Limited',
                   'Extensive'))

    st.text('Result:')

    if q1 == '' and q2 == '' and q3 == '' and q4 == '' and q5 == '' and q6 == '':
        st.write('Please select an answer for all of the above questions.')

    elif q1 == 'To grow capital over a long term' and q2 == 'More than 5 years' and q3 == 'High' \
        and q4 == 'More than $50,000' and q5 == 'Extensive' and q6 == 'Extensive':
        st.write('You are a growth-oriented investor with a long-term focus and a high tolerance for risk. You have a'
                 'significant amount of money available to invest and extensive experience with investing. You are also'
                 'willing to commit a significant amount of time to managing your investments.')

    elif q1 == 'To preserve capital and generate income' and q2 == 'Less than 3 years' and q3 == 'Low' \
        and q4 == 'Less than $10,000' and q5 == 'None' and q6 == 'None':
        st.write('You are a conservative investor with a short-term focus and a low tolerance for risk. You have a'
                 'small amount of money available to invest and no experience with investing. You are not interested in'
                 'committing time to managing your investments.')

    else:
        st.write('You are a moderate investor with a combination of income and growth goals. Your time horizon, risk '
                 'tolerance, investment amount, experience, and time commitment are all moderate.')



st.header('Find your ETFs')

df = pd.read_excel('ETF Database Sample V2.0.xlsx', sheet_name='Database')

df = df[['Yahoo Ticker', 'Long Name', 'Fund Family', 'Inception Date', 'Structure', 'Index Weight', 'ESG', 'Leverage', 'Inverse Fund',
         'Derivatives', 'Management Style', 'Strategy', 'Asset Group', 'Geographical Focus', 'Industry', 'Market Cap',
         'Maturity', 'Ratings', 'Expense Ratio', 'Fund Mgr Stated Fee', 'beta (3Year)']]

df['Inception Date'] = df['Inception Date'].astype('str').str[:10]
df['Inception Date'] = pd.to_datetime(df['Inception Date'], infer_datetime_format=True, errors='coerce')
df = df[df['Inception Date'] < '2017-12-31']
# df['Inception Date'] = df['Inception Date'].astype('str')

df.rename(columns={'Ratings': 'Ratings (Fixed Income Only)', 'beta (3Year)': '3 Year Beta',
                   'Geographical Focus': 'Region'}, inplace=True)

df['ESG'] = np.where(df['ESG'] == 'Y', 'Yes', 'No')
df['Leverage'] = np.where(df['Leverage'] == 'Y', 'Yes', 'No')
df['Inverse Fund'] = np.where(df['Inverse Fund'] == 'Y', 'Yes', 'No')
df['Derivatives'] = np.where(df['Derivatives'] == 'Y', 'Yes', np.where(df['Derivatives'] == 'N', 'No', 'Mixed'))
df['Industry'] = np.where(df['Industry'] == '--', 'Mixed', df['Industry'])
df['Region'] = np.where(df['Region'] == '--', 'Other', df['Region'])
df['Asset Group'] = np.where(df['Asset Group'] == '--', 'Other', df['Asset Group'])
df['Strategy'] = np.where(df['Strategy'] == '--', 'Other', df['Strategy'])

esg = st.radio('Would you like to filter the ETF list to only include ETFs that have a focus on environment, social and'
               'governance (ESG) criteria?', ('No Filter', 'Yes', 'No'), horizontal=True)
if esg != 'No Filter':
    df = df[df['ESG'] == esg]

industries = st.multiselect('Please select the industries you are interested in:', df['Industry'].unique())
if industries:
    df = df[df['Industry'].isin(industries)]

regions = st.multiselect('Please select the regions you are interested in:', df['Region'].unique())
if regions:
    df = df[df['Region'].isin(regions)]

types = st.multiselect('Please select which asset groups you are interested in:', df['Asset Group'].unique())
if types:
    df = df[df['Asset Group'].isin(types)]

strategies = st.multiselect('Please select which strategies you are interested in:', df['Strategy'].unique())
if strategies:
    df = df[df['Strategy'].isin(strategies)]

##
st.markdown('---', unsafe_allow_html=True)
##

filters = st.multiselect('Please select any additional filters you would like to apply:', df.drop([
                         'ESG', 'Industry', 'Region', 'Asset Group', 'Strategy'], axis=1).columns)

for f in filters:
    if f in ('Leverage', 'Inverse Fund', 'Derivatives'):
        #selection = st.radio('Value for ' + f + ':', np.append(['No Filter'], df[f].unique()), horizontal=True)
        selection = st.selectbox('Filter for ' + f + ':', np.append(['Choose an option'], df[f].unique()))

        if selection != 'Choose an option':
            df = df[df[f] == selection]

    elif f in ('Expense Ratio', 'Fund Mgr Stated Fee', '3 Year Beta'):

        c1, c2, c3, c4, _ = st.columns([1, 1, 1, 1, 4])

        with c1:
            num_filt = st.selectbox('Filter for ' + f + ':', ('Equal to', 'Not Equal to', 'Greater than', 'Less than',
                                                      'Greater than or equal to', 'Less than or equal to', 'In Range',
                                                      'Outside Range'))

        with c2:
            if num_filt in ('In Range', 'Outside Range'):
                n1 = st.number_input('Min', key='n1' + f)
            else:
                n1 = st.number_input('', key='n1' + f)

        with c3:
            if num_filt in ('In Range', 'Outside Range'):
                n2 = st.number_input('Max', key='n2' + f)
            else:
                nf_flag = st.selectbox('', ('Filter off', 'Filter on'), key='flg' +f)

        with c4:
            if num_filt in ('In Range', 'Outside Range'):
                nf_flag = st.selectbox('', ('Filter off', 'Filter on'), key='flg' +f)

        if nf_flag == 'Filter on':
            if num_filt == 'Equal to':
                df = df[df[f] == n1]

            elif num_filt == 'Not Equal to':
                df = df[df[f] != n1]

            elif num_filt == 'Greater than':
                df = df[df[f] > n1]

            elif num_filt == 'Less than':
                df = df[df[f] < n1]

            elif num_filt == 'Greater than or equal to':
                df = df[df[f] >= n1]

            elif num_filt == 'Less than or equal to':
                df = df[df[f] <= n1]

            elif num_filt == 'In Range':
                df = df[(df[f] >= n1) & (df[f] <= n2)]

            elif num_filt == 'Outside Range':
                df = df[(df[f] < n1) & (df[f] > n2)]

    else:
        selection = st.multiselect('Values for ' + f + ':', df[f].unique())

        if selection:
            df = df[df[f].isin(selection)]

st.write('Note: Leaving any of the above fields blank will not filter the ETF list and instead display all ETFs')

##
st.markdown('---', unsafe_allow_html=True)
##

st.write('Please select ETFs to add to your portfolio:')

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column('Inception Date', custom_format_string='yyyy-MM-dd', **{'hide': True})
gb.configure_selection('multiple', use_checkbox=True)
grid_options = gb.build()

grid_response = AgGrid(df,
                       gridOptions=grid_options,
                       height=300,
                       )

selected = grid_response['selected_rows']
df_s = pd.DataFrame(selected)

st.text('Selected ETFs:')

if not df_s.empty or 'sel' in st.session_state:
    if 'sel' not in st.session_state:
        st.session_state['sel'] = df_s.drop(['_selectedRowNodeInfo'], axis=1)

    else:
        if not df_s.empty:
            st.session_state['sel'] = pd.concat([st.session_state['sel'], df_s.drop(['_selectedRowNodeInfo'], axis=1)])
        else:
            st.session_state['sel'] = pd.concat([st.session_state['sel'], df_s])

    st.session_state['sel'].drop_duplicates(inplace=True)
    if not st.session_state['sel'].empty:
        st.session_state['sel'].drop_duplicates(inplace=True)
        st.dataframe(st.session_state['sel'], use_container_width=True)

if st.button('Clear ETF List'):
    if 'sel' in st.session_state:
        st.session_state['sel'] = None
    df_s = None

st.header('Test Portfolio Performance')

if 'sel' in st.session_state:
    if st.session_state['sel'] is not None and not st.session_state['sel'].empty:
        df_cart = st.session_state['sel'].copy()
        df_cart['Inception Date'] = pd.to_datetime(df_cart['Inception Date'], infer_datetime_format=True, errors='coerce')
        tickers = df_cart['Yahoo Ticker'].tolist()

        start_dt = df_cart['Inception Date'].max()
        end_dt = start_dt + pd.DateOffset(years=3)

        if len(tickers) > 10:
            st.error('Please reduce list to maximum 10 tickers.')

        else:
            mv = st.number_input('Please enter how much you would like to invest:', value=1000)

            e_or_o = st.radio('Equal Weighted or Optimized Portfolio Weights', ('Equal Weighted', 'Optimize Weights'), horizontal=True)

            if e_or_o == 'Equal Weighted':
                weights, returns = p_optimizer(tickers, start_dt, end_dt, returns_only=True)
                st.write(pd.DataFrame({'Tickers': tickers, 'Weights': weights*mv}).set_index('Tickers'))

            else:
                weights, returns = p_optimizer(tickers, start_dt, end_dt)
                weights_np = weights.to_numpy()
                weights = weights * mv
                weights


            if st.button('Simulate Portfolio Performance'):
                mc_opt(mv, returns, weights*mv)

else:
    st.write('Please select at least 1 ETF')