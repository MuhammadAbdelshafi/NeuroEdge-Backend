from fastapi import APIRouter, Depends
from app.core.taxonomy.taxonomy_provider import TaxonomyProvider
from app.schemas.api_response import ApiResponse
from typing import List, Dict

router = APIRouter()

@router.get("/", response_model=ApiResponse[dict])
def get_taxonomy():
    data = {
        "subspecialties": TaxonomyProvider.get_subspecialties(),
        "research_types": TaxonomyProvider.get_research_types()
    }
    return ApiResponse(success=True, data=data)
