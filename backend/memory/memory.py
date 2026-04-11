from backend.models import db, ConversationMessage

def get_conversation_history(student_id: str, limit: int = 15):
    """
    Retrieves the recent conversation history for a student.
    Returns a list of dicts formatted for the Groq API.
    """
    messages = ConversationMessage.query.filter_by(student_id=student_id).order_by(ConversationMessage.id.desc()).limit(limit).all()
    
    # We ordered by descending to get the latest `limit` messages, but we need them in chronological order
    messages.reverse()
    
    history = []
    for msg in messages:
        msg_dict = {
            "role": msg.role,
        }
        if msg.content is not None:
            msg_dict["content"] = msg.content
        if msg.tool_call_id is not None:
            msg_dict["tool_call_id"] = msg.tool_call_id
        if msg.tool_calls is not None:
            msg_dict["tool_calls"] = msg.tool_calls
            
        history.append(msg_dict)
    
    return history

def add_message(student_id: str, role: str, content: str = None, tool_call_id: str = None, tool_calls: list = None):
    """
    Persists a new message to the database.
    """
    new_msg = ConversationMessage(
        student_id=student_id,
        role=role,
        content=content,
        tool_call_id=tool_call_id,
        tool_calls=tool_calls
    )
    db.session.add(new_msg)
    db.session.commit()
