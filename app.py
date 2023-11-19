import streamlit as st
from PyPDF2 import PdfReader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import os

# Streamlit app title and description
st.title("DMV Chat Assistant")
st.write("Ask questions about DMV services, rules, and procedures.")

# Define the path to the DMV PDF file
default_pdf_path = 'dmv.pdf'  # Replace with the path to your DMV PDF file

# Input for the OpenAI API key
openai_api_key = st.text_input("Enter your OpenAI API Key", type='password')

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ''
            text += page_text
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def chat_with_pdf(text, openai_key, query):
    try:
        os.environ['OPENAI_API_KEY'] = openai_key
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=800,
            chunk_overlap=200,
            length_function=len,
        )
        texts = text_splitter.split_text(text)
        embeddings = OpenAIEmbeddings()
        document_search = FAISS.from_texts(texts, embeddings)
        from langchain.chains.question_answering import load_qa_chain
        from langchain.llms import OpenAI
        chain = load_qa_chain(OpenAI(), chain_type="contextual_qa")
        docs = document_search.similarity_search(query, k=5)  # Adjust 'k' as needed
        result = chain.run(input_documents=docs, question=query)
        return result
    except Exception as e:
        st.error(f"Error processing the query: {str(e)}")
        return None

# User input for questions
user_question = st.text_input("Ask a DMV-related question")

# Process the user question on button click
if st.button("Ask DMV Assistant"):
    if openai_api_key and user_question:
        pdf_text = extract_text_from_pdf(default_pdf_path)
        if pdf_text:
            result = chat_with_pdf(pdf_text, openai_api_key, user_question)
            if result:
                st.write("Answer:", result)
            else:
                st.warning("No answer found for the given question.")
        else:
            st.warning("Unable to extract text from the PDF. Please check the file path.")
    else:
        st.warning("Please provide an OpenAI API Key and enter a question.")

if __name__ == "__main__":
    st.set_option('deprecation.showfileUploaderEncoding', False)

