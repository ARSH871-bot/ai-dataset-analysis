# Image Classification Dataset Analysis

Complete analysis package for AI image detection datasets.

## 📊 Quick Statistics

- **Total Datasets:** 6
- **Total Images:** 313,756
- **Real Images:** 128,850 (41%)
- **AI-Generated:** 184,906 (59%)

## 🚀 Quick Start

### Run Dashboard
```bash
cd analysis/dashboard
python -m streamlit run dashboard.py
```

### View Statistics
- JSON: `analysis/statistics/dataset_statistics.json`
- CSV: `analysis/statistics/dataset_statistics.csv`
- Excel: `analysis/statistics/dataset_statistics.xlsx`

## 📦 Package Contents
```
image-classification-analysis/
├── analysis/
│   ├── dashboard/          # Streamlit dashboard
│   ├── statistics/         # JSON, CSV, Excel
│   └── reports/            # Summary reports
├── scripts/                # Analysis scripts
├── docs/                   # Documentation
├── data/                   # Sample data
├── README.md               # This file
└── requirements.txt        # Dependencies
```

## 🔧 Requirements
```bash
pip install -r requirements.txt
```

## 📍 S3 Location
```
s3://ad-datascience/image-datasets/
```

## 📅 Last Updated

February 19, 2026
