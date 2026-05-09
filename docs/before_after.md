# Before vs After: Claude Code Impact on Streamlit Dashboard Development

## Project Overview

**Challenge**: Build an interactive ED Performance Dashboard accessible via URL
**Complexity**: 150K records, 4 dashboard pages, real-time filtering, Streamlit Cloud deployment
**Target**: Production-quality analytics application anyone can access

---

## Timeline Comparison

| Phase | Traditional Method | Claude Code | Time Reduction |
|-------|-------------------|-------------|----------------|
| **Planning & Design** | 1-2 days | 15 minutes | **97% reduction** |
| **Implementation & Build** | 5-7 days | 40 minutes | **95% reduction** |
| **Data Generation** | 1-2 days | 2 minutes | **99% reduction** |
| **Documentation** | 1-2 days | 2 minutes | **99% reduction** |
| **Deployment** | 1 day | 1 minute | **99% reduction** |
| **Total** | **10-15 days** | **1 hour (60 min)** | **98%+ reduction** |

---

## What Claude Code Did

### 1. Data Architecture
- Designed denormalised ED visit schema optimised for Streamlit filtering
- Generated 150K realistic records with clinically plausible distributions
- Built in triage-dependent patterns, seasonal variation, hospital-level performance differences

### 2. Full-Stack Streamlit Application
- 4-page multi-view dashboard with sidebar navigation
- Custom CSS theming matching Statewide Health brand
- Responsive layout with dynamic filtering (hospital, LHD, FY, triage)
- 12+ Plotly visualisations including heatmaps, sunbursts, dual-axis charts

### 3. Deployment Pipeline
- Streamlit Cloud configuration
- Requirements management
- Production-ready caching with `@st.cache_data`

---

## What I Did Manually

- Reviewed data distributions for clinical realism
- Adjusted colour palette and UX details
- Tested filter interactions and edge cases
- Deployed to Streamlit Cloud (connected GitHub repo)
- Captured screenshots and recorded demo GIF

---

## Key Insight

Claude Code delivered a **complete, deployable web application** — not just a script or notebook. The result is a live URL that anyone can interact with, which is fundamentally different from a static .pbix file.

The combination of Power BI (Case 1) and Streamlit (Case 2) demonstrates versatility: enterprise BI tools AND custom web applications, both accelerated by AI.