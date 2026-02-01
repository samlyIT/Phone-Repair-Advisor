from functools import wraps


class RuleFunctionRegistry:
    """
    A registry for condition and action functions used in rules.
    This replaces direct `eval()` calls with safe, pre-registered functions.
    """
    _conditions = {}
    _actions = {}

    @classmethod
    def register_condition(cls, name):
        """Decorator to register a function as a rule condition."""
        def decorator(func):
            if name in cls._conditions:
                raise ValueError(f"Condition '{name}' already registered.")
            cls._conditions[name] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def register_action(cls, name):
        """Decorator to register a function as a rule action."""
        def decorator(func):
            if name in cls._actions:
                raise ValueError(f"Action '{name}' already registered.")
            cls._actions[name] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def get_condition(cls, name):
        """Retrieve a registered condition function by name."""
        return cls._conditions.get(name)

    @classmethod
    def get_action(cls, name):
        """Retrieve a registered action function by name."""
        return cls._actions.get(name)

    @classmethod
    def list_conditions(cls):
        """List all registered condition names."""
        return list(cls._conditions.keys())

    @classmethod
    def list_actions(cls):
        """List all registered action names."""
        return list(cls._actions.keys())

# Example condition functions (to be moved to rule_functions.py later)
# @RuleFunctionRegistry.register_condition("has_symptom")
# def has_symptom(kb, code):
#    return kb.symptoms.get(code, False)

# @RuleFunctionRegistry.register_condition("has_diagnosis")
# def has_diagnosis(kb, diagnosis_code):
#    return kb.facts.get('diagnosis') == diagnosis_code

# Example action functions (to be moved to rule_functions.py later)
# @RuleFunctionRegistry.register_action("assert_fact")
# def assert_fact(kb, fact_name, value, confidence=1.0, reason=None):
#    kb.add_fact(fact_name, value, confidence, reason)

# @RuleFunctionRegistry.register_action("set_diagnosis")
# def set_diagnosis(kb, diagnosis_code, category, severity, confidence=1.0, urgent=False, explanation=None):
#    kb.add_fact('diagnosis', diagnosis_code, confidence, explanation)
#    kb.add_fact('category', category)
#    kb.add_fact('severity', severity)
#    kb.add_fact('urgent', urgent)
#    kb.add_fact('diagnosis_confidence', confidence)
