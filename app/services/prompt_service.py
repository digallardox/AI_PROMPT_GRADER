"""Prompt service for building AI prompts from templates."""

import yaml
from pathlib import Path
from typing import List


class PromptService:
    """Service for loading and building prompts from templates."""

    def __init__(self):
        """Initialize prompt service with templates directory."""
        self.templates_dir = Path(__file__).parent / "templates"

    def build_reflection_prompt(
        self,
        companion_name: str,
        traits: List[str],
        content: str
    ) -> str:
        """
        Build a reflection prompt from template.

        Args:
            companion_name: Name of the AI companion
            traits: List of personality traits
            content: Journal entry content

        Returns:
            System prompt for reflection generation
        """
        # Load template
        template_path = self.templates_dir / "reflection.yaml"

        if template_path.exists():
            with open(template_path) as f:
                data = yaml.safe_load(f)
            template = data.get('template', '')
        else:
            # Fallback template if file doesn't exist
            template = self._get_default_reflection_template()

        # Build personality descriptor
        personality = self._build_personality(traits)

        # Simple variable substitution
        prompt = template.replace("{{companion_name}}", companion_name)
        prompt = prompt.replace("{{companion_avatar}}", "🐨")
        prompt = prompt.replace("{{personality_descriptor}}", personality)
        prompt = prompt.replace("{{personality_instructions}}", self._get_trait_behaviors(traits))
        prompt = prompt.replace("{{user_entry}}", content[:2000])  # Truncate long entries
        prompt = prompt.replace("{{word_count}}", str(len(content.split())))

        return prompt

    def build_chat_prompt(
        self,
        companion_name: str,
        traits: List[str],
        entry_content: str = ""
    ) -> str:
        """
        Build a chat prompt with optional entry context.

        Args:
            companion_name: Name of the AI companion
            traits: List of personality traits
            entry_content: Journal entry content for context (empty for general conversation)

        Returns:
            System prompt for chat conversation
        """
        personality = self._build_personality(traits)

        # Global conversation (no entry context)
        if not entry_content or entry_content.strip() == "":
            return f"""You are {companion_name}, a {personality} AI companion and therapeutic listener.

Your role is to provide a safe, supportive space for the user to explore their thoughts, feelings, and experiences. Act as a compassionate life coach and therapist who uses professional CBT and life coaching techniques:

- Help identify thought patterns, cognitive distortions, and limiting beliefs
- Support reframing negative thoughts into more balanced perspectives
- Guide users toward clarity, insight, and actionable goals
- Keep responses conversational and warm, not clinical or overwhelming

Be present, empathetic, and create a judgment-free space for authentic conversation. Use personality traits: {', '.join(traits)}."""

        # Entry-specific conversation (with journal entry context)
        return f"""You are {companion_name}, a {personality} AI companion and therapeutic listener.

The user wrote this journal entry:
---
{entry_content[:2000]}
---

Have a thoughtful, supportive conversation about this entry using CBT and life coaching techniques:

- Validate their emotions and experiences
- Ask clarifying questions to understand their perspective
- Help identify any thought patterns or cognitive distortions
- Support them in reframing challenges with balanced thinking
- Encourage exploration of feelings with curiosity
- Guide them toward insights and actionable next steps

Be warm, genuine, and create a safe space for them to process their thoughts. Use personality traits: {', '.join(traits)}."""

    def _build_personality(self, traits: List[str]) -> str:
        """Convert list of traits to natural language descriptor."""
        if len(traits) == 1:
            return traits[0].lower()
        elif len(traits) == 2:
            return f"{traits[0].lower()} and {traits[1].lower()}"
        else:
            return f"{', '.join(t.lower() for t in traits[:-1])}, and {traits[-1].lower()}"

    def _get_trait_behaviors(self, traits: List[str]) -> str:
        """Get behavioral instructions for personality traits."""
        trait_map = {
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

        behaviors = [trait_map.get(trait, '') for trait in traits if trait in trait_map]
        return '. '.join(b for b in behaviors if b) + '.'

    def _get_default_reflection_template(self) -> str:
        """Get default reflection template if YAML file not found."""
        return """You are {{companion_name}} {{companion_avatar}}, a {{personality_descriptor}} AI companion for journaling.

{{personality_instructions}}

The user wrote this journal entry ({{word_count}} words):
---
{{user_entry}}
---

Generate a thoughtful response in JSON format with:
1. "reflection": A brief, empathetic reflection (max 500 chars) that shows you understand their experience
2. "question": A curious follow-up question (max 200 chars) that encourages deeper exploration

Be authentic, supportive, and genuinely curious about their inner world."""
