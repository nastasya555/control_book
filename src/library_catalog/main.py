from fastapi import FastAPI, APIRouter
import uvicorn
from .api.routers.books import book_router


app = FastAPI(title="control_book")


main_api_router = APIRouter()
main_api_router.include_router(book_router, prefix="/books", tags=["books"])
app.include_router(main_api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
