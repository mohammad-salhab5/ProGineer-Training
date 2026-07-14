from os import name, stat
import json
from fastapi import FastAPI
from fastapi import HTTPException



student={}
average_grades={}

from pydantic import BaseModel

class Grade(BaseModel):
    name: str
    grade: int

def add_grades(student, name, grade):
    if name not in student:
        student[name] = []
    if grade > 0 and grade <= 100:
        student[name].append(grade)
    else:
        raise HTTPException(status_code=400, detail="Grade must be between 0 and 100") 

app = FastAPI()

@app.get("/students")
def get_students():
    return list(student.keys())

@app.get("/students/{name}/grades")
def get_student_grades(name: str):
    if name in student:
        return {"name": name, "grades": student[name]}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.post("/add_grade")
def add_grade(grade: Grade):
    add_grades(student, grade.name, grade.grade)
    return {"message": f"Grade {grade.grade} added for student {grade.name}"}

class StudentName(BaseModel):
    name: str


def calculate_average(student, name):
    try:

     return   sum(student[name]) / len(student[name])   
     
      
    except (KeyError, ZeroDivisionError):
     
        return None

@app.post("/average")
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



def class_average(student):
    average_list = []
    
    try:
        for name in student:
            avg = sum(student[name]) / len(student[name])
            average_list.append(avg)
        return sum(average_list) / len(average_list)
    except (KeyError, ZeroDivisionError):
        return None

  
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


 



def printtopstudent(student, average_grades):
    for name in student:
        average_grades[name] = sum(student[name]) / len(student[name])
    top_student = max(average_grades, key=average_grades.get)
    return top_student, average_grades[top_student]


@app.get("/top_student")
def get_top_student():
    top_student, top_average = printtopstudent(student, average_grades)
    return {
        "top_student": top_student,
        "average": top_average
    }







def remove_student(student, name):
    if name in student:
        del student[name]
       

@app.delete("/remove_student/{name}", status_code=204)
def delete_student(name: str):
    if name in student:
        remove_student(student, name)
        return {"message": f"{name} has been removed from the student list."}
    else:
        raise HTTPException(status_code=404, detail="Student not found")



def student_report(student):
    for name in student:
        avg = sum(student[name]) / len(student[name])
        grades = student[name]
        report = f"{name}: {grades}, Average: {avg}"
        return report





@app.get("/student_report/{name}")
def get_student_report(name: str):
    if name in student:
        report = student_report(student)
        return {"report": report}
    else:
        raise HTTPException(status_code=404, detail="Student not found")










def sorted_students(student):
    sorted_list = sorted(student.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)

    return sorted_list  

@app.get("/sorted_students")
def get_sorted_students():
    sorted_list = sorted_students(student)
    return [{"name": name, "grades": grades, "average": sum(grades) / len(grades)} for name, grades in sorted_list]




def letter_grade(score) :
    if score < 0 or score > 100:
        return "Invalid score. Please enter a score between 0 and 100."
    if score >= 90:
        return "A"
    elif score >= 80 and score < 90:
        return "B"
    elif score >= 70 and score < 80:
        return "C"
    elif score >= 60 and score < 70:
        return "D"
    else:
        return "F"
      




    
          




 







with open("student.json", "w") as f:

    json.dump(student, f)



with open("student.json", "r") as f:

    loaded_student = json.load(f)






response = {

    "choices": [

        {

            "message": {

                "role": "assistant",
                "role2": "system",

                "content": "Photosynthesis converts sunlight into energy."

            }

        }

    ]

}







 