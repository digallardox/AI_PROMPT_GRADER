"""Title generation endpoint."""
from fastapi import APIRouter
from app.models import TitleRequest, TitleResponse
from app.dependencies import ClaudeDep

router = APIRouter(tags=["title"])


@router.post("/title", response_model=TitleResponse)
async def generate_title(
    req: TitleRequest,
    claude: ClaudeDep,
):
    """
    Generate a concise title for journal entry.

    Args:
        req: Title request containing entry content
        claude: Claude service (injected)

    Returns:
        TitleResponse: Generated title (5-10 words)
    """
    prompt = "Generate a concise 5-10 word title for this journal entry. Return only the title, nothing else."

    # Call Claude with truncated content
    content = req.content[:1500]
    response = await claude.chat(prompt, content)

    return TitleResponse(title=response.strip())
