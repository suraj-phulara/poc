import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv  
import os
import docx2txt
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
import json
from resume_models import Resume, Rewrite

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate


load_dotenv()
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)


def generate_resume_from_json(json_data, template_path):
    # Load Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("template1.html")

    # Render the template with JSON data
    rendered_resume = template.render({"resume":json_data})

    return rendered_resume


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
            return pdf_contents
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            docx_contents = read_docx(uploaded_file)
            return docx_contents

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



# Define function to categorize resume data
def categorize_resume(resume_text):
    # Define the prompt for OpenAI API
    with open('template1.html', 'r') as file:
        resume_template = file.read()

    prompt = (
        f'analyze the following resume carefully and carefully extract all the key detaild from it like contact details, skills, education, experience, certifications, etc, etc. \n\n'
        f'Resume Data:\n'
        f'{resume_text}\n\n'
        f'--- Read the above resume and return me a detailed json containing the required info\n\n'
   
    )

    # Call OpenAI API to generate categories
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    json_data = response.choices[0].message.content
    json_data = json.loads(response.choices[0].message.content)
    print(json_data)
    return response






def remove_empty_lines(html_content):
    # Split the HTML content into lines
    lines = html_content.splitlines()

    # Filter out empty lines
    non_empty_lines = filter(lambda line: line.strip(), lines)

    # Join the non-empty lines back together
    cleaned_html_content = '\n'.join(non_empty_lines)

    return cleaned_html_content


def structured_output(text):
    # Initialize the GPT API model
    model = ChatOpenAI(temperature=0)

    # And a query intented to prompt a language model to populate the data structure.
    joke_query = f"read this text extracted from a user resume carefully and classify this based on different criteria into the json format.   text : {text} \n\n"

    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=Resume)

    prompt = PromptTemplate(
        template="always write date in this format : %Y-%M-%D for example: '2014-10-01'.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    response = chain.invoke({"query": joke_query})

    # st.write(response)
    return response





def rewrite_with_ai(text):
    # Initialize the GPT API model
    model = ChatOpenAI(temperature=0.5)

    # And a query intented to prompt a language model to populate the data structure.
    joke_query = f"this text contains the summary of my one of the work experience in my resume. your task is to read it carefully and rewrite it in a humanised simpla and easy language. remember to not increse or decrease the length of the summary it should most importantly be exactly {len(text)} words. \n\n  text : {text} \n\n"

    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=Rewrite)

    prompt = PromptTemplate(
        template="rewrite the given text making it ats friendly .\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    response = chain.invoke({"query": joke_query})
    # st.write(response["summary"])
    # print(response)

    # st.write(response)
    return response["summary"]








def display_basics(basics):
    st.header("**Basic Details**")  
    with st.expander("Basic Details"):
        # st.subheader("Name:")
        basics['name'] = st.text_input("**Name**", basics['name'])

        # st.subheader("Label:")
        basics['label'] = st.text_input("Label", basics['label'])

        # st.subheader("Email:")
        basics['email'] = st.text_input("Email", basics['email'])

        st.subheader("Phone:")
        basics['phone'] = st.text_input("Phone", basics['phone'])

    st.subheader("Location:")
    with st.expander("Location"):
        st.subheader("Address:")
        basics['location']['address'] = st.text_input("Address", basics['location']['address'])

        st.subheader("Postal Code:")
        basics['location']['postalCode'] = st.text_input("Postal Code", basics['location']['postalCode'])

        st.subheader("City:")
        basics['location']['city'] = st.text_input("City", basics['location']['city'])

        st.subheader("Country Code:")
        basics['location']['countryCode'] = st.text_input("Country Code", basics['location']['countryCode'])

        st.subheader("Region:")
        basics['location']['region'] = st.text_input("Region", basics['location']['region'])

    st.subheader("Profiles:")
    with st.expander("Profiles"):
        for profile in basics['profiles']:
            st.subheader(profile['network'])
            profile['username'] = st.text_input("Username", profile['username'])
            profile['url'] = st.text_input("URL", profile['url'])



def rewrite_summary_with_ai(summary_ref):
    summary_ref = rewrite_with_ai(summary_ref)
    return summary_ref



def display_work(work):
    st.header("Work Experience")
    with st.expander("Work Experience"):
        st.markdown("---")
        for i, job in enumerate(work):
            st.subheader(f"Job {i + 1}")
            job['name'] = st.text_input(f"Name_{i}", job['name'])
            job['position'] = st.text_input(f"Position_{i}", job['position'])
            # job['url'] = st.text_input(f"URL_{i}", job['url'])
            job['startDate'] = st.text_input(f"Start Date_{i}", job['startDate'])
            job['endDate'] = st.text_input(f"End Date_{i}", job['endDate'])
            
            
            st.markdown("")
            st.subheader("Summary:")
            # Button to rewrite summary with AI
            if st.button("Rewrite with AI", key=i):
                job['summary']=rewrite_summary_with_ai( job['summary'])

            job['summary'] = st.text_area("", job['summary'])
                
            
            
            
            for j, highlight in enumerate(job['highlights']):
                job['highlights'][j] = st.text_input(f"Highlight {j + 1}_{i}", highlight)
            st.markdown("---")
            st.markdown("---")

def display_education(education):
    # pass
    st.header("Education")
    with st.expander("Education"):
        j = 0
        for i, edu in enumerate(education):
            j=j+1
            st.subheader(f"Educational Institution {i + 1}")
            edu['institution'] = st.text_input("Institution", edu['institution'], key=f"{i**i + j*i}a")
            edu['url'] = st.text_input("URL", edu['url'], key=f"{i**i + j*i}b")
            edu['area'] = st.text_input("Area", edu['area'], key=f"{i**i + j*i}c")
            edu['studyType'] = st.text_input("Study Type", edu['studyType'], key=f"{i**i + j*i}d")
            edu['startDate'] = st.text_input("Start Date", edu['startDate'], key=f"{i**i + j*i}e")
            edu['endDate'] = st.text_input("End Date", edu['endDate'], key=f"{i**i + j*i}f")
            edu['score'] = st.text_input("Score", edu['score'], key=f"{i**i + j*i}aa")
        st.markdown("---")

def display_skills(skills):
    st.header("Skills")
    with st.expander("Skills"):
        for skill in skills:
            name_key = f"Skill Name_{skill['name']}"
            skill['name'] = st.text_input("Skill Name", key=name_key, value=skill.get('name', ''))
            # Level and keywords can be added if needed

def display_certificates(certificates):
    st.header("Certificates")
    with st.expander("Certificates"):
        for cert in certificates:
            name_key = f"Certificate Name_{cert['name']}"
            cert['name'] = st.text_input("Certificate Name", key=name_key, value=cert.get('name', ''))
            # Date and issuer can be added if needed


def display_projects(projects):
    st.header("Projects")
    with st.expander("Projects"):
        for i, project in enumerate(projects):
            st.subheader(f"Project {i + 1}: {project.get('name', '')}")
            with st.beta_container():
                project['name'] = st.text_input("Name", project.get('name', ''))
                project['description'] = st.text_area("Description", project.get('description', ''))
                project['startDate'] = st.text_input("Start Date", project.get('startDate', ''))
                project['endDate'] = st.text_input("End Date", project.get('endDate', ''))
                project['url'] = st.text_input("URL", project.get('url', ''))
                st.subheader("Highlights:")
                for j, highlight in enumerate(project.get('highlights', [])):
                    project['highlights'][j] = st.text_input(f"Highlight {j + 1}", highlight)
                st.subheader("Keywords:")
                for j, keyword in enumerate(project.get('keywords', [])):
                    project['keywords'][j] = st.text_input(f"Keyword {j + 1}", keyword)
                st.subheader("Roles:")
                for j, role in enumerate(project.get('roles', [])):
                    project['roles'][j] = st.text_input(f"Role {j + 1}", role)
                project['entity'] = st.text_input("Entity", project.get('entity', ''))
                project['type'] = st.text_input("Type", project.get('type', ''))



def printresume(resume_json_data):
    rendered_resume = generate_resume_from_json(resume_json_data, 'resume_template.html')
    rendered_resume = str(remove_empty_lines(rendered_resume))
    cont = st.container()
    cont.write(rendered_resume,unsafe_allow_html=True, key="hcsiudchwiudchwdci")








# Sidebar navigation
def sidebar_navigation():
    st.sidebar.title('Navigation')
    page = st.sidebar.selectbox("Go to", ["Upload Resume", "Resume Details"])
    return page



def main() :
    page = sidebar_navigation()
    if page == "Upload Resume":
        text = getResume()
        text="gg"
        if text:
            # resume_json_data = structured_output(text)
            # if resume_json_data:
            # if 'json_data' not in st.session_state: 
            with open('resume_data.json', 'r') as f:
                resume_json_data = json.load(f)
            # st.session_state['json_data'] = resume_json_data
            # else:
                # resume_json_data = st.session_state['json_data']

            json_data = resume_json_data
            
            
            if json_data.get('basics'):
                display_basics(json_data['basics'])

            if json_data.get('work'):
                display_work(json_data['work'])

            # Uncomment the below line if you want to include education
            if json_data.get('education'):
                display_education(json_data['education'])

            if json_data.get('skills'):
                display_skills(json_data['skills'])

            if json_data.get('certificates'):
                display_certificates(json_data['certificates'])

            if json_data.get('projects'):
                display_projects(json_data['projects'])


            st.write("Updated Resume JSON:", json_data)



            printresume(resume_json_data)
                






if __name__ == "__main__":
    main()
