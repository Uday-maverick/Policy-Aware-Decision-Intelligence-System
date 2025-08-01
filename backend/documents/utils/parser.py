import re
from django.conf import settings
from typing import Dict

class QueryParser:
    @staticmethod
    def parse(query: str) -> Dict[str, str]:
        entities = {}
        for entity_type in settings.ENTITY_PATTERNS.keys():
            entities[entity_type] = QueryParser._extract_entity(query, entity_type)
        return entities

    @staticmethod
    def _extract_entity(query: str, entity_type: str) -> str:
        pattern = settings.ENTITY_PATTERNS[entity_type]
        match = re.search(pattern, query, re.IGNORECASE)
        if not match:
            return "not specified"
        
        if entity_type == 'procedure':
            return f"{match.group(1)} {match.group(2)}"
        elif entity_type == 'location':
            return match.group(1).strip()
        elif entity_type == 'policy_age':
            return f"{match.group(1)} {match.group(2)}s"
        elif entity_type == 'gender':
            gender = match.group(1).upper()
            return "Male" if gender in ['M', 'MALE'] else "Female"
        return match.group(0)