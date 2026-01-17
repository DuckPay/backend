from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.utils.database import get_db
from app.utils.auth import get_current_user
from app.crud.record import get_records, get_record, create_record, update_record, delete_record
from app.schemas.record import Record, RecordCreate, RecordUpdate, RecordWithCategory
from app.models.user import User

# Create router
router = APIRouter()

# Get all records
@router.get("/", response_model=List[Record])
def read_records(
    skip: int = 0,
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None,
    type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_records(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        type=type
    )

# Get record by ID
@router.get("/{record_id}", response_model=Record)
def read_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_record = get_record(db=db, record_id=record_id, user_id=current_user.id)
    if db_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )
    return db_record

# Create record
@router.post("/", response_model=Record, status_code=status.HTTP_201_CREATED)
def create_new_record(
    record: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_record(db=db, record=record, user_id=current_user.id)

# Update record
@router.post("/update/{record_id}", response_model=Record)
def update_existing_record(
    record_id: int,
    record: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_record = update_record(db=db, record_id=record_id, record=record, user_id=current_user.id)
    if db_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )
    return db_record

# Delete record
@router.post("/delete/{record_id}", status_code=status.HTTP_200_OK)
def delete_existing_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_record(db=db, record_id=record_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )
    return {"status": "success", "message": "Record deleted successfully"}
