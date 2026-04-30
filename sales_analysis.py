
# PRAKTIKUM ANALISIS DATA

# Import Library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


# 1. LOAD DATA

df = pd.read_csv("data_praktikum.csv")

# ubah format tanggal
df['Order_Date'] = pd.to_datetime(df['Order_Date'])

print("Preview Data:")
print(df.head())


# 2. IDENTIFIKASI PRODUK UNDERPERFORMER

print("\n===== PRODUK UNDERPERFORMER =====")

# rata-rata harga
avg_price = df['Price_Per_Unit'].mean()

# filter harga di atas rata-rata
high_price = df[df['Price_Per_Unit'] > avg_price]

# quantity paling kecil
underperformer = high_price.sort_values('Quantity').head(10)

print(underperformer[['Product_Category','Price_Per_Unit','Quantity']])



# 3. RFM ANALYSIS

print("\n===== RFM ANALYSIS =====")

snapshot_date = df['Order_Date'].max() + dt.timedelta(days=1)

rfm = df.groupby('CustomerID').agg({
    'Order_Date': lambda x: (snapshot_date - x.max()).days,
    'Order_ID': 'count',
    'Total_Sales': 'sum'
})

rfm.columns = ['Recency','Frequency','Monetary']

# scoring
rfm['R_Score'] = pd.qcut(rfm['Recency'],5,labels=[5,4,3,2,1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'),5,labels=[1,2,3,4,5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'],5,labels=[1,2,3,4,5])

rfm['RFM_Group'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

print(rfm.head())


# 4. ANALISIS EFISIENSI KATEGORI

print("\n===== EFISIENSI IKLAN PER KATEGORI =====")

category = df.groupby('Product_Category').agg({
    'Total_Sales':'sum',
    'Ad_Budget':'sum'
})

category['Efficiency'] = category['Total_Sales'] / category['Ad_Budget']

category = category.sort_values('Efficiency')

print(category)


# visualisasi
plt.figure(figsize=(8,6))

category['Efficiency'].plot(kind='barh')

plt.title("Advertising Efficiency by Category")
plt.xlabel("Sales / Ad Budget")

plt.show()


# 5. UJI HIPOTESIS IKLAN

print("\n===== UJI HIPOTESIS IKLAN =====")

median_budget = df['Ad_Budget'].median()

high_ads = df[df['Ad_Budget'] > median_budget]
low_ads = df[df['Ad_Budget'] <= median_budget]

avg_high = high_ads['Total_Sales'].mean()
avg_low = low_ads['Total_Sales'].mean()

print("Average Sales High Ads :", avg_high)
print("Average Sales Low Ads :", avg_low)


# visualisasi
df['Ad_Group'] = df['Ad_Budget'].apply(
    lambda x: 'High Ads' if x > median_budget else 'Low Ads'
)

plt.figure(figsize=(6,6))

sns.boxplot(
    x='Ad_Group',
    y='Total_Sales',
    data=df
)

plt.title("Sales Comparison: High vs Low Ads")

plt.show()


# 6. REGRESI LINEAR

print("\n===== REGRESI LINEAR =====")

X = df[['Ad_Budget']]
y = df['Total_Sales']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

model = LinearRegression()

model.fit(X_train, y_train)

print("Koefisien Iklan :", model.coef_[0])
print("R2 Score :", model.score(X_test, y_test))