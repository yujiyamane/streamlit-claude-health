#!/usr/bin/env python3
"""
Statewide Health ED Performance Dashboard - Data Generator

Generates realistic Emergency Department data for Streamlit dashboard.
150K ED visit records across 10 hospitals, 2 financial years.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

HOSPITALS = {
    "Metro Central": [
        ("Royal Metropolitan Hospital", "RMH", 80),
        ("Prince George Hospital", "PGH", 60),
    ],
    "Metro South": [
        ("St Andrews Hospital", "SAH", 55),
        ("Bayside General Hospital", "BGH", 50),
    ],
    "Metro West": [
        ("Westfield Hospital", "WFH", 70),
        ("Parklands Hospital", "PKH", 45),
    ],
    "Metro North": [
        ("Northern Districts Hospital", "NDH", 50),
        ("Harbour View Hospital", "HVH", 40),
    ],
    "Regional South": [
        ("Southern Regional Hospital", "SRH", 35),
        ("Coastal Community Hospital", "CCH", 25),
    ],
}

TRIAGE_CATEGORIES = {
    1: {"name": "Resuscitation", "target_min": 0, "weight": 0.02, "base_wait": 2, "base_los": 180},
    2: {"name": "Emergency", "target_min": 10, "weight": 0.10, "base_wait": 8, "base_los": 240},
    3: {"name": "Urgent", "target_min": 30, "weight": 0.30, "base_wait": 25, "base_los": 200},
    4: {"name": "Semi-urgent", "target_min": 60, "weight": 0.40, "base_wait": 45, "base_los": 150},
    5: {"name": "Non-urgent", "target_min": 120, "weight": 0.18, "base_wait": 90, "base_los": 100},
}

AGE_GROUPS = ["0-4", "5-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85+"]
AGE_WEIGHTS = [0.08, 0.06, 0.12, 0.11, 0.10, 0.12, 0.14, 0.12, 0.10, 0.05]

ARRIVAL_MODES = ["Ambulance", "Walk-in", "Police/Corrections", "Helicopter", "Other"]
ARRIVAL_WEIGHTS = [0.30, 0.62, 0.03, 0.01, 0.04]

DEPARTURE_STATUS = ["Discharged", "Admitted", "Transferred", "Left before treatment", "Died in ED", "Left at own risk"]
DEPARTURE_WEIGHTS = [0.55, 0.28, 0.05, 0.06, 0.005, 0.055]

PRESENTING_COMPLAINTS = [
    "Chest pain", "Abdominal pain", "Shortness of breath", "Laceration",
    "Back pain", "Headache", "Fracture/Dislocation", "Fever",
    "Mental health crisis", "Overdose/Poisoning", "Falls", "Allergic reaction",
    "Seizure", "Motor vehicle accident", "Assault injury", "Urinary symptoms",
    "Skin infection", "Eye injury", "Dental pain", "Other"
]
COMPLAINT_WEIGHTS = [
    0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.06, 0.05,
    0.05, 0.04, 0.05, 0.03, 0.03, 0.04, 0.03, 0.03,
    0.03, 0.02, 0.02, 0.06
]


def generate_ed_visits(n=150000):
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2026, 6, 30)
    total_days = (end_date - start_date).days

    all_hospitals = []
    for lhd, hospitals in HOSPITALS.items():
        for name, code, daily_avg in hospitals:
            all_hospitals.append((lhd, name, code, daily_avg))

    total_daily = sum(h[3] for h in all_hospitals)

    rows = []
    for i in range(n):
        r = np.random.random() * total_daily
        cumulative = 0
        for lhd, hosp_name, hosp_code, daily_avg in all_hospitals:
            cumulative += daily_avg
            if r <= cumulative:
                break

        day_offset = np.random.randint(0, total_days)
        base_dt = start_date + timedelta(days=day_offset)

        hour_probs = np.array([
            0.02, 0.015, 0.01, 0.01, 0.01, 0.015,
            0.03, 0.05, 0.06, 0.07, 0.08, 0.08,
            0.07, 0.06, 0.06, 0.05, 0.05, 0.05,
            0.05, 0.04, 0.04, 0.03, 0.03, 0.025
        ])
        hour_probs = hour_probs / hour_probs.sum()
        hour = np.random.choice(24, p=hour_probs)
        minute = np.random.randint(0, 60)
        arrival_dt = base_dt.replace(hour=hour, minute=minute)

        is_winter = arrival_dt.month in [6, 7, 8]
        is_weekend = arrival_dt.weekday() >= 5
        is_night = hour >= 22 or hour < 6
        is_monday = arrival_dt.weekday() == 0

        triage_weights = [TRIAGE_CATEGORIES[t]["weight"] for t in range(1, 6)]
        if is_night:
            triage_weights[0] *= 1.3
            triage_weights[1] *= 1.2
        triage_weights = np.array(triage_weights) / sum(triage_weights)
        triage = np.random.choice(range(1, 6), p=triage_weights)
        triage_info = TRIAGE_CATEGORIES[triage]

        base_wait = triage_info["base_wait"]
        wait_multiplier = 1.0
        if is_winter:
            wait_multiplier *= 1.2
        if is_weekend:
            wait_multiplier *= 1.1
        if is_monday:
            wait_multiplier *= 1.15
        if 10 <= hour <= 14:
            wait_multiplier *= 1.15

        hospital_factor = {
            "RMH": 1.0, "PGH": 0.95, "SAH": 1.1, "BGH": 1.05,
            "WFH": 0.9, "PKH": 1.15, "NDH": 1.0, "HVH": 0.85,
            "SRH": 1.2, "CCH": 0.8
        }.get(hosp_code, 1.0)
        wait_multiplier *= hospital_factor

        wait_time = max(0, np.random.lognormal(
            mean=np.log(base_wait * wait_multiplier),
            sigma=0.5
        ))
        wait_time = min(wait_time, 600)

        base_los = triage_info["base_los"]
        los_minutes = max(15, np.random.lognormal(
            mean=np.log(base_los * wait_multiplier * 0.8),
            sigma=0.6
        ))
        los_minutes = min(los_minutes, 1440)

        seen_within_target = 1 if wait_time <= triage_info["target_min"] else 0
        four_hour_compliant = 1 if los_minutes <= 240 else 0

        arrival_mode = np.random.choice(ARRIVAL_MODES, p=ARRIVAL_WEIGHTS)
        if triage <= 2:
            if np.random.random() < 0.7:
                arrival_mode = "Ambulance"

        departure = np.random.choice(DEPARTURE_STATUS, p=DEPARTURE_WEIGHTS)
        if triage <= 2:
            dep_weights = [0.30, 0.55, 0.08, 0.02, 0.02, 0.03]
            departure = np.random.choice(DEPARTURE_STATUS, p=dep_weights)

        complaint = np.random.choice(PRESENTING_COMPLAINTS, p=COMPLAINT_WEIGHTS)
        age_group = np.random.choice(AGE_GROUPS, p=AGE_WEIGHTS)
        gender = np.random.choice(["Male", "Female", "Other"], p=[0.48, 0.51, 0.01])

        fy = f"FY{arrival_dt.year}-{str(arrival_dt.year+1)[-2:]}" if arrival_dt.month >= 7 else f"FY{arrival_dt.year-1}-{str(arrival_dt.year)[-2:]}"

        rows.append({
            "visit_id": i + 1,
            "arrival_datetime": arrival_dt.strftime("%Y-%m-%d %H:%M"),
            "arrival_date": arrival_dt.strftime("%Y-%m-%d"),
            "arrival_hour": hour,
            "arrival_day": arrival_dt.strftime("%A"),
            "arrival_month": arrival_dt.strftime("%Y-%m"),
            "financial_year": fy,
            "is_weekend": is_weekend,
            "hospital": hosp_name,
            "hospital_code": hosp_code,
            "lhd": lhd,
            "triage_category": triage,
            "triage_name": triage_info["name"],
            "wait_time_minutes": round(wait_time, 1),
            "los_minutes": round(los_minutes, 1),
            "seen_within_target": seen_within_target,
            "four_hour_compliant": four_hour_compliant,
            "arrival_mode": arrival_mode,
            "departure_status": departure,
            "presenting_complaint": complaint,
            "age_group": age_group,
            "gender": gender,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Statewide Health ED Dashboard - Data Generation")
    print("=" * 50)
    print("Generating 150K ED visit records...")

    df = generate_ed_visits(150000)

    output_path = os.path.join(os.path.dirname(__file__), "ed_visits.csv")
    df.to_csv(output_path, index=False)

    print(f"\n[OK] ed_visits.csv ({len(df):,} rows)")
    print(f"\nData Summary:")
    print(f"  * Date range: {df['arrival_date'].min()} to {df['arrival_date'].max()}")
    print(f"  * Hospitals: {df['hospital'].nunique()}")
    print(f"  * Median wait time: {df['wait_time_minutes'].median():.0f} min")
    print(f"  * Median LOS: {df['los_minutes'].median():.0f} min")
    print(f"  * 4-hour compliance: {df['four_hour_compliant'].mean():.1%}")
    print(f"  * Triage target compliance: {df['seen_within_target'].mean():.1%}")
    print(f"\nReady for Streamlit dashboard.")