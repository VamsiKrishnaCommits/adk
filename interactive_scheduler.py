#!/usr/bin/env python3
"""
Interactive Interview Scheduler
Allows you to test the interview scheduling agent with custom scenarios.
"""

import asyncio
from interview_scheduler_agent import agent
from dotenv import load_dotenv
from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv(override=True)
logs.log_to_tmp_folder()

async def interactive_session():
    """Run an interactive session with the interview scheduling agent."""
    
    app_name = 'interactive_scheduler'
    user_id = 'recruiter_interactive'
    
    runner = InMemoryRunner(
        agent=agent.root_agent,
        app_name=app_name,
    )
    
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    
    print("🤖 Interview Scheduling Agent Ready!")
    print("=" * 50)
    print("I can help you schedule interviews by:")
    print("• Calling candidates to check availability")
    print("• Scheduling calendar appointments") 
    print("• Sending confirmation emails")
    print("• Keeping track of all interactions")
    print("\nType 'quit' to exit\n")
    
    # Sample scenarios for inspiration
    print("💡 Sample scenarios to try:")
    print("1. 'Schedule an interview for John Doe (john@email.com, +1-555-1234) for a Data Scientist role'")
    print("2. 'I need to coordinate interviews for 3 candidates this week'")
    print("3. 'Can you check what interviews we have scheduled so far?'")
    print("4. 'Sarah needs to reschedule her interview - can you help?'")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n🧑‍💼 You: ")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thanks for using the Interview Scheduler!")
                break
                
            if not user_input.strip():
                continue
                
            # Send message to agent
            content = types.Content(
                role='user', parts=[types.Part.from_text(text=user_input)]
            )
            
            print("🤖 Agent:", end=" ")
            response_parts = []
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content,
            ):
                if event.content.parts and event.content.parts[0].text:
                    text = event.content.parts[0].text
                    print(text, end="", flush=True)
                    response_parts.append(text)
            
            print()  # New line after agent response
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using the Interview Scheduler!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")

def main():
    """Main entry point."""
    print("Starting Interactive Interview Scheduler...")
    asyncio.run(interactive_session())

if __name__ == '__main__':
    main() 