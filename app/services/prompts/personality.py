from typing import List


class PersonalityManager:

    # Map of personality traits to specific behavioral instructions
    TRAIT_BEHAVIORS = {
        'Friendly': 'Be warm and approachable, use casual language',
        'Wise': 'Share thoughtful insights gently',
        'Curious': 'Ask clarifying questions and explore deeply',
        'Supportive': 'Be encouraging, validating, and non-judgmental',
        'Creative': 'Suggest imaginative perspectives',
        'Analytical': 'Break down thoughts systematically and logically',
        'Empathetic': 'Show deep understanding and emotional attunement',
        'Motivational': 'Be energizing and focus on growth',
        'Calm': 'Maintain a peaceful, steady, reassuring presence',
        'Energetic': 'Be enthusiastic, dynamic, and uplifting',
        'Thoughtful': 'Be reflective and consider things deeply',
        'Playful': 'Use appropriate humor and lightheartedness',
        'Patient': 'Be unhurried and allow space for processing',
        'Optimistic': 'Focus on hope and possibilities',
        'Grounded': 'Be practical, realistic, and down-to-earth',
    }

    @staticmethod
    def build_personality_descriptor(traits: List[str]) -> str:
        if len(traits) == 1:
            return traits[0].lower()
        elif len(traits) == 2:
            return f"{traits[0].lower()} and {traits[1].lower()}"
        else:
            return f"{', '.join(t.lower() for t in traits[:-1])}, and {traits[-1].lower()}"

    @classmethod
    def get_trait_behaviors(cls, traits: List[str]) -> str:
        behaviors = [
            cls.TRAIT_BEHAVIORS.get(trait, '')
            for trait in traits
            if trait in cls.TRAIT_BEHAVIORS
        ]
        return '. '.join(b for b in behaviors if b) + '.'
