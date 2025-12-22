from typing import List
from app.services.prompts.base import BasePromptBuilder
from app.services.prompts.personality import PersonalityManager


class ChatPromptBuilder(BasePromptBuilder):

    def build(
        self,
        companion_name: str,
        traits: List[str],
        entry_content: str = ""
    ) -> str:
        personality_descriptor = PersonalityManager.build_personality_descriptor(traits)
        traits_list = ', '.join(traits)

        # Global conversation (no entry context)
        if not entry_content or entry_content.strip() == "":
            return self._build_global_chat_prompt(
                companion_name,
                personality_descriptor,
                traits_list
            )

        # Entry-specific conversation (with journal entry context)
        return self._build_entry_chat_prompt(
            companion_name,
            personality_descriptor,
            traits_list,
            entry_content
        )

    def _build_global_chat_prompt(
        self,
        companion_name: str,
        personality_descriptor: str,
        traits_list: str
    ) -> str:
        return f"""You are {companion_name}, a {personality_descriptor} AI companion and therapeutic listener.

Your role is to provide a safe, supportive space for the user to explore their thoughts, feelings, and experiences. Act as a compassionate life coach and therapist who uses professional CBT and life coaching techniques:

- Help identify thought patterns, cognitive distortions, and limiting beliefs
- Support reframing negative thoughts into more balanced perspectives
- Guide users toward clarity, insight, and actionable goals
- Keep responses conversational and warm, not clinical or overwhelming

Be present, empathetic, and create a judgment-free space for authentic conversation. Use personality traits: {traits_list}."""

    def _build_entry_chat_prompt(
        self,
        companion_name: str,
        personality_descriptor: str,
        traits_list: str,
        entry_content: str
    ) -> str:
        # Truncate content to prevent oversized prompts
        truncated_content = entry_content[:2000]

        return f"""You are {companion_name}, a {personality_descriptor} AI companion and therapeutic listener.

The user wrote this journal entry:
---
{truncated_content}
---

Have a thoughtful, supportive conversation about this entry using CBT and life coaching techniques:

- Validate their emotions and experiences
- Ask clarifying questions to understand their perspective
- Help identify any thought patterns or cognitive distortions
- Support them in reframing challenges with balanced thinking
- Encourage exploration of feelings with curiosity
- Guide them toward insights and actionable next steps

Be warm, genuine, and create a safe space for them to process their thoughts. Use personality traits: {traits_list}."""
