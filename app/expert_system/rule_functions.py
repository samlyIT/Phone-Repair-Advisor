from app.expert_system.rule_function_registry import RuleFunctionRegistry
from app.expert_system.knowledge_base import KnowledgeBase  # For type hinting

# --- Condition Implementations ---


@RuleFunctionRegistry.register_condition("has_fact")
def has_fact(kb: KnowledgeBase, fact_name: str) -> bool:
    """Checks if a fact exists in the KnowledgeBase."""
    return kb.has_fact(fact_name)


@RuleFunctionRegistry.register_condition("fact_equals")
def fact_equals(kb: KnowledgeBase, fact_name: str, expected_value: any) -> bool:
    """Checks if a fact's value equals an expected value."""
    fact = kb.get_fact(fact_name)
    return fact and fact.value == expected_value


@RuleFunctionRegistry.register_condition("fact_greater_than")
def fact_greater_than(kb: KnowledgeBase, fact_name: str, expected_value: float) -> bool:
    """Checks if a fact's value is greater than an expected value."""
    fact = kb.get_fact(fact_name)
    return fact and fact.value > expected_value


@RuleFunctionRegistry.register_condition("fact_less_than")
def fact_less_than(kb: KnowledgeBase, fact_name: str, expected_value: float) -> bool:
    """Checks if a fact's value is less than an expected value."""
    fact = kb.get_fact(fact_name)
    return fact and kb.get_fact(fact_name).value < expected_value


@RuleFunctionRegistry.register_condition("symptom_is_present")
def symptom_is_present(kb: KnowledgeBase, symptom_code: str) -> bool:
    """Checks if a specific symptom is present in the KnowledgeBase."""
    return kb.symptoms.get(symptom_code, False)


@RuleFunctionRegistry.register_condition("diagnosis_is")
def diagnosis_is(kb: KnowledgeBase, diagnosis_code: str) -> bool:
    """Checks if the current diagnosis matches a specific code."""
    fact = kb.get_fact('diagnosis')
    return fact and fact.value == diagnosis_code


# --- Logical Operators for Conditions ---
@RuleFunctionRegistry.register_condition("AND")
def logical_and(kb: KnowledgeBase, conditions: list) -> bool:
    """Evaluates if all sub-conditions are true.
    'conditions' is expected to be a list of already compiled partial functions.
    """
    return all(cond_func(kb=kb) for cond_func in conditions)


@RuleFunctionRegistry.register_condition("OR")
def logical_or(kb: KnowledgeBase, conditions: list) -> bool:
    """Evaluates if any sub-condition is true.
    'conditions' is expected to be a list of already compiled partial functions.
    """
    return any(cond_func(kb=kb) for cond_func in conditions)


@RuleFunctionRegistry.register_condition("NOT")
def logical_not(kb: KnowledgeBase, condition_func) -> bool:
    """Evaluates the negation of a single sub-condition.
    'condition_func' is expected to be an already compiled partial function.
    """
    return not condition_func(kb=kb)


# --- Action Implementations ---
@RuleFunctionRegistry.register_action("add_fact")
def add_fact(kb: KnowledgeBase, fact_name: str, fact_value: any, confidence: float = 1.0, reason: str = None):
    """Adds a fact to the KnowledgeBase."""
    kb.add_fact(fact_name, fact_value, confidence)


@RuleFunctionRegistry.register_action("add_to_working_memory")
def add_to_working_memory(kb: KnowledgeBase, key: str, value: any):
    """Adds an item to the KnowledgeBase's working memory."""
    kb.add_to_working_memory(key, value)

@RuleFunctionRegistry.register_action("set_diagnosis")
def set_diagnosis(kb: KnowledgeBase, diagnosis_code: str, category: str, severity: str, confidence: float = 1.0, urgent: bool = False, explanation: str = None):
    """Sets the diagnosis and related attributes in the KnowledgeBase."""
    kb.add_to_working_memory('diagnosis', diagnosis_code)
    kb.add_to_working_memory('category', category)
    kb.add_to_working_memory('severity', severity)
    kb.add_to_working_memory('urgent', urgent)
    kb.add_to_working_memory('confidence', confidence)
    if explanation:
        kb.add_to_working_memory('explanation', explanation)
