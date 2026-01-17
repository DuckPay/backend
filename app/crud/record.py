from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.record import Record
from app.schemas.record import RecordCreate, RecordUpdate

# Get records by user_id
def get_records(db: Session, user_id: int, skip: int = 0, limit: int = 100, start_date: datetime = None, end_date: datetime = None, type: str = None):
    query = db.query(Record).filter(Record.user_id == user_id)
    
    if start_date:
        query = query.filter(Record.date >= start_date)
    if end_date:
        query = query.filter(Record.date <= end_date)
    if type:
        query = query.filter(Record.type == type)
    
    return query.offset(skip).limit(limit).all()

# Get record by id
def get_record(db: Session, record_id: int, user_id: int):
    return db.query(Record).filter(Record.id == record_id, Record.user_id == user_id).first()

# Create record
def create_record(db: Session, record: RecordCreate, user_id: int):
    db_record = Record(
        **record.model_dump(),
        user_id=user_id
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# Update record
def update_record(db: Session, record_id: int, record: RecordUpdate, user_id: int):
    db_record = get_record(db, record_id, user_id)
    if db_record:
        update_data = record.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_record, field, value)
        db.commit()
        db.refresh(db_record)
    return db_record

# Delete record
def delete_record(db: Session, record_id: int, user_id: int):
    db_record = get_record(db, record_id, user_id)
    if db_record:
        db.delete(db_record)
        db.commit()
        return True
    return False
