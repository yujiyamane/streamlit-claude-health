# Prompt Engineering Log — ED Performance Dashboard

This file records the Claude Code interactions used to build the Streamlit ED Performance Dashboard.

---

## Session 1: Data Architecture & Generation (20 min)

### Prompt 1.1: Data Model Design
```
Design a denormalised data model for an ED performance dashboard.
150K records, 10 hospitals across 5 LHDs, 2 Australian financial years.
Include: triage categories 1-5, wait times, LOS, arrival modes, departure status,
presenting complaints, demographics. Optimise for Streamlit sidebar filtering.
```

**Result**: Single CSV schema with 22 fields, triage-dependent distributions, hospital-level performance variation.

### Prompt 1.2: Realistic Data Patterns
```
Generate clinically plausible patterns:
- Winter flu season surge (Jun-Aug)
- Time-of-day arrival curves (peak 10-14, low overnight)
- Triage-dependent: higher acuity → more ambulance arrivals, longer LOS
- Hospital-level performance variation
- Weekend/Monday effect on wait times
```

**Result**: Multi-factor multiplier system producing statistically realistic distributions.

---

## Session 2: Streamlit Application (2 hours)

### Prompt 2.1: App Architecture
```
Build a 4-page Streamlit app with sidebar navigation and global filters.
Pages: Executive Overview, Wait Time Analysis, Patient Flow, Demand Forecast.
Use Plotly for all charts. Custom CSS matching brand colours #002664 and #C00000.
Cache data loading with @st.cache_data.
```

**Result**: Complete app.py with 4 page functions, sidebar filters (hospital, LHD, FY, triage), 12+ visualisations.

### Prompt 2.2: Visualisation Design
```
For each page, design impactful visualisations:
- Overview: KPI cards + dual-axis monthly chart + hospital compliance bars
- Wait Times: Triage breakdown + heatmap (hour × day)
- Patient Flow: Hourly arrivals + departure pie + complaints bar + sunburst
- Forecast: Daily volume with rolling averages + YoY comparison + DOW pattern
```

**Result**: Professional-grade Plotly charts with conditional colouring, reference lines, and interactive hover.

---

## Session 3: Deployment & Documentation (20 min)

### Prompt 3.1: Streamlit Cloud Setup
```
Configure for Streamlit Community Cloud deployment:
- requirements.txt
- .streamlit/config.toml with theme
- Data path handling for both local and cloud environments
```

**Result**: Production-ready deployment configuration.

### Prompt 3.2: Documentation
```
Create README with live demo link, setup instructions, data model documentation,
before/after comparison, and file structure. All in English.
```

**Result**: Comprehensive README with badges, tables, and code blocks.

---

## Effective Patterns Used

### 1. Single-session full-stack
Instead of breaking into micro-tasks, described the complete app in one prompt. Claude Code delivered a working application end-to-end.

### 2. Brand-first design
Specifying exact hex colours and design language upfront produced consistent theming across all pages.

### 3. Data-viz specificity
Naming exact chart types (sunburst, dual-axis, heatmap) rather than leaving it to AI produced better results than "create appropriate visualisations."

### 4. Deployment awareness
Mentioning Streamlit Cloud from the start influenced data path handling and caching strategy.

---

## Total Time: ~3 hours
## Traditional estimate: 10-15 days
## Speed multiplier: ~30x faster