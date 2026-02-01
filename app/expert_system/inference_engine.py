"""
Inference Engine for Phone Repair Expert System
Implements forward and backward chaining algorithms
"""
from flask import current_app


class InferenceEngine:
    """Performs reasoning using rules and facts"""

    def __init__(self, knowledge_base, rule_engine):
        self.kb = knowledge_base
        self.rule_engine = rule_engine
        self.inference_chain = []

    def forward_chaining(self):
        """
        Forward chaining: Start with facts, apply rules to derive conclusions
        Data-driven reasoning
        """
        self.inference_chain = []
        self.rule_engine.reset_all_rules()

        iteration = 0
        max_iterations = 100  # Prevent infinite loops

        while iteration < max_iterations:
            iteration += 1
            rules_fired = False

            # Find applicable rules
            current_app.logger.debug(f"Inference iteration {iteration}: Getting applicable rules.")
            applicable_rules = self.rule_engine.get_applicable_rules(self.kb)
            current_app.logger.debug(f"Inference iteration {iteration}: Found {len(applicable_rules)} applicable rules.")

            if not applicable_rules:
                current_app.logger.debug(f"Inference iteration {iteration}: No applicable rules found. Breaking.")
                break

            # Execute highest priority rule
            for rule in applicable_rules:
                current_app.logger.debug(f"Inference iteration {iteration}: Attempting to execute rule '{rule.name}'.")
                if rule.execute(self.kb):
                    self.inference_chain.append({
                        'iteration': iteration,
                        'rule': rule.name,
                        'confidence': rule.confidence
                    })
                    rules_fired = True
                    current_app.logger.debug(f"Inference iteration {iteration}: Rule '{rule.name}' fired successfully.")
                    break  # Execute one rule per iteration
                else:
                    current_app.logger.debug(f"Inference iteration {iteration}: Rule '{rule.name}' did not fire.")

            if not rules_fired:
                current_app.logger.debug(f"Inference iteration {iteration}: No rules fired in this iteration. Breaking.")
                break

        return self.get_conclusions()

    def get_conclusions(self):
        """Get all derived conclusions"""
        conclusions = {}

        # Extract key facts from working memory
        if self.kb.get_from_working_memory('diagnosis'):
            conclusions['diagnosis'] = self.kb.get_from_working_memory(
                'diagnosis')

        # Get confidence from working memory
        if self.kb.get_from_working_memory('confidence'):
            confidence = self.kb.get_from_working_memory('confidence')
            conclusions['diagnosis_confidence'] = confidence
        else:
            # Default if no confidence found
            conclusions['diagnosis_confidence'] = 0.0

        if self.kb.get_from_working_memory('category'):
            conclusions['category'] = self.kb.get_from_working_memory(
                'category')

        if self.kb.get_from_working_memory('severity'):
            conclusions['severity'] = self.kb.get_from_working_memory(
                'severity')

        if self.kb.get_from_working_memory('urgent'):
            conclusions['urgent'] = self.kb.get_from_working_memory('urgent')

        conclusions['inference_chain'] = self.inference_chain

        # Include custom explanation from working memory if available
        if self.kb.get_from_working_memory('explanation'):
            explanation = self.kb.get_from_working_memory('explanation')
            conclusions['custom_explanation'] = explanation

        return conclusions

    def explain_reasoning(self):
        """Provide explanation of the reasoning process"""
        explanation = []

        for step in self.inference_chain:
            explanation.append(
                f"Step {step.get('iteration', '?')}: "
                f"Applied rule '{step['rule']}' "
                f"(confidence: {step['confidence']:.2f})"
            )

        # If a custom explanation was added by a rule, append it
        if self.kb.get_from_working_memory('explanation'):
            explanation.append(self.kb.get_from_working_memory('explanation'))

        return explanation

    def reset(self):
        """Reset inference engine"""
        self.inference_chain = []
        self.rule_engine.reset_all_rules()

    def __repr__(self):
        return f"InferenceEngine(chain_length={len(self.inference_chain)})"
