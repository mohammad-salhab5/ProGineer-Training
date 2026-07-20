
from fastapi import FastAPI
import json

app = FastAPI()


class StudentService:

    def __init__(self):
        self.students = {}

    def add_grade(self, name, grade):

        if name not in self.students:
            self.students[name] = []

        if 0 <= grade <= 100:
            self.students[name].append(grade)
            return {"message": "Grade added successfully"}
    
        return {"error": "Grade must be between 0 and 100"}

    def calculate_average(self, name):

        if name not in self.students:
            return {"error": "Student not found"}

        grades = self.students[name]

        if len(grades) == 0:
            return {"average": None}

        return {
            "student": name,
            "average": sum(grades) / len(grades)
        }

    def remove_student(self, name):

        if name in self.students:
            del self.students[name]
            return {"message": "Student removed"}

        return {"error": "Student not found"}

    def top_student(self):

        top_name = None
        top_average = -1

        for name, grades in self.students.items():

            if len(grades) == 0:
                continue

            average = sum(grades) / len(grades)

            if average > top_average:
                top_average = average
                top_name = name

        return {
            "student": top_name,
            "average": top_average
        }

    def class_average(self):

        total = 0
        count = 0

        for grades in self.students.values():
            total += sum(grades)
            count += len(grades)

        if count == 0:
            return {"average": None}

        return {"average": total / count}

    def student_report(self, name):

        if name not in self.students:
            return {"error": "Student not found"}

        grades = self.students[name]
        avg = sum(grades) / len(grades)

        return {
            "student": name,
            "grades": grades,
            "average": avg
        }

    def sort_average(self):

        averages = sorted(
            self.students.items(),
            key=lambda item: sum(item[1]) / len(item[1]),
            reverse=True
        )

        return [name for name, grades in averages]

    def letter_grade(self, score):

        if score < 0 or score > 100:
            return {"Invalid score. Please enter a score between 0 and 100."}

        if score >= 90:
            return {"A"}
        elif score >= 80 and score <= 89:
            return {"B"}
        elif score >= 70 and score <= 79:
            return {"C"}
        elif score >= 60 and score <= 69:
            return {"D"}
        else:
            return {"F"}

    def save(self):

        with open("students.json", "w") as f:
            json.dump(self.students, f)

        return {"message": "Saved"}

    def load(self):

        with open("students.json", "r") as f:
            self.students = json.load(f)

        return self.students


service = StudentService()


@app.post("/add_grade")
def add_grade(name: str, grade: int):
    return service.add_grade(name, grade)


@app.get("/average/{name}")
def average(name: str):
    return service.calculate_average(name)


@app.delete("/student/{name}")
def delete_student(name: str):
    return service.remove_student(name)


@app.get("/top_student")
def top_student():
    return service.top_student()


@app.get("/class_average")
def class_average():
    return service.class_average()


@app.get("/report/{name}")
def report(name: str):
    return service.student_report(name)


@app.get("/sort")
def sort_students():
    return service.sort_average()



@app.post("/save")
def save():
    return service.save()


@app.post("/load")
def load():
    return service.load()