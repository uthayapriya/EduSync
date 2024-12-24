import streamlit as st
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
import json
from dotenv import load_dotenv



# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = api_key

# Function to save DataFrame to PDF
def save_dataframe_to_pdf(df, filename):
    pdf_pages = PdfPages(filename)
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.5))
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df.columns)) ))
    pdf_pages.savefig(fig, bbox_inches="tight")
    pdf_pages.close()

# Streamlit App
st.title("Academic Timetable Generator")

# Input: Courses Data
st.header("Course Data")
num_courses = st.number_input("Enter the number of courses:", min_value=1, step=1)
courses_data = []
for i in range(num_courses):
    course_name = st.text_input(f"Course {i+1} Name:", key=f"course_name_{i}")
    hours_required = st.number_input(
        f"Hours Required for {course_name}:",
        min_value=1,
        step=1,
        key=f"hours_required_{i}"
    )
    courses_data.append({"Course Name": course_name, "Hours Required": hours_required})

# Create courses DataFrame
courses_df = pd.DataFrame(courses_data)

# Input: Faculty Data
st.header("Faculty Data")
num_faculty = st.number_input("Enter the number of faculty members:", min_value=1, step=1)
faculty_data = []
for i in range(num_faculty):
    faculty_name = st.text_input(f"Faculty Member {i+1} Name:")
    expertise = st.text_input(f"Expertise of {faculty_name} (comma-separated):", key=f"expertise_{faculty_name}")
    availability_days = st.text_input(f"Availability Days for {faculty_name}:")
    availability_hours = st.text_input(f"Availability Hours for {faculty_name} (e.g., 9 AM - 2 PM):")
    if faculty_name and expertise and availability_days and availability_hours:
        faculty_data.append({
            "Faculty Name": faculty_name,
            "Course Expertise": expertise,
            "Availability Days": availability_days,
            "Availability Hours": availability_hours,
        })
faculty_df = pd.DataFrame(faculty_data)

# Display Input Data
if not courses_df.empty:
    st.subheader("Courses DataFrame")
    st.write(courses_df)
if not faculty_df.empty:
    st.subheader("Faculty DataFrame")
    st.write(faculty_df)

if st.button("Generate Timetable"):
    if not courses_df.empty and not faculty_df.empty:
        try:
            # Prepare data for the prompt
            data_dict = {
                "courses": courses_df.to_dict(orient="records"),
                "faculty_records": faculty_df.to_dict(orient="records"),
            }
            os.environ["GROQ_API_KEY"] = api_key
            model = ChatGroq(model="llama-3.1-8b-instant")

            # Define the prompt template
            prompt_template = """
            You are an academic timetable generator. Using the provided data below, generate a structured output that allocates resources efficiently.
            The data includes:
            - Courses: {courses}
            - Faculty records: {faculty_records}

            Consider the following:
            1. Each course must be assigned to a faculty member based on their expertise and availability.
            2. Ensure fairness in faculty workload distribution.
            3. Allocate sufficient time slots for each course based on the specified hours in the courses data.
            4. Only give the output timetable which should be in a dictionary format covertable to a pdf. Do not output anything else:
                - Course name
                - Faculty assignment
                - Time slots
            """
            formatted_prompt = PromptTemplate(
                template=prompt_template,
                input_variables=list(data_dict.keys())
            ).format(**data_dict)

            # Generate timetable using the model
            response = model.invoke(formatted_prompt)
            data = response.content
            st.write(f"Model Response: {data}")

            data_dict = json.loads(data)
            rows = []
            for course, course_data in data_dict.items():
                faculty_assignment = course_data.get("Faculty Assignment")
                time_slots = course_data.get("Time Slots")
                if faculty_assignment and time_slots:
                    for slot in time_slots:
                        day = slot.get("Day")
                        time = slot.get("Time")
                        if day and time:
                            rows.append({
                                "Course Name": course,
                                "Faculty Assignment": faculty_assignment,
                                "Day": day,
                                "Time": time
                            })

            df = pd.DataFrame(rows)
            save_dataframe_to_pdf(df, "timetable.pdf")
            st.success("Timetable has been successfully generated and saved as timetable.pdf.")
            

        except Exception as e:
            st.error(f"Error generating timetable: {e}")