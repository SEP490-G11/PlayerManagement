class ErrorCode:
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST_ERROR = "BAD_REQUEST_ERROR"


ERROR_MESSAGE_DICT = {
    ErrorCode.INTERNAL_SERVER_ERROR: "Có lỗi xảy ra, vui lòng thử lại",
    ErrorCode.BAD_REQUEST_ERROR: "Param gửi lên không hợp lệ",
}


TIME_ZONE = "Asia/Ho_Chi_Minh"
READABLE_DATE_FORMAT = "%d/%m/%Y"
DEFAULT_DATE_TIME_FORMAT = "%Y-%m-%d"
STANDARD_DATE_FORMAT = "%Y-%m-%d"
STANDARD_TIME_FORMAT = "%H:%M"
TIME_SLOT_FORMAT = "%Y-%m-%d %H:%M"
DISPLAY_TIME_SLOT_FORMAT = "%d/%m/%Y %H:%M"
EXPORT_DATE_FORMAT = "%d%m%Y-%H%M%S"
