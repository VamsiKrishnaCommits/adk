#!/usr/bin/env python3
"""
Contact-Based Interview Scheduler Runner
Initializes the interview scheduling agent with specific contact details.
"""

import asyncio
import sys
import random
from dataclasses import dataclass
from typing import Optional, List
from agent import root_agent
from dotenv import load_dotenv
from google.adk.cli.utils import logs
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

load_dotenv(override=True)
logs.log_to_tmp_folder()

@dataclass
class ContactInfo:
    """Contact information structure."""
    name: str
    email: str
    phone: str
    role: str
    company: str = "TechCorp Inc."
    
    def __str__(self):
        return f"{self.name} ({self.role}) - {self.email}, {self.phone} @ {self.company}"

@dataclass
class InterviewSetup:
    """Complete interview setup with all participants."""
    hr_contact: ContactInfo
    interviewer: ContactInfo
    interviewee: ContactInfo
    position: str
    interview_type: str = "technical"
    preferred_duration: int = 60  # minutes
    company: str = "TechCorp Inc."
    
    def get_initialization_context(self) -> str:
        """Generate initialization context for the agent."""
        return f"""
INTERVIEW COORDINATION SETUP:
=================================

Company: {self.company}
Position: {self.position}
Interview Type: {self.interview_type}
Duration: {self.preferred_duration} minutes

HR CONTACT:
- Name: {self.hr_contact.name}
- Email: {self.hr_contact.email}
- Phone: {self.hr_contact.phone}
- Role: {self.hr_contact.role}

INTERVIEWER:
- Name: {self.interviewer.name} 
- Email: {self.interviewer.email}
- Phone: {self.interviewer.phone}
- Role: {self.interviewer.role}

CANDIDATE TO SCHEDULE:
- Name: {self.interviewee.name}
- Email: {self.interviewee.email}
- Phone: {self.interviewee.phone}
- Applying for: {self.position}

You are now ready to coordinate this interview. Start by reviewing this information and let me know your next steps.
"""

class ContactBasedRunner:
    """Runner that manages interview scheduling with specific contacts."""
    
    def __init__(self, interview_setup: InterviewSetup, db_url: str = "sqlite:///./interview_scheduler.db"):
        self.setup = interview_setup
        self.runner = None
        self.session = None
        self.db_url = db_url
        
    async def initialize(self):
        """Initialize the ADK runner and session."""
        app_name = f'interview_coordination_{self.setup.interviewee.name.replace(" ", "_").lower()}'
        user_id = f'hr_{self.setup.hr_contact.name.replace(" ", "_").lower()}'
        
        # Create a DatabaseSessionService
        session_service = DatabaseSessionService(db_url=self.db_url)
        
        self.runner = Runner(
            agent=root_agent,
            app_name=app_name,
            session_service=session_service  # Use the database session service
        )
        
        self.session = await self.runner.session_service.create_session(
            app_name=app_name, user_id=user_id
        )
        
        # Initialize the agent with contact information
        await self._send_initialization_message()
        
    async def _send_initialization_message(self):
        """Send the initialization context to the agent."""
        print("🚀 [INITIALIZATION] Setting up interview coordination context...")
        print("=" * 60)
        
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text=self.setup.get_initialization_context())]
        )
        
        async for event in self.runner.run_async(
            user_id=f'hr_{self.setup.hr_contact.name.replace(" ", "_").lower()}',
            session_id=self.session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f"🤖 Agent: {event.content.parts[0].text}")
        
        print("=" * 60)
        
    async def send_message(self, message: str):
        """Send a message to the agent."""
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text=message)]
        )
        
        print(f"\n👤 HR ({self.setup.hr_contact.name}): {message}")
        print("-" * 40)
        
        async for event in self.runner.run_async(
            user_id=f'hr_{self.setup.hr_contact.name.replace(" ", "_").lower()}',
            session_id=self.session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f"🤖 Agent: {event.content.parts[0].text}")
    
    async def run_predefined_scenario(self):
        """Run a predefined scenario with the loaded contacts."""
        print(f"\n🎬 [SCENARIO] Starting interview coordination for {self.setup.position} position")
        
        # Step 1: Initial coordination request
        await self.send_message(
            f"Please start coordinating the interview for {self.setup.interviewee.name}. "
            f"We need to schedule a {self.setup.interview_type} interview for the {self.setup.position} position. "
            f"The interviewer is {self.setup.interviewer.name}. Please reach out to the candidate first to check their availability."
        )
        
        # Step 2: Follow up on scheduling
        await self.send_message(
            "Great! Once you have the candidate's availability, please try to schedule the interview and send confirmation emails to all parties."
        )
        
        # Step 3: Check progress
        await self.send_message(
            "Can you provide me with a summary of the current status and what still needs to be done?"
        )
    
    async def run_interactive_mode(self):
        """Run in interactive mode allowing custom messages."""
        print(f"\n💬 [INTERACTIVE MODE] You can now send custom messages to coordinate the interview")
        print(f"Type 'quit' to exit, 'status' for current progress, 'scenario' to run predefined scenario")
        print("-" * 60)
        
        while True:
            try:
                user_input = input(f"\n👤 {self.setup.hr_contact.name}: ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n👋 Interview coordination session ended.")
                    break
                    
                if user_input.lower() == 'status':
                    await self.send_message("Please provide a detailed status update of all interview coordination activities.")
                    continue
                    
                if user_input.lower() == 'scenario':
                    await self.run_predefined_scenario()
                    continue
                    
                if not user_input.strip():
                    continue
                    
                await self.send_message(user_input)
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Interview coordination session ended.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

# Mock HR data for different scenarios
MOCK_HR_CONTACTS = [
    ContactInfo(
        name="Jennifer Martinez",
        email="j.martinez@techcorp.com", 
        phone="+1-555-HR01",
        role="Senior HR Manager",
        company="TechCorp Inc."
    ),
    ContactInfo(
        name="Michael Thompson",
        email="m.thompson@innovatesoft.com",
        phone="+1-555-HR02", 
        role="Talent Acquisition Lead",
        company="InnovateSoft Solutions"
    ),
    ContactInfo(
        name="Sarah Chen",
        email="s.chen@datatech.io",
        phone="+1-555-HR03",
        role="HR Business Partner",
        company="DataTech Analytics"
    ),
    ContactInfo(
        name="David Rodriguez",
        email="d.rodriguez@cloudnext.com",
        phone="+1-555-HR04",
        role="Recruitment Manager", 
        company="CloudNext Technologies"
    ),
    ContactInfo(
        name="Emily Johnson",
        email="e.johnson@fintech.pro",
        phone="+1-555-HR05",
        role="People Operations Manager",
        company="FinTech Pro"
    )
]

MOCK_INTERVIEWERS = [
    ContactInfo(
        name="Alex Kim",
        email="a.kim@techcorp.com",
        phone="+1-555-ENG01", 
        role="Senior Software Engineer",
        company="TechCorp Inc."
    ),
    ContactInfo(
        name="Lisa Wang",
        email="l.wang@innovatesoft.com",
        phone="+1-555-ENG02",
        role="Tech Lead",
        company="InnovateSoft Solutions"
    ),
    ContactInfo(
        name="Robert Brown",
        email="r.brown@datatech.io", 
        phone="+1-555-ENG03",
        role="Principal Engineer",
        company="DataTech Analytics"
    ),
    ContactInfo(
        name="Maria Garcia",
        email="m.garcia@cloudnext.com",
        phone="+1-555-ENG04",
        role="Engineering Manager",
        company="CloudNext Technologies" 
    ),
    ContactInfo(
        name="James Wilson",
        email="j.wilson@fintech.pro",
        phone="+1-555-ENG05",
        role="Staff Software Engineer",
        company="FinTech Pro"
    )
]

MOCK_CANDIDATES = [
    ContactInfo(
        name="Sarah Johnson",
        email="sarah.johnson@email.com",
        phone="+1-555-0123",
        role="Frontend Developer Candidate",
        company="External"
    ),
    ContactInfo(
        name="Carlos Mendez", 
        email="carlos.m@gmail.com",
        phone="+1-555-0456",
        role="Backend Developer Candidate",
        company="External"
    ),
    ContactInfo(
        name="Priya Patel",
        email="priya.patel@outlook.com", 
        phone="+1-555-0789",
        role="Full Stack Developer Candidate",
        company="External"
    ),
    ContactInfo(
        name="Kevin O'Brien",
        email="kevin.obrien@yahoo.com",
        phone="+1-555-0321",
        role="DevOps Engineer Candidate", 
        company="External"
    ),
    ContactInfo(
        name="Aisha Hassan",
        email="aisha.hassan@protonmail.com",
        phone="+1-555-0654",
        role="Data Scientist Candidate",
        company="External"
    )
]

MOCK_POSITIONS = [
    "Senior Frontend Developer",
    "Backend Software Engineer", 
    "Full Stack Developer",
    "DevOps Engineer",
    "Data Scientist",
    "Mobile App Developer",
    "UI/UX Designer",
    "Product Manager",
    "Engineering Manager",
    "Cloud Architect"
]

def create_sample_setup() -> InterviewSetup:
    """Create a sample interview setup for demonstration."""
    return InterviewSetup(
        hr_contact=MOCK_HR_CONTACTS[0],  # Jennifer Martinez
        interviewer=MOCK_INTERVIEWERS[0],  # Alex Kim
        interviewee=MOCK_CANDIDATES[0],   # Sarah Johnson
        position=MOCK_POSITIONS[0],       # Senior Frontend Developer
        interview_type="technical",
        preferred_duration=90,
        company="TechCorp Inc."
    )

def create_random_setup() -> InterviewSetup:
    """Create a random interview setup with mock data."""
    hr = random.choice(MOCK_HR_CONTACTS)
    interviewer = random.choice([i for i in MOCK_INTERVIEWERS if i.company == hr.company])
    candidate = random.choice(MOCK_CANDIDATES)
    position = random.choice(MOCK_POSITIONS)
    
    return InterviewSetup(
        hr_contact=hr,
        interviewer=interviewer,
        interviewee=candidate,
        position=position,
        interview_type=random.choice(["technical", "behavioral", "system design", "cultural fit"]),
        preferred_duration=random.choice([45, 60, 90, 120]),
        company=hr.company
    )

def list_available_setups():
    """Display available mock setups."""
    print("\n📋 Available Mock HR Scenarios:")
    print("=" * 50)
    
    for i, hr in enumerate(MOCK_HR_CONTACTS, 1):
        print(f"{i}. {hr.name} ({hr.role}) at {hr.company}")
        print(f"   Email: {hr.email} | Phone: {hr.phone}")
        print()

def create_custom_setup(hr_index: int) -> InterviewSetup:
    """Create a setup with a specific HR contact."""
    if hr_index < 1 or hr_index > len(MOCK_HR_CONTACTS):
        raise ValueError("Invalid HR contact index")
    
    hr = MOCK_HR_CONTACTS[hr_index - 1]
    # Find interviewer from same company
    company_interviewers = [i for i in MOCK_INTERVIEWERS if i.company == hr.company]
    interviewer = company_interviewers[0] if company_interviewers else MOCK_INTERVIEWERS[0]
    
    candidate = random.choice(MOCK_CANDIDATES)
    position = random.choice(MOCK_POSITIONS)
    
    return InterviewSetup(
        hr_contact=hr,
        interviewer=interviewer,
        interviewee=candidate,
        position=position,
        interview_type="technical",
        preferred_duration=60,
        company=hr.company
    )

def get_contacts_from_input() -> InterviewSetup:
    """Get contact details from user input."""
    print("📋 Please enter the contact details for interview coordination:")
    print("=" * 55)
    
    # HR Contact
    print("\n👔 HR Contact Information:")
    hr_name = input("Name: ")
    hr_email = input("Email: ")
    hr_phone = input("Phone: ")
    hr_company = input("Company: ")
    
    # Interviewer
    print("\n👨‍💻 Interviewer Information:")
    int_name = input("Name: ")
    int_email = input("Email: ")
    int_phone = input("Phone: ")
    
    # Interviewee
    print("\n👤 Candidate Information:")
    candidate_name = input("Name: ")
    candidate_email = input("Email: ")
    candidate_phone = input("Phone: ")
    
    # Position details
    print("\n💼 Position Information:")
    position = input("Position title: ")
    interview_type = input("Interview type [technical]: ") or "technical"
    
    return InterviewSetup(
        hr_contact=ContactInfo(hr_name, hr_email, hr_phone, "HR Manager", hr_company),
        interviewer=ContactInfo(int_name, int_email, int_phone, "Interviewer", hr_company),
        interviewee=ContactInfo(candidate_name, candidate_email, candidate_phone, "Candidate", "External"),
        position=position,
        interview_type=interview_type,
        company=hr_company
    )

async def main():
    """Main entry point."""
    print("🎯 Contact-Based Interview Scheduler")
    print("=" * 40)
    
    # Parse command line arguments
    db_url = None
    remaining_args = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--db-url" and i + 1 < len(sys.argv):
            db_url = sys.argv[i + 1]
            i += 2
        else:
            remaining_args.append(sys.argv[i])
            i += 1
    
    if len(remaining_args) > 0:
        if remaining_args[0] == "--sample":
            print("📝 Using default sample contact details...")
            setup = create_sample_setup()
        elif remaining_args[0] == "--random":
            print("🎲 Using random mock contact details...")
            setup = create_random_setup()
        elif remaining_args[0] == "--list":
            list_available_setups()
            return
        else:
            print("❌ Invalid argument. Use --sample, --random, --list, or no arguments for custom input.")
            print("Optional: Use --db-url <url> to specify a custom database URL")
            return
    else:
        print("Choose setup option:")
        print("1. Default sample setup")
        print("2. Random mock setup") 
        print("3. Choose specific HR contact")
        print("4. Custom input")
        choice = input("Enter choice (1-4): ")
        
        if choice == "1":
            setup = create_sample_setup()
        elif choice == "2":
            setup = create_random_setup()
        elif choice == "3":
            list_available_setups()
            hr_choice = int(input("Select HR contact (1-5): "))
            setup = create_custom_setup(hr_choice)
        else:
            setup = get_contacts_from_input()
    
    print(f"\n✅ Setup Complete!")
    print(f"Company: {setup.company}")
    print(f"HR: {setup.hr_contact}")
    print(f"Interviewer: {setup.interviewer}")
    print(f"Candidate: {setup.interviewee}")
    print(f"Position: {setup.position}")
    print(f"Interview Type: {setup.interview_type} ({setup.preferred_duration} min)")
    
    if db_url:
        print(f"Using database: {db_url}")
        runner = ContactBasedRunner(setup, db_url=db_url)
    else:
        runner = ContactBasedRunner(setup)
    
    await runner.initialize()

if __name__ == '__main__':
    print("Starting Contact-Based Interview Scheduler...")
    asyncio.run(main()) 