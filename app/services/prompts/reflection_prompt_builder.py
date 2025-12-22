from typing import List
from app.services.prompts.base import BasePromptBuilder
from app.services.prompts.personality import PersonalityManager


class ReflectionPromptBuilder(BasePromptBuilder):

    def build(
        self,
        companion_name: str,
        traits: List[str],
        content: str
    ) -> str:
        # Load template (with fallback to default)
        template = self._load_template("reflection.yaml", self._get_default_template())

        # Build personality components
        personality_descriptor = PersonalityManager.build_personality_descriptor(traits)
        personality_instructions = PersonalityManager.get_trait_behaviors(traits)

        # Truncate content to prevent oversized prompts
        truncated_content = content[:2000]
        word_count = len(content.split())

        # Substitute all variables
        prompt = self._substitute_variables(
            template,
            companion_name=companion_name,
            companion_avatar="🐨",  # Could be made configurable
            personality_descriptor=personality_descriptor,
            personality_instructions=personality_instructions,
            user_entry=truncated_content,
            word_count=word_count
        )

        return prompt

    def _get_default_template(self) -> str:
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
