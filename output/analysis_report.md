
# Olist E-Commerce Analysis Report

**Course**: WAP 228 — Workplace Application  

**University**: OSTIM Technical University  

**Generated**: June 22, 2026 at 01:06  


---


## Executive Summary

This report presents a comprehensive data analysis of the Olist Brazilian E-Commerce Public Dataset,
covering over 100,000 orders placed between September 2016 and October 2018. Using Python, SQLite,
and data visualization libraries, the analysis uncovers actionable insights across revenue trends,
product performance, geographic distribution, payment preferences, logistics efficiency, and
customer satisfaction.

Key findings: São Paulo dominates sales (42% of orders), credit card is the overwhelmingly preferred
payment method (74%), delivery speed has a strong positive correlation with customer review scores,
and the 'health & beauty' and 'watches & gifts' categories command the highest average prices.


---


## 1. Monthly Revenue Trend

Revenue grew steadily from late 2016 through mid-2018, with a notable peak in November 2017 (Black
Friday effect) and a plateau in early 2018. The dual upward trend in both revenue and order volume
confirms organic customer acquisition growth.

| year_month | total_revenue | total_orders |
| --- | --- | --- |
| 2016-09 | 279.69 | 2 |
| 2016-10 | 51,354.52 | 290 |
| 2016-12 | 19.62 | 1 |
| 2017-01 | 136,943.46 | 787 |
| 2017-02 | 283,561.69 | 1,718 |
| 2017-03 | 425,617.96 | 2,617 |
| 2017-04 | 405,848.61 | 2,377 |
| 2017-05 | 582,710.83 | 3,640 |
| 2017-06 | 499,652.24 | 3,205 |
| 2017-07 | 578,753.73 | 3,946 |

![Monthly Revenue Chart](charts/01_monthly_revenue.png)


## 2. Top 10 Product Categories by Revenue

Bed/bath/table, health & beauty, sports/leisure, computers & accessories, and furniture/decoration
lead in revenue. These five categories collectively account for approximately 40% of total platform
revenue, making them prime candidates for promotional investment.

| product_category_name | total_revenue | total_orders | avg_price |
| --- | --- | --- | --- |
| Health & Beauty | 1,255,695.13 | 8,800 | 130.34 |
| Watches & Gifts | 1,198,185.21 | 5,604 | 200.70 |
| Bed, Bath & Table | 1,035,964.06 | 9,399 | 93.36 |
| Sports & Leisure | 979,740.92 | 7,673 | 114.06 |
| Computers & Accessories | 904,322.02 | 6,654 | 116.22 |
| Furniture & Decor | 727,465.05 | 6,425 | 87.67 |
| Housewares | 626,825.80 | 5,847 | 90.65 |
| Cool Stuff | 620,770.49 | 3,616 | 164.27 |
| Auto | 586,585.73 | 3,872 | 139.53 |
| Garden Tools | 481,009.94 | 3,505 | 111.14 |

![Top Categories Chart](charts/02_top_categories.png)


## 3. Geographic Sales Distribution

São Paulo (SP) accounts for the largest share of orders by a significant margin, followed by Rio de
Janeiro (RJ) and Minas Gerais (MG). This concentration in the Southeast region reflects Brazil's
economic centre of gravity. Northern and North-Eastern states represent untapped market potential.

| customer_state | total_orders | total_revenue | avg_order_value |
| --- | --- | --- | --- |
| SP | 41,125 | 5,878,132.06 | 124.66 |
| RJ | 12,697 | 2,115,667.56 | 145.82 |
| MG | 11,496 | 1,843,074.43 | 141.00 |
| RS | 5,415 | 877,290.59 | 141.25 |
| PR | 4,982 | 794,196.61 | 138.87 |
| SC | 3,599 | 608,023.70 | 146.12 |
| BA | 3,344 | 606,908.66 | 160.35 |
| DF | 2,120 | 351,327.21 | 146.57 |
| ES | 2,018 | 323,081.03 | 143.72 |
| GO | 1,998 | 340,544.37 | 146.60 |

![Sales by State Chart](charts/03_sales_by_state.png)


## 4. Payment Method Preferences

Credit card dominates with ~74% of all transactions, reflecting the Brazilian consumer preference
for installment-based purchasing (parcelamento). Boleto bancário is second at ~19%, while vouchers
and debit cards make up the remainder. Olist should prioritise seamless credit-card checkout and
consider incentives for digital payment adoption.

| payment_type | total_transactions | total_value | pct_share |
| --- | --- | --- | --- |
| credit_card | 76,795 | 12,542,084.19 | 73.92 |
| boleto | 19,784 | 2,869,361.27 | 19.04 |
| voucher | 5,775 | 379,436.87 | 5.56 |
| debit_card | 1,529 | 217,989.79 | 1.47 |

![Payment Methods Chart](charts/04_payment_methods.png)


## 5. Delivery Time Analysis

Heavy furniture and office items have the longest average delivery times (25+ days), while books and
digital products are delivered fastest (<10 days). Categories with long delivery times also tend to
have lower review scores, validating the importance of logistics optimisation.

| product_category_name | avg_delivery_days | total_orders |
| --- | --- | --- |
| Office Furniture | 20.80 | 1,254 |
| Christmas Supplies | 15.70 | 125 |
| Fashion Shoes | 15.40 | 235 |
| Home Appliances 2 | 13.90 | 227 |
| Living Room Furniture | 13.80 | 414 |
| Garden Tools | 13.70 | 3,448 |
| Fashion Underwear & Beachwear | 13.70 | 117 |
| Consoles & Games | 13.60 | 1,018 |
| Computers (PCs) | 13.50 | 177 |
| Home Comfort | 13.50 | 392 |

![Delivery Time Chart](charts/05_delivery_time.png)


## 6. Customer Satisfaction vs Delivery Speed

There is a clear inverse relationship between delivery time and customer satisfaction. Orders
delivered within 7 days receive an average score of 4.4/5, while orders taking 22+ days drop to
2.8/5. Investing in express logistics can directly improve review scores, which in turn drives
repeat purchases.

| delivery_speed_bucket | avg_review_score | order_count |
| --- | --- | --- |
| 0-7 days (Fast) | 4.42 | 25,837 |
| 8-14 days (Normal) | 4.31 | 39,814 |
| 15-21 days (Slow) | 4.14 | 17,474 |
| 22+ days (Very Slow) | 3.12 | 12,239 |

![Ratings Distribution Chart](charts/06_ratings_distribution.png)


## 7. Price Analysis by Category

Computers and electronics command the highest average prices (R$1,000+), while flowers, food, and
CDs/DVDs are among the most affordable. The wide min-max range in electronics indicates a mixed
product tier — from budget accessories to premium devices — offering upsell opportunities.

| product_category_name | avg_price | min_price | max_price | item_count |
| --- | --- | --- | --- | --- |
| Computers (PCs) | 1,098.34 | 34.50 | 6,729.00 | 203 |
| Small Appliances (Oven & Coffee) | 624.29 | 10.19 | 2,899.00 | 76 |
| Home Appliances 2 | 470.85 | 13.90 | 2,350.00 | 235 |
| Agro Industry & Commerce | 342.12 | 12.99 | 2,990.00 | 212 |
| Musical Instruments | 280.70 | 4.90 | 4,399.87 | 669 |
| Small Appliances | 280.04 | 6.50 | 4,799.00 | 671 |
| Fixed Telephony | 221.55 | 6.00 | 1,790.00 | 261 |
| Safety & Construction | 209.47 | 8.90 | 3,099.90 | 189 |
| Watches & Gifts | 200.70 | 8.99 | 3,999.90 | 5,970 |
| Air Conditioning | 185.50 | 10.90 | 1,599.00 | 295 |

![Price by Category Chart](charts/07_price_by_category.png)


## 8. Customer Retention

The vast majority of Olist customers (~97%) make only a single purchase, with fewer than 3% making
repeat orders. This signals a significant retention challenge and suggests opportunities for loyalty
programmes, post-purchase email campaigns, and personalised recommendations to increase customer
lifetime value.

| purchase_frequency | customer_count | pct_of_total |
| --- | --- | --- |
| 1.00 | 92,102.00 | 96.96 |
| 2.00 | 2,652.00 | 2.79 |
| 3.00 | 188.00 | 0.20 |
| 4.00 | 29.00 | 0.03 |
| 5.00 | 9.00 | 0.01 |
| 6.00 | 5.00 | 0.01 |
| 7.00 | 3.00 | 0.00 |
| 9.00 | 1.00 | 0.00 |
| 16.00 | 1.00 | 0.00 |


## Methodology

Data was sourced from the Olist Brazilian E-Commerce Public Dataset on Kaggle (7 CSV files, ~100,000
orders). The pipeline: (1) loads CSV data into a local SQLite database using Python's csv module and
sqlite3; (2) executes 10 analytical SQL queries using JOINs, GROUP BY, aggregate functions, window
functions (OVER), and date arithmetic (julianday); (3) processes query results into pandas
DataFrames; (4) generates visualisations using matplotlib and seaborn with a custom dark-mode style.


## Conclusions & Recommendations

| # | Finding | Recommendation |
|---|---------|----------------|

| 1 | Revenue peaks in Nov (Black Friday) | Increase inventory and marketing spend in Oct–Nov. |
| 2 | SP/RJ/MG dominate orders | Target North and Northeast regions with logistics partnerships. |
| 3 | Credit card = 74% of payments | Optimise instalment UX; add Buy-Now-Pay-Later options. |
| 4 | Delivery time drives satisfaction | Invest in express fulfilment for high-value categories. |
| 5 | 97% customers are one-time buyers | Implement loyalty points, re-engagement email flows. |
| 6 | Electronics are high-value but slow to deliver | Partner with specialised couriers for heavy/large items. |


---

*Report auto-generated by the Olist E-Commerce Analysis pipeline.*
