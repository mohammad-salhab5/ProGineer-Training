
from fastapi import HTTPException


student={}
average_grades={}

def add_grades(student, name, grade):
    if name not in student:
        student[name] = []
    if grade > 0 and grade <= 100:
        student[name].append(grade)
    else:
        raise HTTPException(status_code=400, detail="Grade must be between 0 and 100") 
    

    
def calculate_average(student, name):
    try:

     return   sum(student[name]) / len(student[name])   
     
      
    except (KeyError, ZeroDivisionError):
     
        return None
    

def class_average(student):
    average_list = []
    
    try:
        for name in student:
            avg = sum(student[name]) / len(student[name])
            average_list.append(avg)
        return sum(average_list) / len(average_list)
    except (KeyError, ZeroDivisionError):
        return None



def printtopstudent(student, average_grades):
    for name in student:
        average_grades[name] = sum(student[name]) / len(student[name])
    top_student = max(average_grades, key=average_grades.get)
    return top_student, average_grades[top_student]



def remove_student(student, name):
    if name in student:
        del student[name]





def student_report(student):
    for name in student:
        avg = sum(student[name]) / len(student[name])
        grades = student[name]
        report = f"{name}: {grades}, Average: {avg}"
        return report
    


def sorted_students(student):
    sorted_list = sorted(student.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)

    return sorted_list  




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
    


import json

def save_json(student):
    with open("student.json", "w") as f:
        json.dump(student, f)



def load_json():
    try:
        with open("student.json", "r") as f:
            return json.load(f)

    except FileNotFoundError:
        return {}