from sqlalchemy.orm import joinedload
from flask import current_app
"""
Phone Repair Advisor - Main Expert System Logic
"""

from app.expert_system.knowledge_base import KnowledgeBase
from app.expert_system.rules import RuleEngine
from app.expert_system.inference_engine import InferenceEngine
from app.models.issue import Issue, Symptom


class PhoneRepairAdvisor:
    """Main advisor that diagnoses phone issues and recommends repairs"""

    def __init__(self):
        self.kb = KnowledgeBase()
        self.rule_engine = RuleEngine()
        self.inference_engine = InferenceEngine(self.kb, self.rule_engine)

    def diagnose(self, symptoms, phone_brand=None, phone_model=None):
        """
        Diagnose phone issue based on symptoms

        Args:
            symptoms: Dict of symptom_code: True/False
            phone_brand: Optional phone brand
            phone_model: Optional phone model

        Returns:
            Dict with diagnosis, recommendations, and explanation
        """
        # Load rules at the beginning of each diagnosis
        try:
            self.rule_engine.load_rules()
        except Exception as e:
            current_app.logger.error(
                f"Failed to load rules during diagnosis: {e}")
            # Depending on desired behavior, you might want to return an
            # error response For now, it will likely result in an 'UNKNOWN'
            # diagnosis

        # Debug print: symptoms received
        current_app.logger.debug(
            f"Advisor.diagnose received symptoms: {symptoms}")  # Debug print

        # Reset knowledge base
        self.kb.reset()
        self.inference_engine.reset()

        # Add symptoms to the knowledge base's symptoms attribute
        self.kb.add_symptoms(symptoms)

        # Add symptoms as facts
        for symptom_code, is_present in symptoms.items():
            self.kb.add_fact(symptom_code, is_present)

        # Add phone info if available
        if phone_brand:
            self.kb.add_fact('phone_brand', phone_brand)
        if phone_model:
            self.kb.add_fact('phone_model', phone_model)

        current_app.logger.debug(f"KB before inference: {self.kb}")

        # Run inference
        conclusions = self.inference_engine.forward_chaining()

        current_app.logger.debug(f"Conclusions: {conclusions}")
        current_app.logger.debug(
            "Inference explanation:\n%s",
            self.inference_engine.explain_reasoning())

        # Get recommendations from database
        recommendations = self._get_recommendations(conclusions)

        # Prepare result
        result = {
            'diagnosis': conclusions.get('diagnosis', 'UNKNOWN'),
            'category': conclusions.get('category', 'Unknown'),
            'severity': conclusions.get('severity', 'Unknown'),
            'confidence': conclusions.get('diagnosis_confidence', 0.0),
            'urgent': conclusions.get('urgent', False),
            'recommendations': recommendations,
            'explanation': self.inference_engine.explain_reasoning(),
            'inference_chain': conclusions.get('inference_chain', []),
            'received_symptoms': symptoms # Add received symptoms for debugging
        }

        return result

    def _get_recommendations(self, conclusions):
        """Get repair recommendations from database based on diagnosis"""
        diagnosis = conclusions.get('diagnosis')
        if not diagnosis:
            return []

        issue = Issue.query.options(joinedload(Issue.repairs)).filter_by(name=diagnosis).first()
        if not issue:
            return []

        recommendations = []
        seen_repair_ids = set()

        # Sort repairs by priority for consistency
        repairs = sorted(
            issue.repairs,
            key=lambda r: r.priority,
            reverse=True)

        for repair in repairs:
            if repair.id not in seen_repair_ids:
                recommendations.append({
                    'issue': issue.name,
                    'issue_description': issue.description,
                    'solution': repair.solution,
                    'cost_min': repair.estimated_cost_min,
                    'cost_max': repair.estimated_cost_max,
                    'time_hours': repair.estimated_time_hours,
                    'difficulty': repair.difficulty,
                    'parts_needed': repair.parts_needed,
                    'tools_needed': repair.tools_needed,
                    'warranty_affected': repair.warranty_affected,
                    'priority': repair.priority
                })
                seen_repair_ids.add(repair.id)

        return recommendations

    def ask_clarifying_questions(self, symptoms_so_far):
        """
        Determine what questions to ask next based on current symptoms

        Args:
            symptoms_so_far: Dict of symptom_code: True/False

        Returns:
            List of suggested questions to ask
        """
        questions = []
        clarifying_questions = self.kb.get_domain_knowledge('clarifying_questions')

        # Add initial facts
        for symptom_code, is_present in symptoms_so_far.items():
            self.kb.add_fact(symptom_code, is_present)
            if is_present and clarifying_questions and symptom_code in clarifying_questions:
                questions.append(clarifying_questions[symptom_code])

        return questions

    def get_cost_estimate(self, diagnosis_code, phone_brand=None):
        """
        Get cost estimate for a specific diagnosis

        Args:
            diagnosis_code: The diagnosis code
            phone_brand: Optional phone brand for brand-specific pricing

        Returns:
            Dict with cost estimates
        """
        diagnosis_mapping = self.kb.get_domain_knowledge('diagnosis_to_cost_category_mapping')
        typical_costs = self.kb.get_domain_knowledge('typical_costs')
        premium_brands = self.kb.get_domain_knowledge('premium_brands')
        premium_multiplier = self.kb.get_domain_knowledge('premium_brand_cost_multiplier')

        if not all([diagnosis_mapping, typical_costs, premium_brands, premium_multiplier]):
             return {'min': 0, 'max': 0, 'currency': 'USD'}
        
        cost_key = diagnosis_mapping.get(diagnosis_code)
        if cost_key and cost_key in typical_costs:
            cost_min, cost_max = typical_costs[cost_key]

            # Adjust for brand (premium brands cost more)
            if phone_brand in premium_brands:
                cost_min *= premium_multiplier
                cost_max *= premium_multiplier

            return {
                'min': round(cost_min, 2),
                'max': round(cost_max, 2),
                'currency': 'USD'
            }

        return {'min': 0, 'max': 0, 'currency': 'USD'}

    def get_prevention_tips(self, diagnosis_code):
        """Get prevention tips for future issues"""
        prevention_tips = self.kb.get_domain_knowledge('prevention_tips')
        if prevention_tips:
            return prevention_tips.get(
                diagnosis_code, ['Maintain your phone regularly'])
        return ['Maintain your phone regularly']

    def __repr__(self):
        return (
            f"PhoneRepairAdvisor(kb={self.kb}, "
            f"rules={len(self.rule_engine.rules)})"
        )
