import os
import sys
import django
import pandas as pd
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TechnikNet_system.settings')
django.setup()

from properties.models import Property, Team
from django.utils import timezone

def clean_str(value):
    """Convert value to string, return empty string if None/NaN"""
    if value is None or value == '':
        return ''
    if pd.isna(value):
        return ''
    return str(value).strip()

def parse_datetime(date_str):
    """Parse datetime, return None if invalid/empty"""
    if date_str is None or date_str == '':
        return None
    if pd.isna(date_str):
        return None
    try:
        if isinstance(date_str, str):
            if not date_str.strip():
                return None
            dt = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
        elif hasattr(date_str, 'to_pydatetime'):
            dt = date_str.to_pydatetime()
        else:
            return None
        # Make timezone aware
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt
    except:
        return None

def safe_get(row, column_name, df_columns, default=''):
    """Safely get column value even if column doesn't exist"""
    if column_name not in df_columns:
        return default
    value = row.get(column_name, default)
    if pd.isna(value) or value == '':
        return default
    return value

def safe_int(value, default=None):
    """Safely convert to integer, return default if empty/invalid"""
    if value is None or value == '':
        return default
    if pd.isna(value):
        return default
    try:
        str_val = str(value).strip().lower()
        if str_val in ['', 'nan', 'none', 'null']:
            return default
        return int(float(value))
    except:
        return default

def import_excel(file_path, default_team=None):
    """Import Excel data with support for empty columns"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"📂 Reading Excel file: {file_path}")
    df = pd.read_excel(file_path)

    print(f"📊 Found {len(df)} rows")
    print(f"📊 Columns: {df.columns.tolist()}")

    # Clean data - only fill NaN values
    df = df.fillna('')
    
    # Get default team for assignment
    team = None
    if default_team:
        try:
            team = Team.objects.get(name=default_team)
            print(f"✅ Will assign properties to team: {team.name}")
        except Team.DoesNotExist:
            print(f"⚠️  Team '{default_team}' not found. Properties will be created without team assignment.")

    success_count = 0
    error_count = 0
    df_columns = df.columns.tolist()

    for idx, row in df.iterrows():
        try:
            # Get Number field (required - only mandatory field)
            number = clean_str(safe_get(row, 'Number', df_columns, ''))
            if not number:
                print(f"❌ Row {idx+2}: Missing 'Number' field (required)")
                error_count += 1
                continue
            
            # Prepare property data - all fields are optional except Number
            property_data = {
                'address_id': clean_str(safe_get(row, 'Address ID', df_columns, '')),
                'village': clean_str(safe_get(row, 'Village', df_columns, '')),
                'street': clean_str(safe_get(row, 'Street', df_columns, '')),
                'house_number': clean_str(safe_get(row, 'House number', df_columns, '')),
                'house_number_affix': clean_str(safe_get(row, 'House number affix', df_columns, '')),
                'owner_email': clean_str(safe_get(row, 'Owner email', df_columns, '')),
                'owner_name': clean_str(safe_get(row, 'Owner name', df_columns, '')),
                'owner_surname': clean_str(safe_get(row, 'Owner surname', df_columns, '')),
                'owner_phone_1': clean_str(safe_get(row, 'Owner phone 1', df_columns, '')),
                'owner_phone_2': clean_str(safe_get(row, 'Owner phone 2', df_columns, '')),
                'pop_code': clean_str(safe_get(row, 'PoP code', df_columns, '')),
                'gebaute_units': safe_int(safe_get(row, 'Gebaute Units', df_columns), None),
                'hbg': clean_str(safe_get(row, 'HBG', df_columns, '')),
                'hbg_termin': parse_datetime(safe_get(row, 'HBG Termin', df_columns)),
                'ausbau_termin': parse_datetime(safe_get(row, 'Ausbau Termin', df_columns)),
                'kl_15m': safe_int(safe_get(row, 'K.L 15M', df_columns), 0),
                'kl_20m': safe_int(safe_get(row, 'K.L 20M', df_columns), 0),
                'kl_30m': safe_int(safe_get(row, 'K.L 30M', df_columns), 0),
                'kl_50m': safe_int(safe_get(row, 'K.L 50M', df_columns), 0),
                'kl_80m': safe_int(safe_get(row, 'K.L 80M', df_columns), 0),
                'kl_100m': safe_int(safe_get(row, 'K.L 100M', df_columns), 0),
                'keller': clean_str(safe_get(row, 'keller', df_columns, '')),
                'huep': clean_str(safe_get(row, 'HÜP', df_columns, '')),
                'spleissen': clean_str(safe_get(row, 'spleissen', df_columns, '')),
                'ohne_infra': safe_int(safe_get(row, 'ohne Infra', df_columns), 0),
                'mit_infra': safe_int(safe_get(row, 'mit Infra', df_columns), 0),
                'status': clean_str(safe_get(row, 'Status', df_columns, '')),
                'comments': clean_str(safe_get(row, 'Comments', df_columns, '')),
            }
            
            # Create or update property
            property_obj, created = Property.objects.update_or_create(
                number=number,
                defaults=property_data
            )

            # Assign teams from Excel column or default team
            team_names_str = clean_str(safe_get(row, 'Team', df_columns, ''))
            teams_assigned = []
            
            if team_names_str:
                # Clear existing teams first for updates
                if not created:
                    property_obj.teams.clear()
                
                # Split by comma and find teams
                team_names = [name.strip() for name in team_names_str.split(',') if name.strip()]
                for team_name in team_names:
                    try:
                        team_obj = Team.objects.get(name=team_name)
                        property_obj.teams.add(team_obj)
                        teams_assigned.append(team_name)
                    except Team.DoesNotExist:
                        print(f"  ⚠️  Team '{team_name}' not found")
            
            elif team and created:
                # Use default team only for new properties
                property_obj.teams.add(team)
                teams_assigned.append(team.name)

            # Success message
            action = "Created" if created else "Updated"
            team_info = f" → Teams: {', '.join(teams_assigned)}" if teams_assigned else ""
            print(f"✅ Row {idx+2}: {action} property '{number}'{team_info}")
            success_count += 1

        except Exception as e:
            print(f"❌ Error at row {idx+2} (Number: {number if 'number' in locals() else 'Unknown'}): {str(e)}")
            error_count += 1
            import traceback
            traceback.print_exc()

    print(f"\n{'='*50}")
    print(f"✅ Successfully imported: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*50}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("╔════════════════════════════════════════════════════╗")
        print("║        TechnikNet Excel Import Tool               ║")
        print("╚════════════════════════════════════════════════════╝")
        print()
        print("Usage: python import_excel.py <excel_file.xlsx> [team_name]")
        print()
        print("Examples:")
        print("  python import_excel.py data.xlsx")
        print("  python import_excel.py data.xlsx 'Team Alpha'")
        print()
        print("📋 Available teams:")
        teams = Team.objects.all()
        if teams.exists():
            for team in teams:
                print(f"  • {team.name}")
        else:
            print("  (No teams available)")
        print()
        print("📌 Notes:")
        print("  • Only 'Number' column is required")
        print("  • All other columns are optional (can be empty)")
        print("  • Column order doesn't matter - system reads by column name")
        print("  • Use 'Team' column in Excel to assign teams (comma-separated)")
        print()
        sys.exit(1)

    file_path = sys.argv[1]
    team_name = sys.argv[2] if len(sys.argv) > 2 else None

    import_excel(file_path, team_name)
