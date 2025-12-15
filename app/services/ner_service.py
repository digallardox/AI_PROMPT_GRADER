"""NER (Named Entity Recognition) service for tag extraction."""
from flair.models import SequenceTagger
from flair.data import Sentence
from typing import List
import logging

logger = logging.getLogger(__name__)


class NERService:
    """Service for extracting named entities/tags from text using Flair NER."""

    def __init__(self):
        """
        Initialize NER service by loading the Flair NER model.

        The model is loaded once at initialization to avoid reloading
        on every request, which would be very slow.

        Raises:
            Exception: If model fails to load
        """
        try:
            logger.info("Loading Flair NER model (flair/ner-english-large)...")
            self.ner_tagger = SequenceTagger.load("flair/ner-english-large")
            logger.info("Flair NER model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Flair NER model: {e}")
            raise

    def extract_tags(self, content: str) -> List[str]:
        """
        Extract named entities from text content.

        Args:
            content: Text content to extract entities from

        Returns:
            List of extracted entity strings (deduplicated)

        Raises:
            Exception: If NER prediction fails
        """
        try:
            # Create Flair Sentence object
            text = Sentence(content)

            # Run NER prediction
            self.ner_tagger.predict(text)

            # Extract entity texts and deduplicate
            tags = [entity.text for entity in text.get_spans('ner')]

            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)

            return unique_tags

        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            raise
