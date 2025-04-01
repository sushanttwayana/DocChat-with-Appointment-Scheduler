# -------------------------------------------------------------------------------------------------------------------------

import re
import sqlite3
import os
from datetime import datetime
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dateutil import parser as date_parser
from chatbot.tools.date_tool import DateExtractionTool

class UserInfoCollector:
    """
    Enhanced class to collect, validate, and store user information in a database,
    including appointment date and time validation and formatting.
    """
    def __init__(self, llm, db_name='user_info.db'):
        self.llm = llm
        self.user_info = {
            "name": None,
            "phone": None,
            "email": None,
            "date": None,
            "time": None,
            "created_at": None
        }
        self.current_field = None
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(llm=llm, memory=self.memory)
        self.date_tool = DateExtractionTool()
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        try:
            db_dir = os.path.dirname(os.path.abspath(self.db_name))
            if not os.path.exists(db_dir) and db_dir:
                os.makedirs(db_dir)

            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        email TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        status TEXT DEFAULT 'pending'
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")

    def _save_to_database(self):
        try:
            self.user_info['created_at'] = datetime.now().isoformat()

            # Ensure all fields are populated
            if not all(self.user_info.values()):
                missing = [k for k, v in self.user_info.items() if v is None]
                print(f"Cannot save: Missing user info fields: {missing}")
                return False

            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_data (name, phone, email, date, time, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    self.user_info['name'],
                    self.user_info['phone'],
                    self.user_info['email'],
                    self.user_info['date'],
                    self.user_info['time'],
                    self.user_info['created_at']
                ))
                conn.commit()
                print(f"User data saved successfully.")
            return True
        except sqlite3.Error as e:
            print(f"SQLite error during save: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during database save: {e}")
            return False


    def validate_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    def validate_phone(self, phone):
        phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        return bool(re.match(r"^[0-9]{10,15}$", phone))

    def validate_time(self, time_input):
        try:
            parsed_time = date_parser.parse(time_input).time()
            return parsed_time.strftime("%H:%M")
        except Exception as e:
            print(f"Time parsing error: {e}")
            return None

    def get_available_times(self):
        return ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

    def process_input(self, user_input):
        if self.current_field == "name":
            self.user_info["name"] = user_input.strip()
            self.current_field = "phone"
            return "Thank you! Now, could you please provide your phone number?"

        elif self.current_field == "phone":
            cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', user_input)
            if self.validate_phone(cleaned_phone):
                self.user_info["phone"] = cleaned_phone
                self.current_field = "email"
                return "Great! What's your email address?"
            else:
                return "The phone number format doesn't seem right. Please enter a valid number (10-15 digits)."

        elif self.current_field == "email":
            email = user_input.strip()
            if self.validate_email(email):
                self.user_info["email"] = email
                self.current_field = "date"
                return "Thanks! On which date would you like to schedule the appointment? (e.g., next Friday, March 15, 2025-01-01)"
            else:
                return "That doesn't look like a valid email. Please enter a correct one."

        elif self.current_field == "date":
            extracted_date = self.date_tool.extract_date(user_input)
            if extracted_date:
                self.user_info["date"] = extracted_date
                self.current_field = "time"
                return "And what time would you prefer for the appointment? (e.g., 10 AM, 2:30 PM)"
            else:
                return "Sorry, I couldn't understand the date. Please try again with a valid format like 'next Friday' or '15th March'."

        elif self.current_field == "time":
            formatted_time = self.validate_time(user_input)
            if formatted_time:
                available_times = self.get_available_times()
                if formatted_time in available_times:
                    self.user_info["time"] = formatted_time
                    self.current_field = None

                    if self._save_to_database():
                        # Get the day of the week
                        appointment_date = datetime.strptime(self.user_info['date'], "%Y-%m-%d")
                        day_of_week = appointment_date.strftime("%A")

                        return (
                            f"Thank you {self.user_info['name']}! Your appointment is scheduled on {self.user_info['date']} on {day_of_week} at {formatted_time}."
                        )
                    else:
                        return "We encountered an error saving your data. Please try again later."
                else:
                    return (f"Sorry, {formatted_time} is not available. "
                            f"Available times are: {', '.join(available_times)}. Please choose one.")
            else:
                return "I couldn't understand the time format. Please try again (e.g., '10 AM', '14:30', '5 PM')."

        return None

    def start_collection(self):
        self.current_field = "name"
        return "Sure, let's get you scheduled. May I have your name first?"

    def is_collecting(self):
        return self.current_field is not None

    def get_user_info(self):
        return self.user_info

    def get_all_users(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM user_data ORDER BY created_at DESC')
                return cursor.fetchall()
        except Exception as e:
            print(f"Database read error: {e}")
            return []

    def test_database_connection(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT sqlite_version()')
                return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
