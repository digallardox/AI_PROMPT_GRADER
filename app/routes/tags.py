"""Tag extraction endpoint using Named Entity Recognition."""
from fastapi import APIRouter, Body
from app.models import TagsRequest, TagsResponse
from app.dependencies import NERDep

router = APIRouter(tags=["tags"])


@router.post("/tags", response_model=TagsResponse)
async def generate_tags(
    ner: NERDep,
    req: TagsRequest = Body(...),
):
    """
    Extract named entities/tags from journal entry content using Claude API.

    Args:
        ner: NER service (injected)
        req: Tags request containing entry content

    Returns:
        TagsResponse: List of extracted named entities/tags
    """
    # Extract tags using Claude-based NER service
    tags = await ner.extract_tags(req.content)

    return TagsResponse(tags=tags)