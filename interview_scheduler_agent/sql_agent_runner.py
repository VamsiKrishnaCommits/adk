#!/usr/bin/env python3
"""
SQL Agent Runner
Interactive runner for the PostgreSQL query agent.
"""

import asyncio
import sys
from sql_agent import sql_agent
from dotenv import load_dotenv
from google.adk.cli.utils import logs
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv(override=True)
logs.log_to_tmp_folder()

class SQLAgentRunner:
    """Runner that manages the SQL query agent."""
    
    def __init__(self, db_url: str = "sqlite:///./sql_agent.db"):
        self.runner = None
        self.session = None
        self.db_url = db_url
        
    async def initialize(self, initial_query: str = None):
        """Initialize the ADK runner and session."""
        app_name = 'sql_query_agent'
        user_id = 'sql_analyst'
        
        # Create a DatabaseSessionService
        session_service = InMemorySessionService()
        
        self.runner = Runner(
            agent=sql_agent,
            app_name=app_name,
            session_service=session_service
        )
        
        self.session = await self.runner.session_service.create_session(
            app_name=app_name, user_id=user_id
        )
        
        # Initialize the agent with database schema information or user query
        if initial_query:
            await self._send_initialization_message(initial_query)
        else:
            await self._send_initialization_message()
        
    async def _send_initialization_message(self, natural_language_query: str = None):
        """Send the initialization context or natural language query to the agent."""
        if natural_language_query:
            print("🚀 [QUERY] Processing natural language query...")
            print("=" * 70)
            message = natural_language_query
        else:
            print("🚀 [INITIALIZATION] Setting up SQL query agent with database schema...")
            print("=" * 70)
            
            message = """
DATABASE SCHEMA LOADED:
=======================

I have access to a customer data processing pipeline database with 8 main tables:

1. CUSTOMER_MASTER - Main customer information with account details and API keys
2. CUSTOMER_PREFERENCES - Additional customer configuration and preferences  
3. API_MASTER - Downstream API definitions and configurations
4. PIPELINE_MASTER - Abstraction layer over API master with meaningful pipeline names
5. PIPLELINE_CUSTOMER_CONFIG - Customer-specific pipeline configurations per queue
6. DI_AUDIT - Audit logs for downstream integration actions and API calls
7. CASE_MASTER - Main case/file processing table with upload and status information
8. DOCUMENT_CLASSIFICATION - Individual documents within cases with classification results

Key Relationships:
- customer_master links to all other tables via customer_id
- case_master connects to document_classification via case_id
- pipeline_master connects to api_master via api_id
- di_audit tracks all downstream actions with full traceability

I'm ready to help you analyze this database! You can:
- Ask me to find specific data patterns
- Request complex analytical queries
- Ask for performance analysis
- Get help with query optimization

What would you like to explore?
"""
        
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text=message)]
        )
        
        async for event in self.runner.run_async(
            user_id='sql_analyst',
            session_id=self.session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f"🤖 SQL Agent: {event.content.parts[0].text}")
        
        print("=" * 70)
        
    async def send_message(self, message: str):
        """Send a message to the SQL agent."""
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text=message)]
        )
        
        print(f"\n👤 User: {message}")
        print("-" * 50)
        
        async for event in self.runner.run_async(
            user_id='sql_analyst',
            session_id=self.session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f"🤖 SQL Agent: {event.content.parts[0].text}")
    
    async def run_sample_queries(self):
        """Run some sample queries to demonstrate the agent's capabilities."""
        print(f"\n🎬 [DEMO] Running sample analytical queries")
        
        sample_queries = [
            "Show me all customers and count how many cases each customer has processed",
            "Find all failed API calls in the last month and group them by customer",
            "Analyze document processing performance - which customers have the most documents per case?",
            "Show me the pipeline configuration for customers who use multiple queues",
            "Find customers who have uploaded files but haven't configured any pipelines"
        ]
        
        for i, query in enumerate(sample_queries, 1):
            print(f"\n📊 Sample Query {i}:")
            await self.send_message(query)
            
            # Add small delay between queries
            await asyncio.sleep(1)
    
    async def run_interactive_mode(self):
        """Run in interactive mode allowing custom SQL queries and analysis."""
        print(f"\n💬 [INTERACTIVE MODE] Ask me anything about the database!")
        print(f"Examples:")
        print(f"  - 'Find all customers in the Healthcare industry'")
        print(f"  - 'Show me API performance metrics for last week'")
        print(f"  - 'Which documents failed classification?'")
        print(f"  - 'Optimize this query: SELECT * FROM customer_master'")
        print(f"Type 'quit' to exit, 'demo' to run sample queries, 'schema' for table info")
        print("-" * 70)
        
        while True:
            try:
                user_input = input(f"\n👤 SQL Query/Question: ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n👋 SQL analysis session ended.")
                    break
                    
                if user_input.lower() == 'demo':
                    await self.run_sample_queries()
                    continue
                    
                if user_input.lower() == 'schema':
                    await self.send_message("Show me the complete database schema with table relationships and key columns")
                    continue
                    
                if not user_input.strip():
                    continue
                    
                await self.send_message(user_input)
                
            except KeyboardInterrupt:
                print(f"\n\n👋 SQL analysis session ended.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

async def main():
    """Main entry point."""
    print("🗃️ PostgreSQL Query Agent")
    print("=" * 30)
    
    # Parse command line arguments
    db_url = None
    run_demo = False
    initial_query = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--db-url" and i + 1 < len(sys.argv):
            db_url = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--demo":
            run_demo = True
            i += 1
        elif sys.argv[i] == "--query" and i + 1 < len(sys.argv):
            initial_query = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if db_url:
        print(f"Using database: {db_url}")
        runner = SQLAgentRunner(db_url=db_url)
    else:
        runner = SQLAgentRunner()
    
    # If no initial query provided via command line, prompt for one
    if not initial_query and not run_demo:
        print("\nEnter your natural language query (or press Enter to skip):")
        initial_query = input("> ").strip()
        if not initial_query:
            initial_query = None
    
    await runner.initialize(initial_query)
    
    if run_demo:
        await runner.run_sample_queries()
        
        print("\n" + "=" * 50)
        print("Demo complete! Switch to interactive mode? (y/n)")
        choice = input("> ")
        if choice.lower().startswith('y'):
            await runner.run_interactive_mode()
    elif not initial_query:
        await runner.run_interactive_mode()
    else:
        # If an initial query was provided, ask if they want to continue with interactive mode
        print("\n" + "=" * 50)
        print("Query processed! Continue with interactive mode? (y/n)")
        choice = input("> ")
        if choice.lower().startswith('y'):
            await runner.run_interactive_mode()

if __name__ == '__main__':
    print("Starting PostgreSQL Query Agent...")
    asyncio.run(main()) 