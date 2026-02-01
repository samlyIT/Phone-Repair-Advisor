from enum import Enum

class PhoneBrand(Enum):
    APPLE = "Apple"
    SAMSUNG = "Samsung"
    XIAOMI = "Xiaomi"
    HUAWEI = "Huawei"
    OPPO = "Oppo"
    VIVO = "Vivo"
    GOOGLE = "Google"
    OTHER = "Other"

class IssueCategory(Enum):
    SCREEN = "Screen"
    BATTERY = "Battery"
    CHARGING = "Charging"
    WATER_DAMAGE = "Water Damage"
    SPEAKER = "Speaker"
    MICROPHONE = "Microphone"
    CAMERA = "Camera"
    BUTTON = "Button"
    SOFTWARE = "Software"
    CONNECTIVITY = "Connectivity"

class SeverityLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class RepairDifficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

# Symptom definitions
SYMPTOMS = {
    'screen_cracked': 'Screen is cracked or shattered',
    'screen_black': 'Screen is completely black',
    'screen_flickering': 'Screen is flickering or showing lines',
    'touch_not_working': 'Touch screen not responding',
    'battery_draining': 'Battery drains quickly',
    'phone_not_charging': 'Phone does not charge',
    'charging_slow': 'Charging is very slow',
    'phone_overheating': 'Phone gets very hot',
    'water_exposed': 'Phone was exposed to water',
    'no_sound': 'No sound from speaker',
    'microphone_not_working': 'Others cannot hear me',
    'camera_blurry': 'Camera produces blurry images',
    'camera_not_working': 'Camera does not open',
    'power_button_stuck': 'Power button is stuck or not working',
    'volume_button_stuck': 'Volume buttons not working',
    'wifi_not_connecting': 'WiFi not connecting',
    'bluetooth_issues': 'Bluetooth not working',
    'phone_freezing': 'Phone freezes frequently',
    'apps_crashing': 'Apps crash frequently'
}