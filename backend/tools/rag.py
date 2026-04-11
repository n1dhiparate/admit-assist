from backend.rag.rag import retrieve_context

def rag_search(query: str) -> str:
    """
    Retrieves information from the college admission brochure.
    """
    result = retrieve_context(query)
    if not result:
        return "No relevant information found in the admission brochure."
    return result

tool_schema = {
    "type": "function",
    "function": {
        "name": "rag_search",
        "description": "Searches the official admission brochure for answers to general queries and FAQs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up in the brochure."
                }
            },
            "required": ["query"]
        }
    }
}
