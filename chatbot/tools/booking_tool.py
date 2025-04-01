from datetime import datetime
import re
import sqlite3

class AppointmentBookingTool:
    def __init__(self, user_info_collector, date_tool, db_name='user_info.db'):
        self.user_info_collector = user_info_collector
        self.date_tool = date_tool
        self.db_name = db_name

        self.available_slots = [
            "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00",
            "15:00", "16:00", "17:00"
        ]

        self._initialize_appointment_database()

    def _initialize_appointment_database(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        status TEXT DEFAULT 'confirmed',
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user_data (id)
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Appointment DB init error: {e}")

    def _parse_time(self, time_str):
        try:
            time_str = time_str.strip().upper()
            if "AM" not in time_str and "PM" not in time_str:
                hour = int(re.search(r'\d+', time_str).group())
                time_str += " AM" if hour < 12 else " PM"
            if ":" not in time_str:
                parts = time_str.split()
                time_str = f"{parts[0]}:00 {parts[1]}"
            return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
        except Exception as e:
            print(f"Time parse error: {e}")
            return None


    def get_booked_slots(self, date_str):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT time FROM appointments WHERE date = ? AND status = "confirmed"', (date_str,))
                return [slot[0] for slot in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching booked slots: {e}")
            return []

    def get_available_slots(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None, "Invalid date format. Use YYYY-MM-DD."

        booked = self.get_booked_slots(date_str)
        return [slot for slot in self.available_slots if slot not in booked], None

    def extract_time_from_query(self, query):
        match = re.search(r'\b(?:at|for|@)?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\b', query, re.IGNORECASE)
        if match:
            return self._parse_time(match.group(1))
        return None

    def save_appointment(self, user_id, date_str, time_str):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO appointments (user_id, date, time, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, date_str, time_str, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Save appointment error: {e}")
            return False

    def get_user_id(self, user_info):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM user_data 
                    WHERE name = ? AND phone = ? AND email = ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (user_info['name'], user_info['phone'], user_info['email']))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"User ID fetch error: {e}")
            return None

    def book_appointment(self, query):
        date_str = self.date_tool.extract_date(query)
        if not date_str:
            return "I couldn't understand the date. Please use a format like 'next Monday' or 'YYYY-MM-DD'."

        time_str = self.extract_time_from_query(query)
        user_info = self.user_info_collector.get_user_info()

        if not all([user_info.get("name"), user_info.get("phone"), user_info.get("email")]):
            self.user_info_collector.appointment_date = date_str
            self.user_info_collector.appointment_time = time_str
            return self.user_info_collector.start_collection()

        available_slots, error = self.get_available_slots(date_str)
        if error:
            return error

        if not time_str:
            return (
                f"Available slots for {self._format_date(date_str)}:\n" +
                "\n".join(f"- {slot}" for slot in available_slots) +
                "\n\nPlease specify a time (e.g., 'at 2:00 PM')."
            )

        if time_str not in available_slots:
            return (
                f"Sorry, {time_str} is not available on {self._format_date(date_str)}.\n" +
                "Available times are:\n" +
                "\n".join(f"- {slot}" for slot in available_slots)
            )

        user_id = self.get_user_id(user_info)
        if not user_id:
            if self.user_info_collector._save_to_database():
                user_id = self.get_user_id(user_info)
            else:
                return "We couldn't save your information. Please try again later."

        if self.save_appointment(user_id, date_str, time_str):
            return (
                f"Appointment confirmed for {self._format_date(date_str)} at {time_str}.\n\n"
                f"Details:\n"
                f"- Name: {user_info['name']}\n"
                f"- Phone: {user_info['phone']}\n"
                f"- Email: {user_info['email']}"
            )
        else:
            return "Appointment was scheduled but failed to save. Please contact support."

    def _format_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d, %Y")
        except ValueError:
            return date_str

# ----------------------------------------------------------------------------------------

# from datetime import datetime, time
# import re
# import sqlite3

# class AppointmentBookingTool:
#     """
#     Enhanced tool for booking appointments with time slot management and database integration
#     """
#     def __init__(self, user_info_collector, date_tool, db_name='user_info.db'):
#         """
#         Initialize the appointment booking tool
        
#         Args:
#             user_info_collector: Instance of UserInfoCollector
#             date_tool: Instance of DateExtractionTool
#             db_name: Name of the SQLite database file
#         """
#         self.user_info_collector = user_info_collector
#         self.date_tool = date_tool
#         self.db_name = db_name
        
#         # Available time slots (9AM-5PM with 1 hour intervals)
#         self.available_slots = [
#             "9:00 AM", "10:00 AM", "11:00 AM", 
#             "12:00 PM", "1:00 PM", "2:00 PM", 
#             "3:00 PM", "4:00 PM", "5:00 PM"
#         ]
        
#         # Initialize database for appointments
#         self._initialize_appointment_database()
    
#     def _initialize_appointment_database(self):
#         """Create the appointments table in the database if it doesn't exist"""
#         try:
#             with sqlite3.connect(self.db_name) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     CREATE TABLE IF NOT EXISTS appointments (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         user_id INTEGER NOT NULL,
#                         date TEXT NOT NULL,
#                         time TEXT NOT NULL,
#                         status TEXT DEFAULT 'confirmed',
#                         created_at TEXT NOT NULL,
#                         FOREIGN KEY (user_id) REFERENCES user_data (id)
#                     )
#                 ''')
#                 conn.commit()
#                 print(f"Appointments table initialized successfully in {self.db_name}")
#         except Exception as e:
#             print(f"Appointment database initialization error: {e}")
    
#     def _parse_time(self, time_str):
#         """Parse time string into datetime.time object"""
#         try:
#             # Handle various time formats (2pm, 2:00pm, 2 PM, etc.)
#             time_str = time_str.strip().upper()
            
#             # Add AM/PM if missing
#             if "AM" not in time_str and "PM" not in time_str:
#                 # Try to handle 24-hour format
#                 if re.match(r'\d{1,2}:\d{2}$', time_str):
#                     try:
#                         return datetime.strptime(time_str, "%H:%M").time()
#                     except ValueError:
#                         pass
                
#                 # Default to AM for times before 12, PM for 12 and after
#                 hour = int(re.search(r'\d+', time_str).group())
#                 if hour < 12:
#                     time_str += " AM"
#                 else:
#                     time_str += " PM"
            
#             # Standardize the format
#             time_str = re.sub(r'\s+', ' ', time_str)
            
#             # Handle format without colon (2 PM -> 2:00 PM)
#             if ":" not in time_str:
#                 parts = time_str.split()
#                 time_str = f"{parts[0]}:00 {parts[1]}"
            
#             return datetime.strptime(time_str, "%I:%M %p").time()
#         except Exception as e:
#             print(f"Time parsing error for '{time_str}': {str(e)}")
#             return None
    
#     def _format_time(self, time_obj):
#         """Format time object into readable string"""
#         if isinstance(time_obj, str):
#             return time_obj
#         return time_obj.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
    
#     def get_booked_slots(self, date_str):
#         """Get all booked time slots for a given date from the database"""
#         try:
#             with sqlite3.connect(self.db_name) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     SELECT time FROM appointments 
#                     WHERE date = ? AND status = 'confirmed'
#                 ''', (date_str,))
#                 booked = cursor.fetchall()
#                 return [slot[0] for slot in booked]
#         except Exception as e:
#             print(f"Error retrieving booked slots: {e}")
#             return []
    
#     def get_available_slots(self, date_str):
#         """
#         Get available time slots for a given date
        
#         Args:
#             date_str (str): Date in YYYY-MM-DD format
            
#         Returns:
#             list: Available time slots
#             str: Error message if any
#         """
#         # Check if date is valid
#         try:
#             datetime.strptime(date_str, "%Y-%m-%d")
#         except ValueError:
#             return None, "Invalid date format. Please use YYYY-MM-DD."
        
#         # Get all booked slots for this date from the database
#         booked_slots = self.get_booked_slots(date_str)
#         print(f"Booked slots for {date_str}: {booked_slots}")
        
#         # Return available slots
#         available = [slot for slot in self.available_slots if slot not in booked_slots]
#         return available, None
    
#     def extract_time_from_query(self, query):
#         """Extract time from user query"""
#         # Check for time in query with improved regex
#         time_match = re.search(
#             r'\b(?:at|for|@)?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\b', 
#             query, 
#             re.IGNORECASE
#         )
        
#         if time_match:
#             time_str = time_match.group(1)
#             time_obj = self._parse_time(time_str)
            
#             if time_obj:
#                 return self._format_time(time_obj)
        
#         return None
    
#     def save_appointment(self, user_id, date_str, time_str):
#         """Save appointment to database"""
#         try:
#             with sqlite3.connect(self.db_name) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     INSERT INTO appointments (user_id, date, time, created_at)
#                     VALUES (?, ?, ?, ?)
#                 ''', (
#                     user_id,
#                     date_str,
#                     time_str,
#                     datetime.now().isoformat()
#                 ))
#                 conn.commit()
#                 print(f"Appointment saved successfully with ID: {cursor.lastrowid}")
#                 return True
#         except Exception as e:
#             print(f"Error saving appointment: {e}")
#             return False
    
#     def get_user_id(self, user_info):
#         """Get user ID from database based on user info"""
#         try:
#             with sqlite3.connect(self.db_name) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     SELECT id FROM user_data 
#                     WHERE name = ? AND phone = ? AND email = ?
#                     ORDER BY created_at DESC LIMIT 1
#                 ''', (
#                     user_info['name'],
#                     user_info['phone'],
#                     user_info['email']
#                 ))
#                 result = cursor.fetchone()
#                 return result[0] if result else None
#         except Exception as e:
#             print(f"Error retrieving user ID: {e}")
#             return None
    
#     def book_appointment(self, query):
#         """
#         Book an appointment based on user query with database integration
        
#         Args:
#             query (str): User's query text
            
#         Returns:
#             str: Response to the user
#         """
#         # Extract date from query
#         date_str = self.date_tool.extract_date(query)
#         if not date_str:
#             return "I couldn't determine the date for your appointment. Please specify a date like 'next Monday' or 'YYYY-MM-DD'."
        
#         # Extract time from query
#         time_str = self.extract_time_from_query(query)
        
#         # Get user info
#         user_info = self.user_info_collector.get_user_info()
        
#         # If we don't have complete user information, start collection
#         if not all([user_info.get("name"), user_info.get("phone"), user_info.get("email")]):
#             # Store date and time in session for later use
#             self.user_info_collector.appointment_date = date_str
#             self.user_info_collector.appointment_time = time_str
            
#             # Start collecting user information
#             return self.user_info_collector.start_collection()
        
#         # If time was not provided, show available slots
#         if not time_str:
#             available_slots, error = self.get_available_slots(date_str)
#             if error:
#                 return error
            
#             if not available_slots:
#                 return f"No available slots on {self._format_date(date_str)}. Please try another date."
            
#             return (
#                 f"Available slots for {self._format_date(date_str)}:\n" +
#                 "\n".join(f"- {slot}" for slot in available_slots) +
#                 "\n\nPlease specify your preferred time (e.g., 'at 2:00 PM')"
#             )
        
#         # Check slot availability
#         available_slots, error = self.get_available_slots(date_str)
#         if error:
#             return error
        
#         if time_str not in available_slots:
#             return (
#                 f"Sorry, {time_str} is not available on {self._format_date(date_str)}. "
#                 f"Please choose from:\n" + 
#                 "\n".join(f"- {slot}" for slot in available_slots)
#             )
        
#         # Get user ID from database
#         user_id = self.get_user_id(user_info)
#         if not user_id:
#             print("User ID not found, attempting to save user info first")
#             if self.user_info_collector._save_to_database():
#                 user_id = self.get_user_id(user_info)
#             else:
#                 return "We encountered an issue saving your information. Please contact support."
        
#         # Save appointment to database
#         if self.save_appointment(user_id, date_str, time_str):
#             return (
#                 f"Appointment confirmed for {self._format_date(date_str)} at {time_str}!\n\n"
#                 f"Details:\n"
#                 f"- Name: {user_info['name']}\n"
#                 f"- Phone: {user_info['phone']}\n"
#                 f"- Email: {user_info['email']}\n\n"
#                 "Your appointment has been successfully saved to our system."
#             )
#         else:
#             return (
#                 f"We've confirmed your appointment for {self._format_date(date_str)} at {time_str}, "
#                 f"but encountered an issue saving it to our system. Please contact support."
#             )
    
#     def _format_date(self, date_str):
#         """Format date string into readable format"""
#         try:
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#             return date_obj.strftime("%A, %B %d, %Y")
#         except ValueError:
#             return date_str