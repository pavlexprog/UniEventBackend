from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.comment import Comment
from app.db.models.event import Event
from app.db.models.user import User
# import Comment, Event, User
from app.schemas.comment import CommentCreate, CommentRead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/comments", tags=["Комментарии"])


@router.post("/", response_model=CommentRead)
def create_comment(comment_in: CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Проверим, что мероприятие существует
    event = db.query(Event).filter(Event.id == comment_in.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    comment = Comment(
        text=comment_in.text,
        user_id=user.id,
        event_id=comment_in.event_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/event/{event_id}", response_model=list[CommentRead])
def get_comments_for_event(event_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.event_id == event_id).order_by(Comment.created_at.desc()).all()


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.user_id == user.id).first()
    if not comment:
        raise HTTPException(
            status_code=404, detail="Комментарий не найден или нет доступа")
    db.delete(comment)
    db.commit()
