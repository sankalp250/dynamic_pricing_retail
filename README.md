📊 Dynamic Pricing & Retail Analytics Engine
<p align="center"><em>An end-to-end data science application that transforms raw sales data into interactive tools for business intelligence and predictive analytics.</em></p> <p align="center"> <img src="docs/images/dashboard.png" alt="Executive Dashboard Screenshot"/> </p>
🚀 Live Demonstrations
🔗 Live Streamlit App

📊 Live Tableau Dashboard

📝 Project Summary & Purpose
Retailers struggle to set the right price in dynamic markets. This project solves that with a full-stack data pipeline and AI-driven insights. It cleans raw sales data, loads it into MySQL, runs advanced analytics (RFM segmentation, forecasting, elasticity modeling), and presents it through a Streamlit app and Tableau dashboard.

The goal is to enable real-time price simulations, customer behavior analysis, and actionable decision-making—all backed by clean, reliable data.

✨ Key Features & Screenshots
💰 Profit Forecasting & Price Recommendation
Simulate price changes and predict revenue impact using the automated recommendation engine.

<p align="center"> <img src="docs/images/simulator.png" width="800" alt="Profit Simulator Screenshot"/> </p>
📈 Time-Series Demand Forecasting
Uses Facebook Prophet to predict future sales revenue by product or category.

<p align="center"> <img src="docs/images/forecast.png" width="800" alt="Forecast Screenshot"/> </p>
👥 RFM Customer Segmentation
Cluster customers using Recency, Frequency, and Monetary metrics into actionable groups.

<p align="center"> <img src="docs/images/segments.png" width="800" alt="Customer Segments Screenshot"/> </p>
🔄 Cross-Price Elasticity
Understand if products behave as substitutes or complements to optimize bundle pricing.

<p align="center"> <img src="docs/images/cross_price.png" width="800" alt="Cross-Price Screenshot"/> </p>
📊 Executive BI Dashboard
Summarized Tableau dashboard for senior stakeholders.

<p align="center"> <img src="docs/images/tableau.png" width="800" alt="Tableau Dashboard Screenshot"/> </p>
🛠️ Tech Stack
<p align="left"> <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white"/> <img src="https://img.shields.io/badge/scikit--learn-F7931A?style=for-the-badge&logo=scikit-learn&logoColor=white"/> <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/> <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/> <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"/> <img src="https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white"/> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/> </p>

📁 Project Structure

'''
dynamic_pricing_retail/
│
├── config/                  # Configuration files (e.g., config.ini.template)
├── data/
│   ├── raw/                 # Raw CSV data
│   └── exports_for_tableau/ # Cleaned CSVs for Tableau
├── docs/
│   └── images/              # README screenshots
├── scripts/
│   ├── 1_run_etl.py         # Clean and load data into MySQL
│   ├── 2_run_analysis_and_export.py # Analysis + MySQL update
│   └── 3_create_parquet_export.py   # Export final Parquet
├── src/
│   ├── analysis/            # Analytical models (elasticity, segmentation)
│   ├── data_processing/     # Data cleaning
│   └── database/            # DB connection helpers
├── streamlit_app/
│   ├── App.py               # Main Streamlit app
│   ├── assets/              # CSS and images
│   ├── components/          # Reusable UI parts
│   ├── data/                # Final Parquet file
│   └── pages/               # Streamlit sub-pages
├── .gitignore
├── README.md
└── requirements.txt '''

⚙️ How to Reproduce Locally
✅ Prerequisites
Python 3.9+

MySQL Server

🔧 1. Clone & Set Up Environment

git clone https://github.com/sankalp250/dynamic_pricing_retail.git
cd dynamic_pricing_retail
python -m venv .venv
source .venv/bin/activate  # Use .venv\Scripts\activate on Windows
pip install -r requirements.txt


🗄️ 2. Set Up MySQL
    Create a new MySQL database and user.

    Update config/config.ini.template with your credentials, rename to config.ini.  

🛠️ 3. Run Data Pipeline
Place Olist CSVs into data/raw/.

# Step 1: ETL
python scripts/1_run_etl.py

# Step 2: Analysis
python scripts/2_run_analysis_and_export.py

# Step 3: Export to Parquet
python scripts/3_create_parquet_export.py

🚀 4. Launch the App

streamlit run streamlit_app/App.py

☁️ Deployment

The Streamlit app is deployed via Streamlit Community Cloud, linked directly to this GitHub repo. It runs in a self-contained mode using master_data.parquet to ensure reliability and speed.