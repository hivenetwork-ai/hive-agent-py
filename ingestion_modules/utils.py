from typing import List,Sequence,Union
from llama_index.core.schema import TextNode,BaseNode
from llama_index.core import Document


def convert_nodes_to_docs(nodes:Sequence[BaseNode]):
    # Define params
    list_documents = []
    # Iterate over node
    for node in nodes:
        # Get node info
        node_info = node.dict()
        # Define source
        node_content = node_info['text']
        metadata = dict(node_info['metadata'])
        # Update source
        metadata.update({"source":node.ref_doc_id})

        # Define temp document
        temp_doc = Document(text = node_content,metadata = metadata)
        # Append doc
        list_documents.append(temp_doc)
    return list_documents

