from datetime import datetime, timedelta
import re
import calendar

class DateExtractionTool:
  
    #  Tool for extracting dates from natural language text
   
    def __init__(self):
        """Initialize the date extraction tool with pattern matchers"""
        # Dictionary mapping day names to their index (0 = Monday, 6 = Sunday)
        self.day_indices = {
            "monday": 0, "mon": 0,
            "tuesday": 1, "tue": 1, "tues": 1,
            "wednesday": 2, "wed": 2,
            "thursday": 3, "thu": 3, "thurs": 3,
            "friday": 4, "fri": 4,
            "saturday": 5, "sat": 5,
            "sunday": 6, "sun": 6
        }
        
        # Dictionary of month names to their index
        self.month_names = {
            "january": 1, "jan": 1,
            "february": 2, "feb": 2,
            "march": 3, "mar": 3,
            "april": 4, "apr": 4,
            "may": 5,
            "june": 6, "jun": 6,
            "july": 7, "jul": 7,
            "august": 8, "aug": 8,
            "september": 9, "sep": 9, "sept": 9,
            "october": 10, "oct": 10,
            "november": 11, "nov": 11,
            "december": 12, "dec": 12
        }
    
    def _next_day_of_week(self, day_index):
        """
        Calculate the date of the next occurrence of a day of the week
        
        Args:
            day_index (int): Index of the day (0 = Monday, 6 = Sunday)
            
        Returns:
            datetime: Date of the next occurrence
        """
        today = datetime.now()
        days_ahead = day_index - today.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    def extract_date(self, query):
        """
        Extract date from natural language query
        
        Args:
            query (str): User's query text
            
        Returns:
            str: Extracted date in YYYY-MM-DD format, or None if no date found
        """
        # Lower case for easier matching
        query = query.lower()
        
        # Check for exact date formats (YYYY-MM-DD)
        date_pattern = r"\b(\d{4}-\d{2}-\d{2})\b"
        date_match = re.search(date_pattern, query)
        if date_match:
            try:
                date_str = date_match.group(1)
                return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
            except ValueError:
                pass
        
        # Check for other common date formats (MM/DD/YYYY, DD/MM/YYYY)
        for pattern, format_str in [
            (r"\b(\d{1,2}/\d{1,2}/\d{4})\b", "%m/%d/%Y"),  # MM/DD/YYYY
            (r"\b(\d{1,2}-\d{1,2}-\d{4})\b", "%m-%d-%Y"),  # MM-DD-YYYY
            (r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b", "%m.%d.%Y")  # MM.DD.YYYY
        ]:
            date_match = re.search(pattern, query)
            if date_match:
                try:
                    date_str = date_match.group(1)
                    return datetime.strptime(date_str, format_str).date().isoformat()
                except ValueError:
                    continue
        
        # Check for today, tomorrow, day after tomorrow
        if "today" in query:
            return datetime.now().date().isoformat()
        elif "tomorrow" in query:
            return (datetime.now() + timedelta(days=1)).date().isoformat()
        elif "day after tomorrow" in query:
            return (datetime.now() + timedelta(days=2)).date().isoformat()
        
        # Check for next [day of week]
        for day_name, day_index in self.day_indices.items():
            if f"next {day_name}" in query:
                return self._next_day_of_week(day_index).date().isoformat()
        
        # Check for this [day of week]
        for day_name, day_index in self.day_indices.items():
            if f"this {day_name}" in query:
                today = datetime.now()
                days_ahead = day_index - today.weekday()
                if days_ahead < 0:  # Already passed this week
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).date().isoformat()
        
        # Check for just [day of week] (assumes next occurrence)
        for day_name, day_index in self.day_indices.items():
            day_pattern = f"\\b{day_name}\\b"
            if re.search(day_pattern, query):
                return self._next_day_of_week(day_index).date().isoformat()
        
        # Check for month and day (e.g., "January 15")
        month_day_pattern = r"(?:(?:on|for)\s+)?([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?"
        month_day_match = re.search(month_day_pattern, query)
        if month_day_match:
            month_name = month_day_match.group(1).lower()
            day = int(month_day_match.group(2))
            
            if month_name in self.month_names:
                month = self.month_names[month_name]
                year = datetime.now().year
                
                # If the date has already passed this year, assume next year
                try:
                    date_obj = datetime(year, month, day)
                    if date_obj.date() < datetime.now().date():
                        date_obj = datetime(year + 1, month, day)
                    return date_obj.date().isoformat()
                except ValueError:
                    # Invalid date (e.g., February 30)
                    pass
        
        # Check for "in X days/weeks/months"
        time_delta_pattern = r"in\s+(\d+)\s+(day|days|week|weeks|month|months)"
        time_delta_match = re.search(time_delta_pattern, query)
        if time_delta_match:
            amount = int(time_delta_match.group(1))
            unit = time_delta_match.group(2)
            
            if unit in ["day", "days"]:
                return (datetime.now() + timedelta(days=amount)).date().isoformat()
            elif unit in ["week", "weeks"]:
                return (datetime.now() + timedelta(weeks=amount)).date().isoformat()
            elif unit in ["month", "months"]:
                # Approximation for months
                return (datetime.now() + timedelta(days=30*amount)).date().isoformat()
        
        # No date found
        return None
