# April 18th, 2025
# wget -r -A.html -P lanchain-docs https://byuistats.github.io/DS250-Course/
# This program takes in a folder as an input *harcode This folder contains downloaded web pages from a website
# DS github html ds 250 
# This folder has a sub and sub-sub folder structure containing .html files that make up the given website
# program recursively reads through the files (Pages/Documents) in the folder, applies a CharacterTextSplitter to create chunks
# loads these individual Chunks as one Vector into a local Vector Database - FAISS
# Semantic Similarity Search which extracts and displays the relevant chunks *Documents* retrieved by the Semantic Search

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

def main():
    #file_count()
    #upload_htmls()
    faiss_query()
    
    
def file_count():
    html_dir = "lanchain-docs/byuistats.github.io/DS250-Course"
    
    # Step 1: Count HTML files in directory
    file_count = sum(
        len([f for f in files if f.endswith(".html")]) 
        for _, _, files in os.walk(html_dir)
    )
    print(f" Found {file_count} HTML files.")

    
def upload_htmls():
    """This function does the following:
    1. Reads recursively through the given folder *ds 250 files within current folder
    2. Loads the Pages (documents)
    3. Loaded Documents are split into chunks using Splitter
    4. These chunks are converted into Language Embeddings and loaded as vectors into a local FAISS Vectors Database
    """
    
    html_dir = "lanchain-docs/byuistats.github.io/DS250-Course"
    html_files = list(Path(html_dir).rglob("*.html"))
    print(f"Found {len(html_files)} .html files")

    # Load HTML files using UnstructuredHTMLLoader
    documents = []
    for html_file in html_files:
        try:
            # Doesn’t rely on file type guessing via libmagic.
            # Forces HTML to be treated as HTML, parsing it with unstructured's internal logic.
            # Cleanly loads each file as a document, so you get exactly what you expect.
            
            loader = UnstructuredHTMLLoader(str(html_file))
            documents.extend(loader.load())
        except Exception as e:
            print(f"⚠️ Skipping {html_file}: {e}")

    print(f"Loaded {len(documents)} documents from HTML files.")
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # Embed and store in FAISS embedding using OpenAIEmbeddings
    print("Generating embeddings and storing in FAISS...")
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Save the FAISS vector store
    vectorstore.save_local("ds250_faiss_index")
    print("Saved FAISS index to: ds250_faiss_index")

    
    

def faiss_query():
    """
    This function does the following:
    1. Load the local FAISS Database
    2. Trigger a Semantic Similarity Search using a Query
    3. This retrieves semantically matching Vectors from the Database
    """   
    
    embeddings = OpenAIEmbeddings()
    # Trust this pickle file because I created it
    new_db = FAISS.load_local("ds250_faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    
    query = "Explain linear regression"
    docs = new_db.similarity_search(query=query)
    
    # Print all the extracted Vectors from the above Query
    for doc in docs:
        print("##------ Page -------##")
        print(doc.metadata['source', 'N/A'])
        print("##------ Content ---- ")
        print(doc.page_content)
    
    
if __name__ == "__main__":
    main()