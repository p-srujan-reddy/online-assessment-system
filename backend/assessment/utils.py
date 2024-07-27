import chromadb
from langchain_community.embeddings import OpenAIEmbeddings  # Updated import
from langchain_community.vectorstores import Chroma  # Updated import

def get_chroma_client():
    return chromadb.Client()

def process_document(file_url, topic):
    # Initialize ChromaDB client
    client = get_chroma_client()
    
    # Load the document from file_url
    document_content = load_document_from_url(file_url)
    
    # Initialize embeddings provider
    embeddings = OpenAIEmbeddings()  # Initialize your embeddings provider
    
    # Embed the document content
    document_embedding = embeddings.embed(document_content)
    
    # Initialize Chroma collection
    collection_name = f"{topic}_collection"
    collection = Chroma(client, collection_name)
    
    # Add document embedding to ChromaDB collection
    collection.add_documents([{
        "id": file_url,  # Use file URL or another unique identifier
        "embedding": document_embedding
    }])

    # Optionally: Perform queries or other operations
    # results = collection.query("example query")  # Example query

def load_document_from_url(file_url):
    # Implement this function to load your document based on the URL
    # This will depend on how you are storing and serving the document
    # For instance, you might need to download the file if it's hosted online
    with open(file_url, 'r') as file:
        return file.read()
