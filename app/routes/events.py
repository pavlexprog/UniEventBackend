# routers/events.py
# Импорт enum, если вынесен отдельно
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.event import Event
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.routes.auth import get_current_user, get_current_admin
from sqlalchemy import desc, asc
from app.schemas.event import EventCategory


router = APIRouter(prefix="/events", tags=["Мероприятия"])


@router.post("/", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    new_event = Event(**event.dict(), creator_id=current_user.id)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


MAX_LIMIT = 100


@router.get("/", response_model=List[EventOut])
def get_all_events(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=MAX_LIMIT),
    sort_by: str = Query("event_date", enum=["event_date", "created_at"]),
    order: str = Query("asc", enum=["asc", "desc"]),
    category: Optional[EventCategory] = Query(None)
):
    order_func = asc if order == "asc" else desc

    query = db.query(Event)

    if category:
        query = query.filter(Event.category == category)

    if sort_by == "event_date":
        query = query.order_by(order_func(Event.event_date))
    else:
        query = query.order_by(order_func(Event.created_at))

    events = query.offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return event


@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, updated: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    if event.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Нет доступа для редактирования")

    for key, value in updated.dict(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    if event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа для удаления")

    db.delete(event)
    db.commit()
    return {"message": "Мероприятие удалено"}
