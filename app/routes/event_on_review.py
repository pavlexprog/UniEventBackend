from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.event import Event
from app.db.models.event_on_review import EventOnReview
from app.schemas.event import EventCreate, EventOut
from app.db.models.user import User
from app.routes.auth import get_current_user, get_current_admin
from typing import List

router = APIRouter(prefix="/event-on-review",
                   tags=["Мероприятие на рассмотрении"])

# Эндпоинт для создания мероприятия (на рассмотрение)


@router.post("/create", response_model=EventOut)
def create_event_on_review(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание мероприятия на рассмотрение (не требует прав администратора).
    Мероприятие сохраняется в таблицу на рассмотрении.
    """
    new_event = EventOnReview(**event.dict(), creator_id=current_user.id)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


# Эндпоинт для получения всех мероприятий на рассмотрении (только для администраторов)
@router.get("/on-review", response_model=List[EventOut])
def get_events_on_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Получить все мероприятия на рассмотрении.
    Доступно только администраторам.
    """
    events_on_review = db.query(EventOnReview).all()
    return events_on_review


# Эндпоинт для одобрения мероприятия
@router.put("/approve/{event_id}", response_model=EventOut)
def approve_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Одобрить мероприятие и переместить его в основную таблицу мероприятий.
    """
    event_on_review = db.query(EventOnReview).filter(
        EventOnReview.id == event_id).first()
    if not event_on_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено"
        )

    # Переносим в основную таблицу
    new_event = Event(
        title=event_on_review.title,
        description=event_on_review.description,
        event_date=event_on_review.event_date,
        category=event_on_review.category,
        creator_id=event_on_review.creator_id
    )
    db.add(new_event)
    db.commit()

    # Удаляем из таблицы на рассмотрении
    db.delete(event_on_review)
    db.commit()

    return new_event


# Эндпоинт для отклонения мероприятия
@router.put("/reject/{event_id}")
def reject_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Отклонить мероприятие и удалить его из таблицы на рассмотрении.
    """
    event_on_review = db.query(EventOnReview).filter(
        EventOnReview.id == event_id).first()
    if not event_on_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено"
        )

    # Удаляем мероприятие из таблицы на рассмотрении
    db.delete(event_on_review)
    db.commit()

    return {"detail": "Мероприятие отклонено и удалено из рассмотрения."}


# Эндпоинт для редактирования мероприятия на рассмотрении
@router.put("/edit/{event_id}", response_model=EventOut)
def edit_event_on_review(
    event_id: int,
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Редактирование мероприятия на рассмотрении.
    """
    event_on_review = db.query(EventOnReview).filter(
        EventOnReview.id == event_id).first()
    if not event_on_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено"
        )

    # Проверяем, что текущий пользователь — создатель мероприятия
    if event_on_review.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для редактирования этого мероприятия"
        )

    # Обновляем информацию
    for key, value in event.dict().items():
        setattr(event_on_review, key, value)

    db.commit()
    db.refresh(event_on_review)

    return event_on_review
