
"""
results.py - HARDENED VERSION
Results Dashboard with deduplication and validation
"""

import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json

from results_free_enhanced import show_enhanced_charts
from results_free import show_free_charts, derive_kpis

@st.cache_data(ttl=900)  # Cache for 15 minutes
def load_responses():
    """
    Load survey responses from Google Sheets with deduplication and validation.
    
    Deduplication strategy:
    1. Group by response_id
    2. Keep only the most recent submission (by submitted_at timestamp)
    3. Remove any rows with missing response_id
    """
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheet_id = st.secrets["sheet_id"]

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1"
        ).execute()

        values = result.get("values", [])
        if not values or len(values) < 2:
            return pd.DataFrame()

        header = values[0]
        width = len(header)

        # Normalize row widths - pad short rows, trim long rows
        normalized = []
        for row in values[1:]:
            row = list(row)
            if len(row) < width:
                row += [""] * (width - len(row))
            elif len(row) > width:
                row = row[:width]
            normalized.append(row)

        df = pd.DataFrame(normalized, columns=header)
        
        # --- Normalize mixed-type columns to fix Arrow serialization ---
        
        def _jsonify_if_collection(x):
            """Convert lists/dicts into JSON strings for stable serialization."""
            if isinstance(x, (list, dict)):
                try:
                    return json.dumps(x)
                except Exception:
                    return str(x)
            return x
        
        # Normalize known multi-type columns before caching/display
        for col in ["kilns", "wheel_inventory", "included_amenities", "event_types"]:
            if col in df.columns:
                df[col] = df[col].map(_jsonify_if_collection)
        
        # === DEDUPLICATION LOGIC ===
        
        # Track original count
        original_count = len(df)
        
        # Remove rows with no response_id
        if 'response_id' in df.columns:
            df = df[df['response_id'].notna() & (df['response_id'] != '')]
            missing_id_count = original_count - len(df)
            
            if missing_id_count > 0:
                st.warning(f"Removed {missing_id_count} rows with missing response_id")
        else:
            st.error("Critical: 'response_id' column not found in data!")
            return pd.DataFrame()
        
        # Parse submitted_at timestamps for sorting
        if 'submitted_at' in df.columns:
            df['_timestamp'] = pd.to_datetime(df['submitted_at'], errors='coerce')
        else:
            # If no timestamp, use row order (later = more recent)
            df['_timestamp'] = pd.to_datetime('now')
        
        # Sort by timestamp (most recent last) and drop duplicates keeping last
        df = df.sort_values('_timestamp')
        
        # Check for duplicates before removing
        duplicate_count = df.duplicated(subset=['response_id'], keep='last').sum()
        
        if duplicate_count > 0:
            st.info(f"Found and removed {duplicate_count} duplicate submissions (kept most recent)")
        
        # Keep only the most recent submission for each response_id
        df = df.drop_duplicates(subset=['response_id'], keep='last')
        
        # Drop temporary timestamp column
        df = df.drop('_timestamp', axis=1)
        
        final_count = len(df)
        
        # Show deduplication summary
        if original_count != final_count:
            st.caption(f"Data loaded: {original_count} rows → {final_count} unique responses")
        
        return df

    except Exception as e:
        st.error(f"Failed to load survey data: {e}")
        return pd.DataFrame()


def validate_data_quality(df: pd.DataFrame) -> dict:
    """
    Perform data quality checks and return metrics.
    """
    issues = {
        'total_rows': len(df),
        'missing_required_fields': {},
        'invalid_values': {},
        'warnings': []
    }
    
    # Check required fields
    required_fields = [
        'response_id', 'location_state', 'space_sqft', 
        'studio_type', 'current_members', 'total_wheels'
    ]
    
    for field in required_fields:
        if field in df.columns:
            missing = df[field].isna().sum() + (df[field] == '').sum()
            if missing > 0:
                issues['missing_required_fields'][field] = missing
    
    # Check for impossible values
    numeric_checks = {
        'space_sqft': (100, 50000),
        'current_members': (0, 1000),
        'total_wheels': (0, 100),
        'rent': (0, 50000)
    }
    
    for field, (min_val, max_val) in numeric_checks.items():
        if field in df.columns:
            df_numeric = pd.to_numeric(df[field], errors='coerce')
            invalid = ((df_numeric < min_val) | (df_numeric > max_val)).sum()
            if invalid > 0:
                issues['invalid_values'][field] = invalid
    
    return issues

def render_results():
    """Main results dashboard with simple country filtering"""
    
    st.title("Pottery Studio Survey Results")
    
    # Load data with deduplication
    with st.spinner("Loading and validating survey responses..."):
        df = load_responses()
    
    if df.empty:
        st.warning("No survey responses available yet. Be the first to submit!")
        if st.button("Take the Survey"):
            st.session_state.page = 'survey'
            st.rerun()
        return
    
    # Derive KPIs
    df = derive_kpis(df)
    
    # === COUNTRY FILTER (SIMPLE) ===
    
    if 'country' in df.columns and df['country'].notna().any():
        country_counts = df['country'].value_counts()
        
        # Show filter if we have any data
        st.subheader("🌍 Filter by Country")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            country_options = ["All Countries"] + sorted(country_counts.index.tolist())
            default_index = country_options.index("United States") if "United States" in country_options else 0

            selected_country = st.selectbox(
                "View data from:",
                options=country_options,
                index=default_index,
                help="Filter results to studios in a specific country"
            )
        
        with col2:
            # Show what countries we have (support older Streamlit without popover)
            if hasattr(st, "popover"):
                with st.popover("📊 Available Data"):
                    st.write("**Responses by country:**")
                    for country, count in country_counts.items():
                        st.write(f"• {country}: {count}")
            else:
                with st.expander("📊 Available Data", expanded=False):
                    st.write("**Responses by country:**")
                    for country, count in country_counts.items():
                        st.write(f"• {country}: {count}")        
 
        # Apply filter
        if selected_country != "All Countries":
            df = df[df['country'] == selected_country]
            
            # Show sample size warning if needed
            if len(df) < 5:
                st.warning(f"⚠️ Only {len(df)} studio(s) from {selected_country}. Results may not be representative.")
            elif len(df) < 10:
                st.info(f"ℹ️ {len(df)} studios from {selected_country}. More responses will improve accuracy.")
        
        st.markdown("---")
    
    # Show success message with count
    st.success(f"✓ Showing {len(df)} unique survey responses")
    
    # Show data quality metrics
    with st.expander("📊 Data Quality Metrics"):
        quality = validate_data_quality(df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Responses", quality['total_rows'])
        with col2:
            total_missing = sum(quality['missing_required_fields'].values())
            st.metric("Missing Required Fields", total_missing)
        with col3:
            total_invalid = sum(quality['invalid_values'].values())
            st.metric("Invalid Values", total_invalid)
        
        if quality['missing_required_fields']:
            st.caption("**Missing required field counts:**")
            for field, count in quality['missing_required_fields'].items():
                st.caption(f"• {field}: {count} responses")
        
        if quality['invalid_values']:
            st.caption("**Out-of-range value counts:**")
            for field, count in quality['invalid_values'].items():
                st.caption(f"• {field}: {count} responses")
    
    # Refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Your existing visualizations (now with filtered df)
    # show_free_charts(df)
    show_enhanced_charts(df)
    
    st.markdown("---")
    



if __name__ == "__main__":
    render_results()