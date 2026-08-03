<div align="center">

# ⚡ DataCleanX Studio

<p align="center">
  <b>The Smart Data Cleaning, Analysis & Interactive Visualization Platform</b>
</p>

<p align="center">
  <a href="#-about-the-project">About</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-key-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-repository-structure">Structure</a> •
  <a href="#-security--performance">Security</a> •
  <a href="#-license">License</a>
</p>

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat-square&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=flat-square)

</div>

---

## 💡 About The Project

**DataCleanX Studio** is an open-source, high-performance data analytics and data cleaning workspace designed for data analysts, engineers, researchers, and businesses. 

It provides an all-in-one interactive web interface for handling Excel files (`.xlsx`, `.xls`), CSV, JSON, and Parquet formats. Users can perform 1-click missing value imputation, duplicate removal, text normalization, exploratory data analysis (EDA), feature engineering, and export beautifully formatted reports.

---

## 🛠️ Tech Stack & Technologies Used

The application is built using modern, production-grade open-source technologies:

| Category | Technology | Description |
| :--- | :--- | :--- |
| **Core Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | Core data processing and algorithm engine |
| **Web UI Framework** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | Modern reactive Python web framework |
| **Data Processing** | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white) | High-performance vector data manipulation |
| **Statistical Computing** | ![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=flat-square&logo=scipy&logoColor=white) | Outlier detection, interpolation, and distributions |
| **Data Visualizations** | ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white) ![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat-square&logo=chartdotjs&logoColor=white) | Interactive 2D/3D charts and executive 2x2 dashboards |
| **Excel & File Engines** | **OpenPyXL / XlsxWriter / SheetJS** | Native Excel formatting, multi-sheet, and parsing engines |
| **Styling & Aesthetics** | **Vanilla CSS3 / Glassmorphism** | Custom dark theme design system with Google Fonts (Tajawal) |
| **Security & Caching** | **Streamlit Cache & Regex Engine** | In-memory `@st.cache_data` and Formula Injection sanitization |

---

## ✨ Key Features

### 🧩 1. Data Cleaning & Imputation Suite
* **1-Click Smart Auto-Impute**: Automatically fills missing numerical cells with median values and categorical text with mode.
* **Group-By Imputation**: Imputes missing values in a target column based on group statistics of another category column.
* **Duplicate Elimination**: Detects and drops exact duplicate rows across all or selected columns.
* **Text Normalization**: Strips whitespace, adjusts casing, removes special characters, and performs regex search & replace.
* **Outlier Treatment**: Detects outliers using IQR or Z-score algorithms with clipping or removal actions.

### 📊 2. Visual Impact & Comparison
* **Before vs After Cleaning Chart**: Displays a comparative visual breakdown of missing cell counts before and after cleaning.
* **Dual Preview**: Inspect raw input data side-by-side with cleaned output.

### 📈 3. Vibrant Interactive Charts & Dashboards
* **5 Modern Color Themes**: Instant theme switching (Vivid Neon, Cyberpunk, Sunset, Emerald, Midnight Galaxy).
* **2x2 Executive Dashboard**: Synchronized 4-chart executive view (Bar, Histogram, Donut, Box Plot).
* **Multiple Chart Types**: Bar, Line, Area, Scatter, Donut/Pie, Treemap, Sunburst, Histogram, and Scatter Matrix (SPLOM).

### ⚙️ 4. Feature Engineering & Exploratory Analytics
* **Calculated Columns**: Perform mathematical operations (multiply, divide, add, subtract) between numeric features.
* **Datetime Feature Extraction**: Extract Year, Month, Day, Day of Week, and Quarter from date fields automatically.
* **Data Health & Insights**: Automated quality scores, missingness matrix, correlation heatmap, and descriptive statistics.

---

## 💻 Quick Start

To run DataCleanX Studio locally on your system:

```bash
# Clone the repository
git clone https://github.com/username/DataCleanX-Studio.git

# Navigate into the project directory
cd DataCleanX-Studio

# Install dependencies
pip install -r requirements.txt

# Launch the application
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

### Standalone Web App
Alternatively, you can open [`index.html`](index.html) directly in any web browser without installing any Python packages.

---

## 📁 Repository Structure

```text
DataCleanX-Studio/
├── app.py                      # Main Streamlit Application
├── index.html                  # Standalone Web Application
├── requirements.txt            # Python Dependencies
├── README.md                   # Public Documentation
├── sample_dataset.csv          # Sample CSV Data File
├── sample_dataset.json         # Sample JSON Data File
├── .streamlit/
│   └── config.toml             # Dark Modern Theme Configuration
└── modules/
    ├── __init__.py             # Python Package Marker
    ├── sample_data.py          # Sample Data Generator
    ├── data_loader.py          # Multi-format Data Reader & Security Sanitizer
    ├── cleaner.py              # Data Imputation & Feature Engineering
    ├── analyzer.py             # Exploratory Analysis & Statistics
    ├── visualizer.py           # Color Palettes & Interactive Visualizations
    └── exporter.py             # Security-Sanitized Binary Exporter
```

---

## 🔒 Security & Performance

* **Memory DoS Protection**: Enforces a 50MB file size limit to guarantee server stability.
* **Formula Injection Mitigation**: Strips malicious leading characters (`=`, `+`, `-`, `@`) upon export.
* **Performance Caching**: Uses `@st.cache_data` for instantaneous calculation of statistics and correlation matrices.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

<div align="center">
  <br>
  <sub>Built for the global data community • DataCleanX Studio 2026</sub>
</div>
