from app.db.session import Base, engine
from app.routes import auth
from app.routes import upload
from app.routes import events
from app.routes import comments
from app.routes import admin
from app.routes import event_on_review
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.include_router(upload.router)

# Статическая раздача медиа
app.mount("/media", StaticFiles(directory="media"), name="media")

Base.metadata.create_all(bind=engine)

app.include_router(events.router)
app.include_router(auth.router)
app.include_router(comments.router)
app.include_router(admin.router)
app.include_router(event_on_review.router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
