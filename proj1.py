student={}

def add_grades(student, name, grade):
    if name not in student:
        student[name] = []
    student[name].append(grade)


add_grades(student, "mohammad", 70)
add_grades(student, "mohammad", 90)
add_grades(student, "adam", 100)
add_grades(student, "adam", 80)


print(student)

def calculate_average(student, name):
    
    for name in student:
             print(sum(student[name]) / len(student[name]))
    


calculate_average(student, "mohammad")

def print3students(student):
    if len(student) >= 3:
      print(f"The first three students are:{list(student.keys())[:3]}")

      print3students(student)
      


            