import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv  
import openai
import os
import docx2txt
load_dotenv()

def getResume():
    st.title("Resume Uploader")
    st.write("Upload your resume below:")

    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])

    if uploaded_file is not None:
        file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
        st.write(file_details)

        # Display file content
        if uploaded_file.type == "application/pdf":
            pdf_contents = read_pdf(uploaded_file)
            print(pdf_contents)
            st.write(pdf_contents)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            docx_contents = read_docx(uploaded_file)
            st.write(docx_contents)
            pdf(docx_contents)

def read_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        # st.write(text)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF file: {e}")
        return None

def read_docx(file):
    return docx2txt.process(file)



def main() :
    text = getResume()
    openai.api_key = os.getenv("OPENAI_API_KEY")



if __name__ == "__main__":
    main()
