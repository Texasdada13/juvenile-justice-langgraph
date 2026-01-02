"""
Document Loader for Policy Documents

Handles loading and processing of policy documents for the knowledge base.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path


def load_documents(file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Load a document from file path.

    Args:
        file_path: Path to the document
        metadata: Optional metadata to attach

    Returns:
        List of document chunks with content and metadata
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    # Read file content
    content = path.read_text(encoding='utf-8')

    # Create base metadata
    doc_metadata = {
        "source": str(path),
        "filename": path.name,
        "file_type": path.suffix.lower()
    }

    if metadata:
        doc_metadata.update(metadata)

    return [{
        "content": content,
        "metadata": doc_metadata
    }]


def load_policy_directory(
    directory: str,
    recursive: bool = True,
    extensions: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Load all policy documents from a directory.

    Args:
        directory: Path to directory containing documents
        recursive: Whether to search subdirectories
        extensions: File extensions to include (default: .txt, .md, .pdf)

    Returns:
        List of all loaded documents
    """
    if extensions is None:
        extensions = ['.txt', '.md', '.pdf', '.json']

    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    documents = []

    # Get all matching files
    pattern = "**/*" if recursive else "*"
    for file_path in directory.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            try:
                # Determine metadata based on file location
                metadata = extract_metadata_from_path(file_path, directory)

                # Load the document
                docs = load_documents(str(file_path), metadata)
                documents.extend(docs)

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    return documents


def extract_metadata_from_path(file_path: Path, base_dir: Path) -> Dict[str, Any]:
    """
    Extract metadata from file path structure.

    Assumes directory structure like:
    knowledge_base/
        policies/
            eligibility/
            procedures/
        assessment_tools/

    Args:
        file_path: Path to the file
        base_dir: Base directory of the knowledge base

    Returns:
        Extracted metadata
    """
    relative = file_path.relative_to(base_dir)
    parts = relative.parts

    metadata = {
        "category": parts[0] if len(parts) > 1 else "general",
        "subcategory": parts[1] if len(parts) > 2 else None
    }

    # Infer policy type from directory name
    policy_type_mapping = {
        "eligibility": "eligibility",
        "procedures": "procedure",
        "assessment": "risk_assessment",
        "jjdpa": "federal_regulation",
        "state": "state_statute"
    }

    for key, value in policy_type_mapping.items():
        if key in str(relative).lower():
            metadata["policy_type"] = value
            break

    return metadata


def chunk_document(
    content: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Split a document into chunks for vector storage.

    Uses a simple recursive character splitter approach.
    In production, use LangChain's text splitters.

    Args:
        content: Document content
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks
        metadata: Metadata to attach to each chunk

    Returns:
        List of document chunks
    """
    chunks = []

    # Simple splitting by paragraphs first
    paragraphs = content.split('\n\n')

    current_chunk = ""
    current_length = 0

    for para in paragraphs:
        para_length = len(para)

        if current_length + para_length <= chunk_size:
            current_chunk += para + "\n\n"
            current_length += para_length + 2
        else:
            # Save current chunk
            if current_chunk.strip():
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata["chunk_index"] = len(chunks)
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": chunk_metadata
                })

            # Start new chunk with overlap
            if chunk_overlap > 0 and current_chunk:
                overlap_text = current_chunk[-chunk_overlap:]
                current_chunk = overlap_text + para + "\n\n"
                current_length = len(current_chunk)
            else:
                current_chunk = para + "\n\n"
                current_length = para_length + 2

    # Don't forget the last chunk
    if current_chunk.strip():
        chunk_metadata = metadata.copy() if metadata else {}
        chunk_metadata["chunk_index"] = len(chunks)
        chunks.append({
            "content": current_chunk.strip(),
            "metadata": chunk_metadata
        })

    return chunks


# LangChain integration (when available)
def load_with_langchain(file_path: str) -> List[Any]:
    """
    Load documents using LangChain loaders.

    Args:
        file_path: Path to document

    Returns:
        List of LangChain Document objects
    """
    try:
        from langchain.document_loaders import (
            TextLoader,
            PyPDFLoader,
            UnstructuredMarkdownLoader
        )

        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.pdf':
            loader = PyPDFLoader(str(path))
        elif suffix == '.md':
            loader = UnstructuredMarkdownLoader(str(path))
        else:
            loader = TextLoader(str(path))

        return loader.load()

    except ImportError:
        # Fallback to simple loading
        return load_documents(file_path)
