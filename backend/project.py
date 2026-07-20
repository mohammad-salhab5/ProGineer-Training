from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from service import (
    student,
    average_grades,
    add_grades,
    calculate_average,
    printtopstudent,
    class_average,
    remove_student,
    student_report,
    sorted_students,
    save_json,
    load_json
)


class Grade(BaseModel):
    name: str
    grade: int


class StudentName(BaseModel):
    name: str


app = FastAPI()


@app.get("/students")
def get_students():
    return list(student.keys())


@app.get("/students/{name}/grades")
def get_student_grades(name: str):
    if name in student:
        return {
            "name": name,
            "grades": student[name]
        }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


@app.post("/add_grade")
def add_grade(grade: Grade):
    add_grades(student, grade.name, grade.grade)

    return {
        "message": f"Grade {grade.grade} added for student {grade.name}"
    }



@app.get("/average")
def average(data: StudentName):
    avg = calculate_average(student, data.name)

    if avg is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found or no grades available"
        )

    return {
        "name": data.name,
        "average": avg
    }



@app.get("/class_average")
def get_class_average():
    avg = class_average(student)

    if avg is None:
        raise HTTPException(
            status_code=404,
            detail="No students or grades available"
        )

    return {
        "class_average": avg
    }



@app.get("/top_student")
def get_top_student():

    top_student, top_average = printtopstudent(
        student,
        average_grades
    )

    if top_student is None:
        raise HTTPException(
            status_code=404,
            detail="No students available"
        )

    return {
        "top_student": top_student,
        "average": top_average
    }


# تم تعديل status_code هنا
@app.delete("/remove_student/{name}")
def delete_student(name: str):

    if name in student:

        remove_student(
            student,
            average_grades,
            name
        )

        return {
            "message": f"{name} has been removed from the student list."
        }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )



@app.get("/student_report/{name}")
def get_student_report(name: str):

    report = student_report(name)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "report": report
    }



@app.get("/sorted_students")
def get_sorted_students():

    sorted_list = sorted_students(student)

    return [
        {
            "name": name,
            "grades": grades,
            "average": sum(grades) / len(grades)
        }
        for name, grades in sorted_list
    ]



@app.post("/save_json")
def save_students():

    save_json(student)

    return {
        "message": "Data has been saved"
    }



@app.post("/load_json")
def load_students():

    global student

    student = load_json()

    return {
        "message": "Data loaded successfully",
        "students": student
    }