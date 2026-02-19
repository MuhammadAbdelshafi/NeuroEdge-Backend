from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db.repositories.paper_repo import PaperRepository
from app.schemas.api_response import ApiResponse
from app.schemas.paper import PaperResponse, PapersListResponse
# Fix import path
from app.api.deps import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.get("/", response_model=ApiResponse[PapersListResponse])
def get_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of research papers.
    """
    repo = PaperRepository(db)
    papers = repo.list_papers(skip=skip, limit=limit)
    total = repo.count_papers()
    
    return ApiResponse(
        success=True,
        data=PapersListResponse(
            papers=papers,
            total=total,
            page=(skip // limit) + 1,
            size=limit
        ),
        message="Papers retrieved successfully"
    )

@router.get("/{paper_id}", response_model=ApiResponse[PaperResponse])
def get_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific paper by ID.
    """
    # Note: paper_repo currently references ID but basic lookup might need addition if not present
    # Using direct query for now or add get_by_id to repo
    # Let's check repo capabilities from previous context
    # It has get_by_id implicit in update_status but explicit get methods are by doi/pmid
    # We will implement a quick lookup
    repo = PaperRepository(db)
    # Using private access or adding a method. For now let's reuse get_by_doi logic pattern but for id
    paper = db.query(repo.db.models.paper.Paper).filter(repo.db.models.paper.Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
        
    return ApiResponse(
        success=True,
        data=paper,
        message="Paper details retrieved"
    )
