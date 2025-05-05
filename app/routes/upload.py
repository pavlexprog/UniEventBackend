from fastapi import Depends, UploadFile, File, APIRouter, HTTPException, status
from uuid import uuid4
import os
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
# твоя зависимость для получения авторизованного пользователя
from app.routes.auth import get_current_user


router = APIRouter(prefix="/upload", tags=["Загрузка изображений"])

UPLOAD_DIR = "media"


@router.post("/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка расширения (опционально)
    allowed_exts = {"jpg", "jpeg", "png", "gif", "webp"}
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый формат файла"
        )

    # Генерация имени файла
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, "avatars", filename)

    # Создание папки, если не существует
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Сохраняем файл
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    # Обновляем пользователя в БД
    avatar_url = f"/media/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"url": avatar_url}


@router.post("/upload/event_image")
async def upload_event_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, "events", filename)

    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    return {"url": f"/media/events/{filename}"}
