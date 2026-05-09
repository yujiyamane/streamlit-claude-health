# Streamlit × Claude Code — ED Performance Dashboard

> **Enterprise-grade Emergency Department analytics dashboard built in 3 hours with Claude Code**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-FF6B35?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai/claude-code)

---

## 🚀 Live Demo

**[→ Open Dashboard](https://streamlit-claude-health.streamlit.app)**

---

## 📊 Project Overview

Interactive Emergency Department performance dashboard built with Streamlit and Plotly, demonstrating AI-accelerated full-stack data application development. Uses synthetic data modelled on Australian public health system patterns.

### Key Features

- **Executive Overview** — KPI cards, monthly trends, hospital-level compliance comparison
- **Wait Time Analysis** — Triage-based performance, wait time heatmaps by hour × day
- **Patient Flow** — Arrival patterns, departure outcomes, presenting complaints, arrival mode breakdown
- **Demand Forecasting** — Daily volume trends, rolling averages, year-over-year comparison, day-of-week patterns

### Technical Stack

```
Frontend:      Streamlit + Plotly
Backend:       Python (pandas, numpy)
Data:          150,000 synthetic ED visit records
Deployment:    Streamlit Community Cloud
AI Assistant:  Claude Code
```

---

## 📈 Dashboard Pages

### Page 1: Executive Overview
5 KPI cards (Total Visits, Median Wait, Median LOS, 4-Hour Compliance, Triage Target) with monthly volume/compliance dual-axis chart and hospital-level comparison.

### Page 2: Wait Time Analysis
Triage category performance with median and 90th percentile wait times, target compliance rates, and a heat map showing wait time patterns across hours and days of the week.

### Page 3: Patient Flow
Hourly arrival distribution, departure status breakdown (pie/donut), top 10 presenting complaints, and sunburst chart of arrival mode crossed with triage category.

### Page 4: Demand Forecasting
Daily ED volume with 7-day and 30-day moving averages, financial year comparison, and day-of-week average volume.

---

## 🔧 Local Development

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
git clone https://github.com/yujiyamane/streamlit-claude-health.git
cd streamlit-claude-health
pip install -r requirements.txt
```

### Generate Data

```bash
cd data
python generate_data.py
cd ..
```

### Run Locally

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 📁 File Structure

```
streamlit-claude-health/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit theme config
├── data/
│   ├── generate_data.py      # Synthetic data generator
│   └── ed_visits.csv         # 150K ED visit records
├── docs/
│   ├── before_after.md       # Development impact analysis
│   └── prompt_log.md         # Claude Code interaction log
├── screenshots/
│   ├── page1_overview.png
│   ├── page2_waittimes.png
│   ├── page3_flow.png
│   └── page4_forecast.png
└── README.md
```

---

## 🎯 Data Model

Single denormalised table: `ed_visits.csv` (150,000 records)

| Field | Description |
|-------|-------------|
| `visit_id` | Unique visit identifier |
| `arrival_datetime` | Arrival timestamp |
| `hospital` / `hospital_code` / `lhd` | Hospital and Local Health District |
| `triage_category` / `triage_name` | Triage classification (1-5) |
| `wait_time_minutes` | Time to first clinical contact |
| `los_minutes` | Total length of stay in ED |
| `seen_within_target` | Met triage-specific wait target (0/1) |
| `four_hour_compliant` | Total LOS ≤ 240 min (0/1) |
| `arrival_mode` | Ambulance, Walk-in, etc. |
| `departure_status` | Discharged, Admitted, etc. |
| `presenting_complaint` | Reason for visit |
| `age_group` / `gender` | Demographics |
| `financial_year` | Australian FY (Jul–Jun) |

### Realistic Data Patterns

- **Seasonal variation**: Winter flu season (Jun–Aug) increases
- **Time-of-day**: Peak arrivals 10:00–14:00, low overnight
- **Triage-dependent**: Higher acuity → ambulance arrival, longer LOS, more admissions
- **Hospital variation**: Different performance profiles across 10 hospitals
- **Weekend/Monday effect**: Increased wait times on weekends and Mondays

---

## ⚡ Before / After

| Metric | Traditional | Claude Code | Improvement |
|--------|-------------|-------------|-------------|
| **Development Time** | 10+ days | 3 hours | **96% reduction** |
| **Data Generation** | 1-2 days | 20 minutes | **95% reduction** |
| **Dashboard Build** | 5-7 days | 2 hours | **93% reduction** |
| **Documentation** | 1-2 days | 20 minutes | **95% reduction** |
| **Deployment** | 1 day | 10 minutes | **93% reduction** |

---

## 👨‍💻 Author

**Yuji Yamane** — BI Developer | AI-augmented analytics
- GitHub: [yujiyamane](https://github.com/yujiyamane)
- Location: Sydney, Australia