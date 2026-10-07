from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Direct import from rag_engine.py
from rag_engine import rag_engine

app = FastAPI(title="Apex AI Arabia - Healthcare Assistant API")

MOCK_APPOINTMENTS_DB: Dict[str, Dict[str, Any]] = {
    "PAT123": {
        "appointment_id": "APT-9876",
        "patient_name": "Ahmed Al-Farsi",
        "date": "2026-04-15",
        "time": "10:00 AM",
        "department": "Cardiology",
        "status": "confirmed"
    }
}

MOCK_SLOTS = [
    {"date": "2026-04-15", "time": "09:00 AM", "available": True},
    {"date": "2026-04-15", "time": "11:00 AM", "available": True},
    {"date": "2026-04-16", "time": "02:00 PM", "available": True},
]

def tool_check_availability(department: str) -> Dict[str, Any]:
    available_slots = [slot for slot in MOCK_SLOTS if slot["available"]]
    return {"status": "success", "department": department, "available_slots": available_slots}

def tool_book_appointment(patient_id: str, date: str, time: str, department: str) -> Dict[str, Any]:
    if not date or not department:
        return {"status": "error", "message": "Missing required date or department parameters."}
    apt_id = f"APT-{int(datetime.now().timestamp())}"
    MOCK_APPOINTMENTS_DB[patient_id] = {
        "appointment_id": apt_id,
        "date": date,
        "time": time,
        "department": department,
        "status": "confirmed"
    }
    return {"status": "success", "appointment_id": apt_id, "message": "Appointment booked successfully."}

def tool_lookup_appointment(patient_id: str) -> Dict[str, Any]:
    if patient_id in MOCK_APPOINTMENTS_DB:
        apt = MOCK_APPOINTMENTS_DB[patient_id]
        return {"status": "success", "appointment": apt}
    return {"status": "error", "message": "No active appointment found for this patient ID."}

def tool_reschedule_appointment(patient_id: str, appointment_id: str, new_date: str, new_time: str) -> Dict[str, Any]:
    if patient_id in MOCK_APPOINTMENTS_DB and MOCK_APPOINTMENTS_DB[patient_id]["appointment_id"] == appointment_id:
        MOCK_APPOINTMENTS_DB[patient_id]["date"] = new_date
        MOCK_APPOINTMENTS_DB[patient_id]["time"] = new_time
        MOCK_APPOINTMENTS_DB[patient_id]["status"] = "rescheduled"
        return {"status": "success", "appointment_id": appointment_id, "message": "Appointment rescheduled successfully."}
    return {"status": "error", "message": "Appointment not found or invalid ID for rescheduling."}

def tool_cancel_appointment(patient_id: str, appointment_id: str) -> Dict[str, Any]:
    if patient_id in MOCK_APPOINTMENTS_DB and MOCK_APPOINTMENTS_DB[patient_id]["appointment_id"] == appointment_id:
        MOCK_APPOINTMENTS_DB[patient_id]["status"] = "cancelled"
        return {"status": "success", "appointment_id": appointment_id, "message": "Appointment cancelled successfully."}
    return {"status": "error", "message": "Appointment not found or invalid patient ID."}

def tool_escalate_to_human(patient_id: str, reason: str) -> Dict[str, Any]:
    return {"status": "success", "escalation_ticket": "TICK-5541", "message": "Successfully routed to human care team."}

class PatientMessageRequest(BaseModel):
    patient_id: str = Field(..., description="Unique identifier for the patient")
    message: str = Field(..., description="The message sent by the patient")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=[])

class AssistantResponse(BaseModel):
    response_message: str
    intent: str
    requires_human_escalation: bool = False
    tool_calls_executed: List[str] = []
    rag_source_grounding: Optional[Dict[str, Any]] = None

@app.post("/assistant/message", response_model=AssistantResponse)
def handle_assistant_message(payload: PatientMessageRequest):
    msg = payload.message.lower()

    # 1. Guardrail: Prompt Injection Detection
    injection_keywords = ["ignore previous instructions", "system prompt", "override", "developer mode"]
    if any(keyword in msg for keyword in injection_keywords):
        return AssistantResponse(
            response_message="I am restricted to assisting with healthcare services, appointments, and hospital inquiries only.",
            intent="security_violation",
            requires_human_escalation=False,
            tool_calls_executed=[]
        )

    tool_executed = []
    response_msg = "How can I assist you with your healthcare services today?"
    intent = "general"
    escalate = False
    rag_grounding = None

    # 2. Check Explicit Intent Workflows First
    if "book" in msg:
        intent = "booking"
        if "cardiology" not in msg and "general" not in msg and "date" not in msg:
            response_msg = "I'd be happy to help you book. Which department (e.g., Cardiology) and preferred date would you like?"
        else:
            res = tool_book_appointment(payload.patient_id, "2026-04-15", "09:00 AM", "Cardiology")
            if res["status"] == "success":
                tool_executed.append("book_appointment")
                response_msg = f"Confirmed! Your appointment ID is {res['appointment_id']} for April 15 at 09:00 AM."
            else:
                response_msg = "I encountered an error booking your appointment. Let me route you to human assistance."
                escalate = True

    elif "lookup" in msg or "my appointment" in msg or "check status" in msg or "status" in msg:
        intent = "lookup"
        res = tool_lookup_appointment(payload.patient_id)
        tool_executed.append("lookup_appointment")
        if res["status"] == "success":
            apt = res["appointment"]
            response_msg = f"Found your appointment: ID {apt['appointment_id']} for {apt['department']} on {apt['date']} at {apt['time']} (Status: {apt['status']})."
        else:
            response_msg = res["message"]

    elif "reschedule" in msg:
        intent = "rescheduling"
        apt_info = MOCK_APPOINTMENTS_DB.get(payload.patient_id)
        if apt_info:
            res = tool_reschedule_appointment(payload.patient_id, apt_info["appointment_id"], "2026-04-16", "02:00 PM")
            tool_executed.append("reschedule_appointment")
            response_msg = f"Your appointment {apt_info['appointment_id']} has been successfully rescheduled to April 16 at 02:00 PM."
        else:
            response_msg = "I couldn't find an active appointment to reschedule under your patient ID."

    elif "cancel" in msg:
        intent = "cancellation"
        apt_info = MOCK_APPOINTMENTS_DB.get(payload.patient_id)
        if apt_info:
            res = tool_cancel_appointment(payload.patient_id, apt_info["appointment_id"])
            tool_executed.append("cancel_appointment")
            response_msg = f"Your appointment {apt_info['appointment_id']} has been successfully cancelled."
        else:
            response_msg = "I couldn't find an active appointment to cancel."

    elif "available" in msg or "slot" in msg or "when" in msg:
        intent = "availability"
        res = tool_check_availability("Cardiology")
        tool_executed.append("check_availability")
        response_msg = f"Here are the available appointment slots: {res['available_slots']}"

    elif "human" in msg or "agent" in msg or "speak to" in msg:
        intent = "escalation"
        escalate = True
        res = tool_escalate_to_human(payload.patient_id, "Patient requested human assistance.")
        tool_executed.append("escalate_to_human")
        response_msg = "I am routing your request to our human care coordination team. A representative will contact you shortly."

    # 3. Fall Back to RAG Knowledge Base Retrieval
    else:
        rag_result = rag_engine.retrieve(payload.message)
        if rag_result and rag_result.get("confidence_score", 0) > 0.15:
            rag_grounding = {
                "source_id": rag_result.get("source_id"),
                "title": rag_result.get("title"),
                "confidence": rag_result.get("confidence_score", 0.0)
            }
            intent = rag_result.get("category", "info_retrieval")
            response_msg = f"According to hospital guidelines ({rag_result.get('source_id')} - {rag_result.get('title')}): {rag_result.get('content')}"

    return AssistantResponse(
        response_message=response_msg,
        intent=intent,
        requires_human_escalation=escalate,
        tool_calls_executed=tool_executed,
        rag_source_grounding=rag_grounding
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)