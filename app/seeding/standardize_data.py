import random
from app import db
from app.models.phone import Phone
from app.models.issue import Issue, Symptom
from app.models.repair import Repair
from app.models.rule import Rule
import json

# Removed clear_data() function

def seed_data():
    """Seeds the database with standardized data."""
    
    # Removed call to clear_data()
    
    # 1. EXPANDED ISSUES (30 total)
    issues_data = [
        # Audio (4)
        {'category': 'Audio', 'name': 'Distorted Speaker Sound', 'severity': 'Medium', 'code': 'speaker_distorted'},
        {'category': 'Audio', 'name': 'No Sound from Speaker', 'severity': 'Medium', 'code': 'speaker_no_sound'},
        {'category': 'Audio', 'name': 'Microphone Not Working', 'severity': 'Medium', 'code': 'microphone_not_working'},
        {'category': 'Audio', 'name': 'Earpiece Speaker Low Volume', 'severity': 'Low', 'code': 'earpiece_low_volume'},

        # Battery (5)
        {'category': 'Battery', 'name': 'Battery Degradation', 'severity': 'Medium', 'code': 'battery_degradation'},
        {'category': 'Battery', 'name': 'Battery Swelling', 'severity': 'Critical', 'code': 'battery_swelling'},
        {'category': 'Battery', 'name': 'Battery Draining Quickly', 'severity': 'Medium', 'code': 'battery_draining'},
        {'category': 'Battery', 'name': 'Phone Not Charging', 'severity': 'High', 'code': 'phone_not_charging'},
        {'category': 'Battery', 'name': 'Phone Won\'t Turn On', 'severity': 'Critical', 'code': 'phone_not_turning_on'},

        # Camera (4)
        {'category': 'Camera', 'name': 'Front Camera Not Working', 'severity': 'Medium', 'code': 'front_camera_not_working'},
        {'category': 'Camera', 'name': 'Rear Camera Not Working', 'severity': 'Medium', 'code': 'rear_camera_not_working'},
        {'category': 'Camera', 'name': 'Blurry Photos', 'severity': 'Low', 'code': 'blurry_photos'},
        {'category': 'Camera', 'name': 'Camera App Crashing', 'severity': 'Medium', 'code': 'camera_app_crashing'},

        # Charging (2)
        {'category': 'Charging', 'name': 'Charging Port Issue', 'severity': 'High', 'code': 'charging_port_issue'},
        {'category': 'Charging', 'name': 'Wireless Charging Not Working', 'severity': 'Medium', 'code': 'wireless_charging_issue'},

        # Connectivity (5)
        {'category': 'Connectivity', 'name': 'Wi-Fi Not Connecting', 'severity': 'Medium', 'code': 'wifi_not_connecting'},
        {'category': 'Connectivity', 'name': 'Bluetooth Not Working', 'severity': 'Low', 'code': 'bluetooth_not_working'},
        {'category': 'Connectivity', 'name': 'Cellular Signal Drop', 'severity': 'High', 'code': 'cellular_signal_drop'},
        {'category': 'Connectivity', 'name': 'GPS Not Accurate', 'severity': 'Medium', 'code': 'gps_inaccurate'},
        {'category': 'Connectivity', 'name': 'NFC Not Working', 'severity': 'Low', 'code': 'nfc_not_working'},
        
        # Screen (5)
        {'category': 'Screen', 'name': 'Glass Damage', 'severity': 'Medium', 'code': 'glass_damage'},
        {'category': 'Screen', 'name': 'LCD Damage', 'severity': 'High', 'code': 'lcd_damage'},
        {'category': 'Screen', 'name': 'Touchscreen Unresponsive', 'severity': 'High', 'code': 'touchscreen_unresponsive'},
        {'category': 'Screen', 'name': 'Dead Pixels', 'severity': 'Low', 'code': 'dead_pixels'},
        {'category': 'Screen', 'name': 'Screen Flickering', 'severity': 'Medium', 'code': 'screen_flickering'},

        # Software (3)
        {'category': 'Software', 'name': 'Apps Crashing', 'severity': 'Medium', 'code': 'apps_crashing'},
        {'category': 'Software', 'name': 'Phone Running Slow', 'severity': 'Low', 'code': 'phone_running_slow'},
        {'category': 'Software', 'name': 'Operating System Boot Loop', 'severity': 'High', 'code': 'os_boot_loop'},

        # Physical/Mechanical (2)
        {'category': 'Physical', 'name': 'Button Not Working', 'severity': 'Low', 'code': 'button_not_working'},
        {'category': 'Physical', 'name': 'Liquid Damage', 'severity': 'Critical', 'code': 'liquid_damage'},
    ]

    phones = Phone.query.all()
    for data in issues_data:
        # Attach a phone to each standardized issue when possible so the admin UI shows a related phone
        phone_id = random.choice(phones).id if phones else None
        issue = Issue(
            phone_id=phone_id,
            category=data['category'],
            name=data['name'],
            description=data['name'],
            severity=data['severity'],
            code=data['code']
        )
        db.session.add(issue)
    db.session.commit()
    print(f"Seeded {len(issues_data)} Issues.")

    # 2. EXPANDED SYMPTOMS and MAPPING (30 total)
    symptoms_map = {
        # Screen
        'screen_cracked': 'glass_damage',
        'screen_black': 'lcd_damage',
        'touch_not_working': 'touchscreen_unresponsive',
        'visible_lines_on_screen': 'lcd_damage',
        'screen_flickers': 'screen_flickering',
        'dead_spots_on_screen': 'dead_pixels',
        
        # Battery & Charging
        'battery_draining_fast': 'battery_draining',
        'phone_not_charging': 'phone_not_charging',
        'phone_overheating_while_charging': 'battery_degradation',
        'battery_looks_swollen': 'battery_swelling',
        'phone_wont_power_on': 'phone_not_turning_on',
        'wireless_charging_fails': 'wireless_charging_issue',
        'charging_port_loose': 'charging_port_issue',

        # Audio
        'callers_cant_hear_me': 'microphone_not_working',
        'earpiece_volume_is_too_low': 'earpiece_low_volume',
        'speaker_makes_crackling_noise': 'speaker_distorted',
        'no_sound_from_videos_or_music': 'speaker_no_sound',

        # Camera
        'front_camera_is_black': 'front_camera_not_working',
        'rear_camera_shows_black_screen': 'rear_camera_not_working',
        'photos_are_out_of_focus': 'blurry_photos',
        'camera_app_closes_unexpectedly': 'camera_app_crashing',

        # Connectivity
        'wifi_disconnects_frequently': 'wifi_not_connecting',
        'bluetooth_headset_wont_connect': 'bluetooth_not_working',
        'calls_drop_unexpectedly': 'cellular_signal_drop',
        'gps_location_is_wrong': 'gps_inaccurate',
        'cant_make_contactless_payments': 'nfc_not_working',

        # Software & Performance
        'apps_close_on_their_own': 'apps_crashing',
        'phone_is_very_slow_and_laggy': 'phone_running_slow',
        'phone_keeps_restarting': 'os_boot_loop',
        
        # Physical
        'power_button_stuck': 'button_not_working',
        'phone_fell_in_water': 'liquid_damage',
    }

    for symptom_code, issue_code in symptoms_map.items():
        issue_info = next((item for item in issues_data if item["code"] == issue_code), None)
        if not issue_info:
            print(f"Warning: Issue code '{issue_code}' not found for symptom '{symptom_code}'. Skipping.")
            continue

        issue = Issue.query.filter_by(code=issue_info['code']).first() # Filter by code
        if not issue:
            print(f"Warning: Issue '{issue_info['name']}' not found in DB. Skipping symptom mapping.")
            continue
        
        symptom = Symptom.query.filter_by(code=symptom_code).first()
        if not symptom:
            symptom = Symptom(
                code=symptom_code,
                description=symptom_code.replace('_', ' ').capitalize(),
                question=f"Is your phone experiencing: {symptom_code.replace('_', ' ')}?"
            )
            db.session.add(symptom)
        
        if symptom not in issue.symptoms:
            issue.symptoms.append(symptom)

    db.session.commit()
    print(f"Seeded {len(symptoms_map)} Symptoms and established Issue-Symptom relationships.")

    # 3. EXPANDED AND DETAILED REPAIRS (30 total)
    repairs_data = [
        # Critical Priority
        {'issue_code': 'battery_swelling', 'solution': 'Immediate Battery Replacement', 'priority': 1, 'estimated_cost_min': 70, 'estimated_cost_max': 150, 'estimated_time_hours': 1, 'difficulty': 'Medium', 'parts_needed': 'New Battery', 'tools_needed': 'Pentalobe Screwdriver, Suction Cup, Plastic Prying Tool', 'warranty_affected': True},
        {'issue_code': 'phone_not_turning_on', 'solution': 'Battery and Power System Diagnosis', 'priority': 1, 'estimated_cost_min': 50, 'estimated_cost_max': 200, 'estimated_time_hours': 2, 'difficulty': 'High', 'parts_needed': 'Varies (Battery, Charging Port, Logic Board)', 'tools_needed': 'Multimeter, Screwdriver Kit, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'liquid_damage', 'solution': 'Full Liquid Damage Treatment', 'priority': 1, 'estimated_cost_min': 100, 'estimated_cost_max': 500, 'estimated_time_hours': 4, 'difficulty': 'High', 'parts_needed': 'Varies, Isopropyl Alcohol', 'tools_needed': 'Ultrasonic Cleaner, Microscope, Screwdriver Kit', 'warranty_affected': True},

        # High Priority
        {'issue_code': 'phone_not_charging', 'solution': 'Charging Port Replacement', 'priority': 2, 'estimated_cost_min': 60, 'estimated_cost_max': 120, 'estimated_time_hours': 1.5, 'difficulty': 'Medium', 'parts_needed': 'Charging Port Assembly', 'tools_needed': 'Soldering Iron, Screwdriver Kit, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'lcd_damage', 'solution': 'Screen Assembly Replacement', 'priority': 2, 'estimated_cost_min': 150, 'estimated_cost_max': 400, 'estimated_time_hours': 2, 'difficulty': 'Medium', 'parts_needed': 'Screen Assembly', 'tools_needed': 'Heat Gun, Pentalobe Screwdriver, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'touchscreen_unresponsive', 'solution': 'Screen and Digitizer Replacement', 'priority': 2, 'estimated_cost_min': 150, 'estimated_cost_max': 400, 'estimated_time_hours': 2, 'difficulty': 'Medium', 'parts_needed': 'Screen and Digitizer Assembly', 'tools_needed': 'Heat Gun, Pentalobe Screwdriver, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'cellular_signal_drop', 'solution': 'Antenna and Modem Check', 'priority': 2, 'estimated_cost_min': 80, 'estimated_cost_max': 250, 'estimated_time_hours': 2.5, 'difficulty': 'High', 'parts_needed': 'Antenna Flex Cable (if needed)', 'tools_needed': 'Signal Analyzer, Screwdriver Kit', 'warranty_affected': True},
        {'issue_code': 'os_boot_loop', 'solution': 'Software Re-flash', 'priority': 2, 'estimated_cost_min': 50, 'estimated_cost_max': 100, 'estimated_time_hours': 1, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'Computer, USB Cable', 'warranty_affected': False},
        {'issue_code': 'charging_port_issue', 'solution': 'Charging Port Repair or Replacement', 'priority': 2, 'estimated_cost_min': 60, 'estimated_cost_max': 120, 'estimated_time_hours': 1.5, 'difficulty': 'Medium', 'parts_needed': 'Charging Port Assembly', 'tools_needed': 'Soldering Iron, Screwdriver Kit, Prying Tools', 'warranty_affected': True},

        # Medium Priority
        {'issue_code': 'speaker_distorted', 'solution': 'Speaker Module Cleaning or Replacement', 'priority': 3, 'estimated_cost_min': 40, 'estimated_cost_max': 80, 'estimated_time_hours': 1, 'difficulty': 'Low', 'parts_needed': 'Speaker Module (if needed)', 'tools_needed': 'Compressed Air, Prying Tools, Screwdriver', 'warranty_affected': True},
        {'issue_code': 'speaker_no_sound', 'solution': 'Speaker Module Replacement', 'priority': 3, 'estimated_cost_min': 50, 'estimated_cost_max': 100, 'estimated_time_hours': 1, 'difficulty': 'Low', 'parts_needed': 'Speaker Module', 'tools_needed': 'Screwdriver Kit, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'microphone_not_working', 'solution': 'Microphone Replacement', 'priority': 3, 'estimated_cost_min': 50, 'estimated_cost_max': 100, 'estimated_time_hours': 1.5, 'difficulty': 'Medium', 'parts_needed': 'Microphone Component', 'tools_needed': 'Soldering Iron, Screwdriver Kit', 'warranty_affected': True},
        {'issue_code': 'battery_degradation', 'solution': 'Battery Replacement', 'priority': 3, 'estimated_cost_min': 70, 'estimated_cost_max': 150, 'estimated_time_hours': 1, 'difficulty': 'Medium', 'parts_needed': 'New Battery', 'tools_needed': 'Pentalobe Screwdriver, Suction Cup, Plastic Prying Tool', 'warranty_affected': True},
        {'issue_code': 'battery_draining', 'solution': 'Software Optimization and Battery Health Check', 'priority': 3, 'estimated_cost_min': 30, 'estimated_cost_max': 60, 'estimated_time_hours': 0.5, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'Diagnostic Software', 'warranty_affected': False},
        {'issue_code': 'front_camera_not_working', 'solution': 'Front Camera Module Replacement', 'priority': 3, 'estimated_cost_min': 60, 'estimated_cost_max': 130, 'estimated_time_hours': 1, 'difficulty': 'Medium', 'parts_needed': 'Front Camera Module', 'tools_needed': 'Screwdriver Kit, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'rear_camera_not_working', 'solution': 'Rear Camera Module Replacement', 'priority': 3, 'estimated_cost_min': 80, 'estimated_cost_max': 200, 'estimated_time_hours': 1, 'difficulty': 'Medium', 'parts_needed': 'Rear Camera Module', 'tools_needed': 'Screwdriver Kit, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'camera_app_crashing', 'solution': 'Software Troubleshooting and Reset', 'priority': 3, 'estimated_cost_min': 40, 'estimated_cost_max': 80, 'estimated_time_hours': 1, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'Computer, USB Cable', 'warranty_affected': False},
        {'issue_code': 'wireless_charging_issue', 'solution': 'Wireless Charging Coil Replacement', 'priority': 3, 'estimated_cost_min': 70, 'estimated_cost_max': 150, 'estimated_time_hours': 2, 'difficulty': 'High', 'parts_needed': 'Wireless Charging Coil', 'tools_needed': 'Screwdriver Kit, Prying Tools, Heat Gun', 'warranty_affected': True},
        {'issue_code': 'wifi_not_connecting', 'solution': 'Wi-Fi Module and Software Check', 'priority': 3, 'estimated_cost_min': 50, 'estimated_cost_max': 150, 'estimated_time_hours': 2, 'difficulty': 'High', 'parts_needed': 'Wi-Fi Antenna (if needed)', 'tools_needed': 'Screwdriver Kit, Diagnostic Software', 'warranty_affected': True},
        {'issue_code': 'gps_inaccurate', 'solution': 'GPS Module Recalibration', 'priority': 3, 'estimated_cost_min': 50, 'estimated_cost_max': 100, 'estimated_time_hours': 1, 'difficulty': 'Medium', 'parts_needed': 'None', 'tools_needed': 'Diagnostic Software', 'warranty_affected': False},
        {'issue_code': 'glass_damage', 'solution': 'Front Glass Replacement', 'priority': 3, 'estimated_cost_min': 100, 'estimated_cost_max': 300, 'estimated_time_hours': 2, 'difficulty': 'Medium', 'parts_needed': 'Front Glass Panel', 'tools_needed': 'Heat Gun, Prying Tools, OCA Machine', 'warranty_affected': True},
        {'issue_code': 'screen_flickering', 'solution': 'Display Connector and Cable Check', 'priority': 3, 'estimated_cost_min': 50, 'estimated_cost_max': 150, 'estimated_time_hours': 1.5, 'difficulty': 'Medium', 'parts_needed': 'Display Flex Cable (if needed)', 'tools_needed': 'Screwdriver Kit, Prying Tools, Microscope', 'warranty_affected': True},
        {'issue_code': 'apps_crashing', 'solution': 'Clear Cache and Software Update', 'priority': 3, 'estimated_cost_min': 30, 'estimated_cost_max': 60, 'estimated_time_hours': 0.5, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'None', 'warranty_affected': False},

        # Low Priority
        {'issue_code': 'earpiece_low_volume', 'solution': 'Earpiece Speaker Cleaning', 'priority': 4, 'estimated_cost_min': 20, 'estimated_cost_max': 40, 'estimated_time_hours': 0.5, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'Compressed Air, Small Brush', 'warranty_affected': False},
        {'issue_code': 'blurry_photos', 'solution': 'Camera Lens Cleaning and Calibration', 'priority': 4, 'estimated_cost_min': 20, 'estimated_cost_max': 50, 'estimated_time_hours': 0.5, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'Lens Cloth, Cleaning Solution', 'warranty_affected': False},
        {'issue_code': 'bluetooth_not_working', 'solution': 'Bluetooth Software Reset', 'priority': 4, 'estimated_cost_min': 25, 'estimated_cost_max': 50, 'estimated_time_hours': 0.5, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'None', 'warranty_affected': False},
        {'issue_code': 'nfc_not_working', 'solution': 'NFC Antenna and Software Check', 'priority': 4, 'estimated_cost_min': 50, 'estimated_cost_max': 100, 'estimated_time_hours': 1, 'difficulty': 'Medium', 'parts_needed': 'NFC Antenna (if needed)', 'tools_needed': 'Screwdriver Kit, Prying Tools', 'warranty_affected': True},
        {'issue_code': 'dead_pixels', 'solution': 'Monitor (No guaranteed fix, may need screen replacement)', 'priority': 4, 'estimated_cost_min': 0, 'estimated_cost_max': 400, 'estimated_time_hours': 0.2, 'difficulty': 'Low', 'parts_needed': 'Screen Assembly (if replacement)', 'tools_needed': 'None (for monitoring)', 'warranty_affected': True},
        {'issue_code': 'phone_running_slow', 'solution': 'Storage Cleanup and Software Tune-up', 'priority': 4, 'estimated_cost_min': 40, 'estimated_cost_max': 80, 'estimated_time_hours': 1, 'difficulty': 'Low', 'parts_needed': 'None', 'tools_needed': 'Computer, USB Cable', 'warranty_affected': False},
        {'issue_code': 'button_not_working', 'solution': 'Button Mechanism Cleaning or Replacement', 'priority': 4, 'estimated_cost_min': 40, 'estimated_cost_max': 90, 'estimated_time_hours': 1, 'difficulty': 'Medium', 'parts_needed': 'Button Flex Cable (if needed)', 'tools_needed': 'Screwdriver Kit, Prying Tools', 'warranty_affected': True},
    ]

    for data in repairs_data:
        issue_info = next((item for item in issues_data if item["code"] == data['issue_code']), None)
        if not issue_info:
            print(f"Warning: Issue code '{data['issue_code']}' not found. Cannot add repair.")
            continue
        
        issue = Issue.query.filter_by(code=issue_info['code']).first() # Filter by code
        if issue:
            repair = Repair(
                issue_id=issue.id,
                solution=data['solution'],
                priority=data['priority'],
                estimated_cost_min=data['estimated_cost_min'],
                estimated_cost_max=data['estimated_cost_max'],
                estimated_time_hours=data['estimated_time_hours'],
                difficulty=data['difficulty'],
                parts_needed=data['parts_needed'],
                tools_needed=data['tools_needed'],
                warranty_affected=data['warranty_affected']
            )
            db.session.add(repair)
        else:
            print(f"Warning: Issue '{issue_info['name']}' not found. Cannot add repair.")

    db.session.commit()
    print(f"Seeded {len(repairs_data)} Repairs.")

    # 4. RE-GENERATED EXPERT SYSTEM RULES
    rules_data = []
    for symptom_code, issue_code in symptoms_map.items():
        issue_obj = Issue.query.filter_by(code=issue_code).first() # Get the actual Issue object
        if not issue_obj:
            print(f"Warning: Issue object for code '{issue_code}' not found. Cannot create rule.")
            continue
        
        severity_priority_map = {'Critical': 10, 'High': 8, 'Medium': 5, 'Low': 2}
        priority = severity_priority_map.get(issue_obj.severity, 1)
        confidence = 0.95

        # Find the repair associated with this issue. Assuming one repair per issue for simplicity in standardization.
        repair_obj = Repair.query.filter_by(issue_id=issue_obj.id).first()
        if not repair_obj:
            print(f"Warning: No repair found for issue '{issue_obj.name}'. Skipping rule for this issue.")
            continue

        rule = {
            "name": f"Diagnose {issue_obj.name} from {symptom_code}",
            "conditions": [ # Directly as Python list
                {"function": "symptom_is_present", "args": {"symptom_code": symptom_code}}
            ],
            "actions": [ # Directly as Python list
                {"function": "set_diagnosis", "args": {
                    "diagnosis_code": issue_obj.name, # Use actual issue name for diagnosis
                    "category": issue_obj.category, # Use actual issue category
                    "severity": issue_obj.severity, # Use actual issue severity
                    "confidence": confidence,
                    "urgent": issue_obj.severity == 'Critical' or issue_obj.severity == 'High',
                    "explanation": f"Symptom '{symptom_code.replace('_', ' ')}' suggests {issue_obj.name}. Recommending repair ID {repair_obj.id}."
                }},
                {"function": "add_to_working_memory", "args": {
                    "key": "recommended_repair_id",
                    "value": repair_obj.id
                }}
            ],
            "priority": priority,
            "confidence": confidence,
            "description": f"Rule to diagnose {issue_obj.name} if the symptom '{symptom_code}' is present and recommend repair {repair_obj.id}.",
            "repair_id": repair_obj.id # Link rule to repair
        }
        rules_data.append(rule)

    for data in rules_data:
        new_rule = Rule(**data)
        db.session.add(new_rule)

    db.session.commit()
    print(f"Seeded {len(rules_data)} Rules.")

def run_standardize():
    seed_data()
    print("Data standardization complete.")
