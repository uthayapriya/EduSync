import streamlit as st
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
import json
from utils import nav_title
import re
from fpdf import FPDF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


st.set_page_config(
    page_title="Question Paper Generator & Time Table",
    page_icon="📝",
    layout="wide",
)

nav_title()

def generate_question_paper():

    st.title("Question Paper Generator")
    st.write("Generate customized question papers based on topics, difficulty level, and question types.")

    # Input fields
    
    topics = st.text_area("Enter Topics:")
    difficulty = st.selectbox("Select Difficulty Level:", ["Easy", "Medium", "Hard"])
    num_questions_m = st.number_input("Number of MCQs:", min_value=0, value=25, step=1)
    num_questions_s = st.number_input("Number of SAQs:", min_value=0, value=15, step=1)
    num_questions_l = st.number_input("Number of LAQs:", min_value=0, value=6, step=1)
    weightage_m = st.number_input("Marks per MCQ:", min_value=1, value=1, step=1)
    weightage_s = st.number_input("Marks per SAQ:", min_value=1, value=3, step=1)
    weightage_l = st.number_input("Marks per LAQ:", min_value=1, value=5, step=1)

    if st.button("Generate Question Paper"):
        if not api_key:
            st.error("Please enter your GROQ API Key.")
        else:
            os.environ["GROQ_API_KEY"] = api_key
            model = ChatGroq(model="llama-3.1-8b-instant")

            total_marks = num_questions_m * weightage_m + num_questions_s * weightage_s + num_questions_l * weightage_l

            prompt_template = """
            You are a question paper generator. Use the following variables to generate a well-structured question paper.

            Topics:
            {topics}

            Difficulty Level:
            {difficulty}

            Number of Questions for each type:
            MCQ: {num_questions_MCQ}, SAQ: {num_questions_SAQ}, LAQ: {num_questions_LAQ}

            Weightage Marks for each question for MCQ, SAQ, and LAQ respectively:
            MCQ: {weightage_MCQ}, SAQ: {weightage_SAQ}, LAQ: {weightage_LAQ}

            Total Marks:
            {total_marks}

            Output a question paper covering all topics evenly with the specified question types, difficulty, and weightage.
            Include at the beginning marks distribution, clear instructions, and a variety of question formats with accurate marks allocation.
            """

            merged_data = {
                "topics": topics,
                "difficulty": difficulty,
                "total_marks": total_marks,
                "num_questions_MCQ": num_questions_m,
                "num_questions_SAQ": num_questions_s,
                "num_questions_LAQ": num_questions_l,
                "weightage_MCQ": weightage_m,
                "weightage_SAQ": weightage_s,
                "weightage_LAQ": weightage_l,
            }

            prompt = PromptTemplate(template=prompt_template, input_variables=list(merged_data.keys()))
            formatted_prompt = prompt.format(**merged_data)

            try:
                response = model.invoke(formatted_prompt)
                st.subheader("Generated Question Paper")
                lines = response.content.split("\n")

                # Display lines in the app
                for line in lines:
                    st.write(line)

                # PDF generation
                class PDF(FPDF):
                    def header(self):
                        self.set_font("Arial", "B", 12)
                        self.cell(0, 10, "Question Paper", align="C", ln=True)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font("Arial", "I", 8)
                        self.cell(0, 10, f"Page {self.page_no()}", align="C")

                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in lines:
                    pdf.multi_cell(0, 10, line)

                pdf_file = "Question_Paper.pdf"
                pdf.output(pdf_file)

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="Download Question Paper as PDF",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf",
                    )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")








    # try:
    #     # Step 5: Generate Response Using ChatGroq
    #     model = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)  # Pass the API key
    #     response = model.invoke(formatted_prompt)
    #     print(response.content)
    #     # Step 6: Parse and Clean Response
    #     cleaned_content = re.sub(r'```json\n|```', '', response.content)
    #     st.write("Raw timetable JSON:", timetable_json)

    #     timetable_json = json.loads(cleaned_content)

    #     # Convert JSON response to DataFrame
    #     rows = []
    #     for course, course_data in timetable_json.items():
    #         faculty_assignment = course_data["Faculty Assignment"]
    #         for slot in course_data["Time Slots"]:
    #             rows.append({
    #                 "Course": course,
    #                 "Faculty Assignment": faculty_assignment,
    #                 "Day": slot["Day"],
    #                 "Time": slot["Time"],
    #             })

    #     timetable_df = pd.DataFrame(rows)

    #     # Step 7: Display and Save Timetable
    #     st.write("Generated Timetable:")
    #     st.dataframe(timetable_df)

    #     def save_dataframe_to_pdf(df, filename):
    #         pdf_pages = PdfPages(filename)
    #         fig, ax = plt.subplots(figsize=(10, len(df) * 0.5))
    #         ax.axis("tight")
    #         ax.axis("off")
    #         table = ax.table(
    #             cellText=df.values,
    #             colLabels=df.columns,
    #             cellLoc="center",
    #             loc="center",
    #         )
    #         table.auto_set_font_size(False)
    #         table.set_fontsize(10)
    #         table.auto_set_column_width(col=list(range(len(df.columns))))
    #         pdf_pages.savefig(fig, bbox_inches="tight")
    #         pdf_pages.close()

    #     pdf_filename = "timetable.pdf"
    #     save_dataframe_to_pdf(timetable_df, pdf_filename)

    #     # Download Button for PDF
    #     with open(pdf_filename, "rb") as f:
    #         st.download_button(
    #             label="Download Timetable as PDF",
    #             data=f,
    #             file_name=pdf_filename,
    #             mime="application/pdf",
    #         )

    # except Exception as e:
    #     st.error(f"Error generating timetable: {e}")




########################################

########################################
def dashboard():
    st.title("Dashboard")
    st.write("Welcome to the dashboard! Here, you can analyze data and get insights.")

pages = {
    "Dashboard": dashboard,
    "Question Paper Generator": generate_question_paper,
}

with st.sidebar:
    st.title("About Question Paper Generator & Timetable")
    st.write(
        """
        This application provides tools for generating question papers and timetables.
        Use the navigation menu to switch between functionalities.
        """
    )

page = st.sidebar.selectbox("Select Page:", list(pages.keys()))
pages[page]()
