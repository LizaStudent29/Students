from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from student_db import StudentDB, Student

app = FastAPI()
db = StudentDB()

# Pydantic модель для валидации данных при создании и обновлении
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

@app.post("/students/")
def create_student(student: StudentIn):
    db.insert_student(
        last_name=student.last_name,
        first_name=student.first_name,
        faculty=student.faculty,
        course=student.course,
        score=student.score
    )
    return {"message": "Студент добавлен"}

@app.get("/students/", response_model=List[str])
def get_all_students():
    students = db.get_all_students()
    return [repr(s) for s in students]

@app.get("/students/faculty/{faculty_name}", response_model=List[str])
def get_by_faculty(faculty_name: str):
    return [repr(s) for s in db.get_students_by_faculty(faculty_name)]

@app.get("/students/courses/unique", response_model=List[str])
def get_unique_courses():
    return db.get_unique_courses()

@app.get("/students/faculty/{faculty_name}/average_score")
def avg_score(faculty_name: str):
    return {"faculty": faculty_name, "avg_score": db.get_avg_score_by_faculty(faculty_name)}

@app.get("/students/course/{course_name}/low_score", response_model=List[str])
def students_low_score(course_name: str):
    return [repr(s) for s in db.get_students_by_course_low_score(course_name, threshold=30)]

@app.put("/students/{student_id}")
def update_student(student_id: int, update: StudentUpdate):
    updated = db.update_student(
        student_id,
        last_name=update.last_name,
        first_name=update.first_name,
        faculty=update.faculty,
        course=update.course,
        score=update.score
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"message": "Студент обновлен", "student": repr(updated)}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    success = db.delete_student_by_id(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"message": "Студент удален"}

