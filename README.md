# Document Chatbot with Appointment Booking

A conversational AI chatbot that can answer questions from documents and schedule appointments using natural language processing.

## Features

- **Document Q&A**: Upload any document (PDF, TXT) and ask questions about its content.
- **Conversational Form**: Collects user information (name, phone, email) with validation.
- **Tool Agents**: Intelligent tools for date extraction and appointment booking.
- **Natural Language Date Understanding**: Convert phrases like "next Monday" to proper date formats.
- **Input Validation**: Ensures email and phone formats are correct.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/sushanttwayana/DocChat-with-Appointment-Scheduler.git

2.  Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys:
    ```bash
   OPENAI_API_KEY=your_openai_api_key
   # OR for Gemini
   GOOGLE_API_KEY=your_google_api_key
   ```
4. Start the application:
   ```bash
   streamlit run app.py 
   ```


