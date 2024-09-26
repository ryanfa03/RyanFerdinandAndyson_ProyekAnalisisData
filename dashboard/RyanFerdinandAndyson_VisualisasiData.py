#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return monthly_orders_df

def create_total_order_items_df(df):
    total_order_items_df = df.groupby("product_category_name").product_photos_qty.sum().sort_values(ascending=False).reset_index()
    return total_order_items_df

def demographic_demo_state(df):
    demo_state = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    demo_state.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return demo_state

def create_analysis_rfm(df):
    analysis_rfm = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    analysis_rfm.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    analysis_rfm["max_order_timestamp"] = analysis_rfm["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    analysis_rfm["recency"] = analysis_rfm["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    analysis_rfm.drop("max_order_timestamp", axis=1, inplace=True)
    
    return analysis_rfm

dataset_df = pd.read_csv("https://raw.githubusercontent.com/ryanfa03/RyanFerdinandAndyson_ProyekAnalisisData/refs/heads/main/dashboard/all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
dataset_df.sort_values(by="order_purchase_timestamp", inplace=True)

 
for column in datetime_columns:
    dataset_df[column] = pd.to_datetime(dataset_df[column])
    
min_date = dataset_df["order_purchase_timestamp"].min()
max_date = dataset_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://miro.medium.com/v2/resize:fit:640/format:webp/1*HcUknIwnjCOoQJuE7iiwAg.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu Penjualan Olist',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
        
    )
    
main_df = dataset_df[(dataset_df["order_purchase_timestamp"] >= str(start_date)) & 
                (dataset_df["order_purchase_timestamp"] <= str(end_date))]

monthly_orders_df = create_monthly_orders_df(main_df)
total_order_items_df = create_total_order_items_df(main_df)
demo_state = demographic_demo_state(main_df)
analysis_rfm = create_analysis_rfm(main_df)

st.header('Olist E-Commerce Transaction Dashboard')
st.caption("Welcome to Olist, your one-stop destination for premium products and unbeatable deals! Whether you're shopping for the latest fashion, high-tech gadgets, home essentials, or unique gifts, we've got you covered. Our curated collections bring you top-quality items from trusted brands, all at competitive prices. With fast shipping, secure payments, and exceptional customer service, we aim to make your shopping experience smooth and enjoyable. Explore our wide range of products today and discover why Olist is the go-to choice for savvy shoppers!")    

st.subheader('Monthly Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "R$", locale='es_CO') 
    st.metric("Total Income", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#000000"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Most & Least Sold Product Category")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#000000", "#C0C0C0", "#C0C0C0", "#C0C0C0", "#C0C0C0"]
 
sns.barplot(x="product_photos_qty", y="product_category_name", data=total_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="product_photos_qty", y="product_category_name", data=total_order_items_df.sort_values(by="product_photos_qty", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

st.subheader("Number of Customer by States")
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="customer_count", 
    y="customer_state",
    data=demo_state.sort_values(by="customer_count", ascending=False),
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(analysis_rfm.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(analysis_rfm.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(analysis_rfm.monetary.mean(), "R$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#000000", "#C0C0C0", "#C0C0C0", "#C0C0C0", "#C0C0C0"]
 
sns.barplot(y="recency", x="customer_id", data=analysis_rfm.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=analysis_rfm.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=analysis_rfm.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Olist 2024. All rights reserved.')

dataset_df.to_csv("all_data.csv", index=False)
