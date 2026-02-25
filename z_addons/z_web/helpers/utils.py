import pytz
from datetime import datetime, timedelta

from odoo.addons.z_web.helpers.constants import (
    TIME_ZONE,
    DEFAULT_DATE_TIME_FORMAT,
    STANDARD_DATE_FORMAT,
    STANDARD_TIME_FORMAT,
    TIME_SLOT_FORMAT,
)


class ZUtils:
    @staticmethod
    def escape_special_characters(escaped):
        if not escaped:
            return ""
        for char in ["\\"]:
            escaped = escaped.replace(char, f"\\{char}")
        return escaped

    @staticmethod
    def format_datetime(datetime_obj: datetime, format=DEFAULT_DATE_TIME_FORMAT):
        try:
            return datetime.strftime(datetime_obj, format) if datetime_obj else ""
        except Exception:
            return ""

    @staticmethod
    def now():
        return datetime.now(pytz.timezone(TIME_ZONE))

    @staticmethod
    def str_to_date(date_str: str):
        format_str = STANDARD_DATE_FORMAT
        try:
            result = datetime.strptime(date_str, format_str)
            return result.date()
        except Exception:
            return None

    @staticmethod
    def str_to_time(time_str: str):
        format_str = STANDARD_TIME_FORMAT
        try:
            return datetime.strptime(time_str, format_str)
        except Exception:
            return None

    @staticmethod
    def str_to_datetime(date_str: str, format_str=TIME_SLOT_FORMAT):
        try:
            return datetime.strptime(date_str, format_str)
        except Exception:
            return None

    @staticmethod
    def float_to_time(float_value: float):
        # Convert the float value to seconds
        total_seconds = int(float_value * 3600)

        # Create a datetime object with today's date and the time delta
        base_date = datetime(1900, 1, 1)
        time = base_date + timedelta(seconds=total_seconds)

        # Format the time as a string in HH:MM format
        time_str = time.strftime(STANDARD_TIME_FORMAT)

        return time_str

    @staticmethod
    def time_to_float(time_str: str):
        # Parse the time string into a datetime object
        time_obj = ZUtils.str_to_time(time_str)

        # Calculate the timedelta between the time object and the base date
        base_date = datetime(1900, 1, 1)
        time_delta = time_obj - base_date

        # Calculate the total seconds from the timedelta
        total_seconds = time_delta.total_seconds()

        return total_seconds / 3600

    @staticmethod
    def get(data, key, formater=None):
        value = data.get(key)
        if value is None:
            return None
        if formater is None:
            return value
        try:
            return formater(value)
        except ValueError:
            return None

    @staticmethod
    def parse_to_list_id(payload, key):
        data = payload.get(key, {})
        if isinstance(data, str):
            ids = [int(id_str) for id_str in data.split(",") if id_str.strip()]
            return ids
        return []

    @staticmethod
    def strip_values(data: dict):
        return {
            key: value.strip() if isinstance(value, str) else value
            for key, value in data.items()
        }
    
    @staticmethod
    def calculate_age(birthdate):
        today = datetime.today()
        
        years = today.year - birthdate.year
        if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
            years -= 1
        
        if years > 0:
            return f"{years} tuổi"
        
        months = (today.year - birthdate.year) * 12 + today.month - birthdate.month
        if today.day < birthdate.day:
            months -= 1
        
        return f"{months + 1} tháng"
    
    @staticmethod
    def generate_pattern(length = 16):
        vietnamese_chars = (
            "A-Za-z0-9"
            "ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠ"
            "àáâãèéêìíòóôõùúăđĩũơ"
            "ƯăâêôơƯ"
            "àáảãạèéẻẽẹìíỉĩịòóỏõọ"
            "ùúủũụỳýỷỹỵ"
            "ĂÂÊÔƠƯ"
            "ÁÀẢÃẠÈÉẺẼẸÌÍỈĨỊÒÓỎÕỌ"
            "ÙÚỦŨỤỲÝỶỸỴ"
        )

        pattern = fr'^[{vietnamese_chars}]{{1,{length}}}$'
        
        return pattern

        
    @staticmethod
    def get_content_type_by_path(path_name: str):
        if '.' in path_name:
            extension = path_name.split('.')[-1].lower()
        else:
            extension = ''
        if extension in ['jpg', 'jpeg']:
           return 'image/jpeg'
        elif extension == 'png':
            return 'image/png'
        elif extension == 'pdf':
            return 'application/pdf'
        else:
            return 'image/jpeg'

    @staticmethod
    def convert_number_to_currency_format(number: float):
        formatted_number = f"{int(number):,}".replace(",", ".")
        return formatted_number