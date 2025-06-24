from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from fastapi.openapi.utils import get_openapi
import csv
import json
import redis.asyncio as redis
from fastapi import BackgroundTasks, UploadFile, File
from student_db import StudentDB, Student
from auth import router as auth_router, get_current_user

# -------------------
# Инициализация
# -------------------
app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])

db = StudentDB()
redis_client = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)

# -------------------
# Pydantic модели
# -------------------
class StudentIn(BaseModel):
    last_name: str
    first_name: str
    faculty: str
    course: str
    score: int

class StudentUpdate(BaseModel):
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    faculty: Optional[str] = None
    course: Optional[str] = None
    score: Optional[int] = None

class DeleteStudentsIn(BaseModel):
    ids: List[int]

# -------------------
# Фоновые задачи
# -------------------
def load_csv_to_db(csv_path: str):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            db.insert_student(
                last_name=row["last_name"],
                first_name=row["first_name"],
                faculty=row["faculty"],
                course=row["course"],
                score=int(row["score"])
            )

def delete_students_by_ids(ids: List[int]):
    for student_id in ids:
        db.delete_student_by_id(student_id)

# -------------------
# Кеширование (Redis)
# -------------------
CACHE_EXPIRE_SECONDS = 60

async def get_cached(key: str):
    data = await redis_client.get(key)
    return json.loads(data) if data else None

async def set_cache(key: str, value, expire: int = CACHE_EXPIRE_SECONDS):
    await redis_client.set(key, json.dumps(value), ex=expire)

# -------------------
# Эндпойнты: Students
# -------------------
@app.post("/students/", tags=["students"])
def create_student(student: StudentIn, user: dict = Depends(get_current_user)):
    db.insert_student(**student.dict())
    return {"message": "Студент добавлен"}

@app.put("/students/{student_id}", tags=["students"])
def update_student(student_id: int, update: StudentUpdate, user: dict = Depends(get_current_user)):
    updated = db.update_student(student_id, **update.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"message": "Студент обновлён", "student": repr(updated)}

@app.delete("/students/{student_id}", tags=["students"])
def delete_student(student_id: int, user: dict = Depends(get_current_user)):
    if not db.delete_student_by_id(student_id):
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"message": "Студент удалён"}

@app.post("/students/load_csv/")
async def load_students_from_csv(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    content = await file.read()
    tmp_path = "/tmp/uploaded_students.csv"
    with open(tmp_path, "wb") as f:
        f.write(content)

    background_tasks.add_task(load_csv_to_db, tmp_path)

    return {"message": f"Запуск загрузки данных из файла {file.filename} в фоне"}

@app.delete("/students/batch_delete/", tags=["students"])
def batch_delete_students(payload: DeleteStudentsIn, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    background_tasks.add_task(delete_students_by_ids, payload.ids)
    return {"message": f"Удаление студентов с ID {payload.ids} запущено в фоне"}

# -------------------
# Эндпойнты: Чтение с кешом
# -------------------
@app.get("/students/", response_model=List[str], tags=["students"])
async def get_all_students(user: dict = Depends(get_current_user)):
    cache_key = "students:all"
    if cached := await get_cached(cache_key):
        return cached
    students = [repr(s) for s in db.get_all_students()]
    await set_cache(cache_key, students)
    return students

@app.get("/students/faculty/{faculty_name}", response_model=List[str], tags=["students"])
async def get_by_faculty(faculty_name: str, user: dict = Depends(get_current_user)):
    cache_key = f"students:faculty:{faculty_name}"
    if cached := await get_cached(cache_key):
        return cached
    result = [repr(s) for s in db.get_students_by_faculty(faculty_name)]
    await set_cache(cache_key, result)
    return result

@app.get("/students/courses/unique", response_model=List[str], tags=["students"])
async def get_unique_courses(user: dict = Depends(get_current_user)):
    cache_key = "students:courses:unique"
    if cached := await get_cached(cache_key):
        return cached
    result = db.get_unique_courses()
    await set_cache(cache_key, result)
    return result

@app.get("/students/faculty/{faculty_name}/average_score", tags=["students"])
async def avg_score(faculty_name: str, user: dict = Depends(get_current_user)):
    cache_key = f"students:faculty:{faculty_name}:avg_score"
    if cached := await get_cached(cache_key):
        return cached
    avg = db.get_avg_score_by_faculty(faculty_name)
    result = {"faculty": faculty_name, "avg_score": avg}
    await set_cache(cache_key, result)
    return result

@app.get("/students/course/{course_name}/low_score", response_model=List[str], tags=["students"])
async def students_low_score(course_name: str, user: dict = Depends(get_current_user)):
    cache_key = f"students:course:{course_name}:low_score"
    if cached := await get_cached(cache_key):
        return cached
    result = [repr(s) for s in db.get_students_by_course_low_score(course_name, threshold=30)]
    await set_cache(cache_key, result)
    return result

# -------------------
# Прочее
# -------------------
@app.get("/protected", tags=["auth"])
def protected(user: dict = Depends(get_current_user)):
    return {"message": f"Привет, {user['username']}! Доступ разрешён."}

# -------------------
# Кастомное OpenAPI
# -------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Student DB API",
        version="1.0.0",
        description="API с JWT авторизацией",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi
