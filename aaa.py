students = {}

def add_grades(students, name, grade):
    if name not in students:
        students[name] = []

    if 0 <= grade <= 100:
        students[name].append(grade)
    else:
        print("Grade must be between 0 and 100")

add_grades(students, "John", 155)
add_grades(students, "John", 85)
add_grades(students, "Alice", 90)
add_grades(students, "Alice", 95)
add_grades(students, "Alice", 78)
add_grades(students, "John", 88)
add_grades(students, "Bob", 92)
print(students)

def calculate_average(students, name):
    if name not in students:
        return None

    grades = students[name]

    if not grades:
        return None 

    return sum(grades) / len(grades)

print(calculate_average(students, "John"))
print(calculate_average(students, "Alice"))
print(calculate_average(students, "Bob"))


def remove_student(students, name):
    if name in students:
        del students[name]
        return True
    else:
        return False

remove_student(students, "Bob")
print(students)

def top_student(students):
    top_name = None
    top_average = 0

    for name, grades in students.items():
        average = sum(grades) / len(grades)
        if average > top_average:
            top_average = average
            top_name = name

    return top_name, top_average

print(top_student(students))
#we can do it on calculate_average funcation
def average_grade(students, name):
    if name not in students:
        return "No student found with that name."
       
    grades = students[name]
    return sum(grades) / len(grades)

avg=average_grade(students, "mohammad")
print(avg)
avg2=average_grade(students, "John")
print(avg2)

def class_average(students):
    total_grades=0
    total_students=0
    for grades in students.values():
        total_grades +=sum(grades)
        total_students +=len(grades)
    if total_students==0:
        return "there are no students in the class."
    
    return total_grades/total_students

print(class_average(students))

def student_report(students, name):
    if name not in students:
        return "No student found with that name."

    report = "{name} : grades= {grades} , average={average}".format(
        name=name,
        grades=students[name],
        average=average_grade(students, name)
    )
    return report

   


repo = student_report(students, "Alice")
print(repo)



def sort_average(students):
    averages = {}

    for name in students:
        averages[name] = average_grade(students, name)

    sorted_averages = sorted(averages.items(), key=lambda x: x[1], reverse=True)

    names = []
    for name, average in sorted_averages:
        names.append(name)

    return names


sorted_students = sort_average(students)
print(sorted_students)




def letter_grade(score):
    if score < 0 or score > 100:
        return "Invalid score. Please enter a score between 0 and 100."
    if score >= 90:
        return "A"
    elif score >= 80 and score <= 89:
        return "B"
    elif score >= 70 and score <= 79:
        return "C" 
    elif score >=60 and score <= 69:
        return "D"
    else:
        return "F"
    

    
    
    
letter = letter_grade(87.66666666666667)
print(letter)

letter2 = letter_grade(105)
print(letter2)

letter3 = letter_grade(-5)
print(letter3)

letter4 = letter_grade(22)
print(letter4)
