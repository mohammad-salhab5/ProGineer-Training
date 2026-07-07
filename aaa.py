students = {}

def add_grades(students, name, grade):
    if name not in students:
        students[name] = []
    students[name].append(grade)

add_grades(students, "John", 85)
add_grades(students, "John", 85)
add_grades(students, "Alice", 90)
add_grades(students, "Alice", 95)
add_grades(students, "Alice", 78)
add_grades(students, "John", 88)
add_grades(students, "Bob", 92)
print(students)

def calculate_average(students, name):
    if name in students:
        grades = students[name]
        average = sum(grades) / len(grades)
        return average
    else:
        return None

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