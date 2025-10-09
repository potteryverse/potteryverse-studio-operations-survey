
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Pottery Studio Survey with Conditional Display
Uses session state for progressive disclosure
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import uuid
import time

# Page config
st.set_page_config(
    page_title="Pottery Studio Economics Survey",
    page_icon="🏺",
    layout="wide"
)

# Import services
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Initialize session state
def init_session_state():
    defaults = {
        'page': 'intro',
        'survey_section': 1,
        'survey_data': {},
        'is_update': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Helper functions
def validate_percentage_sum(percentages, target=100, tolerance=0.5):
    total = sum(percentages.values())
    return abs(total - target) < tolerance

def get_all_columns():
    """
    Define the complete schema for all survey fields.
    This ensures consistency across all responses.
    """
    return [
        # Metadata
        "response_id",
        "schema_version",
        "submitted_at",

        # >>> INSERTED to match Sheet header <<<
        "country",
        "currency",
        "uses_metric",

        # Section 1: Studio Profile
        "studio_name",
        "location_state",
        "location_other",
        "area_type",
        "metro_population",
        "space_sqft",
        # >>> INSERTED to match Sheet header <<<
        "space_sqm",

        "years_operating_years",
        "years_operating_months",
        "years_operating_total_months",
        "studio_type",
        "studio_type_other",
        "current_members",
        "time_to_members_months",
        "peak_occupancy",
        "avg_occupancy",

        # …(rest unchanged; your list already matches the header order)…
        "total_wheels",
        "wheel_inventory",
        "wheel_preference",
        "classes_members_overlap",
        "reserved_wheels_for_members_pct",
        "reserved_wheels_for_members_fraction",
        "reserved_wheels_for_members_count",
        "handbuilding_stations",
        "glazing_stations",
        "designated_studios",
        "designated_occupancy_rate",
        "designated_details",
        "designated_membership_cost",
        "designated_shelves",
        "handbuilding_station_sqft",
        "glazing_station_sqft",
        "num_kilns",
        "kilns",
        "additional_equipment",
        # …keep the remainder exactly as you had it…
        "access_model",
        "hours_per_day",
        "days_per_week",
        "total_accessible_hours",
        "staffed_hours",
        "unstaffed_hours",
        "has_staff",
        "studio_manager_hours",
        "front_desk_hours",
        "instructors_hours",
        "tech_support_hours",
        "cleaning_hours",
        "other_staff_hours",
        "other_staff_description",
        "staff_roles",
        "compensation_type",
        "avg_hourly_rate",
        "total_staff_cost",
        "membership_software",
        "scheduling_system",
        "payment_processor",
        "security_system",
        "member_communication",
        "classes_per_month",
        "class_sessions_per_month",
        "instructor_flat_rate",
        "instructor_revenue_percentage",
        "instructor_hourly_rate",
        "equipment_maintenance",
        "building_maintenance",
        "tier_structure",
        "tier1_price",
        "tier2_price",
        "tier3_price",
        "tier4_price",
        "tier1_name",
        "tier1_description",
        "tier2_name",
        "tier2_description",
        "tier3_name",
        "tier3_description",
        "tier4_name",
        "tier4_description",
        "all_tiers_text",
        "firing_model",
        "firing_tier1_lbs",
        "firing_tier1_rate",
        "firing_tier2_lbs",
        "firing_tier2_rate",
        "firing_tier3_rate",
        "bisque_rate_per_lb",
        "firing_rate",
        "firing_rate_cuft",
        "bisque_rate_per_shelf",
        "bisque_rate_per_cuft",
        "firing_small",
        "firing_medium",
        "firing_large",
        "firing_explain",
        "clay_price",
        "clay_types",
        "offers_classes",
        "class_price",
        "class_weeks",
        "class_enrollment",
        "class_format",
        "offers_workshops",
        "workshop_price",
        "workshop_attendance",
        "offers_events",
        "event_types",
        "event_price",
        "event_attendance",
        "events_per_month",
        "event_pricing_model",
        "flat_event_rate",
        "event_piece_price",
        "event_studio_fee",
        "member_pcts",
        "hobbyist_pct",
        "regular_pct",
        "production_pct",
        "seasonal_pct",
        "demographics_usage_accuracy_ok",
        "monthly_gain",
        "monthly_churn",
        "new_members_per_month",
        "top_churn_reasons",
        "retention_churn_feedback",
        "shelf_space_per_member",
        "storage_bins_per_member",
        "avg_pieces_fired_per_member",
        "clay_consumption_per_member",
        "included_amenities",
        "community_events",
        "monthly_marketing_budget",
        "cost_per_acquisition",
        "effective_marketing_channels",
        "new_member_sources",
        "has_trial_offer",
        "trial_offer_type",
        "trial_conversion_rate",
        "rent",
        "utilities_included",
        "electricity",
        "water",
        "insurance",
        "glaze_budget",
        "had_buildout",
        "buildout_work_types",
        "buildout_cost_total",
        "buildout_cost_breakdown",
        "buildout_timeline",
        "unexpected_costs",
        "zoning_types",
        "zoning_other",
        "rent_per_sqft",
        "lease_term_years",
        "revenue_pcts",
        "rev_membership",
        "rev_clay",
        "rev_firing",
        "rev_classes",
        "rev_events",
        "rev_other",
        "monthly_revenue_range",
        "profitability_status",
        "monthly_profit_range",
        "cash_runway_months",
        "startup_capital_range",
        "time_to_profitability",
        "funding_sources",
        "funding_sources_other",
        "owner_hours_per_week",
        "capacity_utilization",
        "has_waitlist",
        "waitlist_length",
        "waitlist_avg_wait_weeks",
        "waitlist_conversion",
        "peak_crowding",
        "competing_studios",
        "pricing_vs_competitors",
        "market_population",
        "kiln_utilization",
        "competitive_advantages",
        "plans_expand_space",
        "plans_add_equipment",
        "plans_raise_prices",
        "target_member_count",
        "studio_status",
        "struggle_areas",
        "struggle_other",
        "closure_year",
        "months_operated",
        "closure_reasons",
        "lessons_learned",
        "macro_impact",
        "impact_details",
        "liability_coverage",
        "class_fill_rate",
        "instructor_compensation_model",
        "survey_feedback",
        "suggested_questions",
        "topics_interest",
        "followup",
        "followup_email",
        "_sheet_row",
    ]

# Helpers (place near top of file)
def _sqft_to_sqm(x): 
    return None if x is None else x / 10.7639

def _sqm_to_sqft(x): 
    return None if x is None else x * 10.7639


def check_for_existing_response(response_id):
    """
    Check if a response_id already exists in the sheet.
    Returns: (exists: bool, row_number: int or None)
    """
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheet_id = st.secrets["sheet_id"]
        
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1"
        ).execute()
        
        values = result.get('values', [])
        if len(values) < 2:
            return False, None
            
        headers = values[0]
        rows = values[1:]
        
        response_id_col = headers.index('response_id') if 'response_id' in headers else None
        if response_id_col is None:
            return False, None
            
        for idx, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
            if len(row) > response_id_col and row[response_id_col] == response_id:
                return True, idx
        
        return False, None
        
    except Exception as e:
        st.warning(f"Could not check for duplicates: {e}")
        return False, None

def save_response(data):
    """
    Save or update response with duplicate prevention.
    
    Strategy:
    1. Check if response_id already exists
    2. If exists, update that row
    3. If not, append new row
    """
    
    # Ensure response_id exists
    if 'response_id' not in data:
        data['response_id'] = str(uuid.uuid4())
    
    # Add metadata
    data = {
        "schema_version": "v1.1",
        "submitted_at": datetime.now().isoformat(),
        **data,
    }

    flat = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in data.items()}
    columns = get_all_columns()

    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheet_id = st.secrets["sheet_id"]

        # Check if this response_id already exists
        exists, row_number = check_for_existing_response(data['response_id'])
        
        if exists and row_number:
            # UPDATE existing row
            st.info(f"Updating existing response (found at row {row_number})")
            body_row = {'values': [[flat.get(c, "") for c in columns]]}
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"Sheet1!A{row_number}",
                valueInputOption='RAW',
                body=body_row
            ).execute()
            return True
        
        # NEW submission - check if sheet is empty and add header if needed
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A1:A1"
        ).execute()
        
        values = result.get('values', [])
        is_empty = len(values) == 0 or len(values[0]) == 0
        
        if is_empty:
            header_body = {'values': [columns]}
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range="Sheet1!A1",
                valueInputOption='RAW',
                body=header_body
            ).execute()
        
        # APPEND new row
        body_row = {'values': [[flat.get(c, "") for c in columns]]}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Sheet1!A1",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body_row
        ).execute()
        return True
        
    except Exception as e:
        # Fallback to CSV with duplicate checking
        import csv, os
        path = "survey_responses.csv"
        
        # Check local CSV for duplicates
        existing_ids = set()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_ids = {row.get('response_id') for row in reader if row.get('response_id')}
        
        if data['response_id'] in existing_ids:
            st.warning(f"Response ID already exists in local backup. Skipping save to prevent duplicate.")
            return False
        
        # Append to CSV
        new_file = not os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=columns)
            if new_file:
                w.writeheader()
            w.writerow(flat)
        
        st.warning(f"Saved locally to survey_responses.csv. Error with Sheets: {str(e)}")
        return True

    
def load_response_by_id(response_id):
    """Load a specific response by ID from sheets"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheet_id = st.secrets["sheet_id"]
        
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1"
        ).execute()
        
        values = result.get('values', [])
        if len(values) < 2:
            return None
            
        headers = values[0]
        rows = values[1:]
        
        response_id_col = headers.index('response_id') if 'response_id' in headers else None
        if response_id_col is None:
            return None
            
        for idx, row in enumerate(rows, start=2):
            if len(row) > response_id_col and row[response_id_col] == response_id:
                # Reconstruct data dict
                data = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
                data['_sheet_row'] = idx  # Store row number for updates
                
                # Parse JSON fields
                json_cols = ['wheel_inventory', 'kilns', 'member_pcts', 'revenue_pcts', 
                           'top_churn_reasons', 'included_amenities', 'security_system', 
                           'member_communication', 'buildout_work_types']
                for col in json_cols:
                    if col in data and data[col]:
                        try:
                            data[col] = json.loads(data[col])
                        except:
                            pass
                
                return data
        
        return None
        
    except Exception as e:
        st.error(f"Error loading response: {e}")
        return None

def update_response(data):
    """Update existing response in sheets"""
    try:
        row_number = data.get('_sheet_row')
        if not row_number:
            return False
            
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheet_id = st.secrets["sheet_id"]
        
        # Update timestamp
        data['submitted_at'] = datetime.now().isoformat()
        
        # Flatten data
        flat = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in data.items()}
        columns = get_all_columns()
        
        body_row = {'values': [[flat.get(c, "") for c in columns]]}
        
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"Sheet1!A{row_number}",
            valueInputOption='RAW',
            body=body_row
        ).execute()
        
        return True
        
    except Exception as e:
        st.error(f"Failed to update: {e}")
        return False

def render_intro():
    st.title("🏺 Pottery Studio Economics Survey")
    
    st.markdown("""
    ### Why this exists
    
    I'm trying to open a community pottery studio. When I started planning, I realized 
    basic questions don't have public answers:
    - How many wheels do I need for 50 members?
    - What's reasonable rent per square foot?
    - Will a $175/month membership cover costs?
    
    This data exists—locked in spreadsheets at studios across the country. But it's not 
    shared. So everyone reinvents the wheel (pun intended).
    
    ### What you get
    
    **Immediately after submitting:**
    - See how your studio compares to others (pricing, space efficiency, equipment ratios)
    - Benchmark your key metrics against median values
    - Identify potential optimization opportunities
    
    **For the community:**
    - Help establish industry baselines
    - Support people trying to make data-driven decisions
    - Build a public dataset that benefits everyone
    
    ### Privacy
        
    - All responses are **100% anonymous**
    - Each response gets a random 4-letter code (like "A3F2") for identification in charts
    - No studio names are collected
    - You receive a unique Response ID to update your answers later
    - Raw data includes only aggregates (no member lists, no detailed P&L)
    - Results dashboard is **public and free**—no email required
    
    ### Time commitment
    
    About **15-20 minutes** depending on your studio's complexity.
    
    ---
    
    **Built by:** Someone trying to open a studio and frustrated by the data gap. I'm a 
    tech professional, not affiliated with any studio chain or consultancy. This is a 
    passion project and public good.
    
    """)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Start Survey", type="primary", use_container_width=True):
            st.session_state.page = 'survey'
            st.session_state.is_update = False
            st.rerun()
    with col2:
        if st.button("View Results Dashboard First", use_container_width=True):
            st.session_state.page = 'results'
            st.rerun()
    
    st.markdown("---")
    
    with st.expander("📝 Update a Previous Response"):
        st.write("""
        Already submitted the survey? Things change - new equipment, different membership count, 
        updated pricing. Use your Response ID to update your previous answers.
        
        Your updates help track how studios evolve over time, which is valuable data for the community.
        """)
        
        response_id_input = st.text_input(
            "Enter your Response ID:",
            help="You received this ID when you first submitted the survey"
        )
        
        if st.button("Load Previous Response", type="secondary"):
            if response_id_input:
                with st.spinner("Loading your previous response..."):
                    previous_data = load_response_by_id(response_id_input)
                    if previous_data:
                        st.session_state.survey_data = previous_data
                        st.session_state.is_update = True
                        st.session_state.page = 'survey'
                        st.success("✓ Previous response loaded! You can now update any fields.")
                        st.rerun()
                    else:
                        st.error("Response ID not found. Please check the ID and try again.")
            else:
                st.warning("Please enter a Response ID")


def render_survey():
    st.title("Studio Economics Survey")
    
    # Generate response_id at the very start if not already set
    data = st.session_state.survey_data
    if 'response_id' not in data:
        data['response_id'] = str(uuid.uuid4())
        data['studio_name'] = data['response_id'][:4].upper()
    
    # Show if in update mode
    if st.session_state.get('is_update', False):
        st.info("📝 You are updating a previous response. All fields show your previous answers.")
    
    
    total_sections = 11
    progress = (st.session_state.survey_section - 1) / total_sections
    st.progress(progress)
    st.caption(f"Section {st.session_state.survey_section} of {total_sections}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.survey_section > 1:
            if st.button("← Previous", use_container_width=True):
                st.session_state.survey_section -= 1
                st.rerun()
    with col3:
        if st.session_state.survey_section < total_sections:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.survey_section += 1
                st.rerun()
    
    st.markdown("---")
    
    if st.session_state.survey_section == 1:
        render_section_1_profile()
    elif st.session_state.survey_section == 2:
        render_section_2_equipment()
    elif st.session_state.survey_section == 3:
        render_section_3_operations()
    elif st.session_state.survey_section == 4:
        render_section_4_pricing()
    elif st.session_state.survey_section == 5:
        render_section_5_member_experience()
    elif st.session_state.survey_section == 6:
        render_section_6_costs()
    elif st.session_state.survey_section == 7:
        render_section_7_revenue()
    elif st.session_state.survey_section == 8:
        render_section_8_market()
    elif st.session_state.survey_section == 9:
        render_section_9_growth()
    elif st.session_state.survey_section == 10:
        render_section_10_challenges()
    elif st.session_state.survey_section == 11:
        render_section_11_feedback()
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.survey_section > 1:
            if st.button("← Previous ", key="prev_bottom", use_container_width=True):
                st.session_state.survey_section -= 1
                st.rerun()
    with col3:
        if st.session_state.survey_section < total_sections:
            if st.button("Next → ", key="next_bottom", type="primary", use_container_width=True):
                st.session_state.survey_section += 1
                st.rerun()
        else:
            if st.button("Submit Survey", type="primary", use_container_width=True):
                submit_survey()


def render_section_1_profile():
    st.header("1. Studio Profile")
    st.caption("Basic information about your studio")
    
    data = st.session_state.survey_data
    # Ensure dict exists in session
    st.session_state.setdefault("survey_data", data)

    
    # UUID and studio_name already set in render_survey()
    # Just show the identifier to the user
    st.caption(f"Your anonymous studio ID: **{data.get('studio_name', 'XXXX')}**")

    
     #=== NEW: INTERNATIONAL SUPPORT ===
    col1, col2 = st.columns(2)
    with col1:
        country_options = [
            "",
            "United States",
            "Canada", 
            "United Kingdom",
            "Australia",
            "New Zealand",
            "Germany",
            "France",
            "Netherlands",
            "Other"
        ]
        _saved_country = data.get('country', '')
        try:
            _country_index = country_options.index(_saved_country) if _saved_country else 0
        except ValueError:
            _country_index = 0
        
        country = st.selectbox(
            "Country *",
            options=country_options,
            index=_country_index
        )
        data['country'] = country
        
        # Set measurement system based on country
        metric_countries = ["Germany", "France", "Netherlands", "Other"]
        is_metric = country in metric_countries
        data['uses_metric'] = is_metric
        
        # Set currency based on country
        currency_map = {
            "United States": "USD",
            "Canada": "CAD",
            "United Kingdom": "GBP",
            "Australia": "AUD",
            "New Zealand": "NZD",
            "Germany": "EUR",
            "France": "EUR",
            "Netherlands": "EUR",
        }
        data['currency'] = currency_map.get(country, "USD")
        
    with col2:
        if country == "United States":
            state_options = [""] + ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                                    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                                    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                                    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                                    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
            _saved_state = data.get('location_state', '')
            try:
                _state_index = state_options.index(_saved_state) if _saved_state else 0
            except ValueError:
                _state_index = 0
            location_state = st.selectbox(
                "State *",
                options=state_options,
                index=_state_index
            )
            data['location_state'] = location_state
        elif country == "Canada":
            province_options = [""] + ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"]
            _saved_prov = data.get('location_state', '')
            try:
                _prov_index = province_options.index(_saved_prov) if _saved_prov else 0
            except ValueError:
                _prov_index = 0
            location_state = st.selectbox(
                "Province *",
                options=province_options,
                index=_prov_index
            )
            data['location_state'] = location_state
        else:
            location_other = st.text_input(
                "State/Province/Region:",
                value=data.get('location_state', '')
            )
            data['location_state'] = location_other
    
    # === DYNAMIC UNITS BASED ON COUNTRY ===
    col1, col2 = st.columns(2)
    with col1:
        # if is_metric:
        #     space_label = "Total usable studio space (m²) *"
        #     space_help = "Member-accessible space only"
        #     space_default = data.get('space_sqm', 10)
        #     space_min, space_max = 10, 5000
        # else:
        #     space_label = "Total usable studio space (sq ft) *"
        #     space_help = "Member-accessible space only"
        #     space_default = data.get('space_sqft', 100)
        #     space_min, space_max = 100, 50000
        
        # space_value = st.number_input(
        #     space_label,
        #     min_value=space_min, 
        #     max_value=space_max, 
        #     step=10 if is_metric else 50,
        #     value=space_default,
        #     help=space_help
        # )
        
        # # Store both formats for consistency
        # if is_metric:
        #     data['space_sqm'] = space_value
        #     data['space_sqft'] = int(space_value * 10.764)  # Convert to sqft for analysis
        # else:
        #     data['space_sqft'] = space_value
        #     data['space_sqm'] = int(space_value / 10.764)
         # --- canonicalize & convert to avoid min_value errors on unit switch ---
         # Keep canonical sqft in state
        canonical_sqft = data.get('space_sqft', None)

        # Conversion helpers
        _to_sqm = lambda x: None if x is None else x / 10.7639
        _to_sqft = lambda x: None if x is None else x * 10.7639

        # Determine which unit system to show
        if is_metric:
            space_label = "Total usable studio space (m²) *"
            space_help = "Member-accessible space only"
            disp_val = _to_sqm(canonical_sqft)
            space_min, space_max = 10.0, 5000.0
            step_val = 1.0
            widget_key = "space_value_sqm"
        else:
            space_label = "Total usable studio space (sq ft) *"
            space_help = "Member-accessible space only"
            disp_val = canonical_sqft
            space_min, space_max = 100, 50000
            step_val = 50
            widget_key = "space_value_sqft"

        # --- normalize default so Streamlit doesn't crash ---
        if disp_val is not None and disp_val < space_min:
            disp_val = space_min
        elif disp_val is None:
            disp_val = space_min

        # Ensure consistent numeric types
        if isinstance(space_min, float):
            disp_val = float(disp_val)
            space_max = float(space_max)
            step_val = float(step_val)

        space_value = st.number_input(
            space_label,
            min_value=space_min,
            max_value=space_max,
            value=disp_val,
            step=step_val,
            help=space_help,
            key=widget_key,
        )

        # Store back in both units
        if is_metric:
            data['space_sqm'] = space_value
            data['space_sqft'] = round(_to_sqft(space_value))
        else:
            data['space_sqft'] = space_value
            data['space_sqm'] = round(_to_sqm(space_value))
  
    with col2:
        # Years operating (universal)
        coly, colm = st.columns(2)
        with coly:
            years = st.number_input(
                "Years operating",
                min_value=0, max_value=100, step=1,
                value=data.get('years_operating_years', 0)
            )
            data['years_operating_years'] = years
        with colm:
            months = st.number_input(
                "Additional months",
                min_value=0, max_value=11, step=1,
                value=data.get('years_operating_months', 0)
            )
            data['years_operating_months'] = months
        
        data['years_operating_total_months'] = years * 12 + months
        st.caption(f"Total: {data['years_operating_total_months']} months")
    
    
    
    st.write("**Area characteristics:**")
    col1, col2 = st.columns(2)
    with col1:
        area_options = ["Urban core (downtown)", "Urban neighborhood", "Suburban",
                       "Small town/rural", "Mixed use district"]
        _saved_area = data.get('area_type', '')
        try:
            _area_index = area_options.index(_saved_area) if _saved_area else 2
        except ValueError:
            _area_index = 2
        area_type = st.selectbox(
            "Area type *",
            area_options,
            index=_area_index
        )
        data['area_type'] = area_type
    
    with col2:
        metro_options = ["Under 50,000", "50,000-100,000", "100,000-250,000",
                        "250,000-500,000", "500,000-1M", "Over 1M"]
        _saved_metro = data.get('metro_population', '')
        try:
            _metro_index = metro_options.index(_saved_metro) if _saved_metro else 0
        except ValueError:
            _metro_index = 0
        metro_population = st.selectbox(
            "Metro area population",
            metro_options,
            index=_metro_index
        )
        data['metro_population'] = metro_population
    
    studio_type_options = ["Non-profit", "For-profit LLC/Corp", "Sole proprietorship",
                           "Community center (within larger org)", "Other"]
    _saved_type = data.get('studio_type', '')
    try:
        _type_index = studio_type_options.index(_saved_type) if _saved_type else 0
    except ValueError:
        _type_index = 0
    studio_type = st.radio(
        "Studio type *",
        studio_type_options,
        index=_type_index
    )
    data['studio_type'] = studio_type
    
    if studio_type == "Other":
        studio_type_other = st.text_input(
            "Please specify studio type:",
            value=data.get('studio_type_other', '')
        )
        data['studio_type_other'] = studio_type_other
    
    current_members = st.number_input(
        "Current active members *",
        min_value=0, max_value=1000, step=1,
        value=data.get('current_members', 0),
        help="Total currently paying/active"
    )
    data['current_members'] = current_members
    
    col1, col2 = st.columns(2)
    with col1:
        time_to_members = st.number_input(
            "Months to reach this number",
            min_value=0, max_value=600, step=1,
            value=data.get('time_to_members_months', 0)
        )
        data['time_to_members_months'] = time_to_members
    
    with col2:
        peak_occupancy = st.number_input(
            "Max simultaneous occupancy",
            min_value=0, max_value=500, step=1,
            value=data.get('peak_occupancy', 0)
        )
        data['peak_occupancy'] = peak_occupancy


def render_section_2_equipment():
    st.header("2. Equipment Inventory")
    data = st.session_state.survey_data
    
    st.subheader("Pottery Wheels")
    total_wheels = st.number_input(
        "Total wheels *",
        min_value=0, max_value=50, step=1,
        value=data.get('total_wheels', 0)
    )
    data['total_wheels'] = total_wheels
    
    if total_wheels and total_wheels > 0:
        st.write("**Wheel inventory by brand/model:**")
        st.caption("Enter quantities for wheels you have (leave rest at 0)")
        
        wheel_inv = data.get('wheel_inventory', {})
        
       # Define all major wheel brands and models
        wheel_options = {
            "Brent": ["CXC", "Model C", "Model B", "Model A", "IE", "EX"],
            "Shimpo": ["VL-Lite", "VL-Whisper", "Aspire", "RK-3E", "RK-5T", "RK-55"],
            "Speedball": ["Artista", "Boss", "Big Boss", "Clay Boss"],
            "Thomas Stuart": ["TurnMaster", "Victoria", "Venco"],
            "Pacifica": ["GT400", "GT800", "GX400"],
            "Skutt": ["Prodigy", "Legend", "Elite"],
            "Bailey": ["Pro 100", "Pro 110", "Pro 120"],
            "Amaco": ["Intro", "Master", "Excel"],
            "Lockerbie": ["Compact", "Standard", "Heavy Duty"],
            "Creative Industries": ["Soldner Original", "Soldner Alpha"],
            "Other/Mixed": ["Other brand/model"]
        }
        
        # Organize into tabs for cleaner UI
        tabs = st.tabs(list(wheel_options.keys()))
        
        for tab, (brand, models) in zip(tabs, wheel_options.items()):
            with tab:
                # Create columns for each brand (3 columns per row)
                cols_per_row = 3
                for i in range(0, len(models), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, model in enumerate(models[i:i+cols_per_row]):
                        with cols[j]:
                            key = f"{brand} {model}"
                            wheel_inv[key] = st.number_input(
                                model, 
                                0, 50, 
                                wheel_inv.get(key, 0), 
                                key=f"w_{brand.lower().replace(' ', '_')}_{model.lower().replace(' ', '_').replace('/', '_')}"
                            )
        
        # Allow for truly custom entries
        with st.expander("Add custom wheel brand/model"):
            st.caption("For wheels not listed above")
            custom_brand = st.text_input("Brand name", key="custom_wheel_brand")
            custom_model = st.text_input("Model name", key="custom_wheel_model")
            custom_count = st.number_input("Quantity", 0, 50, 0, key="custom_wheel_count")
            
            if st.button("Add Custom Wheel"):
                if custom_brand and custom_model and custom_count > 0:
                    custom_key = f"{custom_brand} {custom_model}"
                    wheel_inv[custom_key] = custom_count
                    st.success(f"Added {custom_count}x {custom_key}")
                    st.rerun()
                else:
                    st.warning("Please fill in all fields")
        
        # Store only non-zero entries
        data['wheel_inventory'] = {k: v for k, v in wheel_inv.items() if v > 0}
        
        # Validation
        total_entered = sum(wheel_inv.values())
        if total_entered != total_wheels:
            st.warning(f"⚠️ Inventory counts ({total_entered}) don't match total wheels ({total_wheels})")
        else:
            st.success(f"✓ Counts match: {total_wheels} wheels")
        
        # Show summary of what they have
        if data['wheel_inventory']:
            st.write("**Your inventory:**")
            inv_summary = ", ".join([f"{v}x {k}" for k, v in data['wheel_inventory'].items()])
            st.caption(inv_summary)
        
        st.markdown("---")
        
        # Wheel preference question
        if data['wheel_inventory']:
            wheel_brands_owned = list(set([k.split()[0] for k in data['wheel_inventory'].keys()]))
            wheel_preference = st.multiselect(
                "Which brands would you buy again?",
                options=wheel_brands_owned,
                default=data.get('wheel_preference', [])
            )
            data['wheel_preference'] = wheel_preference
        
        classes_overlap = st.checkbox(
            "Classes and members use studio simultaneously",
            value=data.get('classes_members_overlap', False)
        )
        data['classes_members_overlap'] = classes_overlap
        
        if classes_overlap:
            reserved_pct = st.slider(
                "% of wheels reserved for members during overlap",
                0, 100, data.get('reserved_wheels_for_members_pct', 50), 5
            )
            data['reserved_wheels_for_members_pct'] = reserved_pct
            data['reserved_wheels_for_members_fraction'] = reserved_pct / 100
            data['reserved_wheels_for_members_count'] = int(total_wheels * reserved_pct / 100)    
    
    st.subheader("Work Stations")
    col1, col2, col3 = st.columns(3)
    with col1:
        hb_stations = st.number_input(
            "Handbuilding stations *", min_value=0, max_value=200,
            value=int(data.get('handbuilding_stations', 0)), step=1,
            help="6 sq ft = 1 station", key="handbuilding_stations"
        )
        data['handbuilding_stations'] = hb_stations
    with col2:
        glaze_stations = st.number_input(
            "Glazing stations *", min_value=0, max_value=200,
            value=int(data.get('glazing_stations', 0)), step=1, key="glazing_stations"
        )
        data['glazing_stations'] = glaze_stations
    with col3:
        designated = st.number_input(
            "Private studio rentals", min_value=0, max_value=200,
            value=int(data.get('designated_studios', 0)), step=1, key="designated_studios"
        )
        data['designated_studios'] = designated
    
    if designated and designated > 0:
        st.markdown("**Designated studio details:**")
        col1, col2 = st.columns(2)
        with col1:
            des_cost = st.number_input(
                "Monthly cost ($)", min_value=0, max_value=2000,
                value=int(data.get('designated_membership_cost', 25) or 25), step=5,
                key="designated_membership_cost"
            )
            data['designated_membership_cost'] = des_cost
            
            des_occupancy = st.slider(
                "Occupancy rate (%)",
                0, 100, data.get('designated_occupancy_rate', 50), 5,
                help="What % of private studios are currently rented?"
            )
            data['designated_occupancy_rate'] = des_occupancy
            
        with col2:
            des_shelves = st.number_input(
                "Shelves per space", min_value=0, max_value=20,
                value=int(data.get('designated_shelves', 1) or 1), step=1,
                key="designated_shelves", help="6 sq ft = 1 shelf"
            )
            data['designated_shelves'] = des_shelves
    
    st.subheader("Kilns")
    num_kilns = st.number_input("Number of kilns *", 0, 10, data.get('num_kilns', 0))
    data['num_kilns'] = num_kilns
    
    if num_kilns and num_kilns > 0:
        kilns = data.get('kilns', [])
        for i in range(num_kilns):
            with st.expander(f"Kiln {i+1}", expanded=(i==0)):
                if i >= len(kilns):
                    kilns.append({})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    kiln_type_options = ["Electric cone 6", "Electric cone 10", "Gas", "Wood", "Other"]
                    try:
                        kiln_type_index = kiln_type_options.index(kilns[i].get('type', 'Electric cone 6')) if kilns[i].get('type') in kiln_type_options else 0
                    except (ValueError, KeyError):
                        kiln_type_index = 0
                    kiln_type = st.selectbox("Type", 
                        kiln_type_options,
                        index=kiln_type_index,
                        key=f"k_type_{i}"
                    )
                    kilns[i]['type'] = kiln_type
                with col2:
                    kiln_size_options = ["Small (<7)", "Medium (7-12)", "Large (12-18)", "XL (18+)"]
                    try:
                        kiln_size_index = kiln_size_options.index(kilns[i].get('size', 'Small (<7)')) if kilns[i].get('size') in kiln_size_options else 0
                    except (ValueError, KeyError):
                        kiln_size_index = 0
                    kiln_size = st.selectbox("Size (cu ft)",
                        kiln_size_options,
                        index=kiln_size_index,
                        key=f"k_size_{i}"
                    )
                    kilns[i]['size'] = kiln_size
                with col3:
                    firings = st.number_input("Firings/month", 0, 50, kilns[i].get('firings', 4), key=f"k_fire_{i}")
                    kilns[i]['firings'] = firings
        
        data['kilns'] = kilns


def render_section_3_operations():
    st.header("3. Studio Access & Operations")
    st.caption("How members access the studio and operational details")
    data = st.session_state.survey_data
    
    access_options = [
        "Open studio hours only",
        "24/7 keycard access for all",
        "24/7 for some (premium tier)",
        "Appointment/reservation required",
    ]
    _saved_access = data.get('access_model', '')
    try:
        _access_index = access_options.index(_saved_access) if _saved_access else 0
    except ValueError:
        _access_index = 0
    
    access_model = st.radio(
        "Access model *",
        access_options,
        index=_access_index,
    )
    data['access_model'] = access_model
    
    st.write("**Studio hours:**")
    col1, col2 = st.columns(2)
    with col1:
        hours_per_day = st.number_input(
            "Average accessible hours per day", 
            min_value=0, max_value=24, value=data.get('hours_per_day', 0), step=1,
            help="Average hours studio is open/accessible"
        )
        data['hours_per_day'] = hours_per_day
    with col2:
        days_per_week = st.number_input(
            "Number of days per week open", 
            min_value=0, max_value=7, value=data.get('days_per_week', 0), step=1
        )
        data['days_per_week'] = days_per_week
    
    total_accessible_hours = (hours_per_day or 0) * (days_per_week or 0)
    data['total_accessible_hours'] = total_accessible_hours
    if total_accessible_hours > 0:
        st.info(f"Total accessible hours: {total_accessible_hours} hours/week")
    
    st.write("**Staff presence:**")
    col1, col2 = st.columns(2)
    with col1:
        staffed_hours = st.number_input(
            "Hours per week with staff present",
            min_value=0, max_value=168, value=data.get('staffed_hours', 0), step=1,
            help="Total hours across all days when staff is on-site"
        )
        data['staffed_hours'] = staffed_hours
    with col2:
        unstaffed_hours = st.number_input(
            "Hours per week members access without staff",
            min_value=0, max_value=168, value=data.get('unstaffed_hours', 0), step=1,
            help="Self-access hours (keycard, etc.)"
        )
        data['unstaffed_hours'] = unstaffed_hours
    
    st.subheader("Staffing")
    has_staff = st.checkbox("We have paid staff (not including owner/founder)", value=data.get('has_staff', False))
    data['has_staff'] = has_staff
    
    st.write("**Staff roles and hours:** *(fill in only if you have staff)*")
    st.caption("Enter total hours per week for each role")
    
    col1, col2 = st.columns(2)
    with col1:
        studio_manager_hours = st.number_input(
            "Studio manager (hours/week)",
            min_value=0.0, max_value=168.0, step=1.0, value=data.get('studio_manager_hours', 0.0),
            help="Total hours per week"
        )
        data['studio_manager_hours'] = studio_manager_hours
        
        front_desk_hours = st.number_input(
            "Front desk/reception (hours/week)",
            min_value=0.0, max_value=168.0, step=1.0, value=data.get('front_desk_hours', 0.0)
        )
        data['front_desk_hours'] = front_desk_hours
        
        instructors_hours = st.number_input(
            "Instructors/teachers (hours/week)",
            min_value=0.0, max_value=168.0, step=1.0, value=data.get('instructors_hours', 0.0)
        )
        data['instructors_hours'] = instructors_hours
    
    with col2:
        tech_support_hours = st.number_input(
            "Studio technician/kiln loader (hours/week)",
            min_value=0.0, max_value=168.0, step=1.0, value=data.get('tech_support_hours', 0.0)
        )
        data['tech_support_hours'] = tech_support_hours
        
        cleaning_hours = st.number_input(
            "Cleaning/maintenance (hours/week)",
            min_value=0.0, max_value=168.0, step=1.0, value=data.get('cleaning_hours', 0.0)
        )
        data['cleaning_hours'] = cleaning_hours
        
        other_staff_hours = st.number_input(
            "Other staff (hours/week)",
            min_value=0.0, max_value=168.0, step=1.0, value=data.get('other_staff_hours', 0.0)
        )
        data['other_staff_hours'] = other_staff_hours
        
    other_staff_description = st.text_input(
        "Describe other staff role(s) (if applicable)",
        value=data.get('other_staff_description', ''),
        placeholder="e.g., Marketing coordinator, Events manager"
    )
    data['other_staff_description'] = other_staff_description
    
    st.write("**Compensation structure:** *(fill in only if you have staff)*")
    col1, col2 = st.columns(2)
    with col1:
        comp_options = ["N/A - no staff", "Hourly wages", "Salary", "Mix of hourly and salary", "Contract/1099"]
        _saved_comp = data.get('compensation_type', 'N/A - no staff')
        try:
            _comp_index = comp_options.index(_saved_comp) if _saved_comp else 0
        except ValueError:
            _comp_index = 0
        
        compensation_type = st.radio(
            "Primary compensation model",
            comp_options,
            index=_comp_index
        )
        data['compensation_type'] = compensation_type
    with col2:
        avg_hourly_rate = st.number_input(
            "Average hourly rate if applicable ($)",
            min_value=0.0, max_value=100.0, step=0.50, value=data.get('avg_hourly_rate', 0.0),
            help="Leave blank if salaried or no staff"
        )
        data['avg_hourly_rate'] = avg_hourly_rate
    
    total_staff_cost = st.number_input(
        "Total monthly staff cost ($)",
        min_value=0, max_value=50000, step=100, value=data.get('total_staff_cost', 0),
        help="Including wages, taxes, benefits. Leave blank if no staff."
    )
    data['total_staff_cost'] = total_staff_cost
    
    st.subheader("Technology & Systems")
    
    col1, col2 = st.columns(2)
    with col1:
        membership_software_options = [
            "None (spreadsheets/manual)",
            "Pike13",
            "Mindbody",
            "Wodify",
            "Custom database",
            "Square",
            "Glofox",
            "Other"
        ]
        _saved_membership = data.get('membership_software', 'None (spreadsheets/manual)')
        try:
            _membership_index = membership_software_options.index(_saved_membership) if _saved_membership else 0
        except ValueError:
            _membership_index = 0
        
        membership_software = st.selectbox(
            "Membership management software *",
            membership_software_options,
            index=_membership_index
        )
        data['membership_software'] = membership_software
        
        scheduling_options = [
            "None needed",
            "Built into membership software",
            "Calendly",
            "Google Calendar/Sheets",
            "Square Appointments",
            "Acuity",
            "Other"
        ]
        _saved_scheduling = data.get('scheduling_system', 'None needed')
        try:
            _scheduling_index = scheduling_options.index(_saved_scheduling) if _saved_scheduling else 0
        except ValueError:
            _scheduling_index = 0
        
        scheduling_system = st.selectbox(
            "Scheduling/booking system",
            scheduling_options,
            index=_scheduling_index
        )
        data['scheduling_system'] = scheduling_system
    
    with col2:
        payment_options = [
            "Square",
            "Stripe",
            "PayPal",
            "Venmo/Cash App",
            "Built into membership software",
            "Bank ACH",
            "Other"
        ]
        _saved_payment = data.get('payment_processor', 'Square')
        try:
            _payment_index = payment_options.index(_saved_payment) if _saved_payment else 0
        except ValueError:
            _payment_index = 0
        
        payment_processor = st.selectbox(
            "Payment processing platform *",
            payment_options,
            index=_payment_index
        )
        data['payment_processor'] = payment_processor
        
        security_system = st.multiselect(
            "Security/access control (select all)",
            ["None",                 
             "Security cameras",
             "Keycard/fob access",
             "Smart lock with codes",
             "Alarm system",
             "Other"],
            default=data.get('security_system', [])
        )
        data['security_system'] = security_system
    
    member_communication = st.multiselect(
        "Primary member communication methods (select all) *",
        ["Email",
         "Slack",
         "Discord",
         "WhatsApp/group text",
         "Facebook group",
         "Instagram",
         "In-person bulletin board",
         "Membership software messaging",
         "Other"],
        default=data.get('member_communication', [])
    )
    data['member_communication'] = member_communication


def render_section_4_pricing():
    """Modified to show currency dynamically"""
    st.header("4. Pricing Structure")
    data = st.session_state.survey_data
    
    # Get currency symbol
    currency = data.get('currency', 'USD')
    currency_symbol = {
        'USD': '$',
        'CAD': 'C$',
        'GBP': '£',
        'EUR': '€',
        'AUD': 'A$',
        'NZD': 'NZ$'
    }.get(currency, '$')
    
    st.subheader("Membership Tiers")
    tier_options = ["Single tier", "Two tiers", "Three tiers", "Four or more"]
    _saved_tier = data.get('tier_structure', '')
    try:
        _tier_index = tier_options.index(_saved_tier) if _saved_tier else 0
    except ValueError:
        _tier_index = 0
    tier_structure = st.radio(
        "Number of tiers *",
        tier_options,
        index=_tier_index
    )
    data['tier_structure'] = tier_structure
    
    num_tiers = {"Single tier": 1, "Two tiers": 2, "Three tiers": 3, "Four or more": 4}.get(tier_structure, 1)
    
    cols = st.columns(num_tiers)
    for i in range(num_tiers):
        with cols[i]:
            price = st.number_input(
                f"Tier {i+1} ({currency_symbol})",  # Dynamic currency
                0, 1000, 
                value=data.get(f'tier{i+1}_price', 5),
                step=5
            )
            data[f'tier{i+1}_price'] = price
    
    st.write("**What's included at each tier?**")
    st.caption("Brief description of what distinguishes each tier")
    
    for i in range(num_tiers):
        if data.get(f'tier{i+1}_price'):
            tier_name = st.text_input(
                f"Tier {i+1} name (optional)",
                value=data.get(f'tier{i+1}_name', ''),
                placeholder=f"e.g., Basic, Premium, Unlimited",
                key=f"tier{i+1}_name"
            )
            data[f'tier{i+1}_name'] = tier_name
            
            tier_description = st.text_area(
                f"Tier {i+1} - What's included?",
                value=data.get(f'tier{i+1}_description', ''),
                placeholder="e.g., 8 hours/week, 2 firings/month, 2 shelves",
                height=80,
                key=f"tier{i+1}_desc"
            )
            data[f'tier{i+1}_description'] = tier_description
    
    st.subheader("Firing Fees")
    firing_options = ["Included in membership", "Per pound", "Per piece",
                      "Per shelf/space", "Per volume (cu ft)", "Other"]
    _saved_firing = data.get('firing_model', '')
    try:
        _firing_index = firing_options.index(_saved_firing) if _saved_firing else 0
    except ValueError:
        _firing_index = 0
    firing_model = st.radio(
        "Firing fee model *",
        firing_options,
        index=_firing_index
    )
    data['firing_model'] = firing_model
    
    if firing_model == "Per pound":
        st.write("**Per-pound rate schedule:**")
        st.caption("Example: First 20 lbs at $3/lb, next 20 lbs at $4/lb, everything above 40 lbs at $5/lb")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            tier1_lbs = st.number_input(
                "Tier 1: First X pounds", 
                5, 100, data.get('firing_tier1_lbs', 20), 5,
                help="How many pounds at the first rate?"
            )
            data['firing_tier1_lbs'] = tier1_lbs
            tier1_rate = st.number_input(
                "Tier 1: Rate ($/lb)", 
                0.0, 10.0, data.get('firing_tier1_rate', 3.0), 0.25
            )
            data['firing_tier1_rate'] = tier1_rate
        
        with col2:
            tier2_lbs = st.number_input(
                "Tier 2: Next X pounds", 
                5, 100, data.get('firing_tier2_lbs', 20), 5,
                help="Additional pounds at second rate"
            )
            data['firing_tier2_lbs'] = tier2_lbs
            tier2_rate = st.number_input(
                "Tier 2: Rate ($/lb)", 
                0.0, 10.0, data.get('firing_tier2_rate', 4.0), 0.25
            )
            data['firing_tier2_rate'] = tier2_rate
        
        with col3:
            tier3_rate = st.number_input(
                "Tier 3: Rate ($/lb) for anything above", 
                0.0, 10.0, data.get('firing_tier3_rate', 5.0), 0.25,
                help=f"Rate for anything over {tier1_lbs + tier2_lbs} lbs"
            )
            data['firing_tier3_rate'] = tier3_rate
        
        st.info(f"Example total: 50 lbs would cost ${tier1_lbs * tier1_rate + tier2_lbs * tier2_rate + (50 - tier1_lbs - tier2_lbs) * tier3_rate:.2f}")
    
    elif firing_model == "Per piece":
        st.write("**Per-piece rates:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            firing_small = st.number_input("Small (<6\") ($)", 0.0, 50.0, data.get('firing_small', 5.0), 0.5)
            data['firing_small'] = firing_small
        with col2:
            firing_medium = st.number_input("Medium (6-12\") ($)", 0.0, 50.0, data.get('firing_medium', 10.0), 0.5)
            data['firing_medium'] = firing_medium
        with col3:
            firing_large = st.number_input("Large (>12\") ($)", 0.0, 100.0, data.get('firing_large', 15.0), 0.5)
            data['firing_large'] = firing_large
    
    elif firing_model == "Per shelf/space":
        firing_rate = st.number_input("Per shelf ($)", 0.0, 500.0, data.get('firing_rate', 20.0), 1.0)
        data['firing_rate'] = firing_rate
    
    elif firing_model == "Per volume (cu ft)":
        firing_rate_cuft = st.number_input("Per cu ft ($)", 0.0, 200.0, data.get('firing_rate_cuft', 18.0), 1.0)
        data['firing_rate_cuft'] = firing_rate_cuft
    
    elif firing_model == "Other":
        firing_explain = st.text_area("Describe your model:", data.get('firing_explain', ''), height=80)
        data['firing_explain'] = firing_explain
    
    col1, col2 = st.columns(2)
    with col1:
        clay_price = st.number_input("Clay price per 25lb bag ($) *", 0, 100, value=data.get('clay_price', 1), step=1)
        data['clay_price'] = clay_price
    with col2:
        clay_types = st.number_input("Number of clay options", 1, 20, value=data.get('clay_types', 1), step=1)
        data['clay_types'] = clay_types
    
    st.subheader("Classes")

    offers_classes = st.checkbox("We offer classes", value=data.get('offers_classes', False))
    data['offers_classes'] = offers_classes
    
    if offers_classes:
        col1, col2 = st.columns(2)
        with col1:
            class_price = st.number_input(
                "Typical class price ($)", 
                0, 2000, 
                value=data.get('class_price', 25),
                step=25,
                help="For a typical class series or workshop"
            )
            data['class_price'] = class_price
            
            class_weeks = st.number_input(
                "Length (weeks)", 
                1, 52, 
                value=data.get('class_weeks', 1),
                step=1
            )
            data['class_weeks'] = class_weeks
        with col2:
            class_enrollment = st.number_input(
                "Typical enrollment", 
                1, 50, 
                value=data.get('class_enrollment', 1),
                step=1
            )
            data['class_enrollment'] = class_enrollment
    
        st.write("**Class economics:**")
        
        col1, col2 = st.columns(2)
        with col1:
            class_sessions_per_month = st.number_input(
                "Total class sessions per month",
                min_value=0, max_value=200, step=1,
                value=data.get('class_sessions_per_month', 0),
                help="Total number of class meetings held per month (e.g., if you run 3 weekly classes, that's ~12 sessions/month)"
            )
            data['class_sessions_per_month'] = class_sessions_per_month
        
        with col2:
            class_format_options = ["One-time workshop", "Multi-week series (4-8 weeks)", 
                                   "Ongoing/drop-in", "Mix"]
            _saved_format = data.get('class_format', '')
            try:
                _format_index = class_format_options.index(_saved_format) if _saved_format else 1
            except ValueError:
                _format_index = 1
            class_format = st.radio(
                "Typical class format",
                class_format_options,
                index=_format_index
            )
            data['class_format'] = class_format
        
        st.write("**Instructor compensation:**")
        instructor_comp_options = [
            "Flat rate per session",
            "Percentage of revenue",
            "Hourly rate",
            "Owner teaches (no separate cost)",
            "Other"
        ]
        instructor_comp = st.selectbox(
            "How do you compensate instructors?",
            instructor_comp_options,
            index=instructor_comp_options.index(data.get('instructor_compensation_model', 'Flat rate per session')) 
                  if data.get('instructor_compensation_model') in instructor_comp_options else 0
        )
        data['instructor_compensation_model'] = instructor_comp
        
        if instructor_comp == "Flat rate per session":
            flat_rate = st.number_input(
                "Rate per session ($)",
                0, 1000, data.get('instructor_flat_rate', 0), 25,
                help="What you pay the instructor per class session"
            )
            data['instructor_flat_rate'] = flat_rate
        elif instructor_comp == "Percentage of revenue":
            pct = st.number_input(
                "Instructor percentage (%)",
                0, 100, data.get('instructor_revenue_percentage', 0), 5
            )
            data['instructor_revenue_percentage'] = pct
        elif instructor_comp == "Hourly rate":
            hourly = st.number_input(
                "Hourly rate ($)",
                0, 200, data.get('instructor_hourly_rate', 0), 5
            )
            data['instructor_hourly_rate'] = hourly
    
    st.markdown("---")
    st.subheader("Events & Parties")
    st.caption("Paint-your-own-pottery, private parties, team building, etc.")
    
    offers_events = st.checkbox(
        "We offer events/parties",
        value=bool(data.get("offers_events", False)),
        help="Private events, PYOP sessions, team building, birthday parties, etc.",
    )
    data["offers_events"] = offers_events
    
    # --- Always ensure all keys exist with consistent types ---
    data.setdefault("event_types", [])               # list
    data.setdefault("event_price", 0)                # number
    data.setdefault("event_attendance", 0)           # number
    data.setdefault("events_per_month", 0)           # number
    data.setdefault("event_pricing_model", "Per person")
    data.setdefault("flat_event_rate", 0)            # number
    data.setdefault("event_piece_price", 0)          # number
    data.setdefault("event_studio_fee", 0)           # number
    
    if offers_events:
        col1, col2 = st.columns(2)
        with col1:
            event_type = st.multiselect(
                "Types of events offered:",
                [
                    "Paint-your-own-pottery (PYOP)",
                    "Private parties (birthdays, etc.)",
                    "Team building/corporate",
                    "Date nights",
                    "Kids parties",
                    "Other",
                ],
                default=data.get("event_types", []),
            )
            data["event_types"] = event_type
    
            event_price = st.number_input(
                "Typical event price per person ($)",
                min_value=0,
                max_value=500,
                step=5,
                value=int(data.get("event_price", 25)),
                help="Average price per attendee",
            )
            data["event_price"] = event_price
    
        with col2:
            events_per_month = st.number_input(
                "Events per month (average)",
                min_value=0,
                max_value=100,
                step=1,
                value=int(data.get("events_per_month", 0)),
                help="How many events/parties do you host monthly?",
            )
            data["events_per_month"] = events_per_month
    
            event_attendance = st.number_input(
                "Avg attendance per event",
                min_value=0,
                max_value=100,
                step=1,
                value=int(data.get("event_attendance", 10)),
                help="Typical number of people per event",
            )
            data["event_attendance"] = event_attendance
    
        event_pricing_model = st.radio(
            "Event pricing model:",
            ["Per person", "Flat rate (full buyout)", "Per piece + studio fee", "Other"],
            index=["Per person", "Flat rate (full buyout)", "Per piece + studio fee", "Other"].index(
                data.get("event_pricing_model", "Per person")
            ),
        )
        data["event_pricing_model"] = event_pricing_model
    
        if event_pricing_model == "Flat rate (full buyout)":
            flat_event_rate = st.number_input(
                "Flat rate for full event ($)",
                min_value=0,
                max_value=5000,
                step=50,
                value=int(data.get("flat_event_rate", 200)),
            )
            data["flat_event_rate"] = flat_event_rate
    
        elif event_pricing_model == "Per piece + studio fee":
            piece_price = st.number_input(
                "Price per piece ($)",
                min_value=0,
                max_value=100,
                step=5,
                value=int(data.get("event_piece_price", 15)),
            )
            data["event_piece_price"] = piece_price
    
            studio_fee = st.number_input(
                "Studio/setup fee ($)",
                min_value=0,
                max_value=500,
                step=25,
                value=int(data.get("event_studio_fee", 50)),
            )
            data["event_studio_fee"] = studio_fee
    
    else:
        # If unchecked, keep types stable but empty out values
        data["event_types"] = []
        data["event_price"] = 0
        data["event_attendance"] = 0
        data["events_per_month"] = 0
        data["event_pricing_model"] = "Per person"
        data["flat_event_rate"] = 0
        data["event_piece_price"] = 0
        data["event_studio_fee"] = 0
        
        
def render_section_5_member_experience():
    st.header("5. Member Experience")
    st.caption("Understanding who your members are and how they use the studio")
    data = st.session_state.survey_data
    
    st.subheader("5a. Demographics & Behavior")
    st.write("**Estimate what percentage of your members fall into each category:**")
    st.caption("Percentages should sum to 100%")
    
    hobbyist_pct = st.slider(
        "Hobbyists (1x/week or less, casual)",
        0, 100, data.get('hobbyist_pct', 35), 5,
        help="Occasional users, often have other primary hobbies"
    )
    data['hobbyist_pct'] = hobbyist_pct
    
    regular_pct = st.slider(
        "Regular artists (2-3x/week, consistent)",
        0, 100, data.get('regular_pct', 40), 5,
        help="Core members who come reliably"
    )
    data['regular_pct'] = regular_pct
    
    production_pct = st.slider(
        "Production potters (4+x/week, heavy users)",
        0, 100, data.get('production_pct', 10), 5,
        help="Making pottery to sell, very frequent usage"
    )
    data['production_pct'] = production_pct
    
    seasonal_pct = st.slider(
        "Seasonal/occasional (sporadic attendance)",
        0, 100, data.get('seasonal_pct', 15), 5,
        help="Irregular users, often gift memberships"
    )
    data['seasonal_pct'] = seasonal_pct
    
    member_pcts = {
        'hobbyist': hobbyist_pct,
        'regular': regular_pct,
        'production': production_pct,
        'seasonal': seasonal_pct
    }
    data['member_pcts'] = member_pcts
    
    total_pct = sum(member_pcts.values())
    
    if abs(total_pct - 100) > 1:
        st.error(f"Percentages sum to {total_pct}%. Please adjust to equal 100%.")
    else:
        st.success(f"✓ Percentages sum to {total_pct}%")
    
    demographics_accuracy = st.checkbox(
        "These demographics are reasonably accurate",
        value=data.get('demographics_usage_accuracy_ok', False)
    )
    data['demographics_usage_accuracy_ok'] = demographics_accuracy
    
    col1, col2 = st.columns(2)
    with col1:
        monthly_churn = st.number_input(
            "Monthly churn rate (%)",
            min_value=0.0, max_value=50.0, step=0.5, 
            value=data.get('monthly_churn', 0.0),
            help="Percentage of members who don't renew each month"
        )
        data['monthly_churn'] = monthly_churn
    
    with col2:
        new_members_per_month = st.number_input(
            "New members per month (average)",
            min_value=0, max_value=100, step=1,
            value=data.get('new_members_per_month', 0),
            help="Average number of new members joining monthly"
        )
        data['new_members_per_month'] = new_members_per_month
    
    top_churn_reasons = st.multiselect(
        "Top reasons members leave:",
        ["Cost/affordability", "Not enough time to use membership",
         "Moving away/relocation", "Scheduling conflicts", "Studio too crowded",
         "Lost interest", "Interpersonal issues", "Equipment availability",
         "Don't track this", "Other"],
        default=data.get('top_churn_reasons', [])
    )
    data['top_churn_reasons'] = top_churn_reasons
    
    st.markdown("---")
    st.subheader("5b. Amenities & Resources")
    
    col1, col2 = st.columns(2)
    with col1:
        shelf_space_per_member = st.number_input(
            "Shelf space per member (linear feet) *",
            min_value=0.0, max_value=50.0, step=0.5,
            value=data.get('shelf_space_per_member', 0.0)
        )
        data['shelf_space_per_member'] = shelf_space_per_member
        
        storage_bins_per_member = st.number_input(
            "Storage bins per member",
            min_value=0, max_value=20, step=1,
            value=data.get('storage_bins_per_member', 0)
        )
        data['storage_bins_per_member'] = storage_bins_per_member
    with col2:
        avg_pieces_fired_per_member = st.number_input(
            "Avg pieces fired per member/month",
            min_value=0, max_value=100, step=1,
            value=data.get('avg_pieces_fired_per_member', 0)
        )
        data['avg_pieces_fired_per_member'] = avg_pieces_fired_per_member
        
        clay_consumption_per_member = st.number_input(
            "Avg clay consumption (lbs/month)",
            min_value=0, max_value=500, step=5,
            value=data.get('clay_consumption_per_member', 0)
        )
        data['clay_consumption_per_member'] = clay_consumption_per_member
    
    included_amenities = st.multiselect(
        "Included amenities:",
        ["Basic pottery tools", "Trimming tools", "Bats", "Sponges and cleanup",
         "Aprons", "Underglazes", "Studio glazes", "Wi-Fi", "Coffee/tea",
         "None - members bring all"],
        default=data.get('included_amenities', [])
    )
    data['included_amenities'] = included_amenities
    
    st.markdown("---")
    st.subheader("5c. Marketing")
    
    col1, col2 = st.columns(2)
    with col1:
        marketing_budget_options = ["$0 (word of mouth)", "Under $100", "$100-$250", "$250-$500",
             "$500-$1,000", "$1,000-$2,000", "Over $2,000"]
        _saved_marketing = data.get('monthly_marketing_budget', '$0 (word of mouth)')
        try:
            _marketing_index = marketing_budget_options.index(_saved_marketing) if _saved_marketing else 0
        except ValueError:
            _marketing_index = 0
        
        monthly_marketing_budget = st.selectbox(
            "Monthly marketing budget",
            marketing_budget_options,
            index=_marketing_index
        )
        data['monthly_marketing_budget'] = monthly_marketing_budget
    with col2:
        cpa_options = ["Don't track", "Under $25", "$25-$50", "$50-$100",
             "$100-$200", "$200-$500", "Over $500"]
        _saved_cpa = data.get('cost_per_acquisition', "Don't track")
        try:
            _cpa_index = cpa_options.index(_saved_cpa) if _saved_cpa else 0
        except ValueError:
            _cpa_index = 0
        
        cost_per_acquisition = st.selectbox(
            "Cost per acquisition",
            cpa_options,
            index=_cpa_index
        )
        data['cost_per_acquisition'] = cost_per_acquisition
    
    has_trial = st.checkbox("We offer trial/intro membership", value=data.get('has_trial_offer', False))
    data['has_trial_offer'] = has_trial
    
    if has_trial:
        col1, col2 = st.columns(2)
        with col1:
            trial_options = ["First month discounted", "Free trial", "Intro package",
                 "Punch card", "Other"]
            _saved_trial = data.get('trial_offer_type', 'First month discounted')
            try:
                _trial_index = trial_options.index(_saved_trial) if _saved_trial else 0
            except ValueError:
                _trial_index = 0
            
            trial_offer_type = st.selectbox(
                "Trial offer type",
                trial_options,
                index=_trial_index
            )
            data['trial_offer_type'] = trial_offer_type
        with col2:
            conversion_options = ["Don't track", "Under 25%", "25-50%", "50-75%", "Over 75%"]
            _saved_conversion = data.get('trial_conversion_rate', "Don't track")
            try:
                _conversion_index = conversion_options.index(_saved_conversion) if _saved_conversion else 0
            except ValueError:
                _conversion_index = 0
            
            trial_conversion_rate = st.selectbox(
                "Conversion to full membership",
                conversion_options,
                index=_conversion_index
            )
            data['trial_conversion_rate'] = trial_conversion_rate


def render_section_6_costs():
    """Modified to handle weight units dynamically"""
    st.header("6. Operating Costs")
    st.caption("Monthly expenses and build-out investments")
    data = st.session_state.survey_data
    
    currency = data.get('currency', 'USD')
    currency_symbol = {
        'USD': '$', 'CAD': 'C$', 'GBP': '£', 
        'EUR': '€', 'AUD': 'A$', 'NZD': 'NZ$'
    }.get(currency, '$')
    
    col1, col2 = st.columns(2)
    with col1:
        rent = st.number_input(
            f"Monthly rent/mortgage ({currency_symbol}) *",
            min_value=0, max_value=50000, step=100,
            value=data.get('rent', 0)
        )
        data['rent'] = rent
        
        utilities_included = st.checkbox(
            "Utilities included in rent",
            value=data.get('utilities_included', False)
        )
        data['utilities_included'] = utilities_included
        
        if not utilities_included:
            electricity = st.number_input(
                "Monthly electricity ($)",
                min_value=0, max_value=5000, step=50,
                value=data.get('electricity', 0)
            )
            data['electricity'] = electricity
            
            water = st.number_input(
                "Monthly water/sewer ($)",
                min_value=0, max_value=1000, step=25,
                value=data.get('water', 0)
            )
            data['water'] = water
    
    with col2:
        insurance = st.number_input(
            "Monthly insurance ($) *",
            min_value=0, max_value=2000, step=25,
            value=data.get('insurance', 0)
        )
        data['insurance'] = insurance
        
        glaze_budget = st.number_input(
            "Monthly glaze/materials ($)",
            min_value=0, max_value=5000, step=50,
            value=data.get('glaze_budget', 0)
        )
        data['glaze_budget'] = glaze_budget
    
    st.subheader("Maintenance & Repairs")
    col1, col2 = st.columns(2)
    with col1:
        equipment_maintenance = st.number_input(
            "Monthly equipment maintenance/repairs ($)",
            min_value=0, max_value=5000, step=50,
            value=data.get('equipment_maintenance', 0),
            help="Wheel repairs, kiln elements, general equipment upkeep"
        )
        data['equipment_maintenance'] = equipment_maintenance

    with col2:
        building_maintenance = st.number_input(
            "Monthly building/facility maintenance ($)",
            min_value=0, max_value=2000, step=50,
            value=data.get('building_maintenance', 0),
            help="Plumbing, HVAC, cleaning supplies, general facility upkeep"
        )
        data['building_maintenance'] = building_maintenance
    
    st.markdown("---")
    st.subheader("Build-Out & Leasehold Improvements")
    
    had_buildout = st.checkbox(
        "We did leasehold improvements",
        value=data.get('had_buildout', False)
    )
    data['had_buildout'] = had_buildout
    
    if had_buildout:
        st.write("**Type of work (check all that apply):**")
        col1, col2 = st.columns(2)
        
        buildout_work = data.get('buildout_work_types', {})
        with col1:
            plumbing = st.checkbox("Plumbing", value=buildout_work.get('plumbing', False))
            buildout_work['plumbing'] = plumbing
            electrical = st.checkbox("Electrical", value=buildout_work.get('electrical', False))
            buildout_work['electrical'] = electrical
            hvac = st.checkbox("HVAC", value=buildout_work.get('hvac', False))
            buildout_work['hvac'] = hvac
            flooring = st.checkbox("Flooring", value=buildout_work.get('flooring', False))
            buildout_work['flooring'] = flooring
        with col2:
            kiln_room = st.checkbox("Kiln room", value=buildout_work.get('kiln_room', False))
            buildout_work['kiln_room'] = kiln_room
            storage = st.checkbox("Storage systems", value=buildout_work.get('storage', False))
            buildout_work['storage'] = storage
            paint = st.checkbox("Paint/finishes", value=buildout_work.get('paint', False))
            buildout_work['paint'] = paint
            other_build = st.checkbox("Other", value=buildout_work.get('other', False))
            buildout_work['other'] = other_build
        
        data['buildout_work_types'] = buildout_work
        
        col1, col2 = st.columns(2)
        with col1:
            buildout_cost_total = st.number_input(
                "Total cost ($)",
                min_value=0, max_value=500000, step=1000,
                value=data.get('buildout_cost_total', 0)
            )
            data['buildout_cost_total'] = buildout_cost_total
        with col2:
            buildout_timeline = st.number_input(
                "Timeline (weeks)",
                min_value=0, max_value=104, step=1,
                value=data.get('buildout_timeline', 0)
            )
            data['buildout_timeline'] = buildout_timeline


def render_section_7_revenue():
    st.header("7. Revenue & Financial Performance")
    st.caption("All optional if you prefer not to share")
    data = st.session_state.survey_data
    
    st.subheader("Revenue Breakdown")
    st.caption("Percentages should sum to 100%")
    
    rev_membership = st.slider("Membership fees", 0, 100, data.get('rev_membership', 60), 5)
    data['rev_membership'] = rev_membership
    
    rev_clay = st.slider("Clay sales", 0, 100, data.get('rev_clay', 15), 5)
    data['rev_clay'] = rev_clay
    
    rev_firing = st.slider("Firing fees", 0, 100, data.get('rev_firing', 10), 5)
    data['rev_firing'] = rev_firing
    
    rev_classes = st.slider("Classes/workshops", 0, 100, data.get('rev_classes', 10), 5)
    data['rev_classes'] = rev_classes
    
    rev_events = st.slider("Events/parties", 0, 100, data.get('rev_events', 5), 5)
    data['rev_events'] = rev_events
    
    rev_other = st.slider("Other", 0, 100, data.get('rev_other', 0), 5)
    data['rev_other'] = rev_other
    
    revenue_pcts = {
        'membership': rev_membership,
        'clay': rev_clay,
        'firing': rev_firing,
        'classes': rev_classes,
        'events': rev_events,
        'other': rev_other
    }
    data['revenue_pcts'] = revenue_pcts
    
    total_rev = sum(revenue_pcts.values())
    
    if abs(total_rev - 100) > 1:
        st.error(f"Revenue percentages sum to {total_rev}%. Please adjust to 100%.")
    else:
        st.success(f"✓ Revenue percentages sum to {total_rev}%")
    
    st.markdown("---")
    st.subheader("Financial Performance")
    
    col1, col2 = st.columns(2)
    with col1:
        revenue_options = ["Prefer not to say", "Under $5,000", "$5,000-$10,000",
             "$10,000-$20,000", "$20,000-$35,000", "$35,000-$50,000",
             "$50,000-$75,000", "Over $75,000"]
        _saved_revenue = data.get('monthly_revenue_range', 'Prefer not to say')
        try:
            _revenue_index = revenue_options.index(_saved_revenue) if _saved_revenue else 0
        except ValueError:
            _revenue_index = 0
        
        monthly_revenue_range = st.selectbox(
            "Monthly revenue range",
            revenue_options,
            index=_revenue_index
        )
        data['monthly_revenue_range'] = monthly_revenue_range
        
        profit_options = ["Breaking even", "Profitable", "Operating at loss",
             "Too early to tell", "Prefer not to say"]
        _saved_profit = data.get('profitability_status', '')
        try:
            _profit_index = profit_options.index(_saved_profit) if _saved_profit else 0
        except ValueError:
            _profit_index = 0
        
        profitability_status = st.radio(
            "Profitability status",
            profit_options,
            index=_profit_index
        )
        data['profitability_status'] = profitability_status
    
    with col2:
        startup_options = ["Under $10,000", "$10,000-$25,000", "$25,000-$50,000",
             "$50,000-$75,000", "$75,000-$100,000", "$100,000-$150,000",
             "Over $150,000"]
        _saved_startup = data.get('startup_capital_range', 'Under $10,000')
        try:
            _startup_index = startup_options.index(_saved_startup) if _saved_startup else 0
        except ValueError:
            _startup_index = 0
        
        startup_capital_range = st.selectbox(
            "Startup capital required",
            startup_options,
            index=_startup_index
        )
        data['startup_capital_range'] = startup_capital_range
        
        time_to_profit_options = ["Not yet profitable", "Under 6 months", "6-12 months",
             "12-18 months", "18-24 months", "Over 24 months"]
        _saved_time = data.get('time_to_profitability', 'Not yet profitable')
        try:
            _time_index = time_to_profit_options.index(_saved_time) if _saved_time else 0
        except ValueError:
            _time_index = 0
        
        time_to_profitability = st.selectbox(
            "Time to profitability",
            time_to_profit_options,
            index=_time_index
        )
        data['time_to_profitability'] = time_to_profitability
    
    owner_hours_per_week = st.number_input(
        "Owner hours per week",
        min_value=0, max_value=168, step=5,
        value=data.get('owner_hours_per_week', 0)
    )
    data['owner_hours_per_week'] = owner_hours_per_week


def render_section_8_market():
    st.header("8. Capacity, Market & Competition")
    data = st.session_state.survey_data
    
    col1, col2 = st.columns(2)
    with col1:
        capacity_utilization = st.slider(
            "Capacity utilization (%)",
            0, 100, data.get('capacity_utilization', 70), 5
        )
        data['capacity_utilization'] = capacity_utilization
        
        has_waitlist = st.checkbox(
            "We have a waitlist",
            value=data.get('has_waitlist', False)
        )
        data['has_waitlist'] = has_waitlist
    
    with col2:
        crowding_options = ["Never an issue", "Rarely mentioned",
             "Sometimes complained about", "Frequent complaints"]
        _saved_crowding = data.get('peak_crowding', '')
        try:
            _crowding_index = crowding_options.index(_saved_crowding) if _saved_crowding else 0
        except ValueError:
            _crowding_index = 0
        
        peak_crowding = st.radio(
            "Peak hour crowding feedback:",
            crowding_options,
            index=_crowding_index
        )
        data['peak_crowding'] = peak_crowding
    
    if has_waitlist:
        st.write("**Waitlist details:**")
        col1, col2 = st.columns(2)
        with col1:
            waitlist_length = st.number_input(
                "People on waitlist",
                min_value=0, max_value=500, step=1,
                value=data.get('waitlist_length', 0)
            )
            data['waitlist_length'] = waitlist_length
        with col2:
            waitlist_avg_wait_weeks = st.number_input(
                "Avg wait time (weeks)",
                min_value=0, max_value=104, step=1,
                value=data.get('waitlist_avg_wait_weeks', 0)
            )
            data['waitlist_avg_wait_weeks'] = waitlist_avg_wait_weeks
    
    if has_waitlist and data.get('waitlist_length', 0) > 0:
        waitlist_conversion = st.number_input(
            "Waitlist conversion rate (%)",
            min_value=0, max_value=100, step=5,
            value=data.get('waitlist_conversion', 0),
            help="What % of waitlisted people eventually join?"
        )
        data['waitlist_conversion'] = waitlist_conversion
    
    st.markdown("---")
    st.subheader("Competition")
    
    col1, col2 = st.columns(2)
    with col1:
        competing_studios = st.number_input(
            "Competing studios within 20 miles",
            min_value=0, max_value=50, step=1,
            value=data.get('competing_studios', 0)
        )
        data['competing_studios'] = competing_studios
        
        pricing_options = ["Don't know/No competitors", "Significantly lower",
             "Somewhat lower", "About the same", "Somewhat higher",
             "Significantly higher"]
        _saved_pricing = data.get('pricing_vs_competitors', '')
        try:
            _pricing_index = pricing_options.index(_saved_pricing) if _saved_pricing else 0
        except ValueError:
            _pricing_index = 0
        
        pricing_vs_competitors = st.radio(
            "Your pricing vs competitors",
            pricing_options,
            index=_pricing_index
        )
        data['pricing_vs_competitors'] = pricing_vs_competitors
    
    with col2:
        population_options = ["Under 10,000", "10,000-50,000", "50,000-100,000",
             "100,000-250,000", "250,000-500,000", "Over 500,000"]
        _saved_population = data.get('market_population', 'Under 10,000')
        try:
            _population_index = population_options.index(_saved_population) if _saved_population else 0
        except ValueError:
            _population_index = 0
        
        market_population = st.selectbox(
            "Population within 10 miles",
            population_options,
            index=_population_index
        )
        data['market_population'] = market_population
        
        kiln_utilization = st.slider(
            "Kiln utilization (%)",
            0, 100, data.get('kiln_utilization', 70), 5
        )
        data['kiln_utilization'] = kiln_utilization


def render_section_9_growth():
    st.header("9. Growth Plans & Future")
    data = st.session_state.survey_data
    
    col1, col2 = st.columns(2)
    with col1:
        expand_options = ["No plans", "Considering", "Within 6 months",
             "Within 1 year", "Within 2 years"]
        _saved_expand = data.get('plans_expand_space', '')
        try:
            _expand_index = expand_options.index(_saved_expand) if _saved_expand else 0
        except ValueError:
            _expand_index = 0
        
        plans_expand_space = st.radio(
            "Plans to expand space?",
            expand_options,
            index=_expand_index
        )
        data['plans_expand_space'] = plans_expand_space
        
        plans_add_equipment = st.multiselect(
            "Plans to add equipment:",
            ["No plans", "Additional wheels", "Additional kiln(s)",
             "Slab roller", "Pug mill", "Extruder", "Other"],
            default=data.get('plans_add_equipment', [])
        )
        data['plans_add_equipment'] = plans_add_equipment
    
    with col2:
        raise_prices_options = ["No plans", "Within 3 months", "Within 6 months",
             "Within 1 year", "Unsure/as needed"]
        _saved_raise = data.get('plans_raise_prices', '')
        try:
            _raise_index = raise_prices_options.index(_saved_raise) if _saved_raise else 0
        except ValueError:
            _raise_index = 0
        
        plans_raise_prices = st.radio(
            "Plans to raise prices?",
            raise_prices_options,
            index=_raise_index
        )
        data['plans_raise_prices'] = plans_raise_prices
        
        target_member_count = st.number_input(
            "Target member capacity",
            min_value=0, max_value=1000, step=5,
            value=data.get('target_member_count', 0)
        )
        data['target_member_count'] = target_member_count


def render_section_10_challenges():
    st.header("10. Challenges & Risk Management")
    st.caption("Optional but valuable for understanding common issues")
    data = st.session_state.survey_data
    
    status_options = [
        "Currently operating sustainably",
        "Currently operating but struggling",
        "Closed/ceased operations",
        "Prefer not to say"
    ]
    _saved_status = data.get('studio_status', '')
    try:
        _status_index = status_options.index(_saved_status) if _saved_status else 0
    except ValueError:
        _status_index = 0
    
    studio_status = st.radio(
        "Studio status:",
        status_options,
        index=_status_index
    )
    data['studio_status'] = studio_status
    
    if studio_status == "Currently operating but struggling":
        struggle_areas = st.multiselect(
            "Current challenges:",
            ["Cash flow negative", "Member growth stalled",
             "High churn", "Equipment maintenance costs",
             "Staffing difficulties", "Marketing ineffective",
             "Pricing pressure", "Seasonal swings",
             "Rent increase concerns", "Owner compensation insufficient",
             "Other"],
            default=data.get('struggle_areas', [])
        )
        data['struggle_areas'] = struggle_areas
    
    if studio_status == "Closed/ceased operations":
        col1, col2 = st.columns(2)
        with col1:
            closure_options = ["N/A"] + list(range(2025, 2014, -1))
            _saved_closure = data.get('closure_year', 'N/A')
            # Handle both string and int saved values
            if isinstance(_saved_closure, int):
                _saved_closure = str(_saved_closure)
            try:
                _closure_index = closure_options.index(_saved_closure) if _saved_closure in [str(x) for x in closure_options] else 0
            except (ValueError, TypeError):
                _closure_index = 0
            
            closure_year = st.selectbox(
                "Year closed:",
                closure_options,
                index=_closure_index
            )
            data['closure_year'] = closure_year
        with col2:
            months_operated = st.number_input(
                "Months in operation:",
                min_value=0, max_value=240, step=1,
                value=data.get('months_operated', 0)
            )
            data['months_operated'] = months_operated
        
        closure_reasons = st.multiselect(
            "Reasons for closure:",
            ["Insufficient membership", "Rent increase",
             "Could not break even", "Owner burnout",
             "Lost lease", "COVID-19", "Inadequate capital",
             "Unexpected expense", "Competition", "Other"],
            default=data.get('closure_reasons', [])
        )
        data['closure_reasons'] = closure_reasons
    
    st.markdown("---")
    
    impact_options = ["Significantly positive", "Somewhat positive", "No impact",
         "Somewhat negative", "Significantly negative", "Too new"]
    _saved_impact = data.get('macro_impact', '')
    try:
        _impact_index = impact_options.index(_saved_impact) if _saved_impact else 0
    except ValueError:
        _impact_index = 0
    
    macro_impact = st.radio(
        "Economic impact (past 2 years):",
        impact_options,
        index=_impact_index
    )
    data['macro_impact'] = macro_impact
    
    liability_options = ["No insurance", "Under $500k", "$500k-$1M",
         "$1M-$2M", "$2M+", "Not sure"]
    _saved_liability = data.get('liability_coverage', 'No insurance')
    try:
        _liability_index = liability_options.index(_saved_liability) if _saved_liability else 0
    except ValueError:
        _liability_index = 0
    
    liability_coverage = st.selectbox(
        "Liability coverage amount",
        liability_options,
        index=_liability_index
    )
    data['liability_coverage'] = liability_coverage


def render_section_11_feedback():
    st.header("11. Help Us Improve This Survey")
    data = st.session_state.survey_data
    
    survey_feedback = st.text_area(
        "Feedback on this survey:",
        value=data.get('survey_feedback', ''),
        placeholder="Too long? Confusing? Missing topics?",
        height=100
    )
    data['survey_feedback'] = survey_feedback
    
    suggested_questions = st.text_area(
        "Questions we should ask:",
        value=data.get('suggested_questions', ''),
        placeholder="What are we missing?",
        height=100
    )
    data['suggested_questions'] = suggested_questions
    
    topics_interest = st.multiselect(
        "Topics needing more data:",
        ["Loan/financing", "Marketing effectiveness",
         "Retention tactics", "Seasonal patterns",
         "COVID recovery", "Insurance", "Equipment maintenance", "Other"],
        default=data.get('topics_interest', [])
    )
    data['topics_interest'] = topics_interest
    
    st.subheader("Future Follow-Up")
    
    followup_options = ["No thanks", "Maybe - occasional updates",
         "Yes - email in 6 months", "Yes - email in 12 months"]
    _saved_followup = data.get('followup', 'No thanks')
    try:
        _followup_index = followup_options.index(_saved_followup) if _saved_followup else 0
    except ValueError:
        _followup_index = 0
    
    followup = st.radio(
        "Update survey in 6-12 months?",
        followup_options,
        index=_followup_index
    )
    data['followup'] = followup
    
    if followup != "No thanks":
        followup_email = st.text_input(
            "Email (for survey updates only):",
            value=data.get('followup_email', '')
        )
        data['followup_email'] = followup_email


def render_results():
    from results import render_results as render_results_dashboard
    render_results_dashboard()


# def submit_survey():
#     data = st.session_state.survey_data
    
#     required_fields = {
#         'location_state': 'Location',
#         'space_sqft': 'Studio space',
#         'studio_type': 'Studio type',
#         'current_members': 'Current members',
#         'total_wheels': 'Total wheels',
#         'handbuilding_stations': 'Handbuilding stations',
#         'glazing_stations': 'Glazing stations',
#         'rent': 'Monthly rent',
#         'insurance': 'Monthly insurance'
#     }
    
#     errors = [name for field, name in required_fields.items() if not data.get(field)]
    
#     if errors:
#         st.error("Please complete required fields:")
#         for error in errors:
#             st.error(f"• {error}")
#         return
    
#     # Check if this is an update or new submission
#     is_update = st.session_state.get('is_update', False)
    
#     if is_update and data.get('_sheet_row'):
#         # Update existing response
#         if update_response(data):
#             response_id = data.get('response_id')  # Already exists from previous submission
#             st.success("Survey updated successfully!")
#             st.balloons()
            
#             st.info(f"""
#             **Your Response ID:** `{response_id}`
            
#             Your response has been updated. Keep this ID if you need to make future updates.
#             """)
            
#             st.code(response_id, language=None)
            
#             # Clear the update flag
#             st.session_state.is_update = False
            
#             if st.button("View Results Dashboard", type="primary"):
#                 st.session_state.page = 'results'
#                 st.rerun()
#         else:
#             st.error("Failed to update response. Please try again.")
#     else:
#         # New submission - response_id already generated in render_survey()
#         # Just use the existing one
#         response_id = data.get('response_id')
        
#         # Safety check: if somehow response_id doesn't exist, generate it
#         if not response_id:
#             response_id = str(uuid.uuid4())
#             data['response_id'] = response_id
#             data['studio_name'] = response_id[:4].upper()
        
#         if save_response(data):
#             st.success("Survey submitted!")
#             st.balloons()
            
#             st.info(f"""
#             **Your Response ID:** `{response_id}`
            
#             **Important:** Save this ID! You can use it to update your responses later as your studio evolves.
#             """)
            
#             # Show copyable code block
#             st.code(response_id, language=None)
            
#             if st.button("View Results Dashboard", type="primary"):
#                 st.session_state.page = 'results'
#                 st.rerun()

def submit_survey():
    """
    Enhanced submit with better duplicate prevention messaging
    """
    data = st.session_state.survey_data
    
    required_fields = {
        'location_state': 'Location',
        'space_sqft': 'Studio space',
        'studio_type': 'Studio type',
        'current_members': 'Current members',
        'total_wheels': 'Total wheels',
        'handbuilding_stations': 'Handbuilding stations',
        'glazing_stations': 'Glazing stations',
        'rent': 'Monthly rent',
        'insurance': 'Monthly insurance'
    }
    
    errors = [name for field, name in required_fields.items() if not data.get(field)]
    
    if errors:
        st.error("Please complete required fields:")
        for error in errors:
            st.error(f"• {error}")
        return
    
    # Check if this is an update or new submission
    is_update = st.session_state.get('is_update', False)
    
    # For new submissions, response_id already generated in render_survey()
    response_id = data.get('response_id')
    
    # Safety check
    if not response_id:
        response_id = str(uuid.uuid4())
        data['response_id'] = response_id
        data['studio_name'] = response_id[:4].upper()
    
    # Save (function will handle update vs new internally)
    if save_response(data):
        st.success("Survey submitted successfully!" if not is_update else "Survey updated successfully!")
        st.balloons()
        
        st.info(f"""
        **Your Response ID:** `{response_id}`
        
        {"Your response has been updated." if is_update else "**Important:** Save this ID! You can use it to update your responses later as your studio evolves."}
        """)
        
        st.code(response_id, language=None)
        
        # Clear the update flag
        if is_update:
            st.session_state.is_update = False
        
        if st.button("View Results Dashboard", type="primary"):
            st.session_state.page = 'results'
            st.rerun()
    else:
        st.error("Failed to save response. Please try again or contact support.")

def main():
    with st.sidebar:
        st.title("Navigation")
        if st.button("🏠 Home"):
            st.session_state.page = 'intro'
            st.rerun()
        if st.button("📝 Survey"):
            st.session_state.page = 'survey'
            st.rerun()
        if st.button("📊 Results"):
            st.session_state.page = 'results'
            st.rerun()
    
    if st.session_state.page == 'intro':
        render_intro()
    elif st.session_state.page == 'survey':
        render_survey()
    elif st.session_state.page == 'results':
        render_results()


if __name__ == "__main__":
    main()           