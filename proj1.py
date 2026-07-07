from os import name


student={}
average_grades={}

def add_grades(student, name, grade):
    if name not in student:
        student[name] = []
    student[name].append(grade)


add_grades(student, "mohammad", 70)
add_grades(student, "mohammad", 90)
add_grades(student, "adam", 100)
add_grades(student, "adam", 80)
add_grades(student, "baha", 60)
add_grades(student, "baha", 55)
print(student)

def calculate_average(student, name):
    try:
        print(sum(student[name]) / len(student[name]))
    except (KeyError, ZeroDivisionError):
        print("Student not found or no grades available.")


calculate_average(student, "zoozo")






      

def printtopstudent(student, average_grades):
    for name in student:
        average_grades[name] = sum(student[name]) / len(student[name])
    top_student = max(average_grades, key=average_grades.get)
    print(f"{top_student} is the top student with an average grade of {average_grades[top_student]}")

printtopstudent(student, average_grades)




def remove_student(student, name):
    if name in student:
        del student[name]
        print(f"{name} has been removed from the student list.")
    else:
        print(f"{name} is not in the student list.")





remove_student(student, "adam")
print(student)









      
        