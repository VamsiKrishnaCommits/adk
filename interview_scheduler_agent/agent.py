import datetime
from typing import Dict, Any
from google.adk.agents import Agent

# In-memory notepad storage
notepad_storage = {"notes": ""}

def call_contact(contact_name: str, phone_number: str, purpose: str) -> Dict[str, Any]:
    """Mock tool to call someone and get user input as the response.
    
    Args:
        contact_name (str): Name of the person to call
        phone_number (str): Phone number to call
        purpose (str): Purpose of the call
    
    Returns:
        dict: Call summary based on user input
    """
    # Extract role from purpose or default to "Contact"
    role = ""
    if "interviewer" in purpose.lower():
        role = "Interviewer"
    elif "candidate" in purpose.lower():
        role = "Candidate"
    elif "hr" in purpose.lower() or "recruiter" in purpose.lower():
        role = "HR/Recruiter"
    else:
        role = "Contact"

    print(f"\n📞 Simulating call to {contact_name} ({role})")
    print(f"Phone: {phone_number}")
    print(f"Purpose: {purpose}")
    print(f"\nPlease describe the call outcome with {role}:")
    
    outcome = input("> ")
    
    # Check if it was a successful call based on keywords
    success = "no answer" not in outcome.lower() and "failed" not in outcome.lower()
    
    result = {
        "status": "success" if success else "no_answer",
        "contact_name": contact_name,
        "contact_role": role,
        "phone_number": phone_number,
        "discussion_summary": outcome,
        "duration_minutes": 5 if success else 0,
        "next_steps": "Follow up via email" if not success else "Proceed with scheduling"
    }
    
    print(f"\n📞 Call Result with {role}: {outcome}")
    return result

def schedule_calendar(candidate_name: str, date: str, time: str, duration_minutes: int = 60, interview_type: str = "technical") -> Dict[str, Any]:
    """Mock tool to schedule a calendar appointment with user input.
    
    Args:
        candidate_name (str): Name of the candidate
        date (str): Date for the interview
        time (str): Time for the interview
        duration_minutes (int): Duration of the interview
        interview_type (str): Type of interview
    
    Returns:
        dict: Scheduling result based on user input
    """
    print(f"\n📅 Attempting to schedule: {interview_type} interview")
    print(f"For: {candidate_name}")
    print(f"Date: {date} at {time} ({duration_minutes} minutes)")
    print("\nEnter scheduling result (e.g., confirmed, conflict, alternative time, etc.):")
    
    outcome = input("> ")
    
    # Check if scheduling was successful based on keywords
    success = "conflict" not in outcome.lower() and "fail" not in outcome.lower()
    
    result = {
        "status": "success" if success else "conflict",
        "candidate_name": candidate_name,
        "scheduled_date": date,
        "scheduled_time": time,
        "duration_minutes": duration_minutes,
        "interview_type": interview_type,
        "confirmation": outcome,
        "meeting_id": f"INT_{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
    }
    
    print(f"\n📅 Scheduling Result: {outcome}")
    return result

def send_email(recipient_email: str, subject: str, message_type: str, additional_details: str = "") -> Dict[str, Any]:
    """Mock tool to send emails and get immediate simulated response.
    
    Args:
        recipient_email (str): Email address of the recipient
        subject (str): Email subject line
        message_type (str): Type of email
        additional_details (str): Any additional details
    
    Returns:
        dict: Email sending result and recipient's response
    """
    # Extract role from message_type or subject
    role = ""
    if any(word in message_type.lower() or word in subject.lower() for word in ["interviewer", "interview availability"]):
        role = "Interviewer"
    elif any(word in message_type.lower() or word in subject.lower() for word in ["candidate", "applicant"]):
        role = "Candidate"
    elif any(word in message_type.lower() or word in subject.lower() for word in ["hr", "recruiter", "recruitment"]):
        role = "HR/Recruiter"
    else:
        role = "Recipient"

    print(f"\n📧 Sending {message_type} email")
    print(f"To: {recipient_email} ({role})")
    print(f"Subject: {subject}")
    print(f"Additional Details: {additional_details}")
    print("\nEnter email sending result:")
    
    outcome = input("> ")
    
    # If email was delivered successfully, get the simulated response
    if "fail" not in outcome.lower() and "error" not in outcome.lower():
        print(f"\n📨 Simulate {role}'s response to this email:")
        print("(Enter their reply or press Enter for no response)")
        email_response = input("> ")
        
        # If they provided a response, get response time
        if email_response.strip():
            print(f"\nHow long did {role} take to respond? (e.g., '5 minutes', '2 hours', etc.)")
            response_time = input("> ")
        else:
            email_response = "No response received"
            response_time = "N/A"
    else:
        email_response = "Email not delivered"
        response_time = "N/A"
    
    result = {
        "status": "success" if "fail" not in outcome.lower() and "error" not in outcome.lower() else "failed",
        "recipient_email": recipient_email,
        "recipient_role": role,
        "subject": subject,
        "message_type": message_type,
        "delivery_confirmation": outcome,
        "recipient_response": email_response,
        "response_time": response_time,
        "sent_at": datetime.datetime.now().isoformat()
    }
    
    print(f"\n📧 Email Result to {role}: {outcome}")
    if result["status"] == "success":
        print(f"📨 {role}'s Response: {email_response}")
        if response_time != "N/A":
            print(f"⏱️ Response Time: {response_time}")
    
    return result

def manage_notes(action: str, content: str = "") -> Dict[str, Any]:
    """Mock notepad tool with user input for verification.
    
    Args:
        action (str): Either "read", "write", or "append"
        content (str): Content to write/append
    
    Returns:
        dict: Result of the notepad operation
    """
    print(f"\n📝 Notes Operation: {action}")
    if content:
        print(f"Content: {content}")
    
    if action == "read":
        print("\nEnter current notes content for testing:")
        notes = input("> ")
        return {
            "status": "success",
            "action": "read",
            "current_notes": notes,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    print("\nEnter result of notes operation (e.g., saved, failed, etc.):")
    outcome = input("> ")
    
    result = {
        "status": "success" if "fail" not in outcome.lower() else "error",
        "action": action,
        "message": outcome,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if action in ["write", "append"]:
        result["content"] = content
    
    print(f"\n📝 Notes Result: {outcome}")
    return result

def human_in_loop(situation: str, context: str, suggested_actions: str = "") -> Dict[str, Any]:
    """Function for human intervention in conflict resolution.
    
    Args:
        situation (str): The current situation or problem that needs resolution
        context (str): Background information about the situation
        suggested_actions (str): Optional suggested actions or solutions
    
    Returns:
        dict: Human decision and any additional instructions
    """
    print("\n🤝 Human Intervention Needed")
    print("=" * 50)
    print(f"Situation: {situation}")
    print(f"Context: {context}")
    if suggested_actions:
        print(f"Suggested Actions: {suggested_actions}")
    
    print("\nPlease provide your decision/guidance:")
    decision = input("> ")
    
    # Get any additional instructions if needed
    print("\nAny additional instructions? (Press Enter if none)")
    additional_instructions = input("> ")
    
    result = {
        "status": "resolved" if "cancel" not in decision.lower() else "cancelled",
        "decision": decision,
        "additional_instructions": additional_instructions if additional_instructions else "None",
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    print(f"\n🤝 Human Decision: {decision}")
    if additional_instructions:
        print(f"Additional Instructions: {additional_instructions}")
    
    return result

# Create the interview scheduling agent
root_agent = Agent(
    name="interview_scheduler_agent",
    model="gemini-2.5-flash-preview-04-17",
    description=(
        "An intelligent interview scheduling agent that coordinates interviews by calling participants, "
        "scheduling appointments, sending emails, and maintaining detailed notes, with all responses "
        "being simulated through user input for testing purposes."
    ),
    instruction=(
        "You are an experienced interview coordinator. Your job is to efficiently schedule interviews following this specific workflow:\n"
        "1. First contact the interviewer:\n"
        "   - Call them to get available time slots\n"
        "   - If no answer, send them an email requesting availability\n"
        "   - If still no response, escalate to HR/recruiter via call\n\n"
        "2. For any conflicts or issues:\n"
        "   - Always contact HR/recruiter by phone first\n"
        "   - If call not answered, follow up with email\n"
        "   - Clearly explain the situation and what resolution is needed\n"
        "   - Wait for their guidance before proceeding\n\n"
        "3. Once interviewer slots are confirmed:\n"
        "   - Contact the candidate to check their preference from available slots\n"
        "   - If no answer, send a follow-up email\n"
        "   - If scheduling conflicts arise, escalate to recruiter\n\n"
        "4. For any complex situations or blockers:\n"
        "   - Immediately call the recruiter to explain the situation\n"
        "   - Provide all relevant details and attempted solutions\n"
        "   - Follow their guidance for resolution\n\n"
        "Always be professional and organized. Consider time zones and "
        "scheduling constraints. For any uncertainty or conflicts, always escalate to the recruiter - "
        "call first, then email if no response. Make sure to use the tools to the best of your ability "
        "and to not make up information."
    ),
    tools=[call_contact, schedule_calendar, send_email],
) 