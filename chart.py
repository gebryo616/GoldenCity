from datetime import datetime,date
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob, os
import altair as alt
from io import BytesIO
import matplotlib.dates as mpl_dates


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
Companies = ['Xiaomi','Viva BioTech']


#effortless caching: relieve long-running computation in your code for continuously updating
@st.cache(allow_output_mutation=True)
def load_fdata(data):
    data = pd.read_csv(data)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    data.set_index("Date",inplace=True)
    return data

def Metrics_Calc(data):
  data['Days Sales Out.']=(data['A/R']/data['Revenue'])*365
  data['Days Inventory Out.']=(data['Inventory']/data['COGS'])*365
  data['Days Payable Out.']=(data['A/P']/data['COGS'])*365
  data['Cash Conversion Cycle']=data['Days Sales Out.']+data['Days Inventory Out.']-data['Days Payable Out.']

space(2)

############## Visualze the data
def Chart(data,title):
  st.line_chart(data)
  plt.title(title,fontsize='xx-large',fontweight='heavy')
  plt.xticks(rotation=45, ha='right')
  plt.axhline(0, ls='--', linewidth=2, color='red')

def Visual_Metrics(data):
  visual_metrics = data[['Days Sales Out.','Days Inventory Out.','Days Payable Out.','Cash Conversion Cycle']]
  return visual_metrics

##########Visualizing stock price1
#Load data from csv files


mydir1 = "data/chart1"
mydir2 = "data/chart2"

csvfiles1 = glob.glob(os.path.join(mydir1, '*.csv'))
df_dict1 = dict()
for file in csvfiles1:
    df_dict1[file.split('/')[2].split('.')[0]] = load_fdata(file)

csvfiles2 = glob.glob(os.path.join(mydir2, '*.csv'))
df_dict2 = dict()
for file in csvfiles2:
    df_dict2[file.split('/')[2].split('.')[0]] = load_fdata(file)

with st.sidebar:
    st.subheader("Configure the plot")
    option = st.selectbox(
         'Choose one company to visualize',
         Companies)
data1 = df_dict1[option]
data2 = df_dict2[option]
Metrics_Calc(data2)
s1, s2 = st.columns(2)
with s1:
    st.subheader('Economic Returns')
    space(1)
    Chart(data1,option)

with s2:
    st.subheader('Conversion Cycle')
    space(1)
    Chart(Visual_Metrics(data2),option)
