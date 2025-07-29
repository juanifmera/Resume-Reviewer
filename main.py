from dotenv import load_dotenv, find_dotenv
import os
import PyPDF2
import io
from openai import OpenAI
import streamlit as st

def main():

    load_dotenv(find_dotenv())
    icon = os.path.join(os.getcwd(), 'Resume Reviewer', 'icons', 'reviewer.png')

    st.set_page_config(page_title='AI Resume Reviewer', page_icon=icon, layout='centered')

    st.title('AI Resume Reviewer')
    st.markdown('Upload your resume and get AI-powered feedback tailored to your needs')

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    uploaded_file = st.file_uploader('Upload your resume (PDF or TXT)', type=['pdf', 'txt'])
    job_role = st.text_input('Enter the job role you are targetting (optional)')

    analyze = st.button('Analyze Resume')

    def extract_text_from_pdf(pdf_file):
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text

    def extract_text_from_file(uploaded_file):
        if uploaded_file.type == 'application/pdf':
            return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))

        raw_bytes = uploaded_file.read()
        try:
            return raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return raw_bytes.decode('latin1')
            except UnicodeDecodeError:
                raise ValueError("No se pudo decodificar el archivo. Asegurate de que sea un archivo .txt legible.")

    if analyze and uploaded_file:

        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error('File does not have any content...')
                st.stop()

            prompt = f'''
            You are an expert resume reviewer with deep experience in HR and recruitment.

            You will receive the resume content of a candidate and the job role they are applying for. Your task has **two steps**:

            **Step 1: Score the Resume**
            Give a rating from 1 to 10 indicating how well the resume aligns with the job role provided. Base your score on relevance of skills, experience, clarity, and completeness. Explain briefly the rationale behind the score.

            **Step 2: Recommendations**
            Based on the score, provide tailored and practical suggestions on how the candidate can improve their resume to better align with the job role "{job_role if job_role else 'general position'}". Be specific — include what to add, remove or modify, and why.

            Here is the resume content:
            {file_content}
            '''

            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role':'system', 'content':'You are an expert resume reviewer with years of ecperience in HR and recruitment'},
                    {'role':'user', 'content':prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            st.markdown('### Analysis Results')
            st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error(f'There was an error while trying to read and analyze the file content. ERROR: {e}')

if __name__ == '__main__':
    main()