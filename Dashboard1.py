import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="sales data analysis", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: sales analysis")
fl = st.file_uploader(":file_folder: upload a file",type=["csv","txt","xls","xlsx"])
if fl is not None:
    file = fl.name
    st.write(file)
    try:
        # Try reading as CSV
        data = pd.read_csv(file)
        print("Successfully read as CSV.")

    except pd.errors.ParserError:
        try:
            # Try reading as TXT (tab-separated)
            data = pd.read_csv(file, delimiter='\t')
            print("Successfully read as TXT (tab-separated).")

        except pd.errors.ParserError:
            try:
                # Try reading as XLS
                data = pd.read_excel(file, engine='xlrd')
                print("Successfully read as XLS.")

            except pd.errors.ParserError:
                try:
                    # Try reading as XLSX
                    data = pd.read_excel(file, engine='openpyxl')
                    print("Successfully read as XLSX.")

                except pd.errors.ParserError:
                    pass
else:
    df = pd.read_csv("Sales_Data.csv")

st.header("plotting addresses on a map")
data = pd.read_csv("coordinates.csv")

st.map(data,zoom=2.5)
col1, col2 = st.columns(2)

# time filter
df["Order Date"] = pd.to_datetime(df["Order Date"])
min_date = df["Order Date"].min()
max_date = df["Order Date"].max()
with col1:
    start_date = pd.to_datetime(st.date_input("Select Start Date",min_date))
with col2:
    end_date = pd.to_datetime(st.date_input("Select End Date",max_date))
filtered_df = df[(df["Order Date"] >= start_date) & (df["Order Date"] <= end_date)]



st.sidebar.header("select your filters:")

# filter region


region  = st.sidebar.multiselect("Select the region:",filtered_df["City"].unique())
if not region:
    filtered_df1 = filtered_df.copy()
else:
    filtered_df1 = filtered_df[filtered_df["City"].isin(region)]

# product filter
products  = st.sidebar.multiselect("Select the products:",filtered_df["Product"].unique())
if not products:
    filtered_df2 = filtered_df1.copy()
else:
    filtered_df2 = filtered_df1[filtered_df1["Product"].isin(products)]

with col1:
    st.subheader("product wise sales")
    fig = px.bar(filtered_df2,x= "Product",y="Sales",template="seaborn")
    st.plotly_chart(fig,use_container_width=True)

with col2:
    st.subheader("city wise sales")
    fig = px.pie(filtered_df2,values="Sales",names="City",hole=.5)
    st.plotly_chart(fig,use_container_width=True)

filtered_df2["month_year"] = filtered_df2["Order Date"].dt.to_period("M")

st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df2.groupby(filtered_df2["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")

st.subheader("Hierarchical view of Sales using TreeMap: City :point_right: Product :point_right: Sales")
fig3 = px.treemap(filtered_df2, path = ["City","Product"], values = "Sales",hover_data = ["Sales"],
                  color = "Product")
fig3.update_layout(width = 1000, height = 800)
st.plotly_chart(fig3, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Product Sales Summary")
with st.expander("Summary_Table"):
    st.markdown("Month wise Product Table")
    filtered_df2["month"] = filtered_df2["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df2, values = "Sales", index = ["Product"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))









