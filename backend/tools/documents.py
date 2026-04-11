from backend.models import Student

def document_checker(student_id: str = None) -> str:
    """
    Checks the document submission status for a specific student.
    Returns whether documents are completed or missing.
    """
    if not student_id:
        return "Error: Missing student context."

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return "Error: Student not found in the system."
        
    status = student.onboarding_status
    if status.get("documents", False):
        return "Documents are COMPLETE and verified."
    else:
        return "Documents are PENDING/MISSING."

tool_schema = {
    "type": "function",
    "function": {
        "name": "document_checker",
        "description": "Checks whether the student has completed their document verification.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "The student ID to check documents for."
                }
            },
            "required": ["student_id"]
        }
    }
}
