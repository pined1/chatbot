# April 21st 2025


import os
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI



import streamlit as st 
from dotenv import load_dotenv


load_dotenv()

def main():
    show_ui()


def query(question, chat_history):
    """
    THis function does the following:
    // Retrieve relevant chunks from the FAISS vector database *website*
    // Use previous chat history to maintain conversational context
    // Respond to ther user's new question intelligently
    // chat history is in a tuple (question, answer)
    
    1. Recieves two parameters - "question" - a string and chat_history -- a python list of tuples containing accumulating question-answer pairs
    2. Load the Local FAISS database where the entire website is stored as Embedding vectors
    3. Create a ConversationalBufferMemory object with chat_history
    4. Create a ConversationalRetrievalChain object with the FAISS DB as the Retriever *LLM lets us create Retriever objects against data stores
    5. Invoke the Retriever object with the query and chat history
    6. Returns the response
    """
    
    
    # needed to bring in the embedding object from OpenAI
    embeddings = OpenAIEmbeddings()
    new_db = FAISS.load_local("ds250_faiss_index", embeddings, allow_dangerous_deserialization=True)
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    
    
    # initialize a conversationalretrievalchain
    # retrieves relevant chunks from a db
    # feeds those chunks + question+ history into the LLM 
    # generates a new answer using the retrieved context 
    query = ConversationalRetrievalChain.from_llm(
        llm = llm,
        ## converts the faiss index into the retriever object that langchain can use
        retriever = new_db.as_retriever(),
        return_source_documents = True
    )
    # invoke the chain with
    return query({"question": question, "chat_history": chat_history})
    
    


def show_ui():
    """
    This function does the following:
    1. Implements the Streamlim UI
    2. Implements two session_state vatiables - "messages" - to contain the accumulation Questions and Answers to be displayed on the UI and 
    'chat_history' - the accumulating question-answer pairs as alist of tuples to be served to the retriever obejct as chat_history
    3. For each user query, the response is obtained by invoking the query function and the chat histories are buitl up
    """
    
    st.title("Data Science 250 Chat Bot @ BYU-Idaho")
    st.image("ds_250_Logo.png")
    st.subheader("Please enter your DataScience query")
    
    # here we will initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []
        
    
    # Display chat messages from history on app return 
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            
    # accpting user input
    if prompt := st.chat_input("Enter your question about Data Science 250 course: "):
        
        # now going to invoke the function with the retriever with chat history and display responss in chat container in question - answer pairs
        with st.spinner("Query Loading...."):
            response = query(question=prompt, chat_history=st.session_state.chat_history)
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                st.markdown(response["answer"])
                
            # append the user message into the chat history list
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
            st.session_state.chat_history.extend([(prompt, response["answer"])])
        
    
    
    
    
if __name__ == "__main__":
    main()