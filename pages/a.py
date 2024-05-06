import streamlit as st
from jinja2 import Environment, FileSystemLoader


def remove_empty_lines(html_content):
    # Split the HTML content into lines
    lines = html_content.splitlines()

    # Filter out empty lines
    non_empty_lines = filter(lambda line: line.strip(), lines)

    # Join the non-empty lines back together
    cleaned_html_content = '\n'.join(non_empty_lines)

    return cleaned_html_content

def generate_resume_from_json(json_data, template_path):
    # Load Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("template1.html")

    # Render the template with JSON data
    rendered_resume = template.render({"resume":json_data})

    return rendered_resume

def printresume(resume_json_data):
    rendered_resume = generate_resume_from_json(resume_json_data, 'resume_template.html')
    rendered_resume = str(remove_empty_lines(rendered_resume))
    
    # Write the resume content
    st.write(rendered_resume, unsafe_allow_html=True)


json_data = st.session_state['json_data']
printresume(json_data)