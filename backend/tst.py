from fastapi import FastAPI
from pydantic import BaseModel

# إنشاء التطبيق
app = FastAPI()

# قاعدة بيانات مؤقتة (List)
students = []

# نموذج البيانات
class Student(BaseModel):
    id: int
    name: str
    age: int


# الصفحة الرئيسية
@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}


# إرجاع جميع الطلاب
@app.get("/students")
def get_students():
    return students


# إرجاع طالب حسب الـ id
@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    return {"error": "Student not found"}


# إضافة طالب جديد
@app.post("/students")
def add_student(student: Student):
    students.append(student.model_dump())
    return {
        "message": "Student added successfully",
        "student": student
    }