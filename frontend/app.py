import streamlit as st
import requests

# FastAPI URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Student Grade Manager",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Grade Management System")

menu = st.sidebar.selectbox(
    "Choose an Action",
    [
        "Add Grade",
        "Student Average",
        "Student Report",
        "Top Student",
        "Class Average",
        "Sort Students",
        "Delete Student",
        "Save Data",
        "Load Data"
    ]
)

# ------------------------
# Add Grade
# ------------------------
if menu == "Add Grade":

    st.header("Add Grade")

    name = st.text_input("Student Name")
    grade = st.number_input(
        "Grade",
        min_value=0,
        max_value=100,
        step=1
    )

    if st.button("Add"):

        response = requests.post(
            f"{API_URL}/add_grade",
            params={
                "name": name,
                "grade": grade
            }
        )

        st.json(response.json())

# ------------------------
# Student Average
# ------------------------
elif menu == "Student Average":

    st.header("Calculate Student Average")

    name = st.text_input("Student Name")

    if st.button("Calculate"):

        response = requests.get(f"{API_URL}/average/{name}")

        st.json(response.json())

# ------------------------
# Student Report
# ------------------------
elif menu == "Student Report":

    st.header("Student Report")

    name = st.text_input("Student Name")

    if st.button("Show Report"):

        response = requests.get(f"{API_URL}/report/{name}")

        st.json(response.json())

# ------------------------
# Top Student
# ------------------------
elif menu == "Top Student":

    st.header("Top Student")

    if st.button("Show"):

        response = requests.get(f"{API_URL}/top_student")

        st.json(response.json())

# ------------------------
# Class Average
# ------------------------
elif menu == "Class Average":

    st.header("Class Average")

    if st.button("Calculate"):

        response = requests.get(f"{API_URL}/class_average")

        st.json(response.json())

# ------------------------
# Sort Students
# ------------------------
elif menu == "Sort Students":

    st.header("Students Sorted by Average")

    if st.button("Sort"):

        response = requests.get(f"{API_URL}/sort")

        data = response.json()

        if isinstance(data, list):
            for i, student in enumerate(data, start=1):
                st.write(f"{i}. {student}")
        else:
            st.json(data)

# ------------------------
# Letter Grade
# ------------------------
elif menu == "Letter Grade":

    st.header("Letter Grade")

    score = st.number_input(
        "Score",
        min_value=0.0,
        max_value=100.0
    )

    if st.button("Convert"):

        response = requests.get(f"{API_URL}/letter/{score}")

        st.json(response.json())

# ------------------------
# Delete Student
# ------------------------
elif menu == "Delete Student":

    st.header("Delete Student")

    name = st.text_input("Student Name")

    if st.button("Delete"):

        response = requests.delete(f"{API_URL}/student/{name}")

        st.json(response.json())

# ------------------------
# Save
# ------------------------
elif menu == "Save Data":

    st.header("Save Students")

    if st.button("Save"):

        response = requests.post(f"{API_URL}/save")

        st.json(response.json())

# ------------------------
# Load
# ------------------------
elif menu == "Load Data":

    st.header("Load Students")

    if st.button("Load"):

        response = requests.post(f"{API_URL}/load")

        st.json(response.json())