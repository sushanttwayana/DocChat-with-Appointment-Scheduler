import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from PIL import Image
from datetime import datetime

from chatbot.document_loader import load_documents
from chatbot.rag_system import create_vector_store, setup_rag_chain
from chatbot.user_info import UserInfoCollector
from chatbot.agent import setup_agent
from chatbot.tools.date_tool import DateExtractionTool
from chatbot.tools.booking_tool import AppointmentBookingTool

from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()

# Load logo
try:
    logo = Image.open("./images/document-and-pen.jpg")
except FileNotFoundError:
    logo = None

# Streamlit page configuration
st.set_page_config(
    page_title="DocChat with Appointment Scheduler",
    page_icon=logo if logo else None,
    layout="wide"
)

class DocumentChatbot:
    def __init__(self, document_path):
        self.llm = OpenAI(temperature=0.7)

        # Load and embed document
        documents = load_documents(document_path)
        vector_store = create_vector_store(documents)
        self.qa_chain = setup_rag_chain(vector_store, self.llm)

        # Tools and agent setup
        self.user_info_collector = UserInfoCollector(self.llm)
        self.date_tool = DateExtractionTool()
        self.booking_tool = AppointmentBookingTool(self.user_info_collector, self.date_tool)
        self.tools = setup_agent(self.llm, self.user_info_collector, self.date_tool, self.booking_tool)
        self.memory = ConversationBufferMemory(return_messages=True)

    def process_message(self, user_message):
        user_message_lower = user_message.lower()

        # Collecting user info
        if self.user_info_collector.is_collecting():
            return self.user_info_collector.process_input(user_message)

        # Trigger info collection
        if "call me" in user_message_lower or "contact me" in user_message_lower:
            return self.user_info_collector.start_collection()

    
        # Trigger appointment booking
        if any(kw in user_message_lower for kw in ["book", "schedule", "appointment", "meeting"]):
            date_str = self.date_tool.extract_date(user_message)
            if date_str:
                try:
                    response = self.booking_tool.book_appointment(user_message)
                    return response
                except Exception as e:
                    return f"Error during appointment booking: {e}"
            else:
                # Skip this message and directly ask for name
                return self.user_info_collector.start_collection()


        # Fallback to document Q&A
        try:
            response = self.qa_chain({"query": user_message})
            return response["result"]
        except Exception as e:
            return f"I'm sorry, I encountered an error while answering: {str(e)}"


# Page layout
col1, col2 = st.columns([1, 5])
with col1:
    if logo:
        st.image(logo, width=90)
with col2:
    st.title("DocChat with Appointment Scheduler")

st.markdown(
    "Upload a document to chat about it, or schedule an appointment directly through conversation."
)

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF or TXT document", type=["pdf", "txt"])

    if uploaded_file and "chatbot" not in st.session_state:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name

        with st.spinner("Processing document..."):
            try:
                st.session_state.chatbot = DocumentChatbot(file_path)
                st.success("Document loaded successfully.")
            except Exception as e:
                st.error(f"Failed to load document: {e}")

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and interaction
if "chatbot" in st.session_state:
    prompt = st.chat_input("Ask a question or schedule an appointment...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            response = st.session_state.chatbot.process_message(prompt)

        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)
else:
    st.info("Please upload a document to begin.")

# Footer
st.markdown("---")
st.markdown("Built with RAG, LangChain, and Streamlit")


# -------------------------------------------------------------------------------------------------------

# import streamlit as st
# import os
# import tempfile
# from dotenv import load_dotenv
# from chatbot.document_loader import load_documents
# from chatbot.rag_system import create_vector_store, setup_rag_chain
# from chatbot.user_info import UserInfoCollector
# from chatbot.agent import setup_agent
# from chatbot.tools.date_tool import DateExtractionTool
# from chatbot.tools.booking_tool import AppointmentBookingTool
# from langchain.llms import OpenAI
# from langchain.memory import ConversationBufferMemory
# from PIL import Image 
# from datetime import datetime

# # Load environment variables
# load_dotenv()

# # Load the image
# try:
#     logo = Image.open("./images/docs.jpg")
# except FileNotFoundError:
#     st.warning("Image 'docs.jpg' not found. Using default icon instead.")
#     logo = None

# # Page config
# st.set_page_config(
#     page_title="Document Chatbot",
#     page_icon=logo,
#     layout="wide"
# )

# class DocumentChatbot:
#     def __init__(self, document_path):
#         # Initialize LLM
#         self.llm = OpenAI(temperature=0.7)  
        
#         # Set up document processing
#         documents = load_documents(document_path)
#         vector_store = create_vector_store(documents)
#         self.qa_chain = setup_rag_chain(vector_store, self.llm)
        
#         # Set up user info collection
#         self.user_info_collector = UserInfoCollector(self.llm)
        
#         # Set up date extraction tool
#         self.date_tool = DateExtractionTool()
        
#         # Set up appointment booking tool
#         self.booking_tool = AppointmentBookingTool(self.user_info_collector, self.date_tool)
        
#         # Set up agent with tools
#         self.tools = setup_agent(self.llm, self.user_info_collector, 
#                                 self.date_tool, self.booking_tool)
        
#         # Conversation memory
#         self.memory = ConversationBufferMemory(return_messages=True)
    
#     def process_message(self, user_message):
#         # First check if we're in the middle of collecting user info
#         if self.user_info_collector.is_collecting():
#             return self.user_info_collector.process_input(user_message)
        
#         # Check for call request triggers
#         if "call me" in user_message.lower() or "contact me" in user_message.lower():
#             return self.user_info_collector.start_collection()
        
#         # Enhanced appointment booking detection
#         if any(phrase in user_message.lower() for phrase in ["book", "schedule", "appointment", "meeting"]):
#             # Use the date extraction tool
#             date_str = self.date_tool.extract_date(user_message)
#             if date_str:
#                 response = self.booking_tool.book_appointment(user_message)
                
#                 # If response contains available slots, format it better
#                 if "Available slots for" in response:
#                     return response.replace("Available slots for", "Available slots for")
#                 return response
#             else:
#                 return ("I'd be happy to book an appointment. Please specify:\n\n"
#                     "1. The date (e.g., 'next Monday', 'March 15th')\n"
#                     "2. Preferred time (e.g., 'at 2:00 PM')\n\n"
#                     "You can say something like 'Schedule for tomorrow at 3 PM'")
        
#         # Use RAG for document-based questions
#         try:
#             response = self.qa_chain({"query": user_message})
#             return response["result"]
#         except Exception as e:
#             return f"I'm sorry, I encountered an error: {str(e)}. Please try again."

# # App layout
# col1, col2 = st.columns([1, 4])
# with col1:
#     if logo:
#         st.image(logo, width=100)  # Display the logo image
#     else:
#         st.markdown("Logo not found") 
# with col2:
#     st.title("Document Chatbot with Appointment Booking")

# st.markdown("""
# Upload a document and ask questions about it, or use the chatbot to book an appointment!
# """)

# # Sidebar for document upload
# with st.sidebar:
#     st.header("Document Upload")
#     uploaded_file = st.file_uploader("Upload a document (PDF, TXT)", type=["pdf", "txt"])
    
#     if uploaded_file and "chatbot" not in st.session_state:
#         # Save the uploaded file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
#             tmp_file.write(uploaded_file.getvalue())
#             file_path = tmp_file.name
        
#         with st.spinner("Processing document..."):
#             try:
#                 st.session_state.chatbot = DocumentChatbot(file_path)
#                 st.success("Document loaded successfully!")
#             except Exception as e:
#                 st.error(f"Error loading document: {e}")

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Chat input
# if "chatbot" in st.session_state:
#     # Accept user input
#     prompt = st.chat_input("Ask a question about the document, or schedule an appointment...")
    
#     if prompt:
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         # Display user message
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         # Get response from chatbot with a spinner
#         with st.spinner("Thinking..."):
#             response = st.session_state.chatbot.process_message(prompt)
        
#         # Add assistant response to chat history
#         st.session_state.messages.append({"role": "assistant", "content": response})
        
#         # Display assistant response
#         with st.chat_message("assistant"):
#             st.markdown(response)
# else:
#     st.info("Please upload a document to start conversation!")

# # Footer
# st.markdown("---")
# st.markdown("Document Chatbot with RAG and Tool Agents")