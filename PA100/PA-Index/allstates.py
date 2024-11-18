import seaborn as sns
import streamlit as st
from datetime import date, timedelta
import pandas as pd
import pickle
import warnings
import plotly.express as px
from collections import defaultdict

st.set_page_config(layout="wide")

st.sidebar.title('Welcome!')

indexes, analytics = st.tabs(["Index", "Analytics"])

universe_options = ['Russell 3000']
weighting_method_options = ['Market Cap','Equal Weight','Price Weight']
selection_method_options = ['Market Cap','Price']
filters_options = ['States','GICS Sector']
states_options = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
                  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
                  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
                  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
gics_sectors_options = ['Communication Services', 'Consumer Discretionary', 'Consumer Staples', 
                    'Energy', 'Financials', 'Health Care', 'Industrials',
                    'Information Technology', 'Materials', 'Real Estate', 'Utilities']

# Sidebar Information
universe = st.sidebar.selectbox('Select Your Universe',universe_options)
weighting_method = st.sidebar.selectbox('Select Your Weighting Method',weighting_method_options)
if weighting_method == 'Price Weight':
    selection_method = st.sidebar.selectbox('Select Your Selection Method',selection_method_options)
else:
    selection_method = 'Market Cap'
filters = st.sidebar.multiselect('Add Filters',filters_options)
if 'States' in filters:
    states = st.sidebar.multiselect('Select States',states_options,'PA')
else:
    states = states_options
if 'GICS Sector' in filters:
    gics_sectors = st.sidebar.multiselect('Select GICS Sectors',gics_sectors_options,'Information Technology')
else:
    gics_sectors = gics_sectors_options
num_companies = st.sidebar.number_input("Set Number of Companies", min_value=1, max_value=3000, value=100)
start_date = st.sidebar.date_input('Set Start Date',value=date(2023,11,10),min_value=date(2023,11,10),max_value=date.today() - timedelta(2))
end_date = st.sidebar.date_input('Set End Date',value=date.today() - timedelta(1),min_value=start_date + timedelta(1),max_value=date.today() - timedelta(1))
start_date = start_date.strftime('%Y-%m-%d')
end_date = end_date.strftime('%Y-%m-%d')
initial_value = st.sidebar.number_input('Set Initial Index Value', value=100, min_value=1, max_value=999999999999)



with open('corporate_events/stock_splits.pkl','rb') as file:
    stock_splits = pickle.load(file)

with open('input/date_dataframes.pkl', 'rb') as file:
    date_dataframes = pickle.load(file)



def generate_rebalancing(universe, start_date, end_date):

    if universe == 'Russell 3000':
        dates = ['2023-11-10', '2024-06-28', '2025-06-28', '2026-06-28']
    if universe == 'S&P 500':
        dates = ['2023-11-10', '2023-12-31', '2024-12-31', '2025-12-31']
    
    rebalancing = {}
    
    for i in range(len(dates) - 1):
        if start_date < dates[i + 1] and end_date > dates[i]:
            rebalancing[dates[i]] = [max(start_date, dates[i]), min(end_date, dates[i + 1])]
    
    if end_date > dates[-1]:
        rebalancing[dates[-1]] = [max(start_date, dates[-1]), end_date]
    
    return rebalancing

rebalancing = generate_rebalancing(universe,start_date,end_date)

# rebalancing generates a dictionary where the keys are the dates of rebalancing
# and the values are the start and end date for that rebalancing period
# {'2023-11-10': ['2023-11-10', '2024-06-28'], '2024-06-28': ['2024-06-28', '2024-08-20']}

unique_dates = list(date_dataframes.keys())

eod_pivot = {}

for rebalancing_date in rebalancing.keys():
    excel_file = f'input/{universe.replace(" ","")}_{rebalancing_date}.xlsx' # the excels are named to align with the code
    df = pd.read_excel(excel_file)
    df.columns = df.columns.str.rstrip('\n') # the column names originally have a '\n' in them
    df['Ticker'] = df['Ticker'].str.split(' ',n=1,expand=True)[0].replace(' ','')
    df['Ticker'] = df['Ticker'].str.replace('/', '.')
    df = df[df['State of Domicile'].isin(states)]
    df = df[df['GICS Sector'].isin(gics_sectors)]
    if selection_method == 'Market Cap':
        df = df.sort_values('Market Cap', ascending=False)
    else:
        df = df.sort_values('Price', ascending=False)
    df_later = df.copy()
    df = df.head(num_companies)
    float_df = df[['Ticker','Equity Float','GICS Sector']]
    # don't rewrite df because we wan't to use it for analytics later

    eod_pivot[rebalancing_date] = pd.DataFrame()
    # {eod_pivot} and {rebalancing} will share the same keys

    for date in unique_dates:
        if date >= rebalancing[rebalancing_date][0] and date <= rebalancing[rebalancing_date][1]:
            eod_df = date_dataframes[date]
            merged_df = pd.merge(float_df,eod_df,left_on='Ticker',right_on='underlying_symbol')
         
            if weighting_method != 'Price Weight':
                for i,ticker in enumerate(merged_df['Ticker']):
                    for company in stock_splits.keys():
                        if ticker == company and date >= stock_splits[ticker][0]:
                            merged_df.at[i,'Equity Float'] = merged_df.at[i,'Equity Float'] * stock_splits[ticker][1]
                merged_df['Market Cap'] = merged_df['Equity Float'] * merged_df['close']
                eod_daily = merged_df.pivot_table(values='Market Cap',index='quote_date',columns='Ticker',aggfunc='sum')
                eod_pivot[rebalancing_date] = pd.concat([eod_pivot[rebalancing_date],eod_daily])
            else:
                for i,ticker in enumerate(merged_df['Ticker']):
                    for company in stock_splits.keys():
                        if ticker == company and date >= stock_splits[ticker][0]:
                            merged_df.at[i,'close'] = merged_df.at[i,'close'] * stock_splits[ticker][1]
                eod_daily = merged_df.pivot_table(values='close',index='quote_date',columns='Ticker',aggfunc='sum')
                eod_pivot[rebalancing_date] = pd.concat([eod_pivot[rebalancing_date],eod_daily])                

    eod_pivot[rebalancing_date] = eod_pivot[rebalancing_date].rename_axis(index='Date')
    eod_pivot[rebalancing_date].index = pd.to_datetime(eod_pivot[rebalancing_date].index,errors='coerce')

    eod_pivot[rebalancing_date]['deleted_stock'] = 0
    
    for ticker in eod_pivot[rebalancing_date].keys()[:-1]:
        last_valid = None
        first_deletion = False
    
        for date_index, date in enumerate(eod_pivot[rebalancing_date].index):
    
            if date != eod_pivot[rebalancing_date].index[-1]:
            
                next_date = eod_pivot[rebalancing_date].index[date_index + 1]
            
                value = eod_pivot[rebalancing_date].at[date,ticker]
    
                value_next_date = eod_pivot[rebalancing_date].at[next_date,ticker]
    
                if (pd.isna(value) or value == 0) and (pd.isna(value_next_date) or value_next_date == 0):
                    if not first_deletion and last_valid is not None:
                        if weighting_method != 'Equal Weight':
                            eod_pivot[rebalancing_date].at[date, 'deleted_stock'] = last_valid
                        else:
                            eod_pivot[rebalancing_date].at[date, 'deleted_stock'] = last_valid / eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[0], ticker]
                        first_deletion = True
    
                if (pd.isna(value) or value == 0) and value_next_date != 0:
                    if not first_deletion and last_valid is not None:
                        eod_pivot[rebalancing_date].at[date,ticker] = last_valid
                        first_deletion = True
                
                else:
                    last_valid = value
                    first_deletion = False
    
            else:
                value = eod_pivot[rebalancing_date].at[date,ticker]
                if pd.isna(value) or value == 0:
                    if not first_deletion and last_valid is not None:
                        eod_pivot[rebalancing_date].at[date,ticker] = last_valid
                        first_deletion = True
                else:
                    last_valid = value
                    first_deletion = False
    
    if weighting_method != 'Equal Weight':
        eod_pivot[rebalancing_date]["close"] = eod_pivot[rebalancing_date].drop(columns='deleted_stock').sum(axis=1)
    else:
        eod_pivot[rebalancing_date]["close"] = (eod_pivot[rebalancing_date].drop(columns='deleted_stock') / eod_pivot[rebalancing_date].iloc[0]).sum(axis=1)
  
   
    
    eod_pivot[rebalancing_date]["adjusted"] = 0
    eod_pivot[rebalancing_date]["divisor"] = 0
    eod_pivot[rebalancing_date]["gross_index_level"] = 0
    eod_pivot[rebalancing_date]["Index Value"] = 0
    
for j,rebalancing_date in enumerate(eod_pivot.keys()):
    if j == 0:
        for i in range(0, len(eod_pivot[rebalancing_date])):
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                if i == 0:
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "adjusted"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "close"]) + float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "deleted_stock"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"] = 1
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "close"]) / float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "Index Value"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"]) / (float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[0], "close"]) / initial_value)
                else:
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "adjusted"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i-1], "close"]) - float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "deleted_stock"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"] = (float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "adjusted"]) / float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i-1], "close"])) * float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i-1], "divisor"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "close"]) / float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "Index Value"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"]) / (float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[0], "close"]) / initial_value)
        last_value = eod_pivot[rebalancing_date].iloc[-1]['Index Value']
    else:
        for i in range(0, len(eod_pivot[rebalancing_date])):
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                if i == 0:
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "adjusted"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "close"]) + float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "deleted_stock"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"] = 1
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "close"]) / float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "Index Value"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"]) / (float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[0], "close"]) / last_value)
                else:
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "adjusted"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i-1], "close"]) - float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "deleted_stock"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"] = (float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "adjusted"]) / float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i-1], "close"])) * float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i-1], "divisor"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "close"]) / float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "divisor"])
                    eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "Index Value"] = float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[i], "gross_index_level"]) / (float(eod_pivot[rebalancing_date].at[eod_pivot[rebalancing_date].index[0], "close"]) / last_value)
        last_value = eod_pivot[rebalancing_date].iloc[-1]['Index Value']        


list_of_dataframes = []

for i,rebalancing_date in enumerate(eod_pivot.keys()):
    if i == 0:
        list_of_dataframes.append(eod_pivot[rebalancing_date])
    else:
        list_of_dataframes.append(eod_pivot[rebalancing_date].iloc[1:])

final_df = pd.concat(list_of_dataframes)
final_df.index = pd.to_datetime(final_df.index).date
index_df = final_df[['Index Value']].copy()



gics_sector_dict = defaultdict(list)


for index, row in df_later.iterrows():
    gics_sector = row['GICS Sector']
    ticker = row['Ticker']
    gics_sector_dict[gics_sector].append(ticker)

gics_sector_dict = dict(gics_sector_dict)

totals_dict = {}

for sector in gics_sector_dict.keys():
    date_totals = []
    for i,date in enumerate(final_df.index):
        date_total = 0
        for ticker in final_df.keys():
            if ticker in gics_sector_dict[sector]:
                if not pd.isna(final_df.at[final_df.index[i],ticker]):
                    date_total += final_df.at[final_df.index[i],ticker]
        date_totals.append(date_total)
    totals_dict[sector] = date_totals

totals = pd.DataFrame(totals_dict)
totals['Date'] = final_df.index
baseline = totals.iloc[0]
totals_relative = totals.copy()
totals_relative.iloc[:, :-1] = totals.iloc[:, :-1].div(baseline[:-1], axis=1) - 1
totals_melted = totals_relative.reset_index(drop=True).melt(id_vars='Date', var_name='Sector', value_name='Return')

final_returns = totals_melted[len(totals_relative)-1::len(totals_relative)]
final_returns = final_returns.reset_index().drop(columns=['index'])
final_returns['Date'] = pd.to_datetime(final_returns['Date']).dt.date
final_returns = final_returns.set_index('Date')
final_returns['Return'] = pd.to_numeric(final_returns['Return'], errors='coerce')
final_returns['Return'] = (final_returns['Return'] * 100).round(2)
final_returns['Return'] = final_returns['Return'].astype(str) + '%'

if st.sidebar.button('Create Index'):
    y_axis_min = index_df.min() - 5
    y_axis_max = index_df.max() + 5


    fig1 = px.line(index_df, y="Index Value", title="Index Value Over Time")

    fig1.update_layout(title='Index Value Over Time',
                  xaxis_title='Date',
                  yaxis_title='Index Value',
                  yaxis=dict(range=[y_axis_min, y_axis_max]),)

    fig2 = sns.relplot(data=totals_melted,
            x='Date',y='Return',kind='line',hue='Sector',palette='bright',linewidth=4,col='Sector',
            zorder=5,col_wrap=4,height=2,aspect=2,legend=False)
    titles = list(totals_melted['Sector'].unique())
    for i, (sector,subplot) in enumerate(fig2.axes_dict.items()):
        sns.lineplot(data=totals_melted, x='Date', y='Return', units='Sector',
                 estimator=None,color='.7',linewidth=1,ax=subplot)
        subplot.set_title(titles[i])
    for ax in fig2.axes.flat:
        ax.get_xaxis().set_visible(False)
    fig2.set_axis_labels('Date','Return')
    
    col1_indexes, col2_indexes = indexes.columns([1, 4])

    # Display the DataFrame in the first column
    with col1_indexes:
        st.write(index_df)
    
    # Display the plotly figure in the second column
    with col2_indexes:
        st.plotly_chart(fig1)

    col1_analytics, col2_analytics = analytics.columns([2,5])

    with col2_analytics:
        st.pyplot(fig2)
        st.write(final_df)

    with col1_analytics:
        st.write(final_returns)