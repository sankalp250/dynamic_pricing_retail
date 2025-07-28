# Dynamic Pricing & Retail Analytics Engine

<p align="center">
  <em>An end-to-end data science application that transforms raw sales data into a suite of powerful, interactive tools for business intelligence and predictive analytics.</em>
</p>

<!-- INSTRUCTIONS: Place your 'dashboard.png' screenshot in the 'docs/images' folder. -->
<p align="center">
  <img src="docs/images/dashboard.png" alt="Executive Dashboard Screenshot"/>
</p>

---

### 🚀 Live Demonstrations

*   **Live Streamlit Application:** [**Click here to view the live app**] https://dynamicpricingretail-wptjwk9uswhjzgqcekjg2f.streamlit.app/ 

*   **Live Tableau Dashboard:** [**Click here to view the live dashboard**]https://public.tableau.com/app/profile/sankalp.singh5474/viz/Book1_17535658131970/Dashboard1 ---

---

### 📝 Project Summary & Purpose

In the competitive retail landscape, setting the optimal price for products is a critical challenge. Static pricing strategies often fail to adapt to market dynamics, leading to lost revenue and inefficient inventory management. This project tackles this problem by building a comprehensive, end-to-end analytics platform that provides data-driven answers to crucial business questions.

The core of this project is a robust **data pipeline** that ingests raw, relational sales data, cleans it using Python and Pandas, and structures it within a **local MySQL database**. This "Data Factory" then serves as the foundation for all subsequent analysis. Advanced machine learning models are used to perform **RFM customer segmentation**, **time-series demand forecasting**, and **price elasticity modeling**.

The final output is not just a report, but a suite of live, interactive tools. A **deployed Streamlit application** serves as the primary interface, allowing users to explore customer behavior, simulate the revenue impact of price changes, and receive AI-driven price recommendations. For high-level reporting, key insights are also aggregated and presented in a polished **Tableau dashboard** suitable for executive stakeholders.

---

## ✨ Key Features & Screenshots

### Profit Forecasting & Price Recommendation
This feature empowers users to simulate price changes and see the projected impact on demand and revenue in real-time. The "Automated Recommendation" button runs hundreds of scenarios to find the optimal price that maximizes revenue within a realistic range.

<!-- INSTRUCTIONS: Place your 'simulator.png' screenshot in the 'docs/images' folder. -->
<p align="center">
  <img src="docs/images/simulator.png" alt="Profit Simulator Screenshot" width="800"/>
</p>

### Time-Series Demand Forecasting
Using Facebook's Prophet library, this tool forecasts future sales revenue for the entire business or for specific product categories, providing valuable insights for inventory and financial planning.

<!-- INSTRUCTIONS: Place your 'forecast.png' screenshot in the 'docs/images' folder. -->
<p align="center">
  <img src="docs/images/forecast.png" alt="Demand Forecast Screenshot" width="800"/>
</p>

### RFM Customer Segmentation Deep-Dive
Instead of just viewing customers as a monolith, the application uses RFM analysis and K-Means clustering to segment them into actionable groups like "Best Customers," "Loyal," and "At-Risk," complete with KPIs and behavioral summaries.

<!-- INSTRUCTIONS: Place your 'segments.png' screenshot in the 'docs/images' folder. -->
<p align="center">
  <img src="docs/images/segments.png" alt="Customer Segments Screenshot" width="800"/>
</p>

### Cross-Price Elasticity Analysis
A sophisticated tool that moves beyond single-product analysis to discover hidden relationships between products, identifying whether they behave as **Substitutes** (competitors) or **Complements** (bought together).

<!-- INSTRUCTIONS: Place your 'cross_price.png' screenshot in the 'docs/images' folder. -->
<p align="center">
  <img src="docs/images/cross_price.png" alt="Cross-Price Elasticity Screenshot" width="800"/>
</p>

### Executive BI Dashboard in Tableau
For high-level, at-a-glance reporting, a summary of the key insights is presented in a polished and interactive Tableau dashboard, suitable for business stakeholders.

<!-- INSTRUCTIONS: Place your 'tableau.png' screenshot in the 'docs/images' folder. -->
<p align="center">
  <img src="docs/images/tableau.png" alt="Tableau Dashboard Screenshot" width="800"/>
</p>

---

## 🛠️ Tech Stack

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/scikit--learn-F7931A?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly"/>
  <img src="https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white" alt="Tableau"/>
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
</p>

---

## 📂 Project Structure

The project is organized into a modular structure that separates the data processing backend, analysis code, and the frontend application.