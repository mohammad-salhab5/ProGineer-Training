students= {}


def add_grade(students, name, grade):
    if grade<0 or grade>100:
       print("grade must be between 0 and 100.")
   
    elif name not in students:
        students[name]= []
    
    students[name].append(grade)

    

add_grade(students, "mohammad", 10)
add_grade(students, "mohammad", 15)
add_grade(students, "mohammad", 20)
add_grade(students, "Adam", 10)
add_grade(students, "Adam", 20)
add_grade(students, "Adam", 17)
add_grade(students, "mohammadS", 30)
add_grade(students, "mohammadS", 25)
add_grade(students, "mohammadS", 19)


def average_grade(students, name):
    if name in students:
     avrg=(sum(students[name]))/(len (students[name]))
    return avrg 

avg = average_grade(students, "mohammad")
print(avg)

      
def top_student(students):
   top= 0
 

   for name in students:
       avg=(sum(students[name]))/(len (students[name]))

       if avg>top:
         top=avg
   return print(f"{name} is the top student")
 


               
         
def remove_student(students, name):
    if name in students:
        del students[name]
        print(f"{name} has been removed")
    else:
        print("This student does not exist")     
       
      

def class_average(students):
   sum=0
   count=0
   for name in students:
      sum += average_grade(students, name)
      count+=1
   return sum/count     

avgc = class_average(students)
print(avgc)
       

def student_report(students, name):
   if name in students:
    report = f"{name}: grades = {students[name]}, average = {average_grade(students, name)}"
    return report
   else:
      return "student not exist"


n=student_report(students, "mohammad")
print(n)
    
def letter_grade(score):
   if score >=90:
      return 'A'
   elif score>=80 and score <90 :
      return 'B'
   elif score>=70 and score <80:
      return 'C'
   elif score >=60 and score <69:
      return  'D'
   elif score >= 0 and score >60:
      return 'F'
   else:
      return 'The grade is not defined'

def sorted_students(students):
    sorted_list = sorted(students.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)

    return sorted_list  


sorted_list = sorted_students(students)
print("Students sorted by average grade (highest to lowest): {}".format([name for name, grades in sorted_list]))

    
