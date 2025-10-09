   #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Free tier results visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import json
import ast
import re

def _parse_jsonish(x):
    """Best-effort parser for survey cells that may contain JSON, Python-literals,
    or comma-separated strings. Returns lists/dicts when possible, else the original.
    """
    if x is None:
        return None
    # pass through native structures
    if isinstance(x, (list, dict)):
        return x
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return None
        # common spreadsheet artifacts
        s = s.replace("\u200b", "")  # zero-widths
        s = s.replace("\ufeff", "")  # BOM
        # try strict JSON first
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass
        # try python literal (handles single quotes, True/False/None, tuples, etc.)
        try:
            val = ast.literal_eval(s)
            # limit to reasonable container types
            if isinstance(val, (list, dict, tuple, set)):
                return list(val) if not isinstance(val, dict) else val
        except Exception:
            pass
        # handle simple comma-separated values like "A, B, C"
        if ("," in s) and not re.search(r"[\[\]\{\}]", s):
            return [part.strip() for part in s.split(",") if part.strip()]
        # handle multiple concatenated JSON objects/arrays e.g. "['A'] ['B']"
        chunks = re.findall(r"(\[[^\]]*\]|\{[^}]*\})", s)
        if len(chunks) > 1:
            out = []
            for ch in chunks:
                try:
                    v = json.loads(ch)
                    out.extend(v if isinstance(v, list) else [v])
                except Exception:
                    continue
            if out:
                return out
        # fall back to original string
        return s
    return x


def derive_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate derived KPIs from raw data"""
    # Ensure numeric columns
    numeric_cols = [
        "space_sqft", "current_members", "total_wheels", "rent",
        "avg_retention_months", "monthly_churn", "total_staff_cost",
        "buildout_cost_total", "kiln_utilization", "capacity_utilization",
        "tier1_price", "clay_price", "handbuilding_stations", "glazing_stations",
        "years_operating_total_months", "time_to_members_months",
        "electricity", "water", "insurance"
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Parse JSON fields if they're strings
    json_cols = ["wheel_inventory", "kilns", "member_pcts", "revenue_pcts", 
                 "top_churn_reasons", "funding_sources"]
    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(_parse_jsonish)
    
    # Derived metrics with safe division (avoid division by zero)
    df["sqft_per_member"] = df["space_sqft"] / df["current_members"].replace(0, np.nan)
    df["members_per_wheel"] = df["current_members"] / df["total_wheels"].replace(0, np.nan)
    df["rent_per_member"] = df["rent"] / df["current_members"].replace(0, np.nan)
    df["rent_per_sqft_annual"] = (df["rent"] * 12) / df["space_sqft"].replace(0, np.nan)
    
    return df

def show_free_charts(df: pd.DataFrame):
    """Display free tier visualizations"""
    
    st.header("🎨 Survey Insights")
    st.caption(f"Based on {len(df)} survey responses")
    
    # Summary stats
    st.subheader("📊 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Median Studio Size", f"{df['space_sqft'].median():.0f} sq ft")
    with col2:
        st.metric("Median Members", f"{df['current_members'].median():.0f}")
    with col3:
        st.metric("Median Wheels", f"{df['total_wheels'].median():.0f}")
    with col4:
        st.metric("Median Membership", f"${df['tier1_price'].median():.0f}/mo")
    
    st.markdown("---")
    
    # Geographic distribution
    if "location_state" in df.columns:
        st.subheader("🗺️ Geographic Distribution")
        state_counts = df["location_state"].value_counts().reset_index()
        state_counts.columns = ["State", "Count"]
        
        chart = alt.Chart(state_counts).mark_bar().encode(
            x=alt.X("Count:Q"),
            y=alt.Y("State:N", sort="-x"),
            tooltip=["State", "Count"]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Studio types
    if "studio_type" in df.columns:
        st.subheader("🏛️ Studio Types")
        type_counts = df["studio_type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        
        chart = alt.Chart(type_counts).mark_bar().encode(
            x=alt.X("Count:Q"),
            y=alt.Y("Type:N", sort="-x"),
            tooltip=["Type", "Count"],
            color=alt.value("#4CAF50")
        ).properties(height=200)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Years in operation
    if "years_operating_total_months" in df.columns:
        st.subheader("📅 Studio Age Distribution")
        df_years = df.copy()
        df_years["years_operating"] = (
            pd.to_numeric(df_years["years_operating_total_months"], errors="coerce") / 12.0
        )
        
        # Filter out NaN values before creating chart
        df_years_clean = df_years[df_years["years_operating"].notna()]
        
        if len(df_years_clean) > 0:
            chart = alt.Chart(df_years_clean).mark_bar().encode(
                x=alt.X("years_operating:Q", bin=alt.Bin(maxbins=15), title="Years Operating"),
                y=alt.Y("count()", title="Number of Studios"),
                tooltip=["count()"]
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    # Space efficiency
    st.subheader("📐 Space Efficiency")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Square Feet per Member**")
        df_sqft = df[df["sqft_per_member"].notna()]
        if len(df_sqft) > 0:
            median_sqft = df_sqft["sqft_per_member"].median()
            st.metric("Median", f"{median_sqft:.1f} sq ft")
            
            chart = alt.Chart(df_sqft).mark_boxplot().encode(
                y=alt.Y("sqft_per_member:Q", title="Sq Ft per Member", scale=alt.Scale(zero=False))
            ).properties(height=200)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption("No data available")
    
    with col2:
        st.markdown("**Members per Wheel**")
        df_ratio = df[df["members_per_wheel"].notna()]
        if len(df_ratio) > 0:
            median_ratio = df_ratio["members_per_wheel"].median()
            st.metric("Median", f"{median_ratio:.1f} members/wheel")
            
            chart = alt.Chart(df_ratio).mark_boxplot().encode(
                y=alt.Y("members_per_wheel:Q", title="Members per Wheel", scale=alt.Scale(zero=False))
            ).properties(height=200)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption("No data available")
    
    st.markdown("---")
    
    # Rent affordability
    st.subheader("💰 Rent Affordability")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Rent per Member**")
        df_rent_member = df[df["rent_per_member"].notna()]
        if len(df_rent_member) > 0:
            median_rent_per_member = df_rent_member["rent_per_member"].median()
            st.metric("Median", f"${median_rent_per_member:.0f}/member/mo")
            
            chart = alt.Chart(df_rent_member).mark_bar().encode(
                x=alt.X("rent_per_member:Q", bin=alt.Bin(step=50), title="Rent per Member ($/month)"),
                y=alt.Y("count()", title="Number of Studios")
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption("No data available")
        
    with col2:
        st.markdown("**Rent per Square Foot (Annual)**")
        df_rent_sqft = df[df["rent_per_sqft_annual"].notna()]
        if len(df_rent_sqft) > 0:
            median_rent_sqft = df_rent_sqft["rent_per_sqft_annual"].median()
            st.metric("Median", f"${median_rent_sqft:.2f}/sq ft/yr")
            
            chart = alt.Chart(df_rent_sqft).mark_boxplot().encode(
                y=alt.Y("rent_per_sqft_annual:Q", title="Annual Rent ($/sq ft)", 
                       scale=alt.Scale(zero=False))
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption("No data available")
    
    st.markdown("---")
    
    # Time to capacity
    if "time_to_members_months" in df.columns and "current_members" in df.columns:
        st.subheader("⏱️ Time to Reach Current Membership")
        
        df_time = df[(df["time_to_members_months"].notna()) & (df["current_members"].notna())].copy()
        
        if len(df_time) > 0:
            chart = alt.Chart(df_time).mark_circle(size=80).encode(
                x=alt.X("time_to_members_months:Q", title="Months to Current Membership"),
                y=alt.Y("current_members:Q", title="Current Members"),
                tooltip=["studio_name", "time_to_members_months", "current_members"]
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            median_time = df_time["time_to_members_months"].median()
            st.caption(f"Median time to reach current membership: {median_time:.0f} months")
    
    st.markdown("---")
    
    # Access models
    if "access_model" in df.columns:
        st.subheader("🔑 Studio Access Models")
        access_counts = df["access_model"].value_counts().reset_index()
        access_counts.columns = ["Access Model", "Count"]
        
        chart = alt.Chart(access_counts).mark_arc().encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Access Model:N"),
            tooltip=["Access Model", "Count"]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    # Pricing distribution
    if "tier1_price" in df.columns:
        st.subheader("💵 Membership Pricing Distribution")
        
        df_pricing = df[df["tier1_price"].notna()]
        if len(df_pricing) > 0:
            chart = alt.Chart(df_pricing).mark_bar().encode(
                x=alt.X("tier1_price:Q", bin=alt.Bin(step=25), title="Monthly Membership Price ($)"),
                y=alt.Y("count()", title="Number of Studios"),
                tooltip=["count()"]
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("25th Percentile", f"${df_pricing['tier1_price'].quantile(0.25):.0f}")
            with col2:
                st.metric("Median", f"${df_pricing['tier1_price'].median():.0f}")
            with col3:
                st.metric("75th Percentile", f"${df_pricing['tier1_price'].quantile(0.75):.0f}")
    
    st.markdown("---")
    
    # Staffing patterns
    if "has_staff" in df.columns:
        st.subheader("👥 Staffing Patterns")
        
        # Helper to convert boolean-like values
        def _to_bool01(s):
            # Handle actual booleans first
            if s.dtype == 'bool':
                return s.astype(int)
            s = s.astype(str).str.strip().str.lower()
            mapping = {
                "yes": 1, "y": 1, "true": 1, "t": 1, "1": 1,
                "no": 0,  "n": 0, "false": 0, "f": 0, "0": 0
            }
            return s.map(mapping)
        
        staffing_counts = df["has_staff"].value_counts().reset_index()
        staffing_counts.columns = ["Has Staff", "Count"]
        staffing_counts["Has Staff"] = staffing_counts["Has Staff"].astype(str).map({
            "True": "Has Paid Staff",
            "False": "No Paid Staff",
            "true": "Has Paid Staff",
            "false": "No Paid Staff",
            "1": "Has Paid Staff",
            "0": "No Paid Staff",
            "yes": "Has Paid Staff",
            "no": "No Paid Staff"
        }).fillna("Unknown")
        
        chart = alt.Chart(staffing_counts).mark_bar().encode(
            x=alt.X("Count:Q"),
            y=alt.Y("Has Staff:N"),
            tooltip=["Has Staff", "Count"],
            color=alt.value("#FF9800")
        ).properties(height=150)
        
        st.altair_chart(chart, use_container_width=True)
        
        # % respondents that have staff
        staff01 = _to_bool01(df["has_staff"])
        denom = staff01.notna().sum() if staff01.notna().any() else len(df)
        if denom > 0:
            pct_with_staff = (staff01.fillna(0).sum() / denom) * 100
            st.caption(f"{pct_with_staff:.1f}% of studios have paid staff")
    
    st.markdown("---")
    
    # Revenue mix
    if "revenue_pcts" in df.columns:
        st.subheader("📈 Revenue Mix (Average)")
        
        # Extract revenue percentages and average them
        revenue_data = []
        for idx, row in df.iterrows():
            rev_dict = row["revenue_pcts"]
            if isinstance(rev_dict, dict):
                for source, pct in rev_dict.items():
                    if isinstance(pct, (int, float)):
                        revenue_data.append({"source": source, "percentage": pct})
        
        if revenue_data:
            rev_df = pd.DataFrame(revenue_data)
            avg_rev = rev_df.groupby("source")["percentage"].mean().reset_index()
            avg_rev.columns = ["Revenue Source", "Average %"]
            
            # Capitalize and clean names
            name_map = {
                "membership": "Membership Fees",
                "clay": "Clay Sales",
                "firing": "Firing Fees",
                "classes": "Classes/Workshops",
                "events": "Events/Parties",
                "other": "Other"
            }
            avg_rev["Revenue Source"] = avg_rev["Revenue Source"].map(
                lambda x: name_map.get(x, x.title())
            )
            
            chart = alt.Chart(avg_rev).mark_arc().encode(
                theta=alt.Theta("Average %:Q"),
                color=alt.Color("Revenue Source:N"),
                tooltip=["Revenue Source", alt.Tooltip("Average %:Q", format=".1f")]
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    # Kiln utilization
    if "kiln_utilization" in df.columns:
        st.subheader("🔥 Kiln Utilization")
        
        df_kiln = df[df["kiln_utilization"].notna()].copy()
        
        if len(df_kiln) > 0:
            chart = alt.Chart(df_kiln).mark_bar().encode(
                x=alt.X("kiln_utilization:Q", bin=alt.Bin(step=10), 
                       title="Kiln Utilization (%)"),
                y=alt.Y("count()", title="Number of Studios")
            ).properties(height=250)
            
            st.altair_chart(chart, use_container_width=True)
            
            median_util = df_kiln["kiln_utilization"].median()
            st.caption(f"Median kiln utilization: {median_util:.0f}%")
    
    st.markdown("---")
    
    # Equipment summary
    st.subheader("🛠️ Equipment Inventory")
    
    equipment_summary = pd.DataFrame({
        "Equipment Type": ["Handbuilding Stations", "Glazing Stations", "Wheels"],
        "Median per Studio": [
            df["handbuilding_stations"].median(),
            df["glazing_stations"].median(),
            df["total_wheels"].median()
        ]
    })
    
    chart = alt.Chart(equipment_summary).mark_bar().encode(
        x=alt.X("Median per Studio:Q"),
        y=alt.Y("Equipment Type:N"),
        tooltip=["Equipment Type", "Median per Studio"],
        color=alt.value("#2196F3")
    ).properties(height=200)
    
    st.altair_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    # Firing fee models
    if "firing_model" in df.columns:
        st.subheader("⚖️ Firing Fee Models")
        
        firing_counts = df["firing_model"].value_counts().reset_index()
        firing_counts.columns = ["Firing Model", "Count"]
        
        chart = alt.Chart(firing_counts).mark_bar().encode(
            x=alt.X("Count:Q"),
            y=alt.Y("Firing Model:N", sort="-x"),
            tooltip=["Firing Model", "Count"],
            color=alt.value("#9C27B0")
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    # NEW: Events & PYOP offerings
    if "offers_events" in df.columns:
        st.subheader("🎉 Events & Parties")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # What % of studios offer events
            def _to_bool01(s):
                if s.dtype == 'bool':
                    return s.astype(int)
                s = s.astype(str).str.strip().str.lower()
                mapping = {
                    "yes": 1, "y": 1, "true": 1, "t": 1, "1": 1,
                    "no": 0,  "n": 0, "false": 0, "f": 0, "0": 0
                }
                return s.map(mapping)
            
            events01 = _to_bool01(df["offers_events"])
            denom = events01.notna().sum() if events01.notna().any() else len(df)
            if denom > 0:
                pct_with_events = (events01.fillna(0).sum() / denom) * 100
                st.metric("Studios Offering Events", f"{pct_with_events:.0f}%")
        
        with col2:
            # Average events per month for studios that offer them
            df_events = df[(df["offers_events"].astype(str).str.lower().isin(['true', '1', 'yes'])) & 
                          (df["events_per_month"].notna())]
            if len(df_events) > 0:
                df_events["events_per_month"] = pd.to_numeric(df_events["events_per_month"], errors="coerce")
                avg_events = df_events["events_per_month"].mean()
                st.metric("Avg Events/Month", f"{avg_events:.1f}")
        
        # Event pricing distribution
        if "event_price" in df.columns:
            df_event_price = df[df["event_price"].notna()].copy()
            df_event_price["event_price"] = pd.to_numeric(df_event_price["event_price"], errors="coerce")
            df_event_price = df_event_price[df_event_price["event_price"].notna()]
            
            if len(df_event_price) > 0:
                st.write("**Event Pricing Distribution**")
                
                chart = alt.Chart(df_event_price).mark_bar().encode(
                    x=alt.X("event_price:Q", bin=alt.Bin(step=10), 
                           title="Price per Person ($)"),
                    y=alt.Y("count()", title="Number of Studios")
                ).properties(height=250)
                
                st.altair_chart(chart, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Min", f"${df_event_price['event_price'].min():.0f}")
                with col2:
                    st.metric("Median", f"${df_event_price['event_price'].median():.0f}")
                with col3:
                    st.metric("Max", f"${df_event_price['event_price'].max():.0f}")
    
    
    
    # Build-out costs
    if "buildout_cost_total" in df.columns:
        st.subheader("🔨 Build-Out Investment")
        
        df_buildout = df[df["buildout_cost_total"].notna()].copy()
        
        if len(df_buildout) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                chart = alt.Chart(df_buildout).mark_bar().encode(
                    x=alt.X("buildout_cost_total:Q", bin=alt.Bin(step=25000),
                           title="Build-Out Cost ($)"),
                    y=alt.Y("count()", title="Number of Studios")
                ).properties(height=250)
                
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                median_buildout = df_buildout["buildout_cost_total"].median()
                st.metric("Median Build-Out Cost", f"${median_buildout:,.0f}")
                
                # Cost per sqft
                df_buildout["buildout_per_sqft"] = (
                    df_buildout["buildout_cost_total"] / df_buildout["space_sqft"].replace(0, np.nan)
                )
                df_buildout_sqft = df_buildout[df_buildout["buildout_per_sqft"].notna()]
                if len(df_buildout_sqft) > 0:
                    median_per_sqft = df_buildout_sqft["buildout_per_sqft"].median()
                    st.metric("Median per Sq Ft", f"${median_per_sqft:.2f}/sq ft")  