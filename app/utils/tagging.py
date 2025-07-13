from typing import List


def extract_tags_from_response(response: str) -> List[str]:
    """Extract tags from LLM response based on content analysis"""
    tags = []
    
    # Simple keyword-based tagging
    keywords = {
        "technical": ["error", "bug", "code", "programming", "technical", "implementation"],
        "billing": ["payment", "billing", "invoice", "cost", "price", "subscription"],
        "support": ["help", "support", "assistance", "issue", "problem"],
        "feature": ["feature", "functionality", "capability", "new", "enhancement"],
        "general": ["hello", "hi", "thanks", "thank you", "goodbye"]
    }
    
    response_lower = response.lower()
    for tag, words in keywords.items():
        if any(word in response_lower for word in words):
            tags.append(tag)
    
    # Default tag if none found
    if not tags:
        tags.append("general")
    
    return tags