from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserRead
from app.routes.auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["Админ"])


@router.put("/assign-admin/{user_id}", response_model=UserRead)
def assign_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Назначить пользователя администратором
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Проверяем, что текущий пользователь - администратор
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для назначения администратора"
        )

    # Назначаем пользователя администратором
    user.is_admin = True
    db.commit()
    db.refresh(user)

    return user


@router.put("/revoke-admin/{user_id}", response_model=UserRead)
def revoke_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Забрать права администратора у пользователя
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if user.id == current_user.id:
        raise HTTPException(
            400, "Нельзя убрать привелегии администратора себе!")
    # Проверяем, что текущий пользователь - администратор
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для снятия прав администратора"
        )

    # Забираем права администратора у пользователя
    user.is_admin = False
    db.commit()
    db.refresh(user)

    return user
