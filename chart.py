from datetime import datetime,date
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob, os
import altair as alt
from io import BytesIO
import matplotlib.dates as mpl_dates
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
Companies = ['小米(Xiaomi)','维亚生物(Viva BioTech)','歌尔股份(GoerTek)','信利国际']
ticker = {
              '小米(Xiaomi)':'1810.HK',
              '维亚生物(Viva BioTech)':'1873.HK',
              '歌尔股份(GoerTek)':'002241.SZ',
              '信利国际':'0732.HK'
              }

cap = {
              '小米(Xiaomi)':'324.95B HKD',
              '维亚生物(Viva BioTech)':'3.25B HKD',
              '歌尔股份(GoerTek)':'78.18B CNY',
              '信利国际':'4.26B HKD'
              }



#effortless caching: relieve long-running computation in your code for continuously updating
@st.cache(allow_output_mutation=True)
def load_fdata(data):
    data = pd.read_csv(data)
    data.index = pd.to_datetime(data['Date'], format='%Y-%m-%d').dt.year
    data.set_index("Date",inplace=True)
    return data

def Metrics_Calc(data):
  data['Days Sales Out']=(data['A/R']/data['Revenue'])*365
  data['Days Inventory Out']=(data['Inventory']/data['COGS'])*365
  data['Days Payable Out']=(data['A/P']/data['COGS'])*365
  data['Cash Conversion Cycle']=data['Days Sales Out']+data['Days Inventory Out']-data['Days Payable Out']

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
    points = lines.transform_filter(hover).mark_circle(size=65)

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
    return (lines + points + tooltips).interactive()

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

with st.sidebar:
    st.subheader("Configure the plot")
    option = st.selectbox(
         'Choose one company to visualize',
         Companies)
    st.metric("MARKET CAP", cap[option])
    start_date = st.slider(
    "Choose date to start",
    value=datetime(2022, 1, 1),
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
Metrics_Calc(data2)

tab1, tab2 = st.tabs(["Chart", "Table"])
with tab1:
    st.subheader('Economic Returns')
    space(1)
    c1 = get_chart(data1,"Amount(0.1b)")
    st.altair_chart(c1.interactive(), use_container_width=True)

with tab2:
    st.dataframe(data1)

tab5, tab6 = st.tabs(["Chart", "Table"])
with tab5:
    st.subheader('Conversion Cycle')
    space(1)
    c2 = get_chart(Visual_Metrics(data2),"Days")
    st.altair_chart(c2.interactive(), use_container_width=True)
with tab6:
    st.dataframe(data2)

tab3,tab4 = st.tabs(["Overview", "Financial Ratios"])
with tab3:
    st.subheader("Overall Operation Conditions")
    space(1)
    c3 = get_chart(data3[["Revenue","COGS","Gross Profit","Net Income"]],"Amount(0.1b)")
    st.altair_chart(c3.interactive(), use_container_width=True)
with tab4:
    st.subheader("Percentage of Revenue")
    space(1)
    df = data3[["% COGS","% Selling & Promotion Expenses","% Administrative Expenses","% Research & Development Expenses","% Net Income"]]
    st.bar_chart(df)
    #st.altair_chart(c4.interactive(), use_container_width=True)
