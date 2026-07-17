import requests


class StudentClient:

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"

    def add_grade(self):

        name = input("Student name: ")
        grade = int(input("Grade: "))

        response = requests.post(
            f"{self.base_url}/add_grade",
            params={
                "name": name,
                "grade": grade
            }
        )

        print(response.json())

    def average(self):

        name = input("Student name: ")

        response = requests.get(
            f"{self.base_url}/average/{name}"
        )

        print(response.json())

    def remove_student(self):

        name = input("Student name: ")

        response = requests.delete(
            f"{self.base_url}/student/{name}"
        )

        print(response.json())

    def top_student(self):

        response = requests.get(
            f"{self.base_url}/top_student"
        )

        print(response.json())

    def class_average(self):

        response = requests.get(
            f"{self.base_url}/class_average"
        )

        print(response.json())

    def report(self):

        name = input("Student name: ")

        response = requests.get(
            f"{self.base_url}/report/{name}"
        )

        print(response.json())

    def sort_students(self):

        response = requests.get(
            f"{self.base_url}/sort"
        )

        print(response.json())

    def letter_grade(self):

        score = float(input("Score: "))

        response = requests.get(
            f"{self.base_url}/letter/{score}"
        )

        print(response.json())

    def save(self):

        response = requests.post(
            f"{self.base_url}/save"
        )

        print(response.json())

    def load(self):

        response = requests.post(
            f"{self.base_url}/load"
        )

        print(response.json())

    def menu(self):

        while True:

            print("\n===== Student Management =====")
            print("1. Add Grade")
            print("2. Student Average")
            print("3. Remove Student")
            print("4. Top Student")
            print("5. Class Average")
            print("6. Student Report")
            print("7. Sort Students")
            print("8. Letter Grade")
            print("9. Save")
            print("10. Load")
            print("0. Exit")

            choice = input("Choice: ")

            if choice == "1":
                self.add_grade()

            elif choice == "2":
                self.average()

            elif choice == "3":
                self.remove_student()

            elif choice == "4":
                self.top_student()

            elif choice == "5":
                self.class_average()

            elif choice == "6":
                self.report()

            elif choice == "7":
                self.sort_students()

            elif choice == "8":
                self.letter_grade()

            elif choice == "9":
                self.save()

            elif choice == "10":
                self.load()

            elif choice == "0":
                break

            else:
                print("Invalid choice")


client = StudentClient()
client.menu()