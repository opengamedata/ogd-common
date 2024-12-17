"""Config Class Module
"""
## import standard libraries
from typing import Any, Dict
# import local files
from ogd.common.schemas.Schema import Schema

class Config(Schema):
    """Thin layer over Schema base class to act as a base for all our Config-type classes.
    """
    
    def __init__(self, name: str, other_elements: Dict[str, Any] | None = None):
        super().__init__(name, other_elements)