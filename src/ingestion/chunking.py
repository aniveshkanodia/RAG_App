import os
import sys
import traceback
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType

# Create text splitter once (reused for all non-PDF files)
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
    add_start_index=True
)


def load_and_chunk_document(file_path: str) -> List[Document]:
    """Load and chunk a document based on its file extension.
    
    For PDF files, uses DoclingLoader with DOC_CHUNKS export type which already
    chunks documents using semantic chunking (HybridChunker).
    For other file types, loads documents and then chunks them using RecursiveCharacterTextSplitter.
    
    Args:
        file_path: Path to the file to load and chunk
        
    Returns:
        List of Document chunks ready for indexing
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Load documents
    if file_ext == ".pdf":
        loader = DoclingLoader(
            file_path=file_path,
            export_type=ExportType.DOC_CHUNKS  # Already chunks with semantic chunking
        )
        chunks = loader.load()  # PDFs are already chunked
    elif file_ext == ".txt":
        loader = TextLoader(file_path)
        documents = loader.load()
        chunks = TEXT_SPLITTER.split_documents(documents)
    elif file_ext in [".docx", ".doc"]:
        loader = UnstructuredWordDocumentLoader(file_path)
        documents = loader.load()
        chunks = TEXT_SPLITTER.split_documents(documents)
    else:
        raise ValueError(
            f"Unsupported file type: {file_ext}. "
            f"Supported types: .pdf, .txt, .docx, .doc"
        )
    
    return chunks


if __name__ == "__main__":
    try:
        file_path = sys.argv[1]
        chunks = load_and_chunk_document(file_path)
        print(f"Loaded and chunked: {len(chunks)} chunk(s) from {file_path}\n")
        print("=" * 60)
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"Length: {len(chunk.page_content)} characters")
            
            if chunk.metadata:
                print("Metadata:")
                for key, value in chunk.metadata.items():
                    print(f"  {key}: {value}")
            
            print("Content:")
            print(chunk.page_content)
            print("-" * 60)
        
    except IndexError:
        print("Error: No file path provided")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
