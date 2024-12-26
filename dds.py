import streamlit as st
import pandas as pd
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from fpdf import FPDF
import os
import re
import json
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


# Set up Streamlit page config
st.set_page_config(
    page_title="Question Paper Generator & Timetable",
    page_icon="📝",
    layout="wide",
)

def nav_title():
    st.sidebar.title("About")
    st.sidebar.write(
        """
        This application provides tools for generating question papers and timetables.
        Use the navigation menu to switch between functionalities.
        """
    )

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
            Strictly generate all the questions.
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
                        self.set_font("Helvetica", "B", 12)
                        new_y = round(self.y + 10, 2)
                        self.cell(0, 10, "Question Paper", align="C", new_x=round(self.l_margin), new_y=new_y)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font("Helvetica", "I", 8)
                        self.cell(0, 10, f"Page {self.page_no()}", align="C")

                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=12)
                for line in lines:
                    pdf.multi_cell(0, 10, line.encode('latin-1', errors='replace').decode('latin-1'))

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

def dashboard():
    st.title("Dashboard")
    st.write("Welcome to the dashboard! Here, you can analyze data and get insights.")

# Dictionary for page navigation
pages = {
    "Dashboard": dashboard,
    "Question Paper Generator": generate_question_paper,
}

# Sidebar navigation
nav_title()
selected_page = st.sidebar.selectbox("Navigate to:", list(pages.keys()))
pages[selected_page]()
