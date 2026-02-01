"""
Rule Engine for Phone Repair Expert System
Contains IF-THEN rules for diagnosis and repair recommendations
"""
import json
from functools import partial
from app.models.rule import Rule as RuleModel
from app.expert_system.rule_function_registry import RuleFunctionRegistry
# Ensure condition/action functions are registered
import app.expert_system.rule_functions
from sqlalchemy.exc import ProgrammingError
from flask import current_app


class Rule:
    """Represents an IF-THEN rule"""

    def __init__(self, name, conditions, actions, priority=1, confidence=1.0):
        self.name = name
        self.conditions_json = conditions
        self.actions_json = actions
        self.priority = priority
        self.confidence = confidence
        self.fired = False

        self.conditions = []
        self.actions = []
        self._compile()

    def _compile_expression(self, expression_data: dict, is_condition: bool):
        """
        Recursively compiles a single expression (condition or action) into a callable.
        Handles nested logical operators.
        """
        if not isinstance(expression_data, dict):
            raise TypeError("Expression data must be a dictionary.")

        func_name = expression_data.get("function")
        if not func_name:
            raise ValueError("Function name is missing in expression.")

        args = expression_data.get("args", {})
        
        # Handle logical operators for conditions
        if is_condition and func_name in ["AND", "OR", "NOT"]:
            if func_name == "AND" or func_name == "OR":
                sub_conditions_data = args.get("conditions")
                if not isinstance(sub_conditions_data, list) or not sub_conditions_data:
                    raise ValueError(f"'{func_name}' operator requires a non-empty list of 'conditions'.")
                
                compiled_sub_conditions = [
                    self._compile_expression(sub_cond_data, True)
                    for sub_cond_data in sub_conditions_data
                ]
                # Pass the compiled sub_conditions as an argument to the logical operator
                return partial(RuleFunctionRegistry.get_condition(func_name), conditions=compiled_sub_conditions)
            
            elif func_name == "NOT":
                sub_condition_data = args.get("condition")
                if not isinstance(sub_condition_data, dict):
                    raise ValueError(f"'{func_name}' operator requires a single 'condition' dictionary.")
                
                compiled_sub_condition = self._compile_expression(sub_condition_data, True)
                # Pass the compiled sub_condition as an argument to the logical operator
                return partial(RuleFunctionRegistry.get_condition(func_name), condition_func=compiled_sub_condition)

        # Handle regular functions
        if is_condition:
            func = RuleFunctionRegistry.get_condition(func_name)
            if not func:
                raise ValueError(f"Condition function '{func_name}' not found in registry.")
            return partial(func, **args)
        else: # is_action
            func = RuleFunctionRegistry.get_action(func_name)
            if not func:
                raise ValueError(f"Action function '{func_name}' not found in registry.")
            return partial(func, **args)


    def _compile(self):
        """
        Compile condition and action JSON structures into callable functions
        using the RuleFunctionRegistry.
        """
        self.conditions = []
        self.actions = []

        try:
            # Compile conditions
            if self.conditions_json:
                # Ensure conditions_json is a list before iterating
                if not isinstance(self.conditions_json, list):
                    raise TypeError("Conditions must be a list of expression objects.")
                for cond_data in self.conditions_json:
                    self.conditions.append(self._compile_expression(cond_data, is_condition=True))
            current_app.logger.debug(
                f"Rule '{self.name}': Conditions compiled.")

            # Compile actions
            if self.actions_json:
                # Ensure actions_json is a list before iterating
                if not isinstance(self.actions_json, list):
                    raise TypeError("Actions must be a list of expression objects.")
                for action_data in self.actions_json:
                    self.actions.append(self._compile_expression(action_data, is_condition=False))
            current_app.logger.debug(f"Rule '{self.name}': Actions compiled.")

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error compiling rule '{
                    self.name}': {e}")
            self.conditions = []
            self.actions = []

    def evaluate(self, kb):
        """Evaluate if all conditions are met"""
        if not self.conditions:
            current_app.logger.debug(
                f"Rule '{self.name}': No conditions to evaluate.")
            return False
        try:
            condition_results = []
            for condition in self.conditions:
                cond_result = condition(kb=kb)
                condition_results.append(cond_result)
                current_app.logger.debug(
                    f"Rule '{self.name}': Condition {condition.func.__name__} (args={condition.keywords}) evaluated to {cond_result}.")
            
            result = all(condition_results)
            current_app.logger.debug(
                f"Rule '{self.name}': All conditions evaluated to {result}.")
            return result
        except Exception as e:
            current_app.logger.error(
                f"Error evaluating rule '{
                    self.name}': {e}")
            return False

    def execute(self, kb):
        """Execute all actions"""
        if not self.fired and self.actions:
            try:
                for action in self.actions:
                    action(kb=kb)
                self.fired = True
                current_app.logger.debug(
                    f"Rule '{self.name}': Executed actions.")
                return True
            except Exception as e:
                current_app.logger.error(
                    f"Error executing rule '{
                        self.name}': {e}")
        return False

    def reset(self):
        """Reset fired state"""
        self.fired = False

    def __repr__(self):
        return f"Rule({self.name}, priority={self.priority})"


class RuleEngine:
    """Manages and executes rules"""

    def __init__(self):
        self.rules = []

    def load_rules(self):
        """Load all rules from the database"""
        self.rules = []
        try:
            all_rules = RuleModel.query.order_by(
                RuleModel.priority.desc()).all()
            if not all_rules:
                current_app.logger.warning(
                    "No rules found in the database. Expert system may not function correctly.")
                return

            for rule_model in all_rules:
                # Deserialize conditions and actions from JSON strings to Python objects
                # SQLAlchemy's JSON type for SQLite might return strings.
                # Explicitly parse if they are strings.
                conditions_obj = rule_model.conditions
                if isinstance(conditions_obj, str):
                    conditions_obj = json.loads(conditions_obj)
                
                actions_obj = rule_model.actions
                if isinstance(actions_obj, str):
                    actions_obj = json.loads(actions_obj)


                self.rules.append(Rule(
                    name=rule_model.name,
                    conditions=conditions_obj, # Pass Python object
                    actions=actions_obj,       # Pass Python object
                    priority=rule_model.priority,
                    confidence=rule_model.confidence
                ))

            current_app.logger.info(
                f"Successfully loaded {len(self.rules)} rules from the database.")

        except ProgrammingError:
            current_app.logger.warning(
                "Warning: 'rule' table not found or accessible. Skipping rule loading during initialization.")
        except Exception as e:
            current_app.logger.error(f"Error loading rules from database: {e}")

    def add_rule(self, rule):
        """Add a new rule"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def get_applicable_rules(self, kb):
        """Get all rules whose conditions are met that have not fired yet"""
        return [
            rule for rule in self.rules if not rule.fired and rule.evaluate(kb)]

    def reset_all_rules(self):
        """Reset all rules to unfired state"""
        for rule in self.rules:
            rule.reset()

    def __repr__(self):
        return f"RuleEngine(rules={len(self.rules)})"