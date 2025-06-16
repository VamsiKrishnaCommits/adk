# ADK Sample Project

This project contains two demonstration agents built with the Google Agent Development Kit (ADK):

1. **Weather & Time Agent** - Simple agent with weather and time tools
2. **Interview Scheduling Agent** - Complex agent with mock tools for interview coordination

## Setup

This project uses `uv` for Python environment management.

### Prerequisites

- Python 3.9+
- uv package manager
- Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Installation

The dependencies are already installed. If you need to reinstall:

```bash
uv add google-adk
```

### Configuration

1. Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Edit `multi_tool_agent/.env` and `interview_scheduler_agent/.env`
3. Replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with your actual API key

## 🌤️ Weather & Time Agent

A simple agent that provides weather and time information for New York.

### Running Options

```bash
# Programmatic test script
uv run python run_agent.py

# Web UI
uv run adk web  # Select "multi_tool_agent"

# Terminal interface
uv run adk run
```

**Features:**
- Get weather information for New York
- Get current time for New York
- Error handling for unsupported cities

## 📅 Interview Scheduling Agent (Enhanced!)

An intelligent interview coordinator with 4 mock tools that simulate real-world interactions.

### 🛠️ Mock Tools (with Visual Feedback)

1. **🔵 `call_contact`** - Simulates phone calls to candidates with random availability responses
2. **🟢 `schedule_calendar`** - Mock calendar scheduling with conflict detection
3. **🟡 `send_email`** - Mock email sending with delivery confirmation  
4. **🟣 `manage_notes`** - Notepad tool for the AI to track progress (read/write/append)

Each tool now provides **distinguishable colored output** to show exactly when it's being called and what it's doing!

### Running Options

```bash
# 1. Contact-based runner with sample data (NEW!)
uv run python contact_based_runner.py --sample

# 2. Contact-based runner with custom contacts (NEW!)
uv run python contact_based_runner.py

# 3. Automated test scenarios
uv run python run_interview_scheduler.py

# 4. Interactive chat mode
uv run python interactive_scheduler.py

# 5. Web UI
uv run adk web  # Select "interview_scheduler_agent"
```

### ✨ NEW: Contact-Based Runner

The `contact_based_runner.py` provides a structured way to initialize the agent with specific contact details:

**With Sample Data:**
```bash
uv run python contact_based_runner.py --sample
```

**With Custom Contacts:**
```bash
uv run python contact_based_runner.py
# Will prompt you for:
# - HR contact details (name, email, phone)
# - Interviewer details (name, email, phone)  
# - Candidate details (name, email, phone)
# - Position information
```

**Features:**
- 🎯 Structured contact management
- 📋 Automatic agent initialization with context
- 🎬 Predefined scenarios or interactive mode
- 📞 Real contact details used throughout the session

### 🎨 Visual Tool Feedback

Watch the tools in action with color-coded output:

```
🔵 [CALLING] Attempting to call Sarah Johnson at +1-555-0123...
🔵 [CALL RESULT] Successfully spoke with Sarah Johnson for 5 min - Prefers morning slots (9-11 AM)

🟢 [SCHEDULING] Attempting to book technical interview for Sarah Johnson on 2025-05-27 at 10:00...
🟢 [SCHEDULING SUCCESS] Interview booked for Sarah Johnson - Meeting ID: INT_4721

🟡 [EMAIL] Sending confirmation email to sarah.johnson@email.com...
🟡 [EMAIL SUCCESS] Sent to sarah.johnson@email.com - Tracking ID: EMAIL_78234

🟣 [NOTES APPEND] Added timestamped entry: 'Called Sarah Johnson - prefers morning slots'
```

### Sample Scenarios

Try these with any runner:

```
"Schedule an interview for Sarah Johnson (sarah@email.com, +1-555-0123) for a Senior Frontend Developer role"

"I need to coordinate interviews for 3 candidates this week for Backend Developer positions"

"Can you check what interviews we have scheduled so far?"

"John needs to reschedule his interview - can you help?"
```

### Mock Behaviors

The tools randomly simulate realistic scenarios:
- **Phone calls**: 85% success rate, various availability responses
- **Scheduling**: 20% chance of conflicts with alternative suggestions
- **Emails**: 95% delivery success rate
- **Notes**: Persistent notepad for tracking progress

## Agent Features Comparison

| Feature | Weather Agent | Interview Agent |
|---------|---------------|-----------------|
| **Complexity** | Simple | Advanced |
| **Tools** | 2 basic tools | 4 sophisticated tools |
| **Mock Data** | Static responses | Dynamic random responses |
| **State Management** | Stateless | Stateful (notepad) |
| **Error Handling** | Basic | Realistic failures |
| **Visual Feedback** | None | Color-coded tool calls |
| **Contact Management** | None | Structured contact system |
| **Use Case** | Learning ADK basics | Real-world simulation |

## Project Structure

```
adk/
├── multi_tool_agent/           # Weather & Time Agent
│   ├── __init__.py
│   ├── agent.py
│   └── .env
├── interview_scheduler_agent/  # Interview Scheduling Agent  
│   ├── __init__.py
│   ├── agent.py               # Enhanced with colored output
│   └── .env
├── run_agent.py               # Weather agent test script
├── run_interview_scheduler.py # Interview agent test scenarios
├── interactive_scheduler.py   # Interactive interview scheduler
├── contact_based_runner.py    # NEW: Contact-based initialization
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Getting Started

1. **Set up your API key** in both `.env` files
2. **Start simple** with the weather agent: `uv run python run_agent.py`  
3. **Try the enhanced interview agent** with contacts: `uv run python contact_based_runner.py --sample`
4. **Watch the colored tool outputs** to see exactly what the agent is doing
5. **Go interactive** for custom testing: `uv run python interactive_scheduler.py`

The interview scheduling agent demonstrates how ADK agents can handle complex, multi-step workflows with realistic tool interactions, state management, and clear visual feedback of all operations! 🎯

