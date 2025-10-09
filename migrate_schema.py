#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 13:13:49 2025

@author: harshadghodke
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration Script: Add International Support Fields
Migrates existing survey responses to new schema with country/currency/metric fields
"""

import pandas as pd
import json
from datetime import datetime

def migrate_schema(input_csv_path, output_csv_path):
    """
    Migrate existing responses to new schema with international fields.
    
    Args:
        input_csv_path: Path to downloaded Google Sheet CSV
        output_csv_path: Path to save migrated CSV (upload this back to Sheets)
    """
    
    print(f"📥 Loading existing data from: {input_csv_path}")
    df = pd.read_csv(input_csv_path)
    
    print(f"   Found {len(df)} existing responses")
    print(f"   Current columns: {len(df.columns)}")
    
    # Backup original data
    backup_path = input_csv_path.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    df.to_csv(backup_path, index=False)
    print(f"💾 Backup saved to: {backup_path}")
    
    # === ADD NEW COLUMNS ===
    
    # 1. Country (default to United States for existing responses)
    if 'country' not in df.columns:
        df.insert(3, 'country', 'United States')  # Insert after submitted_at
        print("   ✅ Added 'country' column (defaulted to 'United States')")
    
    # 2. Currency (default to USD)
    if 'currency' not in df.columns:
        df.insert(4, 'currency', 'USD')
        print("   ✅ Added 'currency' column (defaulted to 'USD')")
    
    # 3. Uses metric (default to False for US)
    if 'uses_metric' not in df.columns:
        df.insert(5, 'uses_metric', False)
        print("   ✅ Added 'uses_metric' column (defaulted to False)")
    
    # 4. Space in square meters (calculate from existing sqft)
    if 'space_sqm' not in df.columns:
        # Find where space_sqft column is
        sqft_col_idx = df.columns.get_loc('space_sqft')
        
        # Convert sqft to sqm (1 sqft = 0.092903 sqm)
        df['space_sqm'] = df['space_sqft'].apply(
            lambda x: round(float(x) / 10.764) if pd.notna(x) and str(x).strip() != '' else ''
        )
        
        # Insert space_sqm right after space_sqft
        space_sqm_col = df.pop('space_sqm')
        df.insert(sqft_col_idx + 1, 'space_sqm', space_sqm_col)
        print("   ✅ Added 'space_sqm' column (converted from space_sqft)")
    
    # === DATA VALIDATION ===
    
    print("\n🔍 Validating migrated data:")
    
    # Check for any responses with missing response_id
    missing_ids = df['response_id'].isna().sum()
    if missing_ids > 0:
        print(f"   ⚠️  Warning: {missing_ids} rows have missing response_id")
    
    # Check for duplicates
    duplicates = df['response_id'].duplicated().sum()
    if duplicates > 0:
        print(f"   ⚠️  Warning: {duplicates} duplicate response_ids found")
        print("      (These will be handled by the deduplication logic in results.py)")
    
    # Verify new columns exist and have data
    new_cols = ['country', 'currency', 'uses_metric', 'space_sqm']
    for col in new_cols:
        non_empty = df[col].notna().sum()
        print(f"   ✓ {col}: {non_empty}/{len(df)} rows populated")
    
    # === SAVE MIGRATED DATA ===
    
    df.to_csv(output_csv_path, index=False)
    print(f"\n💾 Migrated data saved to: {output_csv_path}")
    print(f"   Total columns: {len(df.columns)} (was {len(pd.read_csv(input_csv_path).columns)})")
    print(f"   Total rows: {len(df)}")
    
    # === GENERATE MIGRATION REPORT ===
    
    print("\n" + "="*60)
    print("MIGRATION REPORT")
    print("="*60)
    print(f"Input file:  {input_csv_path}")
    print(f"Output file: {output_csv_path}")
    print(f"Backup file: {backup_path}")
    print(f"\nChanges:")
    print(f"  - Added 'country' column (default: United States)")
    print(f"  - Added 'currency' column (default: USD)")
    print(f"  - Added 'uses_metric' column (default: False)")
    print(f"  - Added 'space_sqm' column (converted from space_sqft)")
    print(f"\nData integrity:")
    print(f"  - Rows before: {len(df)}")
    print(f"  - Rows after:  {len(df)}")
    print(f"  - No data lost: {'✓' if len(df) == len(pd.read_csv(input_csv_path)) else '✗'}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Review the migrated CSV file")
    print("2. Upload to Google Sheets:")
    print("   - Open your Google Sheet")
    print("   - File > Import > Upload")
    print("   - Select 'Replace current sheet'")
    print(f"   - Upload: {output_csv_path}")
    print("3. Deploy updated app.py with international support")
    print("4. Test with a new submission to verify schema works")
    print("="*60)
    
    return df


def preview_migration(input_csv_path):
    """
    Preview what the migration would do without actually doing it.
    """
    print("🔍 MIGRATION PREVIEW (no files will be modified)")
    print("="*60)
    
    df = pd.read_csv(input_csv_path)
    
    print(f"\nCurrent data:")
    print(f"  - Rows: {len(df)}")
    print(f"  - Columns: {len(df.columns)}")
    
    # Show sample of current data
    print(f"\nFirst row sample (first 10 columns):")
    if len(df) > 0:
        first_row = df.iloc[0].head(10)
        for col, val in first_row.items():
            print(f"  {col}: {val}")
    
    print("\nNew columns that will be added:")
    print("  1. country → 'United States' (default)")
    print("  2. currency → 'USD' (default)")
    print("  3. uses_metric → False (default)")
    print("  4. space_sqm → calculated from space_sqft")
    
    if 'space_sqft' in df.columns and len(df) > 0:
        sample_sqft = df['space_sqft'].iloc[0]
        if pd.notna(sample_sqft) and str(sample_sqft).strip() != '':
            sample_sqm = round(float(sample_sqft) / 10.764)
            print(f"\nExample conversion:")
            print(f"  space_sqft: {sample_sqft} → space_sqm: {sample_sqm}")
    
    print("\n" + "="*60)
    print("To run the actual migration, use:")
    print("  migrate_schema('input.csv', 'output_migrated.csv')")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("POTTERY STUDIO SURVEY - SCHEMA MIGRATION")
    print("="*60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate_schema.py <input_csv> [output_csv]")
        print()
        print("Example:")
        print("  python migrate_schema.py survey_responses.csv survey_responses_migrated.csv")
        print()
        print("Or for preview only:")
        print("  python migrate_schema.py preview <input_csv>")
        sys.exit(1)
    
    if sys.argv[1] == "preview" and len(sys.argv) >= 3:
        # Preview mode
        preview_migration(sys.argv[2])
    else:
        # Migration mode
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) >= 3 else input_file.replace('.csv', '_migrated.csv')
        
        print(f"Input:  {input_file}")
        print(f"Output: {output_file}")
        print()
        
        # Confirm before proceeding
        response = input("Proceed with migration? (yes/no): ").lower().strip()
        
        if response == 'yes':
            migrated_df = migrate_schema(input_file, output_file)
            print("\n✅ Migration complete!")
        else:
            print("\n❌ Migration cancelled")