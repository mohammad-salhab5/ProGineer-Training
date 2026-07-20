import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Student Management System")



st.header("Add Grade")

name = st.text_input("Student Name")
grade = st.number_input("Grade", min_value=0, max_value=100)

if st.button("Add Grade"):

    response = requests.post(
        f"{API}/add_grade",
        json={
            "name": name,
            "grade": grade
        }
    )

    st.json(response.json())

st.divider()



st.header("Student Operations")

search_name = st.text_input("Search Student")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("Show Students"):

        response = requests.get(f"{API}/students")

        st.json(response.json())

    if st.button("Student Grades"):

        response = requests.get(f"{API}/students/{search_name}/grades")

        st.json(response.json())

with col2:

    if st.button("Average Grade"):

        response = requests.post(
            f"{API}/average",
            json={"name": search_name}
        )

        st.json(response.json())

    if st.button("Student Report"):

        response = requests.get(
            f"{API}/student_report/{search_name}"
        )

        st.json(response.json())

with col3:

    if st.button("Remove Student"):

        response = requests.delete(
            f"{API}/remove_student/{search_name}"
        )

        if response.status_code == 204:
            st.success("Student Deleted")
        else:
            st.json(response.json())

st.divider()



st.header("Class Operations")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("Class Average"):

        response = requests.get(f"{API}/class_average")

        st.json(response.json())

with col2:

    if st.button("Top Student"):

        response = requests.get(f"{API}/top_student")

        st.json(response.json())

with col3:

    if st.button("Sorted Students"):

        response = requests.get(f"{API}/sorted_students")

        st.json(response.json())

st.divider()



st.header("JSON Operations")

col1, col2 = st.columns(2)

with col1:

    if st.button("Save JSON"):

        response = requests.post(f"{API}/save_json")

        st.json(response.json())

with col2:

    if st.button("Load JSON"):

        response = requests.post(f"{API}/load_json")

        st.json(response.json())