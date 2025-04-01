# from langchain.agents import Tool, AgentExecutor, initialize_agent
# from langchain.agents import AgentType

# def setup_agent(llm, user_info_collector, date_tool, booking_tool):
#     """
#     Set up an agent with tools for various tasks
    
#     Args:
#         llm: Language model instance
#         user_info_collector: UserInfoCollector instance
#         date_tool: DateExtractionTool instance
#         booking_tool: AppointmentBookingTool instance
        
#     Returns:
#         list: List of tools available to the agent
#     """
#     # Define tools
#     tools = [
#         Tool(
#             name="DateExtraction",
#             func=date_tool.extract_date,
#             description="Extracts date from user query and returns in YYYY-MM-DD format. Use this tool when the user mentions a specific date, day of week, or relative time like 'next Monday', 'tomorrow','comming Friday','next SUnday','following Thursday',\
#             'March 15th', '2025-04-20', 'next Monday', 'this Friday','following Thursday', 'tomorrow', 'in 3 days', 'next week', 'today at 2 PM', 'morning slot', 'evening appointment'"
#         ),
#         Tool(
#             name="AppointmentBooking",
#             func=booking_tool.book_appointment,
#             description="Books an appointment on the specified date. Use this when the user wants to book a meeting, schedule a call, or make an appointment."
#         ),
#         Tool(
#             name="UserInfoCollection",
#             func=user_info_collector.start_collection,
#             description="Starts collecting user information (name, phone, email). Use this when you need to gather contact details from the user."
#         )
#     ]
    
#     # Initialize the agent
#     agent = initialize_agent(
#         tools,
#         llm,
#         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#         verbose=True,
#         handle_parsing_errors=True
#     )
    
#     return tools


# ------------------------------------------- Advanced agent --------------------------------------------------

# agent.py
from langchain.agents import Tool, initialize_agent
from langchain.agents import AgentType
from langchain.tools import BaseTool
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import re
from datetime import datetime

class DateExtractionTool(BaseTool):
    name = "DateExtraction"
    # description = """Extracts date from user query and returns in YYYY-MM-DD format. 
    # Handles: specific dates ('March 15th'), relative dates ('next Monday'), 
    # time references ('2 PM'), and fuzzy requests ('ASAP')."""
    
    description = "Extracts date from user query and returns in YYYY-MM-DD format. Use this tool when the user mentions a specific date, day of week, or relative time like 'next Monday', 'tomorrow','comming Friday','next SUnday','following Thursday',\
             'March 15th', '2025-04-20', 'next Monday', 'this Friday','following Thursday', 'tomorrow', 'in 3 days', 'next week', 'today at 2 PM', 'morning slot', 'evening appointment'"
    
    def _run(self, query: str) -> str:
        # Your existing date extraction logic
        return self.extract_date(query)
    
    def extract_date(self, query: str) -> str:
        """Your date extraction implementation"""
        # Add your date parsing logic here
        return "2023-11-15"  # Example return

class AppointmentBookingTool(BaseTool):
    name = "AppointmentBooking"
    description = "Books appointments. Handles booking, rescheduling and cancellations."
    
    def _run(self, booking_info: Dict[str, Any]) -> str:
        return self.book_appointment(booking_info)
    
    def book_appointment(self, booking_info: Dict[str, Any]) -> str:
        """Your booking implementation"""
        return "Appointment booked successfully"

class UserInfoCollector(BaseTool):
    name = "UserInfoCollection"
    description = "Collects and validates user information (name, email, phone)."
    
    def _run(self, info_request: Dict[str, Any]) -> Dict[str, str]:
        return self.start_collection(info_request)
    
    def start_collection(self, info_request: Dict[str, Any]) -> Dict[str, str]:
        """Your info collection implementation"""
        return {"name": "John Doe", "email": "john@example.com", "phone": "1234567890"}

def setup_agent(llm, user_info_collector: UserInfoCollector, date_tool: DateExtractionTool, booking_tool: AppointmentBookingTool):
    """
    Set up an agent with tools for various tasks
    
    Args:
        llm: Language model instance
        user_info_collector: UserInfoCollector instance
        date_tool: DateExtractionTool instance
        booking_tool: AppointmentBookingTool instance
        
    Returns:
        AgentExecutor: Initialized agent
    """
    # Define tools
    tools = [
        Tool(
            name="DateExtraction",
            func=date_tool.extract_date,
            description="Extracts date from user query. Handles: specific dates, relative dates, time references."
        ),
        Tool(
            name="AppointmentBooking",
            func=booking_tool.book_appointment,
            description="Books appointments. Requires date/time and service type."
        ),
        Tool(
            name="UserInfoCollection",
            func=user_info_collector.start_collection,
            description="Collects user information with validation. Returns name, email, phone."
        )
    ]
    
    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent