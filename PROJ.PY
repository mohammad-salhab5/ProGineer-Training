students= {}


def add_grade(students, name, grade):
    if name not in students:
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
  avrg=(sum(students[name]))/(len (students[name]))
  if name in students:
    print(f"{name} has an average {avrg}")




      
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
       
      

          


 
average_grade(students, "mohammad")
average_grade(students, "mohammadS") 
average_grade(students, "Adam") 
top_student(students)
remove_student(students, "Adam") 

       



    




    
