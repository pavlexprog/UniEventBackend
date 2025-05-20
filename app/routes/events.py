# routers/events.py
# Импорт enum, если вынесен отдельно
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Query, Form, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.favorite import Favorite
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.event import Event
from app.schemas.common import UserOut
from app.schemas.event import EventCreate, EventOut, EventRead, EventUpdate
from app.routes.auth import get_current_user, get_current_admin
from sqlalchemy import desc, asc
from app.schemas.event import EventCategory
from sqlalchemy.orm import joinedload


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
    category: Optional[EventCategory] = Query(None),
     is_approved: Optional[bool] = Query(None)
    
):
    order_func = asc if order == "asc" else desc

    query = db.query(Event)

    if category:
        query = query.filter(Event.category == category)
    if is_approved is not None:  # 👈 добавь фильтрацию по статусу
        query = query.filter(Event.is_approved == is_approved)

    if sort_by == "event_date":
        query = query.order_by(order_func(Event.event_date))
    else:
        query = query.order_by(order_func(Event.created_at))

    events = query.options(joinedload(Event.participants)).offset(skip).limit(limit).all()

# добавляем participants_count вручную
    result = [
    EventOut.from_orm(event).model_copy(update={
        "participants_count": len(event.participants)
    })
    for event in events
]
    return result

@router.get("/favorites", response_model=list[EventOut])
def get_favorites(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    favorites = (
        db.query(Event)
        .join(Favorite, Favorite.event_id == Event.id)
        .filter(Favorite.user_id == user.id)
        .all()
    )
    return favorites

@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = (
        db.query(Event)
        .options(joinedload(Event.creator), joinedload(Event.participants))
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    
    is_favorite = (
        db.query(Favorite)
        .filter_by(user_id=current_user.id, event_id=event.id)
        .first() is not None
        
    )

    # Используем from_orm и дополняем вычисляемыми полями
    return EventRead.from_orm(event).model_copy(update={
        "joined": current_user in event.participants,
        "participants_count": len(event.participants),
        "is_favorite": is_favorite,
    })



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

@router.get("/by-user/{user_id}", response_model=List[EventOut])
def get_events_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Event).filter(Event.creator_id == user_id).all()

@router.post("/{event_id}/attend")
def attend_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    if current_user in event.participants:
        raise HTTPException(status_code=400, detail="Вы уже записались")

    event.participants.append(current_user)
    db.commit()
    return {"detail": "Успешно записались на мероприятие"}


@router.get("/{event_id}/participants", response_model=List[UserOut])
def get_event_participants(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return event.participants

@router.post("/{event_id}/cancel")
def cancel_attendance(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    if current_user not in event.participants:
        raise HTTPException(status_code=400, detail="Вы не записаны")

    event.participants.remove(current_user)
    db.commit()
    return {"detail": "Вы отменили участие"}

@router.post("/{event_id}/favorite")
def add_favorite(event_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter_by(user_id=user.id, event_id=event_id).first()
    if favorite:
        raise HTTPException(status_code=400, detail="Уже в избранном")
    db.add(Favorite(user_id=user.id, event_id=event_id))
    db.commit()
    return {"status": "added"}


@router.post("/{event_id}/unfavorite")
def remove_favorite(event_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter_by(user_id=user.id, event_id=event_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Не в избранном")
    db.delete(favorite)
    db.commit()
    return {"status": "removed"}

