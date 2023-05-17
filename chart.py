from datetime import datetime,date
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob, os
import altair as alt
from io import BytesIO
import matplotlib.dates as mpl_dates
#from pandas_datareader import data
import yfinance as yf


#space function to control layout
def space(num_lines=1):
    for _ in range(num_lines):
        st.write("")

st.set_page_config(layout="wide",page_icon="💰",page_title="How Finance Works")

#add a title
st.image('header2.jpeg')
#st.title('Financial Analysis')
space(1)

st.markdown('#### Visualizing historical key factors of the corpartion helps us to understand how are the companies doing overtime, what is their :blue[overall market power] towards their _clients_ and _service_ _providers_, and have a sense of their :red[financial stories] ')
space(2)
###############data preparation
DATE_COLUMN = 'Date'
Companies = ['小米(Xiaomi)','信利国际','旭辉控股(CIFI Holdings)','吉利汽车(Geely)','富力地产','东风集团']
ticker = {
              '小米(Xiaomi)':'1810.HK',
              '信利国际':'0732.HK',
              '旭辉控股(CIFI Holdings)':'0884.HK',
              '吉利汽车(Geely)':'0175.HK',
              '富力地产':'2777.HK',
              '东风集团':'0489.HK'
              }

#effortless caching: relieve long-running computation in your code for continuously updating
@st.cache(allow_output_mutation=True)
def load_fdata(data):
    data = pd.read_csv(data)
    data.index = pd.to_datetime(data['Date'], format='%Y/%m/%d').dt.year
    data.set_index("Date",inplace=True)
    return data

def Metrics_Calc(data):
  data['Days Sales Out']=(data['A/R']/data['Revenue'])*365
  data['Days Inventory Out']=(data['Inventory']/data['COGS'])*365
  data['Days Payable Out']=(data['A/P']/data['COGS'])*365
  data['Cash Conversion Cycle']=data['Days Sales Out']+data['Days Inventory Out']-data['Days Payable Out']

def Ratio_Calc(data):
    data['Current assets/Current liabilities']=data['Current Asset']/data['Current Liabilities']
    data['Cash, maketable securities, and accounts receivable/ Current liabilities']=(data['Current Asset']-data['Inventory'])/data['Current Liabilities']
    data['Total debt/Total assets']=data['Long-term Debt']/data['Total Assets']
    data['Long-term debt/ Capitalization']=data['Long-term Debt']/(data['Shareholders\' Equity']+data['Long-term Debt'])
    data['Revenue/Total Assets']=data['Revenue']/data['Total Assets']
    data['Net Profit/Total Assets']=data['Net Income']/data['Total Assets']
    data['Total assets/ Shareholders\' equity']=data['Total Assets']/data['Shareholders\' Equity']
    data['Net Profit/ Shareholders\' equity']=data['Net Income']/data['Shareholders\' Equity']
    data['EBIT/ Interest Expense']=data['EBIT']/data['Interest Expense']
    data['EBITDA/ Revenue']=(data['EBIT']+data['D&A'])/data['Revenue']


space(2)

############## Visualze the data
def Chart(data,title):
  st.line_chart(data)
  plt.title(title,fontsize='xx-large',fontweight='heavy')
  plt.xticks(rotation=45, ha='right')
  plt.axhline(0, ls='--', linewidth=2, color='red')

def get_chart(data,unit):
    hover = alt.selection_single(
        fields=["Date"],
        nearest=True,
        on="mouseover",
        empty="none",
    )
    names=data.columns.tolist()
    lines = (
        alt.Chart(data.reset_index()).transform_fold(
        names).mark_line().encode(
            alt.X('Date:T',title="Date",axis=alt.Axis(tickCount="year",format="%Y")),
            alt.Y('value:Q',title=unit),
            color='key:N',
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.mark_circle(size=60)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x='Date:T',
            y='value:Q',
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip('Date:T', title="Date"),
                alt.Tooltip('value:Q', title=unit),
            ],
        )
        .add_selection(hover)
    )

    rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='black',strokeDash=[5, 5]).encode(
    y='y')
     # Set the dash style


    return (lines + points + tooltips + rule).interactive()

def bar(data,unit):
    #names=data.columns.tolist()
    bars = (
        alt.Chart(data).mark_bar().encode(
        alt.X('Date:T',title="Date",axis=alt.Axis(tickCount="year",format="%Y")),
        alt.Y('value:Q',title=unit),
        color='Key:N',
        )
    )
    return bars.interactive()

def Visual_Metrics(data):
  visual_metrics = data[['Days Sales Out','Days Inventory Out','Days Payable Out','Cash Conversion Cycle']]
  return visual_metrics

##########Visualizing stock price
#Load data from csv files

mydir1 = "data/chart1"
mydir2 = "data/chart2"
mydir3 = "data/chart3"
mydir4 = "data/Ratios"

csvfiles1 = glob.glob(os.path.join(mydir1, '*.csv'))
df_dict1 = dict()
for file in csvfiles1:
    df_dict1[file.split('/')[2].split('.')[0]] = load_fdata(file)

csvfiles2 = glob.glob(os.path.join(mydir2, '*.csv'))
df_dict2 = dict()
for file in csvfiles2:
    df_dict2[file.split('/')[2].split('.')[0]] = load_fdata(file)

csvfiles3 = glob.glob(os.path.join(mydir3, '*.csv'))
df_dict3 = dict()
for file in csvfiles3:
    df_dict3[file.split('/')[2].split('.')[0]] = load_fdata(file)

csvfiles4 = glob.glob(os.path.join(mydir4, '*.csv'))
df_dict4 = dict()
for file in csvfiles4:
    df_dict4[file.split('/')[2].split('.')[0]] = load_fdata(file)

with st.sidebar:
    st.subheader("Configure the plot")
    option = st.selectbox(
         'Choose one company to visualize',
         Companies)
    #market_cap = str(round(int(data.get_quote_yahoo(ticker[option])['marketCap'])/100000000,2))+"亿"
    #st.metric("MARKET CAP", market_cap)
    start_date = st.slider(
    "Choose date to start",
    value=datetime(2018, 1, 1),
    format="MM/DD/YY")
    st.write("Start date:", start_date)
    stock_data = yf.Ticker(ticker[option])
    #get historical data for searched ticker
    stock_df = stock_data.history(period='1y', start=start_date, end=None)
    #print line chart with daily closing prices for searched ticker
    st.line_chart(stock_df.Close)


data1 = df_dict1[option]
data2 = df_dict2[option]
data3 = df_dict3[option]
data4 = df_dict4[option]
Metrics_Calc(data2)
Ratio_Calc(data4)

st.subheader('Financial Ratios')
st.dataframe(data4.transpose().style.format("{:.2f}").highlight_max(axis=1))
space(1)

tab1, tab2 = st.tabs(["Chart", "Table"])
with tab1:
    st.subheader('Economic Returns')
    space(1)
    c1 = get_chart(data1,"Amount(亿)")
    st.altair_chart(c1, use_container_width=True)

with tab2:
    st.dataframe(data1)

tab5, tab6 = st.tabs(["Chart", "Table"])
with tab5:
    st.subheader('Conversion Cycle')
    space(1)
    c2 = get_chart(Visual_Metrics(data2),"Days")
    st.altair_chart(c2, use_container_width=True)
with tab6:
    st.dataframe(data2)

tab3,tab4 = st.tabs(["Overview", "Operational Components"])
with tab3:
    st.subheader("Overall Operation Conditions")
    space(1)
    c3 = get_chart(data3[["Revenue","COGS","Gross Profit","Net Income"]],"Amount(亿)")
    st.altair_chart(c3, use_container_width=True)
with tab4:
    st.subheader("Percentage of Revenue")
    space(1)
    df = data3[["% COGS","% Selling & Promotion Expenses","% Administrative Expenses","% Research & Development Expenses","% Net Income"]]
    st.bar_chart(df)
    #st.altair_chart(c4.interactive(), use_container_width=True
