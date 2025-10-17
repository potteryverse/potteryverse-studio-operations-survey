#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REORGANIZED: Complete Enhanced Free Tier Results Visualizations
Logical grouping with sequential question numbering Q1-Q61
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import json
import ast
import re


def show_enhanced_charts(df: pd.DataFrame):
    """Complete enhanced visualizations - reorganized for logical flow"""
    
    st.header("🔍 Comprehensive Studio Analysis")
    st.caption("Question-driven insights with individual studio benchmarking")
    
    # === STUDIO SELECTOR ===
    st.markdown("---")
    st.subheader("🎯 Find Your Studio")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        studio_ids = ["View All Studios (No Highlighting)"] + sorted(df['studio_name'].unique().tolist())
        selected_studio = st.selectbox(
            "Select your 4-character studio ID:",
            options=studio_ids,
            help="Your studio ID was provided when you submitted the survey."
        )
    
    highlight_studio = None if selected_studio == "View All Studios (No Highlighting)" else selected_studio
    
    with col2:
        if highlight_studio:
            studio_data = df[df['studio_name'] == highlight_studio].iloc[0]
            st.metric("Your Members", f"{int(studio_data['current_members'])}")
    
    with col3:
        if highlight_studio:
            st.metric("Your Space", f"{int(studio_data['space_sqft'])} sq ft")
    
    if highlight_studio:
        st.success(f"✓ Viewing data for studio **{highlight_studio}**")
    else:
        st.info("💡 Select your studio ID above to see your position on all charts")
    
    st.markdown("---")
    
    # ===================================================================
    # PART 1: STUDIO BASICS (Primary Data)
    # ===================================================================
    
    st.title("📊 PART 1: Studio Basics")
    
    show_physical_studio(df, highlight_studio)
    st.markdown("---")
    
    show_equipment_inventory(df, highlight_studio)
    st.markdown("---")
    
    show_membership_scale(df, highlight_studio)
    st.markdown("---")
    
    # ===================================================================
    # PART 2: SPACE & CAPACITY EFFICIENCY
    # ===================================================================
    
    st.title("📐 PART 2: Space & Capacity Efficiency")
    
    show_space_efficiency(df, highlight_studio)
    st.markdown("---")
    
    # ===================================================================
    # PART 3: PRICING & REVENUE
    # ===================================================================
    
    st.title("💰 PART 3: Pricing & Revenue")
    
    show_membership_pricing(df, highlight_studio)
    st.markdown("---")
    
    show_materials_services_pricing(df, highlight_studio)
    st.markdown("---")
    
    show_revenue_mix(df, highlight_studio)
    st.markdown("---")
    
    # ===================================================================
    # PART 4: COSTS & PROFITABILITY
    # ===================================================================
    
    st.title("💵 PART 4: Costs & Profitability")
    
    show_operating_costs(df, highlight_studio)
    st.markdown("---")
    
    show_financial_performance(df, highlight_studio)
    st.markdown("---")
    
    # ===================================================================
    # PART 5: OPERATIONS
    # ===================================================================
    
    st.title("⚙️ PART 5: Operations")
    
    show_access_staffing(df, highlight_studio)
    st.markdown("---")
    
    show_kiln_operations(df, highlight_studio)
    st.markdown("---")
    
    show_classes_events(df, highlight_studio)
    st.markdown("---")
    
    show_amenities(df, highlight_studio)
    st.markdown("---")
    
    # ===================================================================
    # PART 6: MARKET & GROWTH
    # ===================================================================
    
    st.title("📈 PART 6: Market & Growth")
    
    show_market_context(df, highlight_studio)
    st.markdown("---")
    
    show_member_dynamics(df, highlight_studio)


# ===========================================================================
# PART 1: STUDIO BASICS
# ===========================================================================

def show_physical_studio(df, highlight_studio=None):
    """Section 1: Physical Studio (Q1-Q6)"""
    
    st.header("🏢 Section 1: Physical Studio")
    
    # Q1: Studio size distribution
    st.subheader("Q1: How big are studios typically?")
    
    df_space = df.copy()
    df_space['space_sqft'] = pd.to_numeric(df_space['space_sqft'], errors='coerce')
    df_space = df_space[df_space['space_sqft'].notna()]
    
    if len(df_space) > 0:
        chart = alt.Chart(df_space).mark_bar().encode(
            x=alt.X('space_sqft:Q', bin=alt.Bin(step=500), title='Studio Size (Sq Ft)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#17becf')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Min", f"{df_space['space_sqft'].min():.0f} sq ft")
        with col2:
            st.metric("25th %ile", f"{df_space['space_sqft'].quantile(0.25):.0f} sq ft")
        with col3:
            st.metric("Median", f"{df_space['space_sqft'].median():.0f} sq ft")
        with col4:
            st.metric("75th %ile", f"{df_space['space_sqft'].quantile(0.75):.0f} sq ft")
    
    # Q2: Size by metro population
    st.markdown("---")
    st.subheader("Q2: Does studio size vary by metro population?")
    
    if 'metro_population' in df_space.columns:
        df_metro = df_space[df_space['metro_population'].notna()]
        
        if len(df_metro) > 0:
            fig = px.box(df_metro, 
                        x='metro_population', 
                        y='space_sqft',
                        title='Studio Size by Metro Population',
                        labels={'space_sqft': 'Studio Size (Sq Ft)', 
                               'metro_population': 'Metro Population'},
                        height=400)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Q3: Size by studio type
    st.markdown("---")
    st.subheader("Q3: Does studio size vary by studio type?")
    
    if 'studio_type' in df_space.columns:
        df_type = df_space[df_space['studio_type'].notna()]
        
        if len(df_type) > 0:
            fig = px.box(df_type,
                        x='studio_type',
                        y='space_sqft',
                        title='Studio Size by Type',
                        labels={'space_sqft': 'Studio Size (Sq Ft)',
                               'studio_type': 'Studio Type'},
                        height=400)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Q4: Years in operation
    st.markdown("---")
    st.subheader("Q4: How long have studios been operational?")
    
    df_age = df.copy()
    df_age['years_operating_total_months'] = pd.to_numeric(
        df_age['years_operating_total_months'], errors='coerce')
    df_age['years_operating'] = df_age['years_operating_total_months'] / 12
    
    df_age = df_age[df_age['years_operating'].notna()]
    
    if len(df_age) > 0:
        chart = alt.Chart(df_age).mark_bar().encode(
            x=alt.X('years_operating:Q', bin=alt.Bin(step=1), title='Years Operating'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#8c564b')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Newest", f"{df_age['years_operating'].min():.1f} yrs")
        with col2:
            st.metric("Median Age", f"{df_age['years_operating'].median():.1f} yrs")
        with col3:
            st.metric("Oldest", f"{df_age['years_operating'].max():.1f} yrs")
        with col4:
            young_studios = (df_age['years_operating'] < 2).sum()
            pct_young = (young_studios / len(df_age) * 100)
            st.metric("Under 2 Years", f"{pct_young:.0f}%")
    
    # Q5: Status by age
    st.markdown("---")
    st.subheader("Q5: How does studio status vary by age?")
    
    if 'studio_status' in df_age.columns:
        df_status = df_age[df_age['studio_status'].notna()]
        
        if len(df_status) > 0:
            df_status['age_bin'] = pd.cut(
                df_status['years_operating'],
                bins=[0, 1, 2, 5, 10, 100],
                labels=['<1 yr', '1-2 yrs', '2-5 yrs', '5-10 yrs', '10+ yrs']
            )
            
            status_age = df_status.groupby(['age_bin', 'studio_status']).size().reset_index(name='count')
            
            chart = alt.Chart(status_age).mark_bar().encode(
                x=alt.X('age_bin:N', title='Studio Age'),
                y=alt.Y('count:Q', title='Number of Studios'),
                color=alt.Color('studio_status:N', title='Status'),
                tooltip=['age_bin', 'studio_status', 'count']
            ).properties(height=350)
            
            st.altair_chart(chart, use_container_width=True)
    
    # Q6: Geographic distribution
    st.markdown("---")
    st.subheader("Q6: Where are studios located?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'area_type' in df.columns:
            area_counts = df['area_type'].value_counts().reset_index()
            area_counts.columns = ['Area Type', 'Count']
            
            chart = alt.Chart(area_counts).mark_bar().encode(
                y=alt.Y('Area Type:N', sort='-x'),
                x=alt.X('Count:Q'),
                tooltip=['Area Type', 'Count'],
                color=alt.value('#1f77b4')
            ).properties(height=250, title='Studio Locations by Area Type')
            
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        if 'metro_population' in df.columns:
            metro_counts = df['metro_population'].value_counts().reset_index()
            metro_counts.columns = ['Metro Population', 'Count']
            
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
            ).properties(height=250, title='Metro Area Distribution')
            
            st.altair_chart(chart, use_container_width=True)


def show_equipment_inventory(df, highlight_studio=None):
    """Section 2: Equipment Inventory (Q7-Q12)"""
    
    st.header("🛠️ Section 2: Equipment Inventory")
    
    # Prepare data
    df_equip = df.copy()
    for col in ['total_wheels', 'handbuilding_stations', 'glazing_stations', 'num_kilns', 'space_sqft']:
        df_equip[col] = pd.to_numeric(df_equip[col], errors='coerce')
    
    # Q7-Q10: Distribution of each equipment type
    st.subheader("Q7-Q10: What's the typical equipment inventory?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Q7: Pottery Wheels**")
        df_wheels = df_equip[df_equip['total_wheels'].notna()]
        if len(df_wheels) > 0:
            median_wheels = df_wheels['total_wheels'].median()
            st.metric("Median", f"{median_wheels:.0f} wheels")
            
            chart = alt.Chart(df_wheels).mark_bar().encode(
                x=alt.X('total_wheels:Q', bin=alt.Bin(step=2), title='Total Wheels'),
                y=alt.Y('count()', title='Studios'),
                color=alt.value('#1f77b4')
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        
        st.markdown("**Q9: Glazing Stations**")
        df_glaze = df_equip[df_equip['glazing_stations'].notna()]
        if len(df_glaze) > 0:
            median_glaze = df_glaze['glazing_stations'].median()
            st.metric("Median", f"{median_glaze:.0f} stations")
            
            chart = alt.Chart(df_glaze).mark_bar().encode(
                x=alt.X('glazing_stations:Q', bin=alt.Bin(step=2), 
                       title='Glazing Stations'),
                y=alt.Y('count()', title='Studios'),
                color=alt.value('#ff7f0e')
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown("**Q8: Handbuilding Stations**")
        df_hb = df_equip[df_equip['handbuilding_stations'].notna()]
        if len(df_hb) > 0:
            median_hb = df_hb['handbuilding_stations'].median()
            st.metric("Median", f"{median_hb:.0f} stations")
            
            chart = alt.Chart(df_hb).mark_bar().encode(
                x=alt.X('handbuilding_stations:Q', bin=alt.Bin(step=2), 
                       title='Handbuilding Stations'),
                y=alt.Y('count()', title='Studios'),
                color=alt.value('#2ca02c')
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        
        st.markdown("**Q10: Number of Kilns**")
        df_kilns = df_equip[df_equip['num_kilns'].notna()]
        if len(df_kilns) > 0:
            median_kilns = df_kilns['num_kilns'].median()
            st.metric("Median", f"{median_kilns:.0f} kilns")
            
            chart = alt.Chart(df_kilns).mark_bar().encode(
                x=alt.X('num_kilns:Q', bin=alt.Bin(step=1), title='Number of Kilns'),
                y=alt.Y('count()', title='Studios'),
                color=alt.value('#d62728')
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
    
    # Q11: Equipment density
    st.markdown("---")
    st.subheader("Q11: How much equipment per square foot?")
    
    df_equip['total_stations'] = (df_equip['total_wheels'].fillna(0) + 
                                   df_equip['handbuilding_stations'].fillna(0) + 
                                   df_equip['glazing_stations'].fillna(0))
    
    df_equip['equipment_density'] = (df_equip['total_stations'] / 
                                      df_equip['space_sqft'] * 1000)
    
    df_density = df_equip[df_equip['equipment_density'].notna() & 
                          (df_equip['equipment_density'] > 0) & 
                          (df_equip['equipment_density'] < 100)]
    
    if len(df_density) > 0:
        chart = alt.Chart(df_density).mark_bar().encode(
            x=alt.X('equipment_density:Q', bin=alt.Bin(step=2), 
                   title='Total Stations per 1,000 Sq Ft'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#9467bd')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        median_density = df_density['equipment_density'].median()
        st.caption(f"Median: {median_density:.1f} stations per 1,000 sq ft")
    
    # Q12: Wheel brand preferences
    st.markdown("---")
    st.subheader("Q12: Which wheel brands would studios buy again?")
    
    if 'wheel_preference' in df.columns:
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


def show_membership_scale(df, highlight_studio=None):
    """Section 3: Membership Scale (Q13-Q17)"""
    
    st.header("👥 Section 3: Membership Scale")
    
    df_members = df.copy()
    df_members['current_members'] = pd.to_numeric(df_members['current_members'], errors='coerce')
    df_members = df_members[df_members['current_members'].notna()]
    
    if len(df_members) == 0:
        st.warning("No member data available")
        return
    
    # Q13: Member count distribution
    st.subheader("Q13: What's the typical member count?")
    
    chart = alt.Chart(df_members).mark_bar().encode(
        x=alt.X('current_members:Q', bin=alt.Bin(step=10), title='Current Members'),
        y=alt.Y('count()', title='Number of Studios'),
        color=alt.value('#e377c2')
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Min", f"{df_members['current_members'].min():.0f}")
    with col2:
        st.metric("25th %ile", f"{df_members['current_members'].quantile(0.25):.0f}")
    with col3:
        st.metric("Median", f"{df_members['current_members'].median():.0f}")
    with col4:
        st.metric("75th %ile", f"{df_members['current_members'].quantile(0.75):.0f}")
    
    # Q14: Growth by studio age
    st.markdown("---")
    st.subheader("Q14: How do studios grow over time?")
    
    if 'years_operating_total_months' in df_members.columns:
        df_members['years_operating'] = pd.to_numeric(
            df_members['years_operating_total_months'], errors='coerce') / 12
        
        df_growth = df_members[df_members['years_operating'].notna()]
        
        if len(df_growth) > 0:
            fig = go.Figure()
            
            if highlight_studio and highlight_studio in df_growth['studio_name'].values:
                df_h = df_growth[df_growth['studio_name'] == highlight_studio]
                df_o = df_growth[df_growth['studio_name'] != highlight_studio]
            else:
                df_h = pd.DataFrame()
                df_o = df_growth
            
            fig.add_trace(go.Scatter(
                x=df_o['years_operating'],
                y=df_o['current_members'],
                mode='markers',
                name='Other Studios',
                marker=dict(size=8, color='#7f7f7f', opacity=0.6)
            ))
            
            if not df_h.empty:
                fig.add_trace(go.Scatter(
                    x=df_h['years_operating'],
                    y=df_h['current_members'],
                    mode='markers',
                    name='Your Studio',
                    marker=dict(size=15, color='#FF4B4B', symbol='star')
                ))
            
            fig.update_layout(
                xaxis_title='Years Operating',
                yaxis_title='Current Members',
                height=400,
                xaxis=dict(range=[0, None]),  # start X at 0, let Plotly auto-determine the upper limit
                yaxis=dict(range=[0, None])   # start Y at 0, let Plotly auto-determine the upper limit
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Q15: Time to reach current membership
    st.markdown("---")
    st.subheader("Q15: How long does it take to reach current membership?")
    
    df_time = df.copy()
    df_time['time_to_members_months'] = pd.to_numeric(df_time['time_to_members_months'], errors='coerce')
    df_time['current_members'] = pd.to_numeric(df_time['current_members'], errors='coerce')
    df_time = df_time[df_time['time_to_members_months'].notna() & df_time['current_members'].notna()]
    
    if len(df_time) > 0:
        fig = go.Figure()
        
        if highlight_studio and highlight_studio in df_time['studio_name'].values:
            df_h = df_time[df_time['studio_name'] == highlight_studio]
            df_o = df_time[df_time['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_time
        
        fig.add_trace(go.Scatter(
            x=df_o['time_to_members_months'],
            y=df_o['current_members'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#7f7f7f', opacity=0.6)
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['time_to_members_months'],
                y=df_h['current_members'],
                mode='markers',
                name='Your Studio',
                marker=dict(size=18, color='#FF4B4B', symbol='star')
            ))
        
        fig.update_layout(
            xaxis_title='Months to Reach Current Membership',
            yaxis_title='Current Members',
            height=400,
            xaxis=dict(range=[0, None]),  # start X at 0, let Plotly auto-determine the upper limit
            yaxis=dict(range=[0, None])   # start Y at 0, let Plotly auto-determine the upper limit
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Q16: Member composition
    st.markdown("---")
    st.subheader("Q16: What's typical member composition?")
    
    if 'member_pcts' in df.columns:
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
                        height=400)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Q17: Members per wheel ratio
    st.markdown("---")
    st.subheader("Q17: How many members can each wheel support?")
    
    df_wheel = df.copy()
    df_wheel['members_per_wheel'] = pd.to_numeric(df_wheel['members_per_wheel'], errors='coerce')
    df_wheel['total_wheels'] = pd.to_numeric(df_wheel['total_wheels'], errors='coerce')
    df_wheel = df_wheel[df_wheel['members_per_wheel'].notna()]
    
    if len(df_wheel) > 0:
        fig = go.Figure()
        
        if highlight_studio and highlight_studio in df_wheel['studio_name'].values:
            df_h = df_wheel[df_wheel['studio_name'] == highlight_studio]
            df_o = df_wheel[df_wheel['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_wheel
        
        fig.add_trace(go.Scatter(
            x=df_o['total_wheels'],
            y=df_o['members_per_wheel'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#2ca02c', opacity=0.6)
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['total_wheels'],
                y=df_h['members_per_wheel'],
                mode='markers',
                name='Your Studio',
                marker=dict(size=18, color='#FF4B4B', symbol='star')
            ))
        
        median_ratio = df_wheel['members_per_wheel'].median()
        fig.add_hline(y=median_ratio, line_dash="dash", line_color="gray",
                      annotation_text=f"Median: {median_ratio:.1f}")
        
        fig.update_layout(
            xaxis_title='Total Wheels',
            yaxis_title='Members per Wheel',
            height=400,
            xaxis=dict(range=[0, None]),  # start X at 0, let Plotly auto-determine the upper limit
            yaxis=dict(range=[0, None])   # start Y at 0, let Plotly auto-determine the upper limit
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Median Ratio", f"{median_ratio:.1f} members/wheel")
        with col2:
            st.metric("Range", f"{df_wheel['members_per_wheel'].min():.1f} - {df_wheel['members_per_wheel'].max():.1f}")


# ===========================================================================
# PART 2: SPACE & CAPACITY EFFICIENCY
# ===========================================================================

def show_space_efficiency(df, highlight_studio=None):
    """Section 4: Space Efficiency (Q18-Q21)"""
    
    st.header("📐 Section 4: Space Efficiency")
    
    # Q18: Space per member analysis
    st.subheader("Q18: What's the optimal space per member?")
    
    df_space = df.copy()
    df_space['sqft_per_member'] = pd.to_numeric(df_space['sqft_per_member'], errors='coerce')
    df_space['current_members'] = pd.to_numeric(df_space['current_members'], errors='coerce')
    df_space = df_space[df_space['sqft_per_member'].notna()]
    
    if len(df_space) > 0:
        if highlight_studio and highlight_studio in df_space['studio_name'].values:
            df_h = df_space[df_space['studio_name'] == highlight_studio]
            df_o = df_space[df_space['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_space
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_o['current_members'],
            y=df_o['sqft_per_member'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#1f77b4', opacity=0.6)
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['current_members'],
                y=df_h['sqft_per_member'],
                mode='markers',
                name='Your Studio',
                marker=dict(size=18, color='#FF4B4B', symbol='star')
            ))
        
        median_sqft = df_space['sqft_per_member'].median()
        fig.add_hline(y=median_sqft, line_dash="dash", line_color="gray",
                      annotation_text=f"Median: {median_sqft:.1f}")
        
        fig.update_layout(
            xaxis_title='Current Members',
            yaxis_title='Square Feet per Member',
            height=400,
            xaxis=dict(range=[0, None]),  # start X at 0, let Plotly auto-determine the upper limit
            yaxis=dict(range=[0, None])   # start Y at 0, let Plotly auto-determine the upper limit
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Median", f"{median_sqft:.1f} sq ft/member")
        with col2:
            q25 = df_space['sqft_per_member'].quantile(0.25)
            st.metric("25th Percentile", f"{q25:.1f} sq ft/member")
        with col3:
            q75 = df_space['sqft_per_member'].quantile(0.75)
            st.metric("75th Percentile", f"{q75:.1f} sq ft/member")
    
    # Q19: Space efficiency distribution
    st.markdown("---")
    st.subheader("Q19: How does space efficiency vary?")
    
    chart = alt.Chart(df_space).mark_bar().encode(
        x=alt.X('sqft_per_member:Q', bin=alt.Bin(step=20), title='Square Feet per Member'),
        y=alt.Y('count()', title='Number of Studios'),
        color=alt.value('#1f77b4')
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)
    
    # Q20: Capacity utilization
    st.markdown("---")
    st.subheader("Q20: What's typical capacity utilization?")
    
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
    
    # Q21: Waitlist patterns
    st.markdown("---")
    st.subheader("Q21: At what density do studios develop waitlists?")
    
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
            waitlist_studios = df_wait[df_wait['has_waitlist_bool'] == True]
            no_waitlist_studios = df_wait[df_wait['has_waitlist_bool'] == False]
            
            col1, col2 = st.columns(2)
            with col1:
                if len(waitlist_studios) > 0:
                    median_with_wait = waitlist_studios['members_per_wheel'].median()
                    st.metric("Studios WITH Waitlist", f"{median_with_wait:.1f} members/wheel")
            with col2:
                if len(no_waitlist_studios) > 0:
                    median_without_wait = no_waitlist_studios['members_per_wheel'].median()
                    st.metric("Studios WITHOUT Waitlist", f"{median_without_wait:.1f} members/wheel")


# ===========================================================================
# PART 3: PRICING & REVENUE
# ===========================================================================

def show_membership_pricing(df, highlight_studio=None):
    """Section 5: Membership Pricing (Q22-Q27)"""
    
    st.header("💰 Section 5: Membership Pricing")
    
    # Q22: Base membership pricing
    st.subheader("Q22: What do studios charge for base membership?")
    
    df_price = df.copy()
    df_price['tier1_price'] = pd.to_numeric(df_price['tier1_price'], errors='coerce')
    df_price = df_price[df_price['tier1_price'].notna()]
    
    if len(df_price) > 0:
        chart = alt.Chart(df_price).mark_bar().encode(
            x=alt.X('tier1_price:Q', bin=alt.Bin(step=25), title='Monthly Membership Price ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#9467bd')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Median Price", f"${df_price['tier1_price'].median():.0f}/mo")
        with col2:
            st.metric("25th Percentile", f"${df_price['tier1_price'].quantile(0.25):.0f}/mo")
        with col3:
            st.metric("75th Percentile", f"${df_price['tier1_price'].quantile(0.75):.0f}/mo")
    
    # Q23: Pricing by metro area
    st.markdown("---")
    st.subheader("Q23: How does pricing vary by metro area size?")
    
    if 'metro_population' in df.columns:
        df_location = df[df['tier1_price'].notna() & df['metro_population'].notna()].copy()
        
        if len(df_location) > 0:
            fig = px.box(df_location, x='metro_population', y='tier1_price',
                        labels={'metro_population': 'Metro Population', 'tier1_price': 'Base Membership Price ($)'},
                        height=400)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Q24: Tier structure distribution
    st.markdown("---")
    st.subheader("Q24: How many tiers do studios offer?")
    
    if 'tier_structure' in df.columns:
        tier_counts = df['tier_structure'].value_counts().reset_index()
        tier_counts.columns = ['Tier Structure', 'Count']
        
        tier_order = ["Single tier", "Two tiers", "Three tiers", "Four or more"]
        tier_counts['Tier Structure'] = pd.Categorical(
            tier_counts['Tier Structure'],
            categories=tier_order,
            ordered=True
        )
        tier_counts = tier_counts.sort_values('Tier Structure')
        
        chart = alt.Chart(tier_counts).mark_bar().encode(
            y=alt.Y('Tier Structure:N', sort=tier_order),
            x=alt.X('Count:Q'),
            tooltip=['Tier Structure', 'Count'],
            color=alt.value('#1f77b4')
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)
        
        multi_tier = tier_counts[tier_counts['Tier Structure'] != 'Single tier']['Count'].sum()
        total = tier_counts['Count'].sum()
        pct_multi = (multi_tier / total * 100) if total > 0 else 0
        
        st.caption(f"{pct_multi:.0f}% of studios offer multiple membership tiers")
    
    # Q25-Q26: Price gaps between tiers
    st.markdown("---")
    st.subheader("Q25-Q26: What are typical price differences between tiers?")
    
    df_tiers = df.copy()
    for col in ['tier1_price', 'tier2_price', 'tier3_price', 'tier4_price']:
        df_tiers[col] = pd.to_numeric(df_tiers[col], errors='coerce')
    
    df_multi = df_tiers[
        (df_tiers['tier_structure'] != 'Single tier') & 
        df_tiers['tier1_price'].notna() & 
        df_tiers['tier2_price'].notna()
    ].copy()
    
    if len(df_multi) > 0:
        df_multi['tier2_gap'] = df_multi['tier2_price'] - df_multi['tier1_price']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Q25: Tier 1 → Tier 2 Price Jump**")
            
            gap_data = df_multi[df_multi['tier2_gap'].notna()]
            if len(gap_data) > 0:
                chart = alt.Chart(gap_data).mark_bar().encode(
                    x=alt.X('tier2_gap:Q', bin=alt.Bin(step=25), 
                           title='Price Increase ($)'),
                    y=alt.Y('count()', title='Studios'),
                    color=alt.value('#2ca02c')
                ).properties(height=250)
                
                st.altair_chart(chart, use_container_width=True)
                
                median_gap = gap_data['tier2_gap'].median()
                st.metric("Median Increase", f"${median_gap:.0f}")
        
        with col2:
            df_three = df_multi[
                (df_multi['tier_structure'].isin(['Three tiers', 'Four or more'])) &
                df_multi['tier3_price'].notna()
            ].copy()
            
            if len(df_three) > 0:
                st.markdown("**Q26: Tier 2 → Tier 3 Price Jump**")
                
                df_three['tier3_gap'] = df_three['tier3_price'] - df_three['tier2_price']
                gap3_data = df_three[df_three['tier3_gap'].notna()]
                
                if len(gap3_data) > 0:
                    chart = alt.Chart(gap3_data).mark_bar().encode(
                        x=alt.X('tier3_gap:Q', bin=alt.Bin(step=25),
                               title='Price Increase ($)'),
                        y=alt.Y('count()', title='Studios'),
                        color=alt.value('#ff7f0e')
                    ).properties(height=250)
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    median_gap3 = gap3_data['tier3_gap'].median()
                    st.metric("Median Increase", f"${median_gap3:.0f}")
    
    # Q27: Pricing vs competitors
    st.markdown("---")
    st.subheader("Q27: How do studios price vs. competitors?")
    
    if 'pricing_vs_competitors' in df.columns:
        pricing_comp = df['pricing_vs_competitors'].value_counts().reset_index()
        pricing_comp.columns = ['Pricing Position', 'Count']
        
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
        
        chart = alt.Chart(pricing_comp).mark_bar().encode(
            y=alt.Y('Pricing Position:N', sort=price_order),
            x=alt.X('Count:Q'),
            tooltip=['Pricing Position', 'Count'],
            color=alt.value('#9467bd')
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)


def show_materials_services_pricing(df, highlight_studio=None):
    """Section 6: Materials & Services Pricing (Q28-Q32)"""
    
    st.header("🏺 Section 6: Materials & Services Pricing")
    
    # Q28: Clay pricing
    st.subheader("Q28: What do studios charge for clay?")
    
    df_clay = df.copy()
    df_clay['clay_price'] = pd.to_numeric(df_clay['clay_price'], errors='coerce')
    df_clay = df_clay[df_clay['clay_price'].notna() & (df_clay['clay_price'] > 0)]
    
    if len(df_clay) > 0:
        chart = alt.Chart(df_clay).mark_bar().encode(
            x=alt.X('clay_price:Q', bin=alt.Bin(step=5), 
                   title='Clay Price per 25lb Bag ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#a52a2a')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("25th %ile", f"${df_clay['clay_price'].quantile(0.25):.0f}")
        with col2:
            st.metric("Median", f"${df_clay['clay_price'].median():.0f}")
        with col3:
            st.metric("75th %ile", f"${df_clay['clay_price'].quantile(0.75):.0f}")
    
    # Q29: Clay types offered
    st.markdown("---")
    st.subheader("Q29: How many clay types do studios offer?")
    
    if 'clay_types' in df.columns:
        df_types = df.copy()
        df_types['clay_types'] = pd.to_numeric(df_types['clay_types'], errors='coerce')
        df_types = df_types[df_types['clay_types'].notna()]
        
        if len(df_types) > 0:
            chart = alt.Chart(df_types).mark_bar().encode(
                x=alt.X('clay_types:Q', bin=alt.Bin(step=1), title='Number of Clay Types'),
                y=alt.Y('count()', title='Number of Studios'),
                color=alt.value('#8b4513')
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            median_types = df_types['clay_types'].median()
            st.metric("Median Options", f"{median_types:.0f} types")
    
    # Q30: Firing fee models
    st.markdown("---")
    st.subheader("Q30: What firing fee models do studios use?")
    
    if 'firing_model' in df.columns:
        firing_counts = df['firing_model'].value_counts().reset_index()
        firing_counts.columns = ['Firing Model', 'Count']
        
        chart = alt.Chart(firing_counts).mark_bar().encode(
            x=alt.X('Count:Q'),
            y=alt.Y('Firing Model:N', sort='-x'),
            tooltip=['Firing Model', 'Count'],
            color=alt.value('#ff7f0e')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Q31: Class pricing
    st.markdown("---")
    st.subheader("Q31: What do studios charge for classes?")
    
    df_classes = df.copy()
    df_classes['class_price'] = pd.to_numeric(df_classes['class_price'], errors='coerce')
    df_classes = df_classes[df_classes['class_price'].notna() & (df_classes['class_price'] > 0)]
    
    if len(df_classes) > 0:
        chart = alt.Chart(df_classes).mark_bar().encode(
            x=alt.X('class_price:Q', bin=alt.Bin(step=50), title='Class Price ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#8c564b')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        median_price = df_classes['class_price'].median()
        st.metric("Median Class Price", f"${median_price:.0f}")
    
    # Q32: Event pricing
    st.markdown("---")
    st.subheader("Q32: What do studios charge for events?")
    
    df_events = df.copy()
    df_events['event_price'] = pd.to_numeric(df_events['event_price'], errors='coerce')
    df_events = df_events[df_events['event_price'].notna() & (df_events['event_price'] > 0)]
    
    if len(df_events) > 0:
        chart = alt.Chart(df_events).mark_bar().encode(
            x=alt.X('event_price:Q', bin=alt.Bin(step=10), 
                   title='Event Price per Person ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#e377c2')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Median", f"${df_events['event_price'].median():.0f}/person")
        with col2:
            st.metric("Range", f"${df_events['event_price'].min():.0f} - ${df_events['event_price'].max():.0f}")


def show_revenue_mix(df, highlight_studio=None):
    """Section 7: Revenue Mix (Q33-Q35)"""
    
    st.header("📊 Section 7: Revenue Mix")
    
    # Q33: Average revenue composition
    st.subheader("Q33: Where does revenue come from?")
    
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
            
            fig = px.pie(
                avg_rev, values='Average %', names='Revenue Source',
                title='Average Revenue Mix', height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Build revenue_by_profit from df before plotting
        if 'revenue_pcts' in df.columns and 'profitability_status' in df.columns:
            revenue_by_profit = []
            for idx, row in df.iterrows():
                rev_dict = _parse_jsonish(row['revenue_pcts'])
                status = row['profitability_status']
                if isinstance(rev_dict, dict) and isinstance(status, str):
                    for source, pct in rev_dict.items():
                        if isinstance(pct, (int, float)) and pct > 0:
                            revenue_by_profit.append(
                                {'source': source, 'percentage': pct, 'status': status}
                            )

            if revenue_by_profit:
                rev_df = pd.DataFrame(revenue_by_profit)
                avg_rev = rev_df.groupby(['status', 'source'])['percentage'].mean().reset_index()

                name_map = {
                    'membership': 'Membership',
                    'clay': 'Clay Sales',
                    'firing': 'Firing Fees',
                    'classes': 'Classes',
                    'events': 'Events',
                    'other': 'Other'
                }
                avg_rev['source'] = avg_rev['source'].map(lambda x: name_map.get(x, x.title()))

                fig = px.bar(
                    avg_rev,
                    x='source',
                    y='percentage',
                    color='status',
                    barmode='group',
                    title='Revenue Mix by Profitability Status',
                    labels={'percentage': 'Average %', 'source': 'Revenue Source'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Q35: Multi-tier pricing impact
    st.markdown("---")
    st.subheader("Q35: Does having multiple tiers increase revenue?")
    
    if 'tier_structure' in df.columns and 'monthly_revenue_range' in df.columns:
        tier_revenue = df[df['tier_structure'].notna() & df['monthly_revenue_range'].notna()].copy()
        
        if len(tier_revenue) > 0:
            tier_rev_counts = tier_revenue.groupby(['tier_structure', 'monthly_revenue_range']).size().reset_index(name='count')
            
            revenue_order = [
                "Under $5,000",
                "$5,000-$10,000",
                "$10,000-$20,000",
                "$20,000-$35,000",
                "$35,000-$50,000",
                "$50,000-$75,000",
                "Over $75,000"
            ]
            
            chart = alt.Chart(tier_rev_counts).mark_bar().encode(
                x=alt.X('tier_structure:N', title='Tier Structure'),
                y=alt.Y('count:Q', title='Number of Studios'),
                color=alt.Color('monthly_revenue_range:N', 
                              title='Revenue Range',
                              sort=revenue_order),
                tooltip=['tier_structure', 'monthly_revenue_range', 'count']
            ).properties(height=400)
            
            st.altair_chart(chart, use_container_width=True)


# ===========================================================================
# PART 4: COSTS & PROFITABILITY
# ===========================================================================

def show_operating_costs(df, highlight_studio=None):
    """Section 8: Operating Costs (Q36-Q40)"""
    
    st.header("💵 Section 8: Operating Costs")
    
    df_costs = df.copy()
    for col in ['rent', 'electricity', 'water', 'insurance', 'buildout_cost_total', 'space_sqft']:
        df_costs[col] = pd.to_numeric(df_costs[col], errors='coerce')
    
    # Q36: Rent distribution
    st.subheader("Q36: What does rent cost?")
    
    df_rent = df_costs[df_costs['rent'].notna()]
    
    if len(df_rent) > 0:
        chart = alt.Chart(df_rent).mark_bar().encode(
            x=alt.X('rent:Q', bin=alt.Bin(step=500), title='Monthly Rent ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#d62728')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("25th %ile", f"${df_rent['rent'].quantile(0.25):,.0f}/mo")
        with col2:
            st.metric("Median", f"${df_rent['rent'].median():,.0f}/mo")
        with col3:
            st.metric("75th %ile", f"${df_rent['rent'].quantile(0.75):,.0f}/mo")
    
    # Q37: Rent per member
    st.markdown("---")
    st.subheader("Q37: How much rent per member?")
    
    df_costs['rent_per_member'] = pd.to_numeric(df_costs['rent_per_member'], errors='coerce')
    df_rent_member = df_costs[df_costs['rent_per_member'].notna()]
    
    if len(df_rent_member) > 0:
        chart = alt.Chart(df_rent_member).mark_bar().encode(
            x=alt.X('rent_per_member:Q', bin=alt.Bin(step=50), title='Monthly Rent per Member ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#bcbd22')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        median_rent = df_rent_member['rent_per_member'].median()
        st.metric("Median Rent per Member", f"${median_rent:.0f}/member/month")
    
    # Q38: Utilities
    st.markdown("---")
    st.subheader("Q38: What do utilities cost?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Electricity**")
        df_elec = df_costs[df_costs['electricity'].notna() & (df_costs['electricity'] > 0)]
        if len(df_elec) > 0:
            median_elec = df_elec['electricity'].median()
            st.metric("Median", f"${median_elec:.0f}/mo")
            
            chart = alt.Chart(df_elec).mark_bar().encode(
                x=alt.X('electricity:Q', bin=alt.Bin(step=100), 
                       title='Monthly Electricity ($)'),
                y=alt.Y('count()', title='Studios'),
                color=alt.value('#ff7f0e')
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown("**Water/Sewer**")
        df_water = df_costs[df_costs['water'].notna() & (df_costs['water'] > 0)]
        if len(df_water) > 0:
            median_water = df_water['water'].median()
            st.metric("Median", f"${median_water:.0f}/mo")
            
            chart = alt.Chart(df_water).mark_bar().encode(
                x=alt.X('water:Q', bin=alt.Bin(step=50), 
                       title='Monthly Water ($)'),
                y=alt.Y('count()', title='Studios'),
                color=alt.value('#2ca02c')
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
    
    # Q39: Insurance
    st.markdown("---")
    st.subheader("Q39: What does insurance cost?")
    
    df_insurance = df_costs[df_costs['insurance'].notna() & (df_costs['insurance'] > 0)]
    
    if len(df_insurance) > 0:
        chart = alt.Chart(df_insurance).mark_bar().encode(
            x=alt.X('insurance:Q', bin=alt.Bin(step=50), title='Monthly Insurance ($)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#9467bd')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("25th %ile", f"${df_insurance['insurance'].quantile(0.25):.0f}/mo")
        with col2:
            st.metric("Median", f"${df_insurance['insurance'].median():.0f}/mo")
        with col3:
            st.metric("75th %ile", f"${df_insurance['insurance'].quantile(0.75):.0f}/mo")
    
    # Q40: Build-out costs
    st.markdown("---")
    st.subheader("Q40: How much do leasehold improvements cost?")
    
    df_buildout = df_costs[df_costs['buildout_cost_total'].notna() & 
                           (df_costs['buildout_cost_total'] > 0)]
    
    if len(df_buildout) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            chart = alt.Chart(df_buildout).mark_bar().encode(
                x=alt.X('buildout_cost_total:Q', bin=alt.Bin(step=25000),
                       title='Build-Out Cost ($)'),
                y=alt.Y('count()', title='Number of Studios'),
                color=alt.value('#e377c2')
            ).properties(height=300, title='Total Build-Out Costs')
            
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            median_total = df_buildout['buildout_cost_total'].median()
            st.metric("Median Total Cost", f"${median_total:,.0f}")
        with col2:
            if 'cost_per_sqft' in df_buildout.columns:
                median_sqft = df_buildout_sqft['cost_per_sqft'].median()
                st.metric("Median per Sq Ft", f"${median_sqft:.2f}")
        with col3:
            q75 = df_buildout['buildout_cost_total'].quantile(0.75)
            st.metric("75th Percentile", f"${q75:,.0f}")


def show_financial_performance(df, highlight_studio=None):
    """Section 9: Financial Performance (Q41-Q44)"""
    
    st.header("💰 Section 9: Financial Performance")
    
    # Q41: Profitability status
    st.subheader("Q41: What's the profitability status distribution?")
    
    if 'profitability_status' in df.columns:
        profit_counts = df['profitability_status'].value_counts().reset_index()
        profit_counts.columns = ['Status', 'Count']
        
        chart = alt.Chart(profit_counts).mark_bar().encode(
            x=alt.X('Count:Q'),
            y=alt.Y('Status:N', sort='-x'),
            tooltip=['Status', 'Count'],
            color=alt.value('#2ca02c')
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Q42: Time to profitability
    st.markdown("---")
    st.subheader("Q42: How long until studios become profitable?")
    
    if 'time_to_profitability' in df.columns:
        time_counts = df['time_to_profitability'].value_counts().reset_index()
        time_counts.columns = ['Time to Profit', 'Count']
        
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
        
        chart = alt.Chart(time_counts).mark_bar().encode(
            y=alt.Y('Time to Profit:N', sort=time_order),
            x=alt.X('Count:Q'),
            tooltip=['Time to Profit', 'Count'],
            color=alt.value('#2ca02c')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Q43: Rent burden
    st.markdown("---")
    st.subheader("Q43: What's a sustainable rent burden?")
    
    df_rent_burden = df.copy()
    df_rent_burden['rent'] = pd.to_numeric(df_rent_burden['rent'], errors='coerce')
    df_rent_burden['current_members'] = pd.to_numeric(df_rent_burden['current_members'], errors='coerce')
    df_rent_burden['tier1_price'] = pd.to_numeric(df_rent_burden['tier1_price'], errors='coerce')
    
    df_rent_burden['est_membership_revenue'] = (df_rent_burden['current_members'] * 
                                                df_rent_burden['tier1_price'])
    df_rent_burden['rent_pct'] = (df_rent_burden['rent'] / 
                                  df_rent_burden['est_membership_revenue'] * 100)
    
    df_rent_burden = df_rent_burden[df_rent_burden['rent_pct'].notna() & 
                                   (df_rent_burden['rent_pct'] > 0) &
                                   (df_rent_burden['rent_pct'] < 200)]
    
    if len(df_rent_burden) > 0 and 'profitability_status' in df_rent_burden.columns:
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
    
    # Q44: Startup capital
    st.markdown("---")
    st.subheader("Q44: How much startup capital is required?")
    
    if 'startup_capital_range' in df.columns:
        capital_counts = df['startup_capital_range'].value_counts().reset_index()
        capital_counts.columns = ['Capital Range', 'Count']
        
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


# ===========================================================================
# PART 5: OPERATIONS
# ===========================================================================

def show_access_staffing(df, highlight_studio=None):
    """Section 10: Access & Staffing (Q45-Q47)"""
    
    st.header("⚙️ Section 10: Access & Staffing")
    
    # Q45: Access models
    st.subheader("Q45: What access models do studios use?")
    
    if 'access_model' in df.columns:
        access_counts = df['access_model'].value_counts().reset_index()
        access_counts.columns = ['Access Model', 'Count']
        
        chart = alt.Chart(access_counts).mark_bar().encode(
            y=alt.Y('Access Model:N', sort='-x'),
            x=alt.X('Count:Q'),
            tooltip=['Access Model', 'Count'],
            color=alt.value('#1f77b4')
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Q46: Staffing patterns
    st.markdown("---")
    st.subheader("Q46: Do studios have paid staff?")
    
    if 'has_staff' in df.columns:
        def _to_bool(s):
            if pd.api.types.is_bool_dtype(s):
                return s.astype(int)
            s = s.astype(str).str.strip().str.lower()
            mapping = {
                "yes": 1, "y": 1, "true": 1, "t": 1, "1": 1,
                "no": 0,  "n": 0, "false": 0, "f": 0, "0": 0
            }
            return s.map(mapping)
        
        staff01 = _to_bool(df['has_staff'])
        denom = staff01.notna().sum() if staff01.notna().any() else len(df)
        if denom > 0:
            pct_with_staff = (staff01.fillna(0).sum() / denom) * 100
            st.metric("Studios with Paid Staff", f"{pct_with_staff:.0f}%")
    
    # Q47: Staff roles (placeholder for more detailed analysis if needed)
    st.markdown("---")
    st.subheader("Q47: What are typical staffing patterns by studio size?")
    st.caption("Analysis of staff hours and roles by member count would go here")


def show_kiln_operations(df, highlight_studio=None):
    """Section 11: Kiln Operations (Q48-Q50)"""
    
    st.header("🔥 Section 11: Kiln Operations")
    
    # Q48: Kiln utilization
    st.subheader("Q48: What's typical kiln utilization?")
    
    if 'kiln_utilization' in df.columns:
        df_kiln = df.copy()
        df_kiln['kiln_utilization'] = pd.to_numeric(df_kiln['kiln_utilization'], errors='coerce')
        df_kiln = df_kiln[df_kiln['kiln_utilization'].notna()]
        
        if len(df_kiln) > 0:
            chart = alt.Chart(df_kiln).mark_bar().encode(
                x=alt.X('kiln_utilization:Q', bin=alt.Bin(step=10),
                       title='Kiln Utilization (%)'),
                y=alt.Y('count()', title='Number of Studios'),
                color=alt.value('#ff7f0e')
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                median_util = df_kiln['kiln_utilization'].median()
                st.metric("Median Utilization", f"{median_util:.0f}%")
            with col2:
                high_util = (df_kiln['kiln_utilization'] >= 80).sum() / len(df_kiln) * 100
                st.metric("High Utilization (≥80%)", f"{high_util:.0f}%")
    
    # Q49: Kilns per member
    st.markdown("---")
    st.subheader("Q49: What's the optimal kiln-to-member ratio?")
    
    df_kiln_ratio = df.copy()
    df_kiln_ratio['num_kilns'] = pd.to_numeric(df_kiln_ratio['num_kilns'], errors='coerce')
    df_kiln_ratio['current_members'] = pd.to_numeric(df_kiln_ratio['current_members'], errors='coerce')
    df_kiln_ratio = df_kiln_ratio[df_kiln_ratio['num_kilns'].notna() & 
                                   df_kiln_ratio['current_members'].notna()]
    
    if len(df_kiln_ratio) > 0:
        df_kiln_ratio['members_per_kiln'] = (df_kiln_ratio['current_members'] / 
                                             df_kiln_ratio['num_kilns'])
        median_per_kiln = df_kiln_ratio['members_per_kiln'].median()
        
        st.metric("Median Members per Kiln", f"{median_per_kiln:.0f} members/kiln")
    
    # Q50: Firing frequency
    st.markdown("---")
    st.subheader("Q50: How often do studios fire kilns?")
    
    if 'kilns' in df.columns:
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
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Median Firings/Month", f"{firings_series.median():.0f}")
            with col2:
                st.metric("Average Firings/Month", f"{firings_series.mean():.1f}")


def show_classes_events(df, highlight_studio=None):
    """Section 12: Classes & Events (Q51-Q53)"""
    
    st.header("🎓 Section 12: Classes & Events")
    
    # Q51: Class offerings
    st.subheader("Q51: What percentage of studios offer classes?")
    
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
            st.metric("Studios Offering Classes", f"{pct_offering:.0f}%")
    
    # Q52: Class pricing and format
    st.markdown("---")
    st.subheader("Q52: What do class formats and pricing look like?")
    
    if 'class_format' in df.columns:
        format_counts = df['class_format'].value_counts().reset_index()
        format_counts.columns = ['Format', 'Count']
        
        chart = alt.Chart(format_counts).mark_bar().encode(
            x=alt.X('Count:Q'),
            y=alt.Y('Format:N', sort='-x'),
            tooltip=['Format', 'Count'],
            color=alt.value('#8c564b')
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Q53: Event offerings
    st.markdown("---")
    st.subheader("Q53: What percentage of studios offer events?")
    
    if 'offers_events' in df.columns:
        events01 = _to_bool(df['offers_events'])
        valid = events01.notna().sum()
        
        if valid > 0:
            pct_offering_events = (events01.sum() / valid) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Studios Offering Events", f"{pct_offering_events:.0f}%")
            
            with col2:
                df_events = df[events01 == 1].copy()
                df_events['events_per_month'] = pd.to_numeric(df_events['events_per_month'], errors='coerce')
                df_events_clean = df_events[df_events['events_per_month'].notna()]
                if len(df_events_clean) > 0:
                    avg_events = df_events_clean['events_per_month'].mean()
                    st.metric("Avg Events/Month", f"{avg_events:.1f}")


def show_amenities(df, highlight_studio=None):
    """Section 13: Amenities (Q54-Q55)"""
    
    st.header("🎁 Section 13: Included Amenities")
    
    # Q54: Most common amenities
    st.subheader("Q54: What amenities do studios include?")
    
    if 'included_amenities' in df.columns:
        all_amenities = []
        for amenities in df['included_amenities'].dropna():
            parsed = _parse_jsonish(amenities)
            if isinstance(parsed, list):
                all_amenities.extend(parsed)
            elif isinstance(parsed, str) and parsed:
                all_amenities.append(parsed)
        
        if all_amenities:
            amenity_counts = pd.Series(all_amenities).value_counts().reset_index()
            amenity_counts.columns = ['Amenity', 'Count']
            
            total_studios = len(df[df['included_amenities'].notna()])
            amenity_counts['Percentage'] = (amenity_counts['Count'] / total_studios * 100)
            
            chart = alt.Chart(amenity_counts.head(15)).mark_bar().encode(
                y=alt.Y('Amenity:N', sort='-x'),
                x=alt.X('Percentage:Q', title='% of Studios Offering'),
                tooltip=['Amenity', 'Count', alt.Tooltip('Percentage:Q', format='.1f')],
                color=alt.value('#17becf')
            ).properties(height=400)
            
            st.altair_chart(chart, use_container_width=True)
    
    # Q55: Amenities vs pricing correlation
    st.markdown("---")
    st.subheader("Q55: Do more amenities correlate with higher pricing?")
    
    if 'included_amenities' in df.columns and 'tier1_price' in df.columns:
        df_amenities = df.copy()
        
        df_amenities['amenity_count'] = df_amenities['included_amenities'].apply(
            lambda x: len(_parse_jsonish(x)) if _parse_jsonish(x) and isinstance(_parse_jsonish(x), list) else 0
        )
        
        df_amenities['tier1_price'] = pd.to_numeric(df_amenities['tier1_price'], errors='coerce')
        
        df_amenities = df_amenities[df_amenities['amenity_count'].notna() & 
                                     df_amenities['tier1_price'].notna()]
        
        if len(df_amenities) > 0:
            fig = go.Figure()
            
            if highlight_studio and highlight_studio in df_amenities['studio_name'].values:
                df_h = df_amenities[df_amenities['studio_name'] == highlight_studio]
                df_o = df_amenities[df_amenities['studio_name'] != highlight_studio]
            else:
                df_h = pd.DataFrame()
                df_o = df_amenities
            
            fig.add_trace(go.Scatter(
                x=df_o['amenity_count'],
                y=df_o['tier1_price'],
                mode='markers',
                name='Other Studios',
                marker=dict(size=8, color='#7f7f7f', opacity=0.6)
            ))
            
            if not df_h.empty:
                fig.add_trace(go.Scatter(
                    x=df_h['amenity_count'],
                    y=df_h['tier1_price'],
                    mode='markers',
                    name='Your Studio',
                    marker=dict(size=15, color='#FF4B4B', symbol='star')
                ))
            
            # Add trend line
            if len(df_amenities) > 1:
                z = np.polyfit(df_amenities['amenity_count'], df_amenities['tier1_price'], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(df_amenities['amenity_count'].min(), 
                                     df_amenities['amenity_count'].max(), 100)
                
                fig.add_trace(go.Scatter(
                    x=x_trend,
                    y=p(x_trend),
                    mode='lines',
                    name='Trend',
                    line=dict(color='red', dash='dash')
                ))
            
            fig.update_layout(
                xaxis_title='Number of Included Amenities',
                yaxis_title='Base Membership Price ($)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            correlation = df_amenities['amenity_count'].corr(df_amenities['tier1_price'])
            st.caption(f"Correlation coefficient: {correlation:.3f}")


# ===========================================================================
# PART 6: MARKET & GROWTH
# ===========================================================================

def show_market_context(df, highlight_studio=None):
    """Section 14: Market Context (Q56-Q58)"""
    
    st.header("🗺️ Section 14: Market Context")
    
    # Q56: Area types (already shown in Section 1, Q6 - skip to avoid redundancy)
    # Q57: Competition density
    st.subheader("Q57: How much competition exists?")
    
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
    
    # Q58: Market population
    st.markdown("---")
    st.subheader("Q58: What's the market population distribution?")
    
    if 'market_population' in df.columns:
        population_counts = df['market_population'].value_counts().reset_index()
        population_counts.columns = ['Market Population', 'Count']
        
        pop_order = [
            "Under 10,000",
            "10,000-50,000",
            "50,000-100,000",
            "100,000-250,000",
            "250,000-500,000",
            "Over 500,000"
        ]
        
        population_counts['Market Population'] = pd.Categorical(
            population_counts['Market Population'],
            categories=pop_order,
            ordered=True
        )
        population_counts = population_counts.sort_values('Market Population')
        
        chart = alt.Chart(population_counts).mark_bar().encode(
            y=alt.Y('Market Population:N', sort=pop_order),
            x=alt.X('Count:Q'),
            tooltip=['Market Population', 'Count'],
            color=alt.value('#2ca02c')
        ).properties(height=300, title='Population within 10 Miles')
        
        st.altair_chart(chart, use_container_width=True)


def show_member_dynamics(df, highlight_studio=None):
    """Section 15: Member Dynamics (Q59-Q61)"""
    
    st.header("🔄 Section 15: Member Dynamics")
    
    # Q59: Churn rate distribution
    st.subheader("Q59: What's typical monthly churn?")
    
    df_churn = df.copy()
    df_churn['monthly_churn'] = pd.to_numeric(df_churn['monthly_churn'], errors='coerce')
    df_churn = df_churn[df_churn['monthly_churn'].notna()]
    
    if len(df_churn) > 0:
        chart = alt.Chart(df_churn).mark_bar().encode(
            x=alt.X('monthly_churn:Q', bin=alt.Bin(step=2), title='Monthly Churn Rate (%)'),
            y=alt.Y('count()', title='Number of Studios'),
            color=alt.value('#8c564b')
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        median_churn = df_churn['monthly_churn'].median()
        st.metric("Median Monthly Churn", f"{median_churn:.1f}%")
    
    # Q60: Churn reasons
    st.markdown("---")
    st.subheader("Q60: Why do members leave?")
    
    if 'top_churn_reasons' in df.columns:
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
            ).properties(height=350)
            
            st.altair_chart(chart, use_container_width=True)
    
    # Q61: Churn by studio size
    st.markdown("---")
    st.subheader("Q61: Does churn rate vary by studio size?")
    
    df_churn_size = df.copy()
    df_churn_size['monthly_churn'] = pd.to_numeric(df_churn_size['monthly_churn'], errors='coerce')
    df_churn_size['current_members'] = pd.to_numeric(df_churn_size['current_members'], errors='coerce')
    df_churn_size = df_churn_size[df_churn_size['monthly_churn'].notna() & 
                                   df_churn_size['current_members'].notna()]
    
    if len(df_churn_size) > 0:
        fig = go.Figure()
        
        if highlight_studio and highlight_studio in df_churn_size['studio_name'].values:
            df_h = df_churn_size[df_churn_size['studio_name'] == highlight_studio]
            df_o = df_churn_size[df_churn_size['studio_name'] != highlight_studio]
        else:
            df_h = pd.DataFrame()
            df_o = df_churn_size
        
        fig.add_trace(go.Scatter(
            x=df_o['current_members'],
            y=df_o['monthly_churn'],
            mode='markers',
            name='Other Studios',
            marker=dict(size=10, color='#8c564b', opacity=0.6)
        ))
        
        if not df_h.empty:
            fig.add_trace(go.Scatter(
                x=df_h['current_members'],
                y=df_h['monthly_churn'],
                mode='markers',
                name='Your Studio',
                marker=dict(size=18, color='#FF4B4B', symbol='star')
            ))
        
        median_churn = df_churn_size['monthly_churn'].median()
        fig.add_hline(y=median_churn, line_dash="dash", line_color="gray",
                     annotation_text=f"Median: {median_churn:.1f}%")
        
        fig.update_layout(
            xaxis_title='Current Members',
            yaxis_title='Monthly Churn Rate (%)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# HELPER FUNCTION - _parse_jsonish
# ===========================================================================

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