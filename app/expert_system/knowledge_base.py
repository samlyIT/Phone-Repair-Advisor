"""
Knowledge Base for Phone Repair Expert System
Contains facts and domain knowledge about phone repairs
"""


class Fact:
    """Represents a fact in the knowledge base"""

    def __init__(self, name, value, confidence=1.0):
        self.name = name
        self.value = value
        self.confidence = confidence  # 0.0 to 1.0

    def __repr__(self):
        return f"Fact({self.name}={self.value}, conf={self.confidence})"


class KnowledgeBase:
    """Stores all facts and domain knowledge"""

    def __init__(self):
        self.facts = {}
        self.working_memory = {}
        self.symptoms = {}  # Initialize symptoms attribute
        self._init_domain_knowledge()

    def add_symptoms(self, symptoms):
        """Add symptoms to the knowledge base"""
        self.symptoms.update(symptoms)

    def _init_domain_knowledge(self):
        """Initialize domain-specific knowledge"""
        self.domain_knowledge = {
            # Screen issues knowledge
            'screen_damage_types': [
                'cracked_glass',
                'lcd_damage',
                'digitizer_failure',
                'complete_failure'
            ],

            # Battery issues knowledge
            'battery_indicators': [
                'fast_drain',
                'no_charging',
                'swollen_battery',
                'overheating'
            ],

            # Water damage knowledge
            'water_damage_severity': {
                'minor': 'Quick exposure, dried immediately',
                'moderate': 'Submerged briefly, some moisture',
                'severe': 'Fully submerged, not dried properly'
            },

            # Repair complexity
            'repair_complexity': {
                'screen': 'medium',
                'battery': 'medium',
                'water_damage': 'high',
                'charging_port': 'medium',
                'software': 'low',
                'motherboard': 'expert'
            },

            # Cost ranges (USD) - From domain_knowledge.py
            'typical_costs': {
                'screen_replacement': (100, 300),
                'battery_replacement': (50, 150),
                'charging_port': (40, 80),
                'water_damage_cleaning': (80, 250),
                'camera_replacement': (70, 200),
                'speaker_replacement': (40, 100),
                'software_fix': (30, 100)
            },

            # From domain_knowledge.py
            'diagnosis_to_cost_category_mapping': {
                'LCD_DAMAGE': 'screen_replacement',
                'GLASS_DAMAGE': 'screen_replacement',
                'BATTERY_DEGRADATION': 'battery_replacement',
                'CHARGING_PORT_ISSUE': 'charging_port',
                'WATER_DAMAGE': 'water_damage_cleaning',
                'CAMERA_ISSUE': 'camera_replacement',
                'AUDIO_HARDWARE_ISSUE': 'speaker_replacement',
                'SOFTWARE_ISSUE': 'software_fix'
            },

            # From domain_knowledge.py
            'premium_brands': ['Apple', 'Samsung', 'Google'],
            'premium_brand_cost_multiplier': 1.5,

            # From domain_knowledge.py
            'prevention_tips': {
                'LCD_DAMAGE': [
                    'Use a screen protector',
                    'Use a protective case',
                    'Avoid placing phone face-down'
                ],
                'BATTERY_DEGRADATION': [
                    'Avoid extreme temperatures',
                    'Don\'t let battery drain to 0% regularly',
                    'Use original charger',
                    'Avoid overnight charging'
                ],
                'WATER_DAMAGE': [
                    'Use waterproof case near water',
                    'Check IP rating before exposure',
                    'Act quickly if exposed to liquid'
                ],
                'CHARGING_PORT_ISSUE': [
                    'Clean port regularly with compressed air',
                    'Avoid forcing cable connections',
                    'Use wireless charging when possible'
                ]
            },

            # From domain_knowledge.py
            'clarifying_questions': {
                'screen_cracked': {
                    'symptom_code': 'touch_not_working',
                    'question': 'Does the touch screen still respond to your touches?'
                },
                'battery_draining': {
                    'symptom_code': 'phone_overheating',
                    'question': 'Does your phone get unusually hot?'
                },
                'phone_not_charging': {
                    'symptom_code': 'charging_slow',
                    'question': 'Have you tried different chargers and cables?'
                }
            }
        }

    def add_fact(self, name, value, confidence=1.0):
        """Add a fact to the knowledge base"""
        fact = Fact(name, value, confidence)
        self.facts[name] = fact
        return fact

    def get_fact(self, name):
        """Retrieve a fact from the knowledge base"""
        return self.facts.get(name)

    def has_fact(self, name):
        """Check if a fact exists"""
        return name in self.facts

    def add_to_working_memory(self, key, value):
        """Add temporary data to working memory"""
        self.working_memory[key] = value

    def get_from_working_memory(self, key):
        """Get data from working memory"""
        return self.working_memory.get(key)

    def clear_working_memory(self):
        """Clear all working memory"""
        self.working_memory.clear()

    def get_domain_knowledge(self, key):
        """Get domain-specific knowledge"""
        return self.domain_knowledge.get(key)

    def reset(self):
        """Reset all facts and working memory"""
        self.facts.clear()
        self.working_memory.clear()
        self.symptoms.clear()

    def __repr__(self):
        return (
            f"KnowledgeBase(facts={len(self.facts)}, "
            f"working_memory={len(self.working_memory)})"
        )
