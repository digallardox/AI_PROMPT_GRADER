"""Chat conversation endpoint."""
from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.dependencies import ClaudeDep, PromptDep

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_about_entry(
    req: ChatRequest,
    claude: ClaudeDep,
    prompts: PromptDep,
):
    """
    Have a conversation about a specific journal entry.

    Args:
        req: Chat request containing entry context, message, history, and companion settings
        claude: Claude service (injected)
        prompts: Prompt service (injected)

    Returns:
        ChatResponse: Assistant's response message
    """
    # Build system prompt with entry context
    system_prompt = prompts.build_chat_prompt(
        companion_name=req.companion.name,
        traits=req.companion.traits,
        entry_content=req.entryContent
    )

    # Format conversation history for Claude
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in req.history
    ]
    messages.append({"role": "user", "content": req.message})

    # Call Claude with conversation history
    response = await claude.chat(system_prompt, messages)

    return ChatResponse(
        message={"role": "assistant", "content": response}
    )
