from os import name


student={}
average_grades={}

def add_grades(student, name, grade):
    if name not in student:
        student[name] = []
    if grade > 0 and grade <= 100:
        student[name].append(grade)
    else:
        print("Invalid grade. Please enter a grade between 0 and 100.") 


add_grades(student, "mohammad", 70)
add_grades(student, "mohammad", 90)
add_grades(student, "adam", 100)
add_grades(student, "adam", 80)
add_grades(student, "baha", 60)
add_grades(student, "baha", 50)
print(student)

def calculate_average(student, name):
    try:

     return   sum(student[name]) / len(student[name])   
     
      
    except (KeyError, ZeroDivisionError):
     
        print("Student not found or no grades available.")


avg =calculate_average(student, "mohammad")
print(f"Average grade for mohammad: {avg}")


def class_average(student):
    average_list = []
    
    try:
        for name in student:
            avg = sum(student[name]) / len(student[name])
            average_list.append(avg)
        return sum(average_list) / len(average_list)
    except (KeyError, ZeroDivisionError):
        print("Student not found or no grades available.")
  

 
print(f"Class average for all students: {class_average(student)}")


def printtopstudent(student, average_grades):
    for name in student:
        average_grades[name] = sum(student[name]) / len(student[name])
    top_student = max(average_grades, key=average_grades.get)
    return top_student, average_grades[top_student]


top_student, top_average = printtopstudent(student, average_grades)
print(f"Top student: {top_student} with an average grade of {top_average}")


def remove_student(student, name):
    if name in student:
        del student[name]
        print(f"{name} has been removed from the student list.")
    else:
        print(f"{name} is not in the student list.")


remove_student(student, "adam")
print(student)


def student_report(student):
    for name in student:
        avg = sum(student[name]) / len(student[name])
        grades = student[name]
        report = f"{name}: {grades}, Average: {avg}"
        return report






print(student_report(student))









def sorted_students(student):
    sorted_list = sorted(student.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)

    return sorted_list  

# Return only the student names in sorted order

sorted_list = sorted_students(student)
print("Students sorted by average grade (highest to lowest): {}".format([name for name, grades in sorted_list]))



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
      



letter=letter_grade(-50)
print(f"The letter grade for the score  is: {letter}")
    
          




 


















 