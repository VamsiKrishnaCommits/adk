import datetime
import json
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent

# Optional import for actual database connectivity
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

class DatabaseConnection:
    """Handles PostgreSQL database connections"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "postgresql://user:password@localhost:5432/database"
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        if not PSYCOPG2_AVAILABLE:
            print("psycopg2 not available - using mock database connection")
            return True
        try:
            self.connection = psycopg2.connect(self.connection_string)
            return True
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

# Global database connection instance
db_connection = DatabaseConnection()

# Database schema information for the agent
DATABASE_SCHEMA = {
    "customer_master": {
        "description": "Main customer information table with account details, API keys, and configuration",
        "key_columns": ["customer_id", "CustomerName", "api_key", "extraction_type"],
        "relationships": {
            "customer_preferences": "customer_id",
            "case_master": "customer_id", 
            "document_classification": "customer_id",
            "pipleline_customer_config": "customer_id",
            "di_audit": "customer_id"
        }
    },
    "customer_preferences": {
        "description": "Additional customer configuration and preferences",
        "key_columns": ["id", "customer_id", "preference_name", "preference_value"],
        "relationships": {
            "customer_master": "customer_id"
        }
    },
    "api_master": {
        "description": "Downstream API definitions and configurations",
        "key_columns": ["api_id", "api_url", "api_method_type", "api_type"],
        "relationships": {
            "pipeline_master": "api_id",
            "di_audit": "api_id"
        }
    },
    "pipeline_master": {
        "description": "Abstraction layer over API master with meaningful pipeline names",
        "key_columns": ["pipeline_id", "pipeline_name", "api_id"],
        "relationships": {
            "api_master": "api_id",
            "pipleline_customer_config": "pipeline_id"
        }
    },
    "pipleline_customer_config": {
        "description": "Customer-specific pipeline configurations per queue",
        "key_columns": ["pipeline_customer_id", "pipeline_id", "customer_id", "queue_name"],
        "relationships": {
            "pipeline_master": "pipeline_id",
            "customer_master": "customer_id",
            "di_audit": "pipeline_customer_id"
        }
    },
    "di_audit": {
        "description": "Audit logs for downstream integration actions and API calls",
        "key_columns": ["id", "pipeline_customer_id", "customer_id", "queue_name", "case_id", "doc_id"],
        "relationships": {
            "pipleline_customer_config": "pipeline_customer_id",
            "customer_master": "customer_id",
            "api_master": "api_id",
            "case_master": "case_id"
        }
    },
    "case_master": {
        "description": "Main case/file processing table with upload and status information",
        "key_columns": ["case_id", "customer_id", "user_id", "queue_name", "file_name"],
        "relationships": {
            "customer_master": "customer_id",
            "document_classification": "case_id",
            "di_audit": "case_id"
        }
    },
    "document_classification": {
        "description": "Individual documents within cases with classification and parsing results",
        "key_columns": ["id", "customer_id", "case_id", "document_classification_id", "documnt_class"],
        "relationships": {
            "customer_master": "customer_id",
            "case_master": "case_id"
        }
    }
}

def execute_sql_query(query: str, explanation: str = "") -> Dict[str, Any]:
    """Execute a PostgreSQL query and return results with error handling.
    
    Args:
        query (str): The SQL query to execute
        explanation (str): Optional explanation of what the query is trying to achieve
    
    Returns:
        dict: Query execution results including data, metadata, and any errors
    """
    print(f"\n🔍 Executing SQL Query")
    if explanation:
        print(f"Purpose: {explanation}")
    print(f"Query: {query}")
    print("-" * 50)
    
    # Simulate database connection and execution
    print("Enter query execution result:")
    print("Format: 'success' followed by JSON results, or 'error: <error_message>'")
    outcome = input("> ")
    
    if outcome.lower().startswith('error'):
        error_msg = outcome[6:].strip() if len(outcome) > 6 else "Unknown database error"
        result = {
            "status": "error",
            "query": query,
            "error_message": error_msg,
            "suggestion": "Check table names, column names, and syntax",
            "executed_at": datetime.datetime.now().isoformat()
        }
        print(f"\n❌ Query Error: {error_msg}")
        return result
    
    # For successful queries, parse the result
    try:
        if outcome.lower() == 'success':
            print("Enter the query results (JSON format or row count):")
            results_input = input("> ")
            
            if results_input.isdigit():
                # Just a row count
                results = {"row_count": int(results_input), "rows": []}
            else:
                # Try to parse as JSON
                try:
                    results = json.loads(results_input)
                except json.JSONDecodeError:
                    results = {"raw_output": results_input}
        else:
            # Assume the outcome contains the results
            try:
                results = json.loads(outcome)
            except json.JSONDecodeError:
                results = {"raw_output": outcome}
        
        result = {
            "status": "success",
            "query": query,
            "results": results,
            "row_count": len(results.get("rows", [])) if isinstance(results, dict) and "rows" in results else None,
            "executed_at": datetime.datetime.now().isoformat()
        }
        
        print(f"\n✅ Query executed successfully")
        if result["row_count"] is not None:
            print(f"Rows returned: {result['row_count']}")
            
    except Exception as e:
        result = {
            "status": "error", 
            "query": query,
            "error_message": f"Result parsing error: {str(e)}",
            "executed_at": datetime.datetime.now().isoformat()
        }
        print(f"\n❌ Result parsing error: {e}")
    
    return result

def analyze_query_performance(query: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze query performance and suggest optimizations.
    
    Args:
        query (str): The executed SQL query
        results (dict): Results from the query execution
    
    Returns:
        dict: Performance analysis and optimization suggestions
    """
    print(f"\n📊 Analyzing Query Performance")
    print(f"Query: {query}")
    print("Enter performance metrics (execution time, rows scanned, etc.):")
    
    metrics_input = input("> ")
    
    # Basic analysis based on query patterns
    analysis = {
        "query": query,
        "performance_metrics": metrics_input,
        "suggestions": [],
        "analyzed_at": datetime.datetime.now().isoformat()
    }
    
    # Add automated suggestions based on query patterns
    query_lower = query.lower()
    
    if "select *" in query_lower:
        analysis["suggestions"].append("Consider selecting specific columns instead of SELECT *")
    
    if "where" not in query_lower and ("update" in query_lower or "delete" in query_lower):
        analysis["suggestions"].append("WARNING: Update/Delete without WHERE clause affects all rows")
    
    if "join" in query_lower and "index" not in metrics_input.lower():
        analysis["suggestions"].append("Consider adding indexes on join columns for better performance")
    
    if "order by" in query_lower and "limit" not in query_lower:
        analysis["suggestions"].append("Consider adding LIMIT clause for large result sets")
    
    print(f"\n📊 Performance Analysis Complete")
    for suggestion in analysis["suggestions"]:
        print(f"💡 {suggestion}")
    
    return analysis

def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get detailed schema information for a specific table.
    
    Args:
        table_name (str): Name of the table to analyze
    
    Returns:
        dict: Table schema information including columns, types, and relationships
    """
    print(f"\n📋 Getting Schema for Table: {table_name}")
    
    if table_name in DATABASE_SCHEMA:
        schema_info = DATABASE_SCHEMA[table_name].copy()
        schema_info["table_name"] = table_name
        
        print("Enter actual column details (JSON format) or press Enter for schema info:")
        user_input = input("> ")
        
        if user_input.strip():
            try:
                column_details = json.loads(user_input)
                schema_info["columns"] = column_details
            except json.JSONDecodeError:
                schema_info["columns"] = {"error": "Invalid JSON format"}
        
        print(f"\n📋 Schema Info for {table_name}:")
        print(f"Description: {schema_info['description']}")
        print(f"Key Columns: {schema_info['key_columns']}")
        print(f"Relationships: {schema_info['relationships']}")
        
        return schema_info
    else:
        result = {
            "table_name": table_name,
            "error": f"Table '{table_name}' not found in known schema",
            "available_tables": list(DATABASE_SCHEMA.keys())
        }
        
        print(f"\n❌ Table '{table_name}' not found")
        print(f"Available tables: {', '.join(DATABASE_SCHEMA.keys())}")
        
        return result

def suggest_query_improvements(original_query: str, error_message: str = "", context: str = "") -> Dict[str, Any]:
    """Suggest improvements for a failed or suboptimal query.
    
    Args:
        original_query (str): The original query that needs improvement
        error_message (str): Any error message received
        context (str): Additional context about what the query should accomplish
    
    Returns:
        dict: Suggested query improvements and alternatives
    """
    print(f"\n🔧 Analyzing Query for Improvements")
    print(f"Original Query: {original_query}")
    if error_message:
        print(f"Error: {error_message}")
    if context:
        print(f"Context: {context}")
    
    suggestions = {
        "original_query": original_query,
        "error_message": error_message,
        "context": context,
        "suggested_fixes": [],
        "alternative_queries": [],
        "analyzed_at": datetime.datetime.now().isoformat()
    }
    
    # Automated analysis
    query_lower = original_query.lower()
    
    # Common error patterns
    if "column" in error_message.lower() and "does not exist" in error_message.lower():
        suggestions["suggested_fixes"].append("Check column names and table aliases")
        suggestions["suggested_fixes"].append("Use get_table_schema() to verify column names")
    
    if "table" in error_message.lower() and "does not exist" in error_message.lower():
        suggestions["suggested_fixes"].append("Check table name spelling")
        suggestions["suggested_fixes"].append(f"Available tables: {', '.join(DATABASE_SCHEMA.keys())}")
    
    if "syntax error" in error_message.lower():
        suggestions["suggested_fixes"].append("Check SQL syntax - missing commas, parentheses, or keywords")
    
    # Performance improvements
    if "select *" in query_lower:
        suggestions["suggested_fixes"].append("Replace SELECT * with specific column names")
    
    if "join" in query_lower:
        suggestions["suggested_fixes"].append("Ensure proper JOIN conditions and consider indexes")
    
    print("\nEnter manual suggestions or alternative queries:")
    manual_input = input("> ")
    if manual_input.strip():
        suggestions["manual_suggestions"] = manual_input
    
    print(f"\n🔧 Analysis Complete")
    for fix in suggestions["suggested_fixes"]:
        print(f"🛠️ {fix}")
    
    return suggestions

def build_smart_query(objective: str, tables_involved: List[str] = None, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Intelligently build a SQL query based on high-level objective.
    
    Args:
        objective (str): High-level description of what the query should accomplish
        tables_involved (List[str]): Optional list of tables that should be involved
        filters (Dict[str, Any]): Optional filters to apply
    
    Returns:
        dict: Generated query and explanation
    """
    print(f"\n🧠 Building Smart Query")
    print(f"Objective: {objective}")
    if tables_involved:
        print(f"Tables: {', '.join(tables_involved)}")
    if filters:
        print(f"Filters: {filters}")
    
    # Analyze objective for keywords
    objective_lower = objective.lower()
    suggested_tables = []
    
    # Map keywords to tables
    table_keywords = {
        "customer": ["customer_master", "customer_preferences"],
        "case": ["case_master"],
        "document": ["document_classification"],
        "api": ["api_master", "pipeline_master"],
        "pipeline": ["pipeline_master", "pipleline_customer_config"],
        "audit": ["di_audit"],
        "config": ["customer_preferences", "pipleline_customer_config"]
    }
    
    for keyword, tables in table_keywords.items():
        if keyword in objective_lower:
            suggested_tables.extend(tables)
    
    # Remove duplicates while preserving order
    suggested_tables = list(dict.fromkeys(suggested_tables))
    
    query_builder = {
        "objective": objective,
        "suggested_tables": suggested_tables,
        "tables_involved": tables_involved or suggested_tables,
        "filters": filters or {},
        "query_type": "SELECT",  # Default to SELECT
        "generated_at": datetime.datetime.now().isoformat()
    }
    
    # Determine query type from objective
    if any(word in objective_lower for word in ["count", "how many", "total"]):
        query_builder["query_type"] = "COUNT"
    elif any(word in objective_lower for word in ["update", "modify", "change"]):
        query_builder["query_type"] = "UPDATE"
    elif any(word in objective_lower for word in ["delete", "remove"]):
        query_builder["query_type"] = "DELETE"
    elif any(word in objective_lower for word in ["insert", "add", "create"]):
        query_builder["query_type"] = "INSERT"
    
    print(f"\nQuery Analysis:")
    print(f"Type: {query_builder['query_type']}")
    print(f"Suggested Tables: {', '.join(suggested_tables)}")
    
    print(f"\nEnter the generated SQL query based on this analysis:")
    generated_query = input("> ")
    
    query_builder["generated_query"] = generated_query
    query_builder["explanation"] = f"Generated query to: {objective}"
    
    print(f"\n🧠 Smart Query Generated")
    print(f"Query: {generated_query}")
    
    return query_builder

# Create the SQL query agent
sql_agent = Agent(
    name="postgres_sql_agent",
    model="gemini-2.5-flash-preview-05-20", 
    description=(
        "An intelligent PostgreSQL query agent that can understand database schemas, "
        "execute SQL queries, and iteratively improve queries based on results and errors. "
    ),
    instruction=(
"""You are an elite PostgreSQL query assistant. Your job is to translate any natural-language request
into the most accurate and performant SQL possible for the data described below.

When the request is vague or ambiguous you MUST think and iterate:
• Parse the user intent and choose the most relevant tables/columns.
• Build an initial, reasonably strict SQL statement.
• Execute the query via execute_sql_query().
    – If it errors, immediately diagnose and fix the syntax, table or column names.
    – If it succeeds but returns ZERO rows, treat that as a road-block and REVISE:
        1. Relax equality predicates to partial matches using ILIKE/LIKE with wild-cards (e.g. '%shul%').
        2. Shorten long string filters to prefixes or tokens (e.g. first 4‒5 characters).
        3. Apply fuzzy similarity techniques (pg_trgm similarity/LEVENSHTEIN) when available.
        4. Try alternative columns or JOIN paths that could satisfy the intent.
        5. Repeat until meaningful rows are returned or 5 refinements have been attempted.
• Log each attempt and explain why it was refined.
• After success, output BOTH the final SQL and a brief explanation of how ambiguity was resolved.
• For UPDATE/DELETE statements always include a specific WHERE clause and LIMIT unless explicitly waived.

Think step-by-step, be proactive, and never stop after the first failure – keep refining until you either
return data or exhaust sensible options.
"""
        "Below is the database schema. You can use it to understand the relationships between the tables."
        """Below is the customer master, where all the customer related stuff if present. 
                Extraction type is typically the downstream system
                CREATE TABLE public.customer_master (
                    customer_id serial4 NOT NULL,
                    "CustomerName" varchar(100) NULL,
                    "Industry" varchar(100) NULL,
                    "Country" varchar(100) NULL,
                    "State" varchar(50) NULL,
                    "City" varchar(50) NULL,
                    "Created_date" timestamp NULL,
                    "Created_by" varchar(100) NULL,
                    "Modified_date" timestamp NULL,
                    "Modified_by" varchar(100) NULL,
                    api_key varchar(100) NULL,
                    db_details json NULL,
                    account_type varchar NULL,
                    activation_status bool NULL,
                    canupload bool NULL,
                    customer_approval_key varchar(100) NULL,
                    processs_page_limit int4 NULL,
                    reviewed bool NULL,
                    extraction_type varchar NULL,
                    password_age bool NULL,
                    password_history bool NULL,
                    password_policy bool NULL,
                    password_validity int4 NULL,
                    customer_config json NULL,
                    CONSTRAINT "customer_master_CustomerName_key" UNIQUE ("CustomerName"),
                    CONSTRAINT customer_master_api_key_key UNIQUE (api_key),
                    CONSTRAINT customer_master_customer_approval_key_key UNIQUE (customer_approval_key),
                    CONSTRAINT customer_master_pkey PRIMARY KEY (customer_id)
                );




                Customer preferences is where additional config related to the customer is stored.
                CREATE TABLE public.customer_preferences (
                    id serial4 NOT NULL,
                    customer_id int4 NULL,
                    preference_name varchar(100) NULL,
                    preference_value json NULL,
                    is_active bool NULL,
                    upload_by varchar(100) NULL,
                    upload_date timestamp NULL,
                    modified_by varchar(100) NULL,
                    modified_date timestamp NULL,
                    CONSTRAINT customer_preferences_pkey PRIMARY KEY (id)
                );






                Api_master is where all the downstream API details are stored
                CREATE TABLE public.api_master (
                    api_id serial4 NOT NULL,
                    api_url varchar NULL,
                    api_method_type varchar NULL,
                    api_call_type varchar NULL,
                    api_param json NULL,
                    api_type varchar NULL,
                    api_status int4 NULL,
                    created_date timestamp NULL,
                    created_by int4 NULL,
                    modified_date timestamp NULL,
                    modified_by int4 NULL,
                    CONSTRAINT api_master_pkey PRIMARY KEY (api_id)
                );
                CREATE INDEX ix_api_master ON public.api_master USING btree (api_id, api_status, api_type);






                Pipeline master is an abstraction on top of api_master, where we give a meaningful name for the api so that it can be configured for a given customer and queue in pipeline_customer_config table.
                CREATE TABLE public.pipeline_master (
                    pipeline_id serial4 NOT NULL,
                    pipeline_name varchar NULL,
                    api_id int4 NULL,
                    status int4 NULL,
                    created_date timestamp NULL,
                    created_by int4 NULL,
                    modified_date timestamp NULL,
                    modified_by int4 NULL,
                    payload_config jsonb NULL,
                    CONSTRAINT pipeline_master_pkey PRIMARY KEY (pipeline_id)
                );


                Pipeline customer config is where we configure what actions should the downstream validation trigger for a given customer and queue. 


                CREATE TABLE public.pipleline_customer_config (
                    pipeline_customer_id serial4 NOT NULL,
                    pipeline_id int4 NULL,
                    customer_id int4 NULL,
                    api_sequence int4 NULL,
                    queue_name varchar(100) NULL,
                    created_date timestamp NULL,
                    created_by int4 NULL,
                    modified_date timestamp NULL,
                    modified_by int4 NULL,
                    CONSTRAINT pipleline_customer_config_pkey PRIMARY KEY (pipeline_customer_id)
                );






                di_audit is where all the logs related to the downstream actions are stored. 
                For a given customer and queue, we send files, create actions on the downstream systems. For a given doc, we will perform a bunch of actions.These are the actions that are configured in pipeline_customer_config.


                CREATE TABLE public.di_audit (
                    id serial4 NOT NULL,
                    pipeline_customer_id int4 NULL,
                    customer_id int4 NULL,
                    queue_name varchar NULL,
                    case_id int4 NULL,
                    doc_id varchar(255) NULL,
                    api_id int4 NULL,
                    response_code int4 NULL,
                    response_message varchar NULL,
                    api_output varchar NULL,
                    Pipeline_id varchar NULL,
                    created_date timestamp NULL,
                    created_by int4 NULL,
                    modified_date timestamp NULL,
                    modified_by int4 NULL,
                    CONSTRAINT di_audit_pkey PRIMARY KEY (id)
                );


                This is the table where are the cases sit


                CREATE TABLE public.case_master (
                    case_id serial4 NOT NULL,
                    customer_id int4 NOT NULL,
                    user_id int4 NOT NULL,
                    pages int4 NULL,
                    status varchar NULL,
                    classification_job_id varchar NULL,
                    parse_job_id varchar NULL,
                    file_path varchar NULL,
                    file_name varchar NULL,
                    folder varchar NULL,
                    uploaded_date timestamp NULL,
                    last_modified timestamp NULL,
                    file_status varchar NULL,
                    created_by int4 NULL,
                    modified_by int4 NULL,
                    notes text NULL,
                    is_locked bool NULL,
                    locked_by int4 NULL,
                    operation_details json NULL,
                    ingested_by varchar NULL,
                    confirm_click bool NULL,
                    merged_to json NULL,
                    queue_name varchar NULL,
                    custom_identifier varchar NULL,
                    movealltrash bool NULL,
                    copy_pages_count int4 NULL,
                    ocr_job_id varchar NULL,
                    ocr_job_status varchar NULL,
                    custom_uploaded_date timestamp NULL,
                    assignee varchar NULL,
                    case_level_duplicate_processing bool NULL,
                    CONSTRAINT case_master_pkey PRIMARY KEY (case_id)
                );


                Document_classification is where all the docs in a given case are stored. 

                CREATE TABLE public.document_classification (
                    id serial4 NOT NULL,
                    customer_id int4 NULL,
                    case_id int4 NULL,
                    document_classification_id int4 NULL,
                    user_id int4 NULL,
                    page_range varchar NULL,
                    documnt_class varchar NULL,
                    res_json json NULL,
                    is_edit_key_values bool NULL,
                    table_result_json json NULL,
                    is_edit bool NULL,
                    table_is_edit bool NULL,
                    new_row bool NULL,
                    created_date timestamp NULL,
                    created_by int4 NULL,
                    modified_date timestamp NULL,
                    modified_by int4 NULL,
                    isvalidated bool NULL,
                    ner_json json NULL,
                    ner_edit bool NULL,
                    "label" text NULL,
                    output_file_name varchar NULL,
                    output_file_status varchar NULL,
                    status varchar NULL,
                    confirmed bool NULL,
                    prediction_probabilities json NULL,
                    display_order int4 NULL,
                    parse_job_id varchar NULL,
                    output_file_info json NULL,
                    merged_from varchar NULL,
                    autovalidated bool NULL,
                    autoclassification bool NULL,
                    copy_pages _varchar NULL,
                    document_parsing_status int4 NULL,
                    document_type json NULL,
                    send_downstream bool NULL,
                    duplicate_status varchar NULL,
                    document_level_duplicate_processing bool NULL,
                    reviewed_duplicates bool NULL,
                    user_marked_duplicate bool NULL,
                    metadata_duplicate_info json NULL,
                    ui_document_name varchar NULL,
                    CONSTRAINT document_classification_pkey PRIMARY KEY (id)
                );
"""
    ),
    tools=[execute_sql_query],
) 