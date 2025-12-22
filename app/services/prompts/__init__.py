from typing import List
from app.services.prompts.reflection_prompt_builder import ReflectionPromptBuilder
from app.services.prompts.chat_prompt_builder import ChatPromptBuilder
from app.services.prompts.personality import PersonalityManager


class PromptService:

    def __init__(self):
        self.reflection_builder = ReflectionPromptBuilder()
        self.chat_builder = ChatPromptBuilder()

    def build_reflection_prompt(
        self,
        companion_name: str,
        traits: List[str],
        content: str
    ) -> str:
        return self.reflection_builder.build(companion_name, traits, content)

    def build_chat_prompt(
        self,
        companion_name: str,
        traits: List[str],
        entry_content: str = ""
    ) -> str:
        return self.chat_builder.build(companion_name, traits, entry_content)


# Export all components for direct access if needed
__all__ = [
    'PromptService',
    'ReflectionPromptBuilder',
    'ChatPromptBuilder',
    'PersonalityManager',
]
