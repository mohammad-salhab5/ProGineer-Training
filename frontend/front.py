import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓"
)

st.title("🎓 Student Management System")


def show_error(response):
    try:
        st.error(response.json().get("detail", "Unknown error"))
    except:
        st.error(response.text)



menu = st.radio(
    "Navigation",
    [
        "View Students",
        "View Student Grades",
        "Add Grade",
        "Student Average",
        "Class Average",
        "Top Student",
        "Remove Student",
        "Student Report",
        "Sorted Students",
        "Save JSON",
        "Load JSON",
    ],
    horizontal=True
)


# ---------------- View Students ----------------
if menu == "View Students":

    if st.button("Get Students"):

        response = requests.get(
            f"{BASE_URL}/students"
        )

        if response.status_code == 200:

            students = response.json()

            if students:
                st.success("Students Found")
                st.write(students)
            else:
                st.warning("No students available.")

        else:
            show_error(response)



# ---------------- View Grades ----------------
elif menu == "View Student Grades":

    name = st.text_input("Student Name")

    if st.button("Get Grades"):

        response = requests.get(
            f"{BASE_URL}/students/{name}/grades"
        )

        if response.status_code == 200:
            st.json(response.json())

        else:
            show_error(response)



# ---------------- Add Grade ----------------
elif menu == "Add Grade":

    name = st.text_input("Student Name")
    grade = st.number_input(
        "Grade",
        0,
        100
    )

    if st.button("Add Grade"):

        response = requests.post(
            f"{BASE_URL}/add_grade",
            json={
                "name": name,
                "grade": grade
            }
        )

        if response.status_code == 200:

            st.success(
                response.json()["message"]
            )

        else:
            show_error(response)



# ---------------- Student Average ----------------
elif menu == "Student Average":

    name = st.text_input("Student Name")

    if st.button("Calculate Average"):

        response = requests.get(
            f"{BASE_URL}/average",
            json={
                "name": name
            }
        )

        if response.status_code == 200:

            data = response.json()

            st.success(
                f"Average = {data['average']:.2f}"
            )

        else:
            show_error(response)



# ---------------- Class Average ----------------
elif menu == "Class Average":

    if st.button("Get Class Average"):

        response = requests.get(
            f"{BASE_URL}/class_average"
        )

        if response.status_code == 200:

            st.success(
                f"Class Average = {response.json()['class_average']:.2f}"
            )

        else:
            show_error(response)



# ---------------- Top Student ----------------
elif menu == "Top Student":

    if st.button("Show Top Student"):

        response = requests.get(
            f"{BASE_URL}/top_student"
        )

        if response.status_code == 200:

            data = response.json()

            st.success(
                f"Top Student: {data['top_student']}"
            )

            st.write(
                f"Average: {data['average']:.2f}"
            )

        else:
            show_error(response)



# ---------------- Remove Student ----------------
elif menu == "Remove Student":

    name = st.text_input("Student Name")

    if st.button("Remove"):

        response = requests.delete(
            f"{BASE_URL}/remove_student/{name}"
        )

        # FastAPI يرجع 200 وليس 204
        if response.status_code == 200:

            st.success(
                response.json()["message"]
            )

        else:
            show_error(response)



# ---------------- Student Report ----------------
elif menu == "Student Report":

    name = st.text_input("Student Name")

    if st.button("Generate Report"):

        response = requests.get(
            f"{BASE_URL}/student_report/{name}"
        )

        if response.status_code == 200:

            st.write(
                response.json()["report"]
            )

        else:
            show_error(response)



# ---------------- Sorted Students ----------------
elif menu == "Sorted Students":

    if st.button("Show Ranking"):

        response = requests.get(
            f"{BASE_URL}/sorted_students"
        )

        if response.status_code == 200:

            st.table(
                response.json()
            )

        else:
            show_error(response)



# ---------------- Save JSON ----------------
elif menu == "Save JSON":

    if st.button("Save"):

        response = requests.post(
            f"{BASE_URL}/save_json"
        )

        if response.status_code == 200:

            st.success(
                response.json()["message"]
            )

        else:
            show_error(response)



# ---------------- Load JSON ----------------
elif menu == "Load JSON":

    if st.button("Load"):

        response = requests.post(
            f"{BASE_URL}/load_json"
        )

        if response.status_code == 200:

            data = response.json()

            st.success(
                data["message"]
            )

            st.json(
                data["students"]
            )

        else:
            show_error(response)