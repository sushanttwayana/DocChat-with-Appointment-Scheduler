import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import chatbot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.tools.date_tool import DateExtractionTool
from chatbot.tools.booking_tool import AppointmentBookingTool


class TestDateExtractionTool(unittest.TestCase):
    
    def setUp(self):
        self.date_tool = DateExtractionTool()
        # Fix the current date for testing
        self.today = datetime(2025, 3, 31)  # Monday
        self.tomorrow = self.today + timedelta(days=1)
        
        # Create a patch for datetime.now()
        self.datetime_patch = patch('chatbot.tools.date_tool.datetime')
        self.mock_datetime = self.datetime_patch.start()
        self.mock_datetime.now.return_value = self.today
        # Pass through other datetime methods
        self.mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        self.mock_datetime.strptime = datetime.strptime
        self.mock_datetime.timedelta = timedelta
    
    def tearDown(self):
        self.datetime_patch.stop()
    
    def test_extract_exact_date(self):
        """Test extracting an exact date in YYYY-MM-DD format"""
        result = self.date_tool.extract_date("I want to book for 2025-04-15")
        self.assertEqual(result, "2025-04-15")
    
    def test_extract_tomorrow(self):
        """Test extracting 'tomorrow' from query"""
        result = self.date_tool.extract_date("Schedule for tomorrow please")
        expected = self.tomorrow.date().isoformat()
        self.assertEqual(result, expected)
    
    def test_extract_next_monday(self):
        """Test extracting 'next Monday' from query"""
        # Since today is already Monday (2025-03-31), next Monday should be 2025-04-07
        result = self.date_tool.extract_date("Let's meet next monday")
        expected = (self.today + timedelta(days=7)).date().isoformat()
        self.assertEqual(result, expected)
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        result = self.date_tool.extract_date("I want to book for someday")
        self.assertIsNone(result)


class TestAppointmentBookingTool(unittest.TestCase):
    
    def setUp(self):
        self.mock_user_info_collector = MagicMock()
        self.mock_user_info_collector.get_user_info.return_value = {
            "name": "John Doe",
            "phone": "+1234567890",
            "email": "john@example.com"
        }
        
        # Create a patched DateExtractionTool
        self.date_tool_patch = patch('chatbot.tools.booking_tool.DateExtractionTool')
        self.mock_date_tool_class = self.date_tool_patch.start()
        self.mock_date_tool = MagicMock()
        self.mock_date_tool_class.return_value = self.mock_date_tool
        
        # Create the booking tool with mocked dependencies
        self.booking_tool = AppointmentBookingTool(self.mock_user_info_collector)
        # Replace the date_tool instance with our mock
        self.booking_tool.date_tool = self.mock_date_tool
    
    def tearDown(self):
        self.date_tool_patch.stop()
    
    def test_book_appointment_successful(self):
        """Test successful appointment booking"""
        self.mock_date_tool.extract_date.return_value = "2025-04-15"
        
        result = self.booking_tool.book_appointment("Book me for April 15")
        
        self.mock_date_tool.extract_date.assert_called_once_with("Book me for April 15")
        self.mock_user_info_collector.get_user_info.assert_called_once()
        
        expected_response = "Great! I've booked your appointment for 2025-04-15. We'll contact you at +1234567890 with confirmation."
        self.assertEqual(result, expected_response)
        
        # Check that the appointment was stored
        self.assertIn("2025-04-15", self.booking_tool.appointments)
        self.assertEqual(
            self.booking_tool.appointments["2025-04-15"], 
            {"name": "John Doe", "phone": "+1234567890", "email": "john@example.com"}
        )
    
    def test_book_appointment_no_date(self):
        """Test appointment booking with no recognizable date"""
        self.mock_date_tool.extract_date.return_value = None
        
        result = self.booking_tool.book_appointment("Book me for sometime")
        
        expected_response = "I couldn't determine the date for your appointment. Please specify a date like 'next Monday' or 'YYYY-MM-DD'."
        self.assertEqual(result, expected_response)
    
    def test_book_appointment_no_user_info(self):
        """Test appointment booking with no user info available"""
        self.mock_date_tool.extract_date.return_value = "2025-04-15"
        self.mock_user_info_collector.get_user_info.return_value = {
            "name": None,
            "phone": None,
            "email": None
        }
        
        result = self.booking_tool.book_appointment("Book me for April 15")
        
        expected_response = "I need your contact information before booking an appointment."
        self.assertEqual(result, expected_response)


if __name__ == '__main__':
    unittest.main()