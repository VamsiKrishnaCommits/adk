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
from dotenv import load_dotenv
from google.adk.agents.run_config import RunConfig
from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.genai import types

from agent import root_agent

load_dotenv(override=True)
logs.log_to_tmp_folder()


async def main():
    import pdb; pdb.set_trace()
    app_name = 'weather_time_app'
    user_id_1 = 'user1'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    session_11 = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id_1
    )

    async def run_prompt(session: Session, new_message: str):
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=new_message)]
        )
        print('** User says:', content.model_dump(exclude_none=True))
        async for event in runner.run_async(
            user_id=user_id_1,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f'** {event.author}: {event.content.parts[0].text}')

    async def run_prompt_bytes(session: Session, new_message: str):
        content = types.Content(
            role='user',
            parts=[
                types.Part.from_bytes(
                    data=str.encode(new_message), mime_type='text/plain'
                )
            ],
        )
        print('** User says:', content.model_dump(exclude_none=True))
        async for event in runner.run_async(
            user_id=user_id_1,
            session_id=session.id,
            new_message=content,
            run_config=RunConfig(save_input_blobs_as_artifacts=True),
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f'** {event.author}: {event.content.parts[0].text}')

    start_time = time.time()
    print('Start time:', start_time)
    print('====================================')
    print('Testing Weather & Time Agent')
    print('====================================')
    
    # Test weather functionality
    await run_prompt(session_11, 'Hi there!')
    await run_prompt(session_11, 'What is the weather like in New York?')
    await run_prompt(session_11, 'Can you tell me the weather in London?')  # Should show error handling
    
    # Test time functionality  
    await run_prompt(session_11, 'What time is it in New York?')
    await run_prompt(session_11, 'What time is it in Paris?')  # Should show error handling
    
    # Test combined requests
    await run_prompt(session_11, 'Can you tell me both the weather and time in New York?')
    
    # Test bytes input
    await run_prompt_bytes(session_11, 'What is the current weather in New York?')
    
    print(
        await runner.artifact_service.list_artifact_keys(
            app_name=app_name, user_id=user_id_1, session_id=session_11.id
        )
    )
    end_time = time.time()
    print('====================================')
    print('End time:', end_time)
    print('Total time:', end_time - start_time)


if __name__ == '__main__':
    print("Starting Weather & Time Agent...")
    asyncio.run(main()) 