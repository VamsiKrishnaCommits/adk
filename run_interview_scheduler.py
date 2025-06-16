# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import time

from interview_scheduler_agent import agent
from dotenv import load_dotenv
from google.adk.agents.run_config import RunConfig
from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.genai import types

load_dotenv(override=True)
logs.log_to_tmp_folder()


async def main():
    app_name = 'interview_scheduler_app'
    user_id_1 = 'recruiter1'
    runner = InMemoryRunner(
        agent=agent.root_agent,
        app_name=app_name,
    )
    session_11 = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id_1
    )

    async def run_prompt(session: Session, new_message: str):
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=new_message)]
        )
        print('** Recruiter says:', content.model_dump(exclude_none=True))
        async for event in runner.run_async(
            user_id=user_id_1,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f'** {event.author}: {event.content.parts[0].text}')

    start_time = time.time()
    print('Start time:', start_time)
    print('========================================')
    print('Testing Interview Scheduling Agent')
    print('========================================')
    
    # Scenario 1: New candidate scheduling
    await run_prompt(session_11, 
        """I need you to schedule an interview for a Software Engineer position. 
        Here are the candidate details:
        - Name: Sarah Johnson
        - Phone: +1-555-0123
        - Email: sarah.johnson@email.com
        - Role: Senior Frontend Developer
        
        Please coordinate with her to find a suitable time slot for next week.""")
    
    # Let the agent take some actions, then follow up
    await run_prompt(session_11, 
        "Great! Can you also send her a confirmation email with all the details?")
    
    # Scenario 2: Multiple candidate coordination
    await run_prompt(session_11, 
        """I have another urgent request. We need to schedule interviews for 2 candidates for a Backend Developer role:
        
        Candidate 1:
        - Name: Michael Chen  
        - Phone: +1-555-0456
        - Email: m.chen@techmail.com
        
        Candidate 2:
        - Name: Emily Rodriguez
        - Phone: +1-555-0789  
        - Email: emily.r@devmail.com
        
        Try to schedule both for this Thursday if possible.""")
    
    # Check progress
    await run_prompt(session_11, 
        "Can you give me a summary of what you've accomplished so far and what's still pending?")
    
    # Scenario 3: Rescheduling request
    await run_prompt(session_11,
        "Sarah Johnson just called and said she can't make the original time. Can you help reschedule her interview?")
    
    # Final status check
    await run_prompt(session_11,
        "Please provide a final summary of all scheduled interviews and their statuses.")
    
    print(
        await runner.artifact_service.list_artifact_keys(
            app_name=app_name, user_id=user_id_1, session_id=session_11.id
        )
    )
    end_time = time.time()
    print('========================================')
    print('End time:', end_time)
    print('Total time:', end_time - start_time)


if __name__ == '__main__':
    print("Starting Interview Scheduling Agent...")
    print("This agent can coordinate interviews by calling candidates, scheduling meetings, and sending emails.")
    print("All tools are mocked to simulate realistic responses.\n")
    asyncio.run(main()) 