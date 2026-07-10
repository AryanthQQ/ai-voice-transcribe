import re
from typing import Dict, Any

class Validator:
    """
    Stage 6: Validator
    Ensures the normalized string matches known entity patterns.
    """
    
    def __init__(self):
        # Basic regex patterns for Indian numbers
        self.mobile_pattern = re.compile(r'^(?:(?:\+|00)?91|0)?[6-9]\d{9}$')
        self.landline_pattern = re.compile(r'^0\d{2,4}\d{6,8}$')
        self.toll_free_pattern = re.compile(r'^1800\d{6,7}$')
        self.aadhaar_pattern = re.compile(r'^\d{12}$')
        
    def validate(self, normalized_value: str, context_entity_type: str) -> Dict[str, Any]:
        """
        Validates the string based on its content and context type.
        Returns a dict with 'is_valid', 'inferred_type', 'reason'.
        """
        
        # If context says it's AADHAAR, strictly check Aadhaar length
        if context_entity_type == "AADHAAR":
            is_valid = bool(self.aadhaar_pattern.match(normalized_value))
            return {
                "is_valid": is_valid,
                "inferred_type": "AADHAAR" if is_valid else "INVALID_AADHAAR",
                "reason": "Matches 12 digit format" if is_valid else "Does not match 12 digit format"
            }
            
        # If context says OTP, usually 4 to 8 digits
        if context_entity_type == "OTP":
            is_valid = 4 <= len(normalized_value) <= 8
            return {
                "is_valid": is_valid,
                "inferred_type": "OTP" if is_valid else "INVALID_OTP",
                "reason": "Valid OTP length" if is_valid else f"OTP length {len(normalized_value)} out of bounds"
            }
            
        # Default phone checks if context is PHONE_NUMBER or UNKNOWN
        if self.mobile_pattern.match(normalized_value):
            return {
                "is_valid": True,
                "inferred_type": "PHONE_NUMBER",
                "reason": "Matches standard Indian mobile pattern"
            }
            
        if self.toll_free_pattern.match(normalized_value):
            return {
                "is_valid": True,
                "inferred_type": "TOLL_FREE",
                "reason": "Matches toll-free pattern"
            }
            
        if self.landline_pattern.match(normalized_value):
            return {
                "is_valid": True,
                "inferred_type": "LANDLINE",
                "reason": "Matches landline STD pattern"
            }
            
        # If it's UNKNOWN but looks like a partial number or something else, we could just say False
        return {
            "is_valid": False,
            "inferred_type": context_entity_type,
            "reason": f"Failed validation for length {len(normalized_value)}"
        }
