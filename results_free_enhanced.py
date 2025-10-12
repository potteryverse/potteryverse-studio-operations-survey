# Q24 enhanced:#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced free tier results visualizations with individual studio benchmarking

INTEGRATION INSTRUCTIONS:
Add this to results.py:

    from results_free_enhanced import show_enhanced_charts
    
    def render_results():
        # ... existing code to load df ...
        
        # Add tabs for different views
        tab1, tab2 = st.tabs(["📊 Overview", "🔍 Deep Dive"])
        
        with tab1:
            show_free_charts(df)  # Your existing overview
        
        with tab2:
            show_enhanced_charts(df)  # New enhanced analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import ast
import re

def _parse_jsonish(x):
    """Best-effort parser for survey cells that may contain JSON, Python-literals,
    or comma-separated strings. Returns lists/dicts when possible, else the original.
    """
    if x is None:
        return None
    if isinstance(x, (list, dict)):
        return x
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return None
        s = s.replace("\u200b", "").replace("\ufeff", "")
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass
        try:
            val = ast.literal_eval(s)
            if isinstance(val, (list, dict, tuple, set)):
                return list(val) if not isinstance(val, dict) else val
        except Exception:
            pass
        if ("," in s) and not re.search(r"[\[\]\{\}]", s):
            return [part.strip() for part in s.split(",") if part.strip()]
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
        return s
    return x


def show_enhanced_charts(df: pd.DataFrame):
    """
    Enhanced visualizations with individual studio highlighting
    """
    
    st.header("🔍 Deep Dive Analysis")
    st.caption("Question-driven insights with individual studio benchmarking")
    
    # === STUDIO SELECTOR ===
    st.markdown("---")
    st.subheader("🎯 Find Your Studio")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Get list of studio IDs (4-char codes)
        studio_ids = ["View All Studios (No Highlighting)"] + sorted(df['studio_name'].unique().tolist())
        
        selected_studio = st.selectbox(
            "Select your 4-character studio ID:",
            options=studio_ids,
            help="Your studio ID was provided when you submitted the survey. Selecting it will highlight your position on all charts below."
        )
    
    # Determine if we're highlighting a specific studio
    highlight_studio = None if selected_studio == "View All Studios (No Highlighting)" else selected_studio
    
    with col2:
        if highlight_studio:
            studio_data = df[df['studio_name'] == highlight_studio].iloc[0]
            st.metric("Your Members", f"{int(studio_data['current_members'])}")
    
    with col3:
        if highlight_studio:
            st.metric("Your Space", f"{int(studio_data['space_sqft'])} sq ft")
    
    if highlight_studio:
        st.success(f"✓ Viewing data for studio **{highlight_studio}** (highlighted in red on charts below)")
    else:
        st.info("💡 Select your studio ID above to see your position on all charts")
    
    st.markdown("---")
    
    # === ANALYSIS SECTIONS ===
    show_space_efficiency(df, highlight_studio)
    st.markdown("---")
    
    show_pricing_analysis(df, highlight_studio)
    st.markdown("---")
    
    show_equipment_analysis(df, highlight_studio)
    st.markdown("---")
    
    show_financial_performance(df, highlight_studio)
    st.markdown("---")
    
    show_member_behavior(df, highlight_studio)
    st.markdown("---")
    
    show_events_analysis(df, highlight_studio)
    st.markdown("---")
    
    show_growth_trajectories(df, highlight_studio)
    st.markdown("---")
    
    show_operational_models(df, highlight_studio)
    st.markdown("---")
    
    show_market_context(df, highlight_studio)
    st.markdown("---")
    
    show_classes_workshops(df, highlight_studio)
    st.markdown("---")
    
    show_capacity_waitlists(df, highlight_studio)
    st.markdown("---")
    
    show_buildout_costs(df, highlight_studio)
    st.markdown("---")
    
    show_member_retention(df, highlight_studio)
    st.markdown("---")
    
    show_revenue_optimization(df, highlight_studio)
    st.markdown("---")
    
    show_profitability_patterns(df, highlight_studio)
    st.markdown("---")
    
    show_kiln_analysis(df, highlight_studio)


def show_space_efficiency(df, highlight_studio=None):
    """Section 1: Space Efficiency Deep Dive"""
    
    st.header("📏 Section 1: Space Efficiency")
    st.caption("Understanding how studios use their physical space")
    
    # Q1: What's the optimal space per member?
    st.subheader("Q1: What's the optimal space per member?")
    
    # Ensure numeric types
    df_clean = df.copy()
    df_clean['sqft_per_member'] = pd.to_numeric(df_clean['sqft_per_member'], errors='coerce')
    df_clean['current_members'] = pd.to_numeric(df_clean['current_members'], errors='coerce')
    df_clean = df_clean[df_clean['sqft_per_member'].notna()]
    
    if len(df_clean) == 0:
        st.warning("No data available for this analysis")
        return
    
    # Split data for highlighting
    if highlight_studio and highlight_studio in df_clean['studio_name'].values:
        df_highlight = df_clean[df_clean['studio_name'] == highlight_studio]
        df_others = df_clean[df_clean['studio_name'] != highlight_studio]
    else:
        df_highlight = pd.DataFrame()
        df_others = df_clean
    
    # Create Plotly scatter
    fig = go.Figure()
    
    # Other studios
    fig.add_trace(go.Scatter(
        x=df_others['current_members'],
        y=df_others['sqft_per_member'],
        mode='markers',
        name='Other Studios',
        marker=dict(size=10, color='#1f77b4', opacity=0.6),
        text=df_others['studio_name'],
        hovertemplate='<b>Studio %{text}</b><br>Members: %{x}<br>Sq Ft/Member: %{y:.1f}<extra></extra>'
    ))
    
    # Highlighted studio
    if not df_highlight.empty:
        fig.add_trace(go.Scatter(
            x=df_highlight['current_members'],
            y=df_highlight['sqft_per_member'],
            mode='markers',
            name=f'Your Studio ({highlight_studio})',
            marker=dict(size=18, color='#FF4B4B', symbol='star', 
                       line=dict(width=2, color='darkred')),
            text=df_highlight['studio_name'],
            hovertemplate='<b>YOUR STUDIO</b><br>Members: %{x}<br>Sq Ft/Member: %{y:.1f}<extra></extra>'
        ))
    
    # Add median line
    median_sqft = df_clean['sqft_per_member'].median()
    fig.add_hline(y=median_sqft, line_dash="dash", line_color="gray",
                  annotation_text=f"Median: {median_sqft:.1f}", annotation_position="right")
    
    fig.update_layout(
        xaxis_title='Current Members',
        yaxis_title='Square Feet per Member',
        height=500,
        hovermode='closest',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Median", f"{median_sqft:.1f} sq ft/member")
    with col2:
        q25 = df_clean['sqft_per_member'].quantile(0.25)
        st.metric("25th Percentile", f"{q25:.1f} sq ft/member")
    with col3:
        q75 = df_clean['sqft_per_member'].quantile(0.75)
        st.metric("75th Percentile", f"{q75:.1f} sq ft/member")
    
    if highlight_studio and not df_highlight.empty:
        studio_value = df_highlight['sqft_per_member'].iloc[0]
        percentile = (df_clean['sqft_per_member'] <= studio_value).sum() / len(df_clean) * 100
        
        st.info(f"""
        **Your Studio ({highlight_studio}):** {studio_value:.1f} sq ft/member
        - **Percentile:** {percentile:.0f}th (you provide more space than {percentile:.0f}% of studios)
        - **Interpretation:** {'You provide above-average space per member - members may appreciate the extra room' if studio_value > median_sqft else 'You run a more space-efficient studio - this can improve financial performance'}
        """)
    
    # Q2: How many members can each wheel support?
    st.markdown("---")
    st.subheader("Q2: How many members can each wheel support?")
    
    # Ensure numeric types
    df_wheel = df.copy()
    df_wheel['members_per_wheel'] = pd.to_numeric(df_wheel['members_per_wheel'], errors='coerce')
    df_wheel['total_wheels'] = pd.to_numeric(df_wheel['total_wheels'], errors='coerce')
    df_wheel = df_wheel[df_wheel['members_per_wheel'].notna()]
    
    if len(df_wheel) > 0:
        # Split data
        if highlight_studio and highlight_studio in df_wheel['studio_name'].values:
            df_h = df_wheel[df_wheel['studio_name'] == highlight_studio]
            df_o = df_wheel[df_wheel['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_wheel
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_o['total_wheels'],
            y=df_o['members_per_wheel'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#2ca02c', opacity=0.6),
            text=df_o['studio_name'],
            hovertemplate='<b>Studio %{text}</b><br>Wheels: %{x}<br>Members/Wheel: %{y:.1f}<extra></extra>'
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['total_wheels'],
                y=df_h['members_per_wheel'],
                mode='markers',
                name=f'Your Studio ({highlight_studio})',
                marker=dict(size=18, color='#FF4B4B', symbol='star',
                           line=dict(width=2, color='darkred')),
                hovertemplate='<b>YOUR STUDIO</b><br>Wheels: %{x}<br>Members/Wheel: %{y:.1f}<extra></extra>'
            ))
        
        median_ratio = df_wheel['members_per_wheel'].median()
        fig.add_hline(y=median_ratio, line_dash="dash", line_color="gray",
                      annotation_text=f"Median: {median_ratio:.1f}", annotation_position="right")
        
        fig.update_layout(
            xaxis_title='Total Wheels',
            yaxis_title='Members per Wheel',
            height=500,
            hovermode='closest'
        )
        
        # Force integer ticks for wheels axis since wheels are discrete
        max_wheels = int(df_wheel['total_wheels'].max())
        if max_wheels <= 20:
            fig.update_xaxes(dtick=1)
        elif max_wheels <= 50:
            fig.update_xaxes(dtick=5)
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Median Ratio", f"{median_ratio:.1f} members/wheel")
        with col2:
            st.metric("Min", f"{df_wheel['members_per_wheel'].min():.1f}")
        with col3:
            st.metric("Max", f"{df_wheel['members_per_wheel'].max():.1f}")
        
        if highlight_studio and not df_h.empty:
            your_ratio = df_h['members_per_wheel'].iloc[0]
            pct = (df_wheel['members_per_wheel'] <= your_ratio).sum() / len(df_wheel) * 100
            
            st.info(f"""
            **Your ratio:** {your_ratio:.1f} members/wheel ({pct:.0f}th percentile)
            - {'Consider adding more wheels - your ratio is above the median' if your_ratio > median_ratio else 'Your wheel-to-member ratio looks healthy'}
            """)
    
    # Q3: Distribution of space per member
    st.markdown("---")
    st.subheader("Q3: How does space efficiency vary?")
    
    # Altair histogram
    df_clean['is_highlighted'] = df_clean['studio_name'] == highlight_studio if highlight_studio else False
    
    chart = alt.Chart(df_clean).mark_bar().encode(
        x=alt.X('sqft_per_member:Q', bin=alt.Bin(step=20), title='Square Feet per Member'),
        y=alt.Y('count()', title='Number of Studios'),
        color=alt.condition(
            alt.datum.is_highlighted == True,
            alt.value('#FF4B4B'),
            alt.value('#1f77b4')
        ),
        opacity=alt.condition(
            alt.datum.is_highlighted == True,
            alt.value(1.0),
            alt.value(0.7)
        ),
        tooltip=['count()']
    ).properties(height=350)
    
    st.altair_chart(chart, use_container_width=True)
    
    st.caption(f"Most studios operate between {df_clean['sqft_per_member'].quantile(0.25):.0f} and {df_clean['sqft_per_member'].quantile(0.75):.0f} sq ft per member")


def show_pricing_analysis(df, highlight_studio=None):
    """Section 2: Pricing Benchmarking"""
    
    st.header("💰 Section 2: Pricing Benchmarking")
    st.caption("How do studios price their memberships and services?")
    
    # Q4: What do most studios charge for base membership?
    st.subheader("Q4: What do most studios charge for base membership?")
    
    # Ensure numeric type
    df_price = df.copy()
    df_price['tier1_price'] = pd.to_numeric(df_price['tier1_price'], errors='coerce')
    df_price = df_price[df_price['tier1_price'].notna()]
    
    if len(df_price) == 0:
        st.warning("No pricing data available")
        return
    
    # Histogram with highlight
    df_price['is_highlighted'] = df_price['studio_name'] == highlight_studio if highlight_studio else False
    
    chart = alt.Chart(df_price).mark_bar().encode(
        x=alt.X('tier1_price:Q', bin=alt.Bin(step=25), title='Monthly Membership Price ($)'),
        y=alt.Y('count()', title='Number of Studios'),
        color=alt.condition(
            alt.datum.is_highlighted == True,
            alt.value('#FF4B4B'),
            alt.value('#9467bd')
        ),
        tooltip=['count()']
    ).properties(height=350)
    
    st.altair_chart(chart, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Median Price", f"${df_price['tier1_price'].median():.0f}/mo")
    with col2:
        st.metric("25th Percentile", f"${df_price['tier1_price'].quantile(0.25):.0f}/mo")
    with col3:
        st.metric("75th Percentile", f"${df_price['tier1_price'].quantile(0.75):.0f}/mo")
    
    if highlight_studio and highlight_studio in df_price['studio_name'].values:
        your_price = df_price[df_price['studio_name'] == highlight_studio]['tier1_price'].iloc[0]
        pct = (df_price['tier1_price'] <= your_price).sum() / len(df_price) * 100
        median = df_price['tier1_price'].median()
        
        st.info(f"""
        **Your base membership:** ${your_price:.0f}/mo ({pct:.0f}th percentile)
        - You charge ${abs(your_price - median):.0f} {'more' if your_price > median else 'less'} than the median
        - {'Your pricing is in the upper range - ensure you deliver premium value' if your_price > df_price['tier1_price'].quantile(0.75) else 'Your pricing is competitive with the market' if your_price >= df_price['tier1_price'].quantile(0.25) else 'You may have room to increase prices'}
        """)
    
    # Q8: How does pricing vary by location?
    st.markdown("---")
    st.subheader("Q5: How does pricing vary by metro area size?")
    
    if 'metro_population' in df.columns:
        df_location = df[df['tier1_price'].notna() & df['metro_population'].notna()].copy()
        
        if len(df_location) > 0:
            # Box plot by metro size
            fig = px.box(df_location, x='metro_population', y='tier1_price',
                        labels={'metro_population': 'Metro Population', 'tier1_price': 'Base Membership Price ($)'},
                        height=400)
            
            # Highlight user's point if applicable
            if highlight_studio and highlight_studio in df_location['studio_name'].values:
                user_row = df_location[df_location['studio_name'] == highlight_studio].iloc[0]
                fig.add_trace(go.Scatter(
                    x=[user_row['metro_population']],
                    y=[user_row['tier1_price']],
                    mode='markers',
                    marker=dict(size=15, color='red', symbol='star'),
                    name='Your Studio',
                    hovertext=f"Your Studio: ${user_row['tier1_price']:.0f}"
                ))
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("Larger metro areas tend to support higher pricing, but there's significant variation within each category")
    
    # Q9: What's the going rate for firing fees?
    st.markdown("---")
    st.subheader("Q6: What firing fee models do studios use?")
    
    if 'firing_model' in df.columns:
        firing_counts = df['firing_model'].value_counts().reset_index()
        firing_counts.columns = ['Firing Model', 'Count']
        
        # Highlight user's model
        if highlight_studio and highlight_studio in df['studio_name'].values:
            user_model = df[df['studio_name'] == highlight_studio]['firing_model'].iloc[0]
            firing_counts['is_user'] = firing_counts['Firing Model'] == user_model
        else:
            firing_counts['is_user'] = False
        
        chart = alt.Chart(firing_counts).mark_bar().encode(
            x=alt.X('Count:Q'),
            y=alt.Y('Firing Model:N', sort='-x'),
            color=alt.condition(
                alt.datum.is_user == True,
                alt.value('#FF4B4B'),
                alt.value('#ff7f0e')
            ),
            tooltip=['Firing Model', 'Count']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)


def show_equipment_analysis(df, highlight_studio=None):
    """Section 3: Equipment Analysis"""
    
    st.header("🛠️ Section 3: Equipment Analysis")
    
    # Q18: How many kilns do studios need?
    st.subheader("Q7: How many kilns do studios typically have?")
    
    # Convert num_kilns to numeric, coercing errors
    df_kilns = df.copy()
    df_kilns['num_kilns'] = pd.to_numeric(df_kilns['num_kilns'], errors='coerce')
    df_kilns['current_members'] = pd.to_numeric(df_kilns['current_members'], errors='coerce')
    df_kilns = df_kilns[df_kilns['num_kilns'].notna() & df_kilns['current_members'].notna()]
    
    if len(df_kilns) > 0:
        if highlight_studio and highlight_studio in df_kilns['studio_name'].values:
            df_h = df_kilns[df_kilns['studio_name'] == highlight_studio]
            df_o = df_kilns[df_kilns['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_kilns
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_o['current_members'],
            y=df_o['num_kilns'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#d62728', opacity=0.6),
            text=df_o['studio_name'],
            hovertemplate='<b>Studio %{text}</b><br>Members: %{x}<br>Kilns: %{y}<extra></extra>'
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['current_members'],
                y=df_h['num_kilns'],
                mode='markers',
                name=f'Your Studio',
                marker=dict(size=18, color='#FF4B4B', symbol='star'),
                hovertemplate='<b>YOUR STUDIO</b><br>Members: %{x}<br>Kilns: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            xaxis_title='Current Members',
            yaxis_title='Number of Kilns',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        median_kilns = df_kilns['num_kilns'].median()
        st.caption(f"Median: {median_kilns:.0f} kilns per studio")
    
    # Q17: Wheel brand preferences
    st.markdown("---")
    st.subheader("Q8: Which wheel brands would studios buy again?")
    
    if 'wheel_preference' in df.columns:
        # Extract all preferences
        all_prefs = []
        for prefs in df['wheel_preference'].dropna():
            parsed = _parse_jsonish(prefs)
            if isinstance(parsed, list):
                all_prefs.extend(parsed)
            elif isinstance(parsed, str):
                all_prefs.append(parsed)
        
        if all_prefs:
            pref_counts = pd.Series(all_prefs).value_counts().reset_index()
            pref_counts.columns = ['Brand', 'Count']
            
            chart = alt.Chart(pref_counts.head(10)).mark_bar().encode(
                x=alt.X('Count:Q'),
                y=alt.Y('Brand:N', sort='-x'),
                tooltip=['Brand', 'Count'],
                color=alt.value('#17becf')
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)


def show_financial_performance(df, highlight_studio=None):
    """Section 4: Financial Performance"""
    
    st.header("💵 Section 4: Financial Performance")
    
    # Q12: What rent can a studio afford?
    st.subheader("Q9: Rent per member analysis")
    
    # Ensure numeric type
    df_rent = df.copy()
    df_rent['rent_per_member'] = pd.to_numeric(df_rent['rent_per_member'], errors='coerce')
    df_rent = df_rent[df_rent['rent_per_member'].notna()]
    
    if len(df_rent) > 0:
        chart = alt.Chart(df_rent).mark_bar().encode(
            x=alt.X('rent_per_member:Q', bin=alt.Bin(step=50), title='Monthly Rent per Member ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#bcbd22')
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
        
        median_rent = df_rent['rent_per_member'].median()
        st.metric("Median Rent per Member", f"${median_rent:.0f}/member/month")
        
        if highlight_studio and highlight_studio in df_rent['studio_name'].values:
            your_rent = df_rent[df_rent['studio_name'] == highlight_studio]['rent_per_member'].iloc[0]
            st.info(f"Your rent per member: ${your_rent:.0f} ({'above' if your_rent > median_rent else 'below'} median)")
    
    # Q16: Where does revenue come from?
    st.markdown("---")
    st.subheader("Q10: Average revenue mix across all studios")
    
    if 'revenue_pcts' in df.columns:
        revenue_data = []
        for idx, row in df.iterrows():
            rev_dict = _parse_jsonish(row['revenue_pcts'])
            if isinstance(rev_dict, dict):
                for source, pct in rev_dict.items():
                    if isinstance(pct, (int, float)) and pct > 0:
                        revenue_data.append({'source': source, 'percentage': pct})
        
        if revenue_data:
            rev_df = pd.DataFrame(revenue_data)
            avg_rev = rev_df.groupby('source')['percentage'].mean().reset_index()
            avg_rev.columns = ['Revenue Source', 'Average %']
            
            name_map = {
                'membership': 'Membership Fees',
                'clay': 'Clay Sales',
                'firing': 'Firing Fees',
                'classes': 'Classes/Workshops',
                'events': 'Events/Parties',
                'other': 'Other'
            }
            avg_rev['Revenue Source'] = avg_rev['Revenue Source'].map(lambda x: name_map.get(x, x.title()))
            
            fig = px.pie(avg_rev, values='Average %', names='Revenue Source', 
                        title='Average Revenue Mix', height=400)
            st.plotly_chart(fig, use_container_width=True)


def show_member_behavior(df, highlight_studio=None):
    """Section 5: Member Behavior"""
    
    st.header("👥 Section 5: Member Behavior")
    
    # Q24: What's a normal churn rate?
    st.subheader("Q11: Monthly churn rate distribution")
    
    # Ensure numeric type
    df_churn = df.copy()
    df_churn['monthly_churn'] = pd.to_numeric(df_churn['monthly_churn'], errors='coerce')
    df_churn = df_churn[df_churn['monthly_churn'].notna()]
    
    if len(df_churn) > 0:
        chart = alt.Chart(df_churn).mark_bar().encode(
            x=alt.X('monthly_churn:Q', bin=alt.Bin(step=2), title='Monthly Churn Rate (%)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#8c564b')
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
        
        median_churn = df_churn['monthly_churn'].median()
        st.metric("Median Monthly Churn", f"{median_churn:.1f}%")
        
        if highlight_studio and highlight_studio in df_churn['studio_name'].values:
            your_churn = df_churn[df_churn['studio_name'] == highlight_studio]['monthly_churn'].iloc[0]
            st.info(f"Your churn rate: {your_churn:.1f}% ({'higher' if your_churn > median_churn else 'lower'} than median)")


def show_events_analysis(df, highlight_studio=None):
    """Section 6: Events & Parties Analysis"""
    
    st.header("🎉 Section 6: Events & Parties")
    
    # What % offer events?
    st.subheader("Q12: What percentage of studios offer events/PYOP?")
    
    if 'offers_events' in df.columns:
        def _to_bool(s):
            if pd.api.types.is_bool_dtype(s):
                return s.astype(int)
            s = s.astype(str).str.strip().str.lower()
            mapping = {'yes': 1, 'y': 1, 'true': 1, 't': 1, '1': 1, 'no': 0, 'n': 0, 'false': 0, 'f': 0, '0': 0}
            return s.map(mapping)
        
        events01 = _to_bool(df['offers_events'])
        valid = events01.notna().sum()
        if valid > 0:
            pct_offering = (events01.sum() / valid) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Studios Offering Events", f"{pct_offering:.0f}%")
            
            # Event pricing
            df_events = df[(events01 == 1)].copy()
            df_events['event_price'] = pd.to_numeric(df_events['event_price'], errors='coerce')
            df_events = df_events[df_events['event_price'].notna()]
            
            if len(df_events) > 0:
                with col2:
                    median_price = df_events['event_price'].median()
                    st.metric("Median Event Price", f"${median_price:.0f}/person")
                
                chart = alt.Chart(df_events).mark_bar().encode(
                    x=alt.X('event_price:Q', bin=alt.Bin(step=10), title='Price per Person ($)'),
                    y=alt.Y('count()', title='Number of Studios'),
                    color=alt.value('#e377c2')
                ).properties(height=300)
                
                st.altair_chart(chart, use_container_width=True)


def show_growth_trajectories(df, highlight_studio=None):
    """Section 7: Growth & Timeline Analysis"""
    
    st.header("📈 Section 7: Growth Trajectories")
    
    # Q32: How long to reach X members?
    st.subheader("Q13: How long does it take to reach current membership?")
    
    # Ensure numeric types
    df_growth = df.copy()
    df_growth['time_to_members_months'] = pd.to_numeric(df_growth['time_to_members_months'], errors='coerce')
    df_growth['current_members'] = pd.to_numeric(df_growth['current_members'], errors='coerce')
    df_growth = df_growth[df_growth['time_to_members_months'].notna() & df_growth['current_members'].notna()]
    
    if len(df_growth) > 0:
        if highlight_studio and highlight_studio in df_growth['studio_name'].values:
            df_h = df_growth[df_growth['studio_name'] == highlight_studio]
            df_o = df_growth[df_growth['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_growth
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_o['time_to_members_months'],
            y=df_o['current_members'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#7f7f7f', opacity=0.6),
            text=df_o['studio_name'],
            hovertemplate='<b>Studio %{text}</b><br>Months: %{x}<br>Members: %{y}<extra></extra>'
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['time_to_members_months'],
                y=df_h['current_members'],
                mode='markers',
                name=f'Your Studio',
                marker=dict(size=18, color='#FF4B4B', symbol='star'),
                hovertemplate='<b>YOUR STUDIO</b><br>Months: %{x}<br>Members: %{y}<extra></extra>'
            ))
        
        # Add trend line
        z = np.polyfit(df_growth['time_to_members_months'], df_growth['current_members'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(df_growth['time_to_members_months'].min(), 
                             df_growth['time_to_members_months'].max(), 100)
        
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Trend',
            line=dict(color='gray', dash='dash'),
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            xaxis_title='Months to Reach Current Membership',
            yaxis_title='Current Members',
            height=500,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        median_time = df_growth['time_to_members_months'].median()
        st.caption(f"Median: {median_time:.0f} months to reach current membership level")
        
        if highlight_studio and not df_h.empty:
            your_time = df_h['time_to_members_months'].iloc[0]
            your_members = df_h['current_members'].iloc[0]
            st.info(f"""
            **Your growth:** Reached {your_members:.0f} members in {your_time:.0f} months
            - Growth rate: ~{(your_members/your_time if your_time > 0 else 0):.1f} members/month
            """)
    
    # Q33: Startup capital distribution
    st.markdown("---")
    st.subheader("Q14: How much does it cost to start a studio?")
    
    if 'startup_capital_range' in df.columns:
        capital_counts = df['startup_capital_range'].value_counts().reset_index()
        capital_counts.columns = ['Capital Range', 'Count']
        
        # Order the ranges logically
        range_order = [
            "Under $10,000",
            "$10,000-$25,000", 
            "$25,000-$50,000",
            "$50,000-$75,000",
            "$75,000-$100,000",
            "$100,000-$150,000",
            "Over $150,000"
        ]
        
        capital_counts['Capital Range'] = pd.Categorical(
            capital_counts['Capital Range'], 
            categories=range_order, 
            ordered=True
        )
        capital_counts = capital_counts.sort_values('Capital Range')
        
        chart = alt.Chart(capital_counts).mark_bar().encode(
            x=alt.X('Count:Q'),
            y=alt.Y('Capital Range:N', sort=range_order),
            tooltip=['Capital Range', 'Count'],
            color=alt.value('#2ca02c')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)


def show_operational_models(df, highlight_studio=None):
    """Section 8: Operational Models Comparison"""
    
    st.header("⚙️ Section 8: Operational Models")
    
    # Q20: Access models
    st.subheader("Q15: What access models do studios use?")
    
    if 'access_model' in df.columns:
        access_counts = df['access_model'].value_counts().reset_index()
        access_counts.columns = ['Access Model', 'Count']
        
        if highlight_studio and highlight_studio in df['studio_name'].values:
            user_model = df[df['studio_name'] == highlight_studio]['access_model'].iloc[0]
            access_counts['is_user'] = access_counts['Access Model'] == user_model
        else:
            access_counts['is_user'] = False
        
        chart = alt.Chart(access_counts).mark_bar().encode(
            y=alt.Y('Access Model:N', sort='-x'),
            x=alt.X('Count:Q'),
            color=alt.condition(
                alt.datum.is_user == True,
                alt.value('#FF4B4B'),
                alt.value('#1f77b4')
            ),
            tooltip=['Access Model', 'Count']
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Q22: Staffing patterns
    st.markdown("---")
    st.subheader("Q16: Do studios have paid staff?")
    
    if 'has_staff' in df.columns and 'current_members' in df.columns:
        def _to_bool(s):
            if pd.api.types.is_bool_dtype(s):
                return s
            s = s.astype(str).str.strip().str.lower()
            mapping = {'yes': True, 'y': True, 'true': True, 't': True, '1': True, 
                      'no': False, 'n': False, 'false': False, 'f': False, '0': False}
            return s.map(mapping)
        
        df_staff = df.copy()
        df_staff['has_staff_bool'] = _to_bool(df_staff['has_staff'])
        df_staff = df_staff[df_staff['has_staff_bool'].notna() & df_staff['current_members'].notna()]
        
        if len(df_staff) > 0:
            # Scatter: staffing vs studio size
            if highlight_studio and highlight_studio in df_staff['studio_name'].values:
                df_h = df_staff[df_staff['studio_name'] == highlight_studio]
                df_o = df_staff[df_staff['studio_name'] != highlight_studio]
            else:
                df_h = pd.DataFrame()
                df_o = df_staff
            
            fig = go.Figure()
            
            # Split by has_staff
            for has_staff, color, name in [(True, '#ff7f0e', 'Has Staff'), 
                                           (False, '#2ca02c', 'No Staff')]:
                subset = df_o[df_o['has_staff_bool'] == has_staff]
                fig.add_trace(go.Scatter(
                    x=subset['current_members'],
                    y=[1 if has_staff else 0] * len(subset),
                    mode='markers',
                    name=name,
                    marker=dict(size=10, color=color, opacity=0.6),
                    text=subset['studio_name'],
                    hovertemplate='<b>Studio %{text}</b><br>Members: %{x}<br>' + name + '<extra></extra>'
                ))
            
            if not df_h.empty:
                fig.add_trace(go.Scatter(
                    x=df_h['current_members'],
                    y=[1 if df_h['has_staff_bool'].iloc[0] else 0],
                    mode='markers',
                    name='Your Studio',
                    marker=dict(size=18, color='#FF4B4B', symbol='star'),
                    hovertemplate='<b>YOUR STUDIO</b><br>Members: %{x}<extra></extra>'
                ))
            
            fig.update_layout(
                xaxis_title='Current Members',
                yaxis=dict(
                    tickvals=[0, 1],
                    ticktext=['No Paid Staff', 'Has Paid Staff'],
                    range=[-0.5, 1.5]
                ),
                height=300,
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate typical staffing threshold
            df_with_staff = df_staff[df_staff['has_staff_bool'] == True]
            if len(df_with_staff) > 0:
                median_members_with_staff = df_with_staff['current_members'].median()
                st.caption(f"Studios with paid staff have a median of {median_members_with_staff:.0f} members")


def show_market_context(df, highlight_studio=None):
    """Section 9: Market & Competition Context"""
    
    st.header("🗺️ Section 9: Market & Competition")
    
    # Q29: Where are studios located?
    st.subheader("Q17: Where are studios located?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'area_type' in df.columns:
            area_counts = df['area_type'].value_counts().reset_index()
            area_counts.columns = ['Area Type', 'Count']
            
            if highlight_studio and highlight_studio in df['studio_name'].values:
                user_area = df[df['studio_name'] == highlight_studio]['area_type'].iloc[0]
                area_counts['is_user'] = area_counts['Area Type'] == user_area
            else:
                area_counts['is_user'] = False
            
            chart = alt.Chart(area_counts).mark_bar().encode(
                y=alt.Y('Area Type:N', sort='-x'),
                x=alt.X('Count:Q'),
                color=alt.condition(
                    alt.datum.is_user == True,
                    alt.value('#FF4B4B'),
                    alt.value('#1f77b4')
                ),
                tooltip=['Area Type', 'Count']
            ).properties(height=250, title='Studio Locations by Area Type')
            
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        if 'metro_population' in df.columns:
            metro_counts = df['metro_population'].value_counts().reset_index()
            metro_counts.columns = ['Metro Population', 'Count']
            
            # Order logically
            pop_order = [
                "Under 50,000",
                "50,000-100,000",
                "100,000-250,000",
                "250,000-500,000",
                "500,000-1M",
                "Over 1M"
            ]
            
            metro_counts['Metro Population'] = pd.Categorical(
                metro_counts['Metro Population'],
                categories=pop_order,
                ordered=True
            )
            metro_counts = metro_counts.sort_values('Metro Population')
            
            chart = alt.Chart(metro_counts).mark_bar().encode(
                y=alt.Y('Metro Population:N', sort=pop_order),
                x=alt.X('Count:Q'),
                tooltip=['Metro Population', 'Count'],
                color=alt.value('#2ca02c')
            ).properties(height=250, title='Metro Area Population Distribution')
            
            st.altair_chart(chart, use_container_width=True)
    
    # Q30: Competition analysis
    st.markdown("---")
    st.subheader("Q18: How much competition exists?")
    
    if 'competing_studios' in df.columns:
        df_comp = df.copy()
        df_comp['competing_studios'] = pd.to_numeric(df_comp['competing_studios'], errors='coerce')
        df_comp = df_comp[df_comp['competing_studios'].notna()]
        
        if len(df_comp) > 0:
            chart = alt.Chart(df_comp).mark_bar().encode(
                x=alt.X('competing_studios:Q', bin=alt.Bin(step=1), 
                       title='Competing Studios within 20 Miles'),
                y=alt.Y('count()', title='Number of Studios'),
                color=alt.value('#ff7f0e')
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                median_comp = df_comp['competing_studios'].median()
                st.metric("Median Competition", f"{median_comp:.0f} studios")
            with col2:
                pct_no_comp = (df_comp['competing_studios'] == 0).sum() / len(df_comp) * 100
                st.metric("No Direct Competition", f"{pct_no_comp:.0f}%")
            with col3:
                pct_high_comp = (df_comp['competing_studios'] >= 3).sum() / len(df_comp) * 100
                st.metric("High Competition (3+)", f"{pct_high_comp:.0f}%")
            
            if highlight_studio and highlight_studio in df_comp['studio_name'].values:
                your_comp = df_comp[df_comp['studio_name'] == highlight_studio]['competing_studios'].iloc[0]
                st.info(f"Your competition level: {your_comp:.0f} studios within 20 miles")
    
    # Q31: Pricing vs competitors
    st.markdown("---")
    st.subheader("Q19: How do studios price vs. competitors?")
    
    if 'pricing_vs_competitors' in df.columns:
        pricing_comp = df['pricing_vs_competitors'].value_counts().reset_index()
        pricing_comp.columns = ['Pricing Position', 'Count']
        
        # Order logically
        price_order = [
            "Significantly lower",
            "Somewhat lower",
            "About the same",
            "Somewhat higher",
            "Significantly higher",
            "Don't know/No competitors"
        ]
        
        pricing_comp['Pricing Position'] = pd.Categorical(
            pricing_comp['Pricing Position'],
            categories=price_order,
            ordered=True
        )
        pricing_comp = pricing_comp.sort_values('Pricing Position')
        
        if highlight_studio and highlight_studio in df['studio_name'].values:
            user_pricing = df[df['studio_name'] == highlight_studio]['pricing_vs_competitors'].iloc[0]
            pricing_comp['is_user'] = pricing_comp['Pricing Position'] == user_pricing
        else:
            pricing_comp['is_user'] = False
        
        chart = alt.Chart(pricing_comp).mark_bar().encode(
            y=alt.Y('Pricing Position:N', sort=price_order),
            x=alt.X('Count:Q'),
            color=alt.condition(
                alt.datum.is_user == True,
                alt.value('#FF4B4B'),
                alt.value('#9467bd')
            ),
            tooltip=['Pricing Position', 'Count']
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)


def show_classes_workshops(df, highlight_studio=None):
    """Section 10: Classes & Workshops Detail"""
    
    st.header("🎓 Section 10: Classes & Workshops")
    
    # Q35: What % offer classes?
    st.subheader("Q20: What percentage of studios offer classes?")
    
    if 'offers_classes' in df.columns:
        def _to_bool(s):
            if pd.api.types.is_bool_dtype(s):
                return s.astype(int)
            s = s.astype(str).str.strip().str.lower()
            mapping = {'yes': 1, 'y': 1, 'true': 1, 't': 1, '1': 1, 
                      'no': 0, 'n': 0, 'false': 0, 'f': 0, '0': 0}
            return s.map(mapping)
        
        classes01 = _to_bool(df['offers_classes'])
        valid = classes01.notna().sum()
        
        if valid > 0:
            pct_offering = (classes01.sum() / valid) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Studios Offering Classes", f"{pct_offering:.0f}%")
            
            # Q36: Class pricing
            df_classes = df[classes01 == 1].copy()
            df_classes['class_price'] = pd.to_numeric(df_classes['class_price'], errors='coerce')
            df_classes['class_weeks'] = pd.to_numeric(df_classes['class_weeks'], errors='coerce')
            
            if 'class_price' in df_classes.columns and len(df_classes[df_classes['class_price'].notna()]) > 0:
                with col2:
                    median_price = df_classes['class_price'].median()
                    st.metric("Median Class Price", f"${median_price:.0f}")
            
            st.markdown("---")
            st.subheader("Q21: Class pricing by length")
            
            df_class_price = df_classes[df_classes['class_price'].notna() & 
                                       df_classes['class_weeks'].notna()]
            
            if len(df_class_price) > 0:
                # Scatter: price vs weeks
                if highlight_studio and highlight_studio in df_class_price['studio_name'].values:
                    df_h = df_class_price[df_class_price['studio_name'] == highlight_studio]
                    df_o = df_class_price[df_class_price['studio_name'] != highlight_studio]
                else:
                    df_h = pd.DataFrame()
                    df_o = df_class_price
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_o['class_weeks'],
                    y=df_o['class_price'],
                    mode='markers',
                    name='Other Studios',
                    marker=dict(size=10, color='#8c564b', opacity=0.6),
                    text=df_o['studio_name'],
                    hovertemplate='<b>Studio %{text}</b><br>Weeks: %{x}<br>Price: $%{y}<extra></extra>'
                ))
                
                if not df_h.empty:
                    fig.add_trace(go.Scatter(
                        x=df_h['class_weeks'],
                        y=df_h['class_price'],
                        mode='markers',
                        name='Your Studio',
                        marker=dict(size=18, color='#FF4B4B', symbol='star'),
                        hovertemplate='<b>YOUR STUDIO</b><br>Weeks: %{x}<br>Price: $%{y}<extra></extra>'
                    ))
                
                fig.update_layout(
                    xaxis_title='Class Length (Weeks)',
                    yaxis_title='Class Price ($)',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate price per week
                df_class_price['price_per_week'] = df_class_price['class_price'] / df_class_price['class_weeks']
                median_per_week = df_class_price['price_per_week'].median()
                
                st.caption(f"Median price per week: ${median_per_week:.0f}/week")


def show_capacity_waitlists(df, highlight_studio=None):
    """Section 11: Capacity Utilization & Waitlists"""
    
    st.header("📊 Section 11: Capacity & Waitlists")
    
    # Q40: Capacity utilization
    st.subheader("Q22: What's your capacity utilization?")
    
    if 'capacity_utilization' in df.columns:
        df_cap = df.copy()
        df_cap['capacity_utilization'] = pd.to_numeric(df_cap['capacity_utilization'], errors='coerce')
        df_cap = df_cap[df_cap['capacity_utilization'].notna()]
        
        if len(df_cap) > 0:
            chart = alt.Chart(df_cap).mark_bar().encode(
                x=alt.X('capacity_utilization:Q', bin=alt.Bin(step=10), 
                       title='Capacity Utilization (%)'),
                y=alt.Y('count()', title='Number of Studios'),
                color=alt.value('#17becf')
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                median_cap = df_cap['capacity_utilization'].median()
                st.metric("Median Capacity", f"{median_cap:.0f}%")
            with col2:
                high_cap = (df_cap['capacity_utilization'] >= 80).sum() / len(df_cap) * 100
                st.metric("High Utilization (≥80%)", f"{high_cap:.0f}%")
            with col3:
                low_cap = (df_cap['capacity_utilization'] < 50).sum() / len(df_cap) * 100
                st.metric("Low Utilization (<50%)", f"{low_cap:.0f}%")
            
            if highlight_studio and highlight_studio in df_cap['studio_name'].values:
                your_cap = df_cap[df_cap['studio_name'] == highlight_studio]['capacity_utilization'].iloc[0]
                st.info(f"""
                Your capacity utilization: {your_cap:.0f}%
                - {'Consider expansion or raising prices' if your_cap >= 80 else 'Room to grow membership' if your_cap < 60 else 'Healthy utilization level'}
                """)
    
    # Q3: Waitlists
    st.markdown("---")
    st.subheader("Q23: At what member density do studios develop waitlists?")
    
    if 'has_waitlist' in df.columns:
        def _to_bool(s):
            if pd.api.types.is_bool_dtype(s):
                return s
            s = s.astype(str).str.strip().str.lower()
            mapping = {'yes': True, 'y': True, 'true': True, 't': True, '1': True,
                      'no': False, 'n': False, 'false': False, 'f': False, '0': False}
            return s.map(mapping)
        
        df_wait = df.copy()
        df_wait['has_waitlist_bool'] = _to_bool(df_wait['has_waitlist'])
        df_wait['members_per_wheel'] = pd.to_numeric(df_wait['members_per_wheel'], errors='coerce')
        df_wait = df_wait[df_wait['has_waitlist_bool'].notna() & 
                         df_wait['members_per_wheel'].notna()]
        
        if len(df_wait) > 0:
            # Scatter showing waitlist vs member density
            if highlight_studio and highlight_studio in df_wait['studio_name'].values:
                df_h = df_wait[df_wait['studio_name'] == highlight_studio]
                df_o = df_wait[df_wait['studio_name'] != highlight_studio]
            else:
                df_h = pd.DataFrame()
                df_o = df_wait
            
            fig = go.Figure()
            
            # Split by waitlist status
            for has_wait, color, name in [(True, '#d62728', 'Has Waitlist'),
                                         (False, '#2ca02c', 'No Waitlist')]:
                subset = df_o[df_o['has_waitlist_bool'] == has_wait]
                if len(subset) > 0:
                    fig.add_trace(go.Scatter(
                        x=subset['members_per_wheel'],
                        y=[1 if has_wait else 0] * len(subset),
                        mode='markers',
                        name=name,
                        marker=dict(size=10, color=color, opacity=0.6),
                        text=subset['studio_name'],
                        hovertemplate='<b>Studio %{text}</b><br>Members/Wheel: %{x:.1f}<br>' + 
                                    name + '<extra></extra>'
                    ))
            
            if not df_h.empty:
                fig.add_trace(go.Scatter(
                    x=df_h['members_per_wheel'],
                    y=[1 if df_h['has_waitlist_bool'].iloc[0] else 0],
                    mode='markers',
                    name='Your Studio',
                    marker=dict(size=18, color='#FF4B4B', symbol='star'),
                    hovertemplate='<b>YOUR STUDIO</b><br>Members/Wheel: %{x:.1f}<extra></extra>'
                ))
            
            fig.update_layout(
                xaxis_title='Members per Wheel',
                yaxis=dict(
                    tickvals=[0, 1],
                    ticktext=['No Waitlist', 'Has Waitlist'],
                    range=[-0.5, 1.5]
                ),
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate threshold
            waitlist_studios = df_wait[df_wait['has_waitlist_bool'] == True]
            no_waitlist_studios = df_wait[df_wait['has_waitlist_bool'] == False]
            
            if len(waitlist_studios) > 0:
                median_with_wait = waitlist_studios['members_per_wheel'].median()
                st.caption(f"Studios with waitlists have a median of {median_with_wait:.1f} members/wheel")
            
            if len(no_waitlist_studios) > 0:
                median_without_wait = no_waitlist_studios['members_per_wheel'].median()
                st.caption(f"Studios without waitlists have a median of {median_without_wait:.1f} members/wheel")


def show_buildout_costs(df, highlight_studio=None):
    """Section 12: Build-Out Investment Analysis"""
    
    st.header("🔨 Section 12: Build-Out Investment")
    
    # Q33 (cont): Build-out costs
    st.subheader("Q24: How much do leasehold improvements cost?")
    
    if 'buildout_cost_total' in df.columns:
        df_buildout = df.copy()
        df_buildout['buildout_cost_total'] = pd.to_numeric(df_buildout['buildout_cost_total'], 
                                                           errors='coerce')
        df_buildout['space_sqft'] = pd.to_numeric(df_buildout['space_sqft'], errors='coerce')
        df_buildout = df_buildout[df_buildout['buildout_cost_total'].notna() & 
                                 (df_buildout['buildout_cost_total'] > 0)]
        
        if len(df_buildout) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Histogram of total costs
                chart = alt.Chart(df_buildout).mark_bar().encode(
                    x=alt.X('buildout_cost_total:Q', bin=alt.Bin(step=25000),
                           title='Build-Out Cost ($)'),
                    y=alt.Y('count()', title='Number of Studios'),
                    color=alt.value('#e377c2')
                ).properties(height=300, title='Total Build-Out Costs')
                
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                # Calculate cost per sqft
                df_buildout['cost_per_sqft'] = (df_buildout['buildout_cost_total'] / 
                                               df_buildout['space_sqft'])
                df_buildout_sqft = df_buildout[df_buildout['cost_per_sqft'].notna()]
                
                if len(df_buildout_sqft) > 0:
                    chart = alt.Chart(df_buildout_sqft).mark_bar().encode(
                        x=alt.X('cost_per_sqft:Q', bin=alt.Bin(step=25),
                               title='Cost per Square Foot ($)'),
                        y=alt.Y('count()', title='Number of Studios'),
                        color=alt.value('#bcbd22')
                    ).properties(height=300, title='Build-Out Cost per Sq Ft')
                    
                    st.altair_chart(chart, use_container_width=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                median_total = df_buildout['buildout_cost_total'].median()
                st.metric("Median Total Cost", f"${median_total:,.0f}")
            with col2:
                if 'cost_per_sqft' in df_buildout.columns:
                    median_sqft = df_buildout['cost_per_sqft'].median()
                    st.metric("Median per Sq Ft", f"${median_sqft:.2f}")
            with col3:
                q75 = df_buildout['buildout_cost_total'].quantile(0.75)
                st.metric("75th Percentile", f"${q75:,.0f}")
            
            if highlight_studio and highlight_studio in df_buildout['studio_name'].values:
                your_cost = df_buildout[df_buildout['studio_name'] == highlight_studio]['buildout_cost_total'].iloc[0]
                st.info(f"Your build-out cost: ${your_cost:,.0f}")


def show_member_retention(df, highlight_studio=None):
    """Section 13: Member Retention Deep Dive"""
    
    st.header("🔄 Section 13: Member Retention")
    
    # Q25: Why do members leave?
    st.subheader("Q25: Why do members leave?")
    
    if 'top_churn_reasons' in df.columns:
        # Extract all churn reasons
        all_reasons = []
        for reasons in df['top_churn_reasons'].dropna():
            parsed = _parse_jsonish(reasons)
            if isinstance(parsed, list):
                all_reasons.extend(parsed)
            elif isinstance(parsed, str) and parsed:
                all_reasons.append(parsed)
        
        if all_reasons:
            reason_counts = pd.Series(all_reasons).value_counts().reset_index()
            reason_counts.columns = ['Reason', 'Count']
            
            chart = alt.Chart(reason_counts.head(10)).mark_bar().encode(
                y=alt.Y('Reason:N', sort='-x'),
                x=alt.X('Count:Q'),
                tooltip=['Reason', 'Count'],
                color=alt.value('#d62728')
            ).properties(height=350, title='Top Reasons for Member Churn')
            
            st.altair_chart(chart, use_container_width=True)
            
            st.caption("Understanding why members leave can help improve retention strategies")
    
    # Q23: Member composition
    st.markdown("---")
    st.subheader("Q26: What's typical member composition?")
    
    if 'member_pcts' in df.columns:
        # Extract member percentages and average them
        member_data = []
        for idx, row in df.iterrows():
            pct_dict = _parse_jsonish(row['member_pcts'])
            if isinstance(pct_dict, dict):
                for member_type, pct in pct_dict.items():
                    if isinstance(pct, (int, float)) and pct > 0:
                        member_data.append({'type': member_type, 'percentage': pct})
        
        if member_data:
            mem_df = pd.DataFrame(member_data)
            avg_mem = mem_df.groupby('type')['percentage'].mean().reset_index()
            avg_mem.columns = ['Member Type', 'Average %']
            
            # Clean names
            name_map = {
                'hobbyist': 'Hobbyists\n(1x/week or less)',
                'regular': 'Regular Artists\n(2-3x/week)',
                'production': 'Production Potters\n(4+x/week)',
                'seasonal': 'Seasonal/Occasional'
            }
            avg_mem['Member Type'] = avg_mem['Member Type'].map(
                lambda x: name_map.get(x, x.title())
            )
            
            fig = px.pie(avg_mem, values='Average %', names='Member Type',
                        title='Average Member Composition Across Studios',
                        height=400,
                        color_discrete_sequence=px.colors.qualitative.Set3)
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("Most studios have a mix of casual hobbyists and dedicated regular artists")
    
    # Q24 enhanced: Churn vs member count
    st.markdown("---")
    st.subheader("Q27: Does churn rate vary by studio size?")
    
    df_churn_size = df.copy()
    df_churn_size['monthly_churn'] = pd.to_numeric(df_churn_size['monthly_churn'], errors='coerce')
    df_churn_size['current_members'] = pd.to_numeric(df_churn_size['current_members'], errors='coerce')
    df_churn_size = df_churn_size[df_churn_size['monthly_churn'].notna() & 
                                   df_churn_size['current_members'].notna()]
    
    if len(df_churn_size) > 0:
        if highlight_studio and highlight_studio in df_churn_size['studio_name'].values:
            df_h = df_churn_size[df_churn_size['studio_name'] == highlight_studio]
            df_o = df_churn_size[df_churn_size['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_churn_size
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_o['current_members'],
            y=df_o['monthly_churn'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#8c564b', opacity=0.6),
            text=df_o['studio_name'],
            hovertemplate='<b>Studio %{text}</b><br>Members: %{x}<br>Churn: %{y:.1f}%<extra></extra>'
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['current_members'],
                y=df_h['monthly_churn'],
                mode='markers',
                name='Your Studio',
                marker=dict(size=18, color='#FF4B4B', symbol='star'),
                hovertemplate='<b>YOUR STUDIO</b><br>Members: %{x}<br>Churn: %{y:.1f}%<extra></extra>'
            ))
        
        # Add median line
        median_churn = df_churn_size['monthly_churn'].median()
        fig.add_hline(y=median_churn, line_dash="dash", line_color="gray",
                     annotation_text=f"Median: {median_churn:.1f}%", annotation_position="right")
        
        fig.update_layout(
            xaxis_title='Current Members',
            yaxis_title='Monthly Churn Rate (%)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_revenue_optimization(df, highlight_studio=None):
    """Section 14: Revenue Mix Optimization"""
    
    st.header("💡 Section 14: Revenue Optimization")
    
    # Q14: Revenue mix by profitability
    st.subheader("Q28: What revenue mix do profitable studios have?")
    
    if 'revenue_pcts' in df.columns and 'profitability_status' in df.columns:
        # Extract revenue data by profitability status
        revenue_by_profit = []
        for idx, row in df.iterrows():
            rev_dict = _parse_jsonish(row['revenue_pcts'])
            profit_status = row['profitability_status']
            
            if isinstance(rev_dict, dict) and profit_status in ['Profitable', 'Breaking even', 'Operating at loss']:
                for source, pct in rev_dict.items():
                    if isinstance(pct, (int, float)) and pct > 0:
                        revenue_by_profit.append({
                            'source': source,
                            'percentage': pct,
                            'status': profit_status
                        })
        
        if revenue_by_profit:
            rev_df = pd.DataFrame(revenue_by_profit)
            
            # Calculate average by source and status
            avg_rev = rev_df.groupby(['status', 'source'])['percentage'].mean().reset_index()
            
            # Clean names
            name_map = {
                'membership': 'Membership',
                'clay': 'Clay Sales',
                'firing': 'Firing Fees',
                'classes': 'Classes',
                'events': 'Events',
                'other': 'Other'
            }
            avg_rev['source'] = avg_rev['source'].map(lambda x: name_map.get(x, x.title()))
            
            # Create grouped bar chart
            fig = px.bar(avg_rev, 
                        x='source', 
                        y='percentage',
                        color='status',
                        barmode='group',
                        title='Revenue Mix by Profitability Status',
                        labels={'percentage': 'Average %', 'source': 'Revenue Source'},
                        height=400)
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("Profitable studios tend to have more diversified revenue streams")
    
    # Q7: Does having multiple tiers increase revenue?
    st.markdown("---")
    st.subheader("Q29: Does having multiple tiers increase revenue?")
    
    if 'tier_structure' in df.columns and 'monthly_revenue_range' in df.columns:
        tier_revenue = df[df['tier_structure'].notna() & df['monthly_revenue_range'].notna()].copy()
        
        if len(tier_revenue) > 0:
            # Count by tier structure and revenue range
            tier_rev_counts = tier_revenue.groupby(['tier_structure', 'monthly_revenue_range']).size().reset_index(name='count')
            
            # Order revenue ranges
            revenue_order = [
                "Under $5,000",
                "$5,000-$10,000",
                "$10,000-$20,000",
                "$20,000-$35,000",
                "$35,000-$50,000",
                "$50,000-$75,000",
                "Over $75,000",
                "Prefer not to say"
            ]
            
            tier_rev_counts['monthly_revenue_range'] = pd.Categorical(
                tier_rev_counts['monthly_revenue_range'],
                categories=revenue_order,
                ordered=True
            )
            
            # Use altair instead for more reliable rendering
            chart = alt.Chart(tier_rev_counts).mark_bar().encode(
                x=alt.X('tier_structure:N', title='Tier Structure'),
                y=alt.Y('count:Q', title='Number of Studios'),
                color=alt.Color('monthly_revenue_range:N', 
                              title='Revenue Range',
                              scale=alt.Scale(scheme='category20')),
                tooltip=['tier_structure', 'monthly_revenue_range', 'count']
            ).properties(height=400, title='Revenue Ranges by Tier Structure')
            
            st.altair_chart(chart, use_container_width=True)
            
            st.caption("Analysis shows whether multi-tier pricing correlates with higher revenue")


def show_profitability_patterns(df, highlight_studio=None):
    """Section 15: Profitability Analysis"""
    
    st.header("📈 Section 15: Profitability Patterns")
    
    # Q13: Time to profitability
    st.subheader("Q30: How long until studios become profitable?")
    
    if 'time_to_profitability' in df.columns:
        time_counts = df['time_to_profitability'].value_counts().reset_index()
        time_counts.columns = ['Time to Profit', 'Count']
        
        # Order logically
        time_order = [
            "Under 6 months",
            "6-12 months",
            "12-18 months",
            "18-24 months",
            "Over 24 months",
            "Not yet profitable"
        ]
        
        time_counts['Time to Profit'] = pd.Categorical(
            time_counts['Time to Profit'],
            categories=time_order,
            ordered=True
        )
        time_counts = time_counts.sort_values('Time to Profit')
        
        if highlight_studio and highlight_studio in df['studio_name'].values:
            user_time = df[df['studio_name'] == highlight_studio]['time_to_profitability'].iloc[0]
            time_counts['is_user'] = time_counts['Time to Profit'] == user_time
        else:
            time_counts['is_user'] = False
        
        chart = alt.Chart(time_counts).mark_bar().encode(
            y=alt.Y('Time to Profit:N', sort=time_order),
            x=alt.X('Count:Q'),
            color=alt.condition(
                alt.datum.is_user == True,
                alt.value('#FF4B4B'),
                alt.value('#2ca02c')
            ),
            tooltip=['Time to Profit', 'Count']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Rent burden analysis
    st.markdown("---")
    st.subheader("Q31: What's a sustainable rent burden?")
    
    # Calculate rent as % of estimated revenue for profitable studios
    df_rent_burden = df.copy()
    df_rent_burden['rent'] = pd.to_numeric(df_rent_burden['rent'], errors='coerce')
    df_rent_burden['current_members'] = pd.to_numeric(df_rent_burden['current_members'], errors='coerce')
    df_rent_burden['tier1_price'] = pd.to_numeric(df_rent_burden['tier1_price'], errors='coerce')
    
    # Estimate revenue as members * tier1_price
    df_rent_burden['est_membership_revenue'] = (df_rent_burden['current_members'] * 
                                                df_rent_burden['tier1_price'])
    df_rent_burden['rent_pct'] = (df_rent_burden['rent'] / 
                                  df_rent_burden['est_membership_revenue'] * 100)
    
    df_rent_burden = df_rent_burden[df_rent_burden['rent_pct'].notna() & 
                                   (df_rent_burden['rent_pct'] > 0) &
                                   (df_rent_burden['rent_pct'] < 200)]  # Filter outliers
    
    if len(df_rent_burden) > 0 and 'profitability_status' in df_rent_burden.columns:
        # Box plot by profitability
        df_plot = df_rent_burden[df_rent_burden['profitability_status'].isin(
            ['Profitable', 'Breaking even', 'Operating at loss'])]
        
        if len(df_plot) > 0:
            fig = px.box(df_plot,
                        x='profitability_status',
                        y='rent_pct',
                        title='Rent as % of Membership Revenue by Profitability',
                        labels={'rent_pct': 'Rent (% of Membership Revenue)',
                               'profitability_status': 'Profitability Status'},
                        height=400)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate medians
            profitable = df_plot[df_plot['profitability_status'] == 'Profitable']
            if len(profitable) > 0:
                median_prof = profitable['rent_pct'].median()
                st.caption(f"Profitable studios: Median rent is {median_prof:.0f}% of membership revenue")
            
            if highlight_studio and highlight_studio in df_rent_burden['studio_name'].values:
                your_pct = df_rent_burden[df_rent_burden['studio_name'] == highlight_studio]['rent_pct'].iloc[0]
                st.info(f"Your rent burden: {your_pct:.0f}% of estimated membership revenue")


def show_kiln_analysis(df, highlight_studio=None):
    """Section 16: Kiln Utilization & Efficiency"""
    
    st.header("🔥 Section 16: Kiln Analysis")
    
    # Q19: How often are kilns actually used?
    st.subheader("Q32: How often are kilns actually used?")
    
    if 'kiln_utilization' in df.columns:
        df_kiln_util = df.copy()
        df_kiln_util['kiln_utilization'] = pd.to_numeric(df_kiln_util['kiln_utilization'], 
                                                         errors='coerce')
        df_kiln_util = df_kiln_util[df_kiln_util['kiln_utilization'].notna()]
        
        if len(df_kiln_util) > 0:
            # Distribution
            chart = alt.Chart(df_kiln_util).mark_bar().encode(
                x=alt.X('kiln_utilization:Q', bin=alt.Bin(step=10),
                       title='Kiln Utilization (%)'),
                y=alt.Y('count()', title='Number of Studios'),
                color=alt.value('#ff7f0e')
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                median_util = df_kiln_util['kiln_utilization'].median()
                st.metric("Median Utilization", f"{median_util:.0f}%")
            with col2:
                high_util = (df_kiln_util['kiln_utilization'] >= 80).sum() / len(df_kiln_util) * 100
                st.metric("High Utilization (≥80%)", f"{high_util:.0f}%")
            with col3:
                low_util = (df_kiln_util['kiln_utilization'] < 50).sum() / len(df_kiln_util) * 100
                st.metric("Low Utilization (<50%)", f"{low_util:.0f}%")
    
    # Kiln count vs members (improved - discrete integers)
    st.markdown("---")
    st.subheader("Q33: Optimal kiln count by studio size")
    
    df_kiln_count = df.copy()
    df_kiln_count['num_kilns'] = pd.to_numeric(df_kiln_count['num_kilns'], errors='coerce')
    df_kiln_count['current_members'] = pd.to_numeric(df_kiln_count['current_members'], errors='coerce')
    df_kiln_count = df_kiln_count[df_kiln_count['num_kilns'].notna() & 
                                   df_kiln_count['current_members'].notna()]
    
    if len(df_kiln_count) > 0:
        # Create bins for member count to show patterns
        df_kiln_count['member_range'] = pd.cut(df_kiln_count['current_members'],
                                               bins=[0, 25, 50, 75, 100, 200],
                                               labels=['0-25', '26-50', '51-75', '76-100', '100+'])
        
        # Box plot by member range
        fig = px.box(df_kiln_count,
                    x='member_range',
                    y='num_kilns',
                    title='Number of Kilns by Studio Size',
                    labels={'member_range': 'Member Count', 'num_kilns': 'Number of Kilns'},
                    height=400)
        
        # Force integer y-axis
        fig.update_yaxes(dtick=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate members per kiln
        df_kiln_count['members_per_kiln'] = (df_kiln_count['current_members'] / 
                                             df_kiln_count['num_kilns'])
        median_per_kiln = df_kiln_count['members_per_kiln'].median()
        
        st.caption(f"Median ratio: {median_per_kiln:.0f} members per kiln")
        
        if highlight_studio and highlight_studio in df_kiln_count['studio_name'].values:
            your_kilns = df_kiln_count[df_kiln_count['studio_name'] == highlight_studio]['num_kilns'].iloc[0]
            your_members = df_kiln_count[df_kiln_count['studio_name'] == highlight_studio]['current_members'].iloc[0]
            your_ratio = your_members / your_kilns if your_kilns > 0 else 0
            
            st.info(f"""
            Your setup: {int(your_kilns)} kiln(s) for {int(your_members)} members
            - Ratio: {your_ratio:.0f} members/kiln ({'above' if your_ratio > median_per_kiln else 'below'} median)
            """)
    
    # Firing frequency from kilns data
    st.markdown("---")
    st.subheader("Q34: How many firings per month?")
    
    if 'kilns' in df.columns:
        # Extract firings from kilns JSON
        all_firings = []
        for idx, row in df.iterrows():
            kilns_data = _parse_jsonish(row['kilns'])
            if isinstance(kilns_data, list):
                for kiln in kilns_data:
                    if isinstance(kiln, dict) and 'firings' in kiln:
                        try:
                            firings = int(kiln['firings'])
                            all_firings.append(firings)
                        except (ValueError, TypeError):
                            pass
        
        if all_firings:
            firings_series = pd.Series(all_firings)
            
            chart = alt.Chart(pd.DataFrame({'firings': all_firings})).mark_bar().encode(
                x=alt.X('firings:Q', bin=alt.Bin(step=2), title='Firings per Month'),
                y=alt.Y('count()', title='Number of Kilns'),
                color=alt.value('#d62728')
            ).properties(height=300, title='Firing Frequency Distribution')
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Median Firings/Month", f"{firings_series.median():.0f}")
            with col2:
                st.metric("Average Firings/Month", f"{firings_series.mean():.1f}")