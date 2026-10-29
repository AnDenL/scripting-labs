from contextlib import asynccontextmanager

from fastapi import FastAPI

from labs.lab3.database import initialize_database
from labs.lab3.routers import categories, records
from shared import student


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Channel Load Tracking API",
    description="API for tracking load of channels, measure unit %",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/student")
def get_student_info():
    return {
        "student_name": student.STUDENT_NAME,
        "group_name": student.GROUP_NAME,
        "variant_number": student.VARIANT_NUMBER,
    }
