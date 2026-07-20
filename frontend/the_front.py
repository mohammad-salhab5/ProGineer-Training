import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

# ---------------- Helper ---------------- #

def handle_response(response):
    try:
        return response.json()
    except:
        return {"message": "No response"}

# ---------------- Sidebar ---------------- #

st.sidebar.title("🎓 Navigation")

page = st.sidebar.radio(
    "Choose Section",
    [
        "🏠 Home",
        "➕ Add Grade",
        "👨 Student Operations",
        "📊 Class Statistics",
        "💾 JSON"
    ]
)

# ---------------- Home ---------------- #

if page == "🏠 Home":

    st.title("🎓 Student Management System")

    st.info(
        "Welcome!\n\n"
        "Use the menu on the left to manage students and grades."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Backend", "FastAPI")

    with c2:
        st.metric("Frontend", "Streamlit")

    with c3:
        st.metric("Connection", "Ready")

# ---------------- Add Grade ---------------- #

elif page == "➕ Add Grade":

    st.title("➕ Add Grade")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Student Name")

    with col2:
        grade = st.number_input(
            "Grade",
            min_value=0,
            max_value=100
        )

    if st.button("➕ Add Grade", use_container_width=True):

        response = requests.post(
            f"{API}/add_grade",
            json={
                "name": name,
                "grade": grade
            }
        )

        data = handle_response(response)

        if response.status_code == 200:
            st.success("Grade Added Successfully")
            st.json(data)
        else:
            st.error(data)

# ---------------- Student Operations ---------------- #

elif page == "👨 Student Operations":

    st.title("👨 Student Operations")

    search_name = st.text_input("Student Name")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("📄 Show All Students", use_container_width=True):

            response = requests.get(f"{API}/students")

            st.json(handle_response(response))

        if st.button("📚 Student Grades", use_container_width=True):

            response = requests.get(
                f"{API}/students/{search_name}/grades"
            )

            st.json(handle_response(response))

        if st.button("📋 Student Report", use_container_width=True):

            response = requests.get(
                f"{API}/student_report/{search_name}"
            )

            st.json(handle_response(response))

    with col2:

        if st.button("📈 Average Grade", use_container_width=True):

            response = requests.post(
                f"{API}/average",
                json={
                    "name": search_name
                }
            )

            data = handle_response(response)

            if "average" in data:
                st.metric(
                    label=f"{search_name}'s Average",
                    value=data["average"]
                )
            else:
                st.json(data)

        if st.button("🗑 Remove Student", use_container_width=True):

            response = requests.delete(
                f"{API}/remove_student/{search_name}"
            )

            if response.status_code == 204:
                st.success("Student Deleted Successfully")
            else:
                st.json(handle_response(response))

# ---------------- Statistics ---------------- #

elif page == "📊 Class Statistics":

    st.title("📊 Class Statistics")

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button("👥 Show Students", use_container_width=True):

            response = requests.get(f"{API}/students")

            st.json(handle_response(response))

        if st.button("📊 Class Average", use_container_width=True):

            response = requests.get(f"{API}/class_average")

            data = handle_response(response)

            if "average" in data:
                st.metric(
                    "Class Average",
                    data["average"]
                )
            else:
                st.json(data)

    with c2:

        if st.button("🏆 Top Student", use_container_width=True):

            response = requests.get(f"{API}/top_student")

            data = handle_response(response)

            if "name" in data:

                st.success("Top Student")

                st.metric(
                    data["name"],
                    data.get("average", "-")
                )

                st.json(data)

            else:

                st.json(data)

    with c3:

        if st.button("📑 Sorted Students", use_container_width=True):

            response = requests.get(
                f"{API}/sorted_students"
            )

            st.json(handle_response(response))

# ---------------- JSON ---------------- #

elif page == "💾 JSON":

    st.title("💾 JSON Operations")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("💾 Save JSON", use_container_width=True):

            response = requests.post(f"{API}/save_json")

            st.success("Data Saved")

            st.json(handle_response(response))

    with col2:

        if st.button("📂 Load JSON", use_container_width=True):

            response = requests.post(f"{API}/load_json")

            st.success("Data Loaded")

            st.json(handle_response(response))