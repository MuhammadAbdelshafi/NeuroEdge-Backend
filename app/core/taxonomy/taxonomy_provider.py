import json
import os
from typing import List, Dict, Optional
from app.config.settings import settings

class TaxonomyProvider:
    _subspecialties: List[Dict[str, str]] = []
    _research_types: List[Dict[str, str]] = []
    
    _subspecialties_map: Dict[str, str] = {}
    _research_types_map: Dict[str, str] = {}
    
    @classmethod
    def load_taxonomy(cls):
        base_path = os.path.join(os.getcwd(), "config")
        
        with open(os.path.join(base_path, "subspecialties.json"), "r") as f:
            cls._subspecialties = json.load(f)
            cls._subspecialties_map = {item["id"]: item["label"] for item in cls._subspecialties}
            
        with open(os.path.join(base_path, "research_types.json"), "r") as f:
            cls._research_types = json.load(f)
            cls._research_types_map = {item["id"]: item["label"] for item in cls._research_types}

    @classmethod
    def get_subspecialties(cls) -> List[Dict[str, str]]:
        if not cls._subspecialties:
            cls.load_taxonomy()
        return cls._subspecialties

    @classmethod
    def get_research_types(cls) -> List[Dict[str, str]]:
        if not cls._research_types:
            cls.load_taxonomy()
        return cls._research_types

    @classmethod
    def is_valid_subspecialty(cls, sub_id: str) -> bool:
        if not cls._subspecialties:
            cls.load_taxonomy()
        return sub_id in cls._subspecialties_map

    @classmethod
    def is_valid_research_type(cls, type_id: str) -> bool:
        if not cls._research_types:
            cls.load_taxonomy()
        return type_id in cls._research_types_map
