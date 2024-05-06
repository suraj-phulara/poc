from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv 
import os
import psycopg2

load_dotenv()

index_name = 'chattest'
def doc_reader(directory):
    file_loader=PyPDFDirectoryLoader(directory)
    documents=file_loader.load()
    return documents

document=doc_reader('documents/')

def chunk_data(docs, chunk_size=100, chunk_overlap=10):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    splitted_docs = text_splitter.split_documents(docs)
    return splitted_docs

documents=chunk_data(docs=document)
print(len(documents))

embeddings=GoogleGenerativeAIEmbeddings(api_key=os.environ['GOOGLE_API_KEY'], model='models/embedding-001')
print(embeddings)

for i, embedding in enumerate(embeddings):
    print(f"Embedding {i+1} has {len(embedding)} dimensions : {embedding}")




# from here i am using pinecone
# pinecone_index = PineconeVectorStore(index=index_name,embedding=embeddings)

# vectorstore = pinecone_index.from_documents(documents=documents,index_name=index_name,embedding=embeddings)
# print(vectorstore)


# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="abc",
    user="postgres",
    password="123456",
    host="localhost",
)


cur = conn.cursor()

embeddings=[[2,3],[4,5]]

# Iterate over your embeddings and insert them into the database
for embedding in embeddings:
    if len(embedding) == 2:  # Check if embedding has 768 values
        cur.execute("INSERT INTO item (embedding) VALUES (%s::vector)", (embedding,))
    else:
        print("Skipping embedding - incorrect size:", len(embedding))



# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()