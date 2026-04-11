import json

def deadline_fetcher() -> str:
    """
    Returns important admission deadlines.
    """
    deadlines = {
        "Document Verification": "August 1 - August 10",
        "Hostel Application List": "August 18",
        "Course Registration Opens": "August 20",
        "Semester Fee Deadline": "August 25"
    }
    return json.dumps(deadlines)

tool_schema = {
    "type": "function",
    "function": {
        "name": "deadline_fetcher",
        "description": "Returns a list of important admission deadlines.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
