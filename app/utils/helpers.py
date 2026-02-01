from flask import g

def get_advisor():
    """Lazily loads and returns the PhoneRepairAdvisor instance."""
    if 'advisor' not in g:
        # LOCAL IMPORT to break circular dependency
        from app.expert_system.advisor import PhoneRepairAdvisor
        g.advisor = PhoneRepairAdvisor()
    return g.advisor
