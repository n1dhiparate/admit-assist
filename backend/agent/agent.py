import os
import json
import logging
from groq import Groq

from backend.memory.memory import add_message
from backend.tools.documents import document_checker, tool_schema as doc_schema
from backend.tools.deadlines import deadline_fetcher, tool_schema as deadline_schema
from backend.tools.rag import rag_search, tool_schema as rag_schema

logger = logging.getLogger("AdmitAssist")
logger.setLevel(logging.INFO)


class AdmitAssistAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.tools = [doc_schema, deadline_schema, rag_schema]

        self.system_prompt = (
            "You are Admit-Assist, a smart onboarding assistant. "
            "Always use tools for factual data. Be accurate, clear, and helpful."
        )

    # ---------------- TOOL EXECUTION ----------------
    def execute_tool(self, tool_call, student_id):
        name = tool_call.function.name

        try:
            args = json.loads(tool_call.function.arguments or "{}")
        except:
            args = {}

        try:
            if name == "document_checker":
                return document_checker(student_id)

            elif name == "deadline_fetcher":
                return deadline_fetcher()

            elif name == "rag_search":
                return rag_search(args.get("query", ""))

        except Exception as e:
            logger.error(f"Tool error: {e}")
            return "Unable to fetch data right now."

        return "Tool not found."

    # ---------------- MAIN AGENT ----------------
    def run(self, user_message, student_id):
        from backend.models import Student

        # Save user message
        add_message(student_id, role="user", content=user_message)

        # Fetch student
        student = Student.query.filter_by(student_id=student_id).first()

        # ✅ FIXED KEY: documents (NOT doc)
        onboarding_status = {
            "documents": student.onboarding_status.get("documents", False) if student else False,
            "fees": student.onboarding_status.get("fees", False) if student else False,
            "registration": student.onboarding_status.get("registration", False) if student else False
        }

        # Format clean status
        status_text = f"""
- Documents: {"✅" if onboarding_status["documents"] else "❌"}
- Fees: {"✅" if onboarding_status["fees"] else "❌"}
- Registration: {"✅" if onboarding_status["registration"] else "❌"}
"""

        # ---------------- FIRST LLM CALL ----------------
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "I'm having trouble processing your request. Please try again."

        msg = response.choices[0].message
        tool_calls = msg.tool_calls

        last_tool_result = "No tool used."

        # ---------------- TOOL EXECUTION ----------------
        if tool_calls:
            for tool_call in tool_calls:
                result = self.execute_tool(tool_call, student_id)
                last_tool_result = result

        # ---------------- FINAL CONTROLLED RESPONSE ----------------
        final_prompt = f"""
You are Admit-Assist.

User Question:
{user_message}

Tool Result:
{last_tool_result}

Onboarding Status:
{status_text}

STRICT RULES:
- Answer the question FIRST
- Then show status
- Then suggest ONE next step
- Do NOT show JSON
- Keep response short and clean

FORMAT:

Answer:
<short answer>

Status:
- Documents: ✅ or ❌
- Fees: ✅ or ❌
- Registration: ✅ or ❌

Next Step:
<one clear action>
"""

        try:
            final_response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": final_prompt}]
            )

            reply = final_response.choices[0].message.content

        except Exception as e:
            logger.error(f"Final LLM Error: {e}")
            reply = "I'm having trouble generating a response right now."

        # Save assistant response
        add_message(student_id, role="assistant", content=reply)

        return reply