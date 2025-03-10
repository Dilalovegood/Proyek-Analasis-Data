import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency
sns.set(style='dark')

# Load all_data dari file CSV
all_df = pd.read_csv('all_data.csv')
order_df = pd.read_csv('orders_dataset.csv')

datetime_columns = ["order_purchase_timestamp",
                    "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# Fungsi untuk membuat DataFrame produk teratas


def create_top_products_name_df(all_df):
    # Menghitung 5 produk teratas berdasarkan kategori
    top_products = all_df['product_category_name'].value_counts().head(
        5).sort_values(ascending=True)
    return top_products


top_products = create_top_products_name_df(main_df)


# Fungsi untuk membuat DataFrame jumlah pelanggan per kota

def create_customer_count_per_city_df(all_df):
    # Menghitung jumlah pelanggan unik per kota
    customer_count_per_city = all_df.groupby(
        'customer_city')['customer_unique_id'].nunique().reset_index()
    customer_count_per_city = customer_count_per_city.rename(
        columns={'customer_unique_id': 'customer_count'})
    customer_count_per_city = customer_count_per_city.sort_values(
        by='customer_count', ascending=False)
    return customer_count_per_city


customer_count_per_city = create_customer_count_per_city_df(main_df)


# Fungsi untuk membuat DataFrame jumlah pesanan bulanan

def create_sales_per_year_df(all_df):
    # Mengubah kolom tanggal order menjadi tipe data datetime
    all_df['order_purchase_timestamp'] = pd.to_datetime(
        all_df['order_purchase_timestamp'])

    # Mengelompokkan jumlah pesanan per bulan
    sales_per_year = all_df.groupby(pd.Grouper(
        key='order_purchase_timestamp', freq='Y')).count()['order_id']
    return sales_per_year


sales_per_year = create_sales_per_year_df(main_df)


# Fungsi untuk membuat DataFrame analisis RFM


def create_rfm_df(all_df):
    # Melakukan analisis RFM: Recency, Frequency, Monetary
    rfm_df = all_df.groupby(by='customer_unique_id', as_index=False).agg({
        'order_purchase_timestamp': 'max',  # Tanggal order terakhir
        'order_id': 'nunique',  # Jumlah order
        'total_price': 'sum'  # Jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ['customer_unique_id',
                      'max_order_timestamp', 'frequency', 'monetary']

    # Menghitung recency (berapa hari yang lalu terakhir kali pelanggan melakukan transaksi)
    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_date = pd.to_datetime(
        order_df['order_purchase_timestamp']).dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(
        lambda x: (recent_date - x).days)
    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)
    return rfm_df


rfm_df = create_rfm_df(main_df)


st.header('Brazilian E-Commerce Store Dashboard :sparkles:')
st.subheader('Penjualan Produk')
st.write('Top 5 product categories')

# Plot 1: 5 Produk Terlaris
fig, ax = plt.subplots(figsize=(6, 4))
# Menampilkan hanya 5 produk teratas
top_products.plot(kind='barh', color='skyblue', ax=ax)
plt.xlabel('Number of Sales')
plt.ylabel('Product Category')
plt.title('Top 5 product categories')
plt.tight_layout()
# Menampilkan plot 1
st.pyplot(fig)


st.subheader('Distribusi Pelanggan Berdasarkan Kota')
st.write('top 10 highest customers based on Cities')
# Plot 2: Distribusi Pelanggan Tertinggi di Kota
top_cities = 10
top_customer_count_per_city = customer_count_per_city.head(
    top_cities).reset_index()  # Mengonversi Series menjadi DataFrame
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(x='customer_count', y='customer_city',
            data=top_customer_count_per_city, color='skyblue')

plt.xlabel('Customers')
plt.ylabel('City')
plt.title(f'Top {top_cities} Kota dengan Distribusi Pelanggan Tertinggi')
# Menampilkan plot 2
st.pyplot(fig2)


st.subheader('Sales Per Year')
# Plot 3: Tren Tahunan Jumlah Penjualan
fig3, ax3 = plt.subplots(figsize=(10, 6))
sales_per_year.plot(kind='line', marker='o', color='skyblue', ax=ax3)
plt.title('Sale Per Year')
plt.xlabel('Tahun')
plt.ylabel('Jumlah Penjualan')
plt.grid(True)
# Menampilkan plot 3
st.pyplot(fig3)

st.subheader('Analisis RFM')
st.write('Analisis RFM (Recency, Frequency, Monetary) digunakan untuk mengelompokkan pelanggan berdasarkan perilaku pembelian mereka.')
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(
        rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

# Plot 4: Pelanggan Terbaik Berdasarkan RFM Analysis
fig4, ax4 = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(
    by="recency", ascending=True).head(5), palette=colors, ax=ax4[0])
ax4[0].set_ylabel(None)
ax4[0].set_xlabel(None)
ax4[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax4[0].tick_params(axis='x', labelsize=15)
# Atur rotasi label sumbu x
ax4[0].set_xticklabels(ax4[0].get_xticklabels(), rotation=90)

sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(
    by="frequency", ascending=False).head(5), palette=colors, ax=ax4[1])
ax4[1].set_ylabel(None)
ax4[1].set_xlabel(None)
ax4[1].set_title("By Frequency", loc="center", fontsize=18)
ax4[1].tick_params(axis='x', labelsize=15)
# Atur rotasi label sumbu x
ax4[1].set_xticklabels(ax4[1].get_xticklabels(), rotation=90)

sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(
    by="monetary", ascending=False).head(5), palette=colors, ax=ax4[2])
ax4[2].set_ylabel(None)
ax4[2].set_xlabel(None)
ax4[2].set_title("By Monetary", loc="center", fontsize=18)
ax4[2].tick_params(axis='x', labelsize=15)
# Atur rotasi label sumbu x
ax4[2].set_xticklabels(ax4[2].get_xticklabels(), rotation=90)

plt.suptitle(
    "Pelanggan Terbaik Berdasarkan RFM Analysis (customer_unique_id)", fontsize=20)
# Menampilkan plot 4
st.pyplot(fig4)

st.caption('Copyright (c) Dila Aura Futri Dicoding 2025')
