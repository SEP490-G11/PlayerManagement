class AppointmentSortKey:
    START_TIME_DESC = 1
    START_TIME_ASC = 2


class AppointmentSortValue:
    START_TIME_DESC = "time_slot_start_time desc"
    START_TIME_ASC = "time_slot_start_time asc"


class AppointmentType:
    NEW_EXAMINATION = "1"
    RE_EXAMINATION = "2"


class AppointmentState:
    NOT_YET_ARRIVED = "1"
    WAITING = "2"
    EXAMINING = "3"
    CONSULT = "4"
    FINISHED = "5"
    WAITING_FOR_CONCLUDE = "6"
    CYCLOGYL = "7"
    SUBCLINICAL = "8"
    EXPIRED = "9"


class BookingType:
    BY_DATE = "1"
    BY_DOCTOR = "2"
    BY_TECHNICIAN = "3"


class AppointmentErrorCode:
    APPOINTMENT_DOES_NOT_EXIST = "APPOINTMENT_DOES_NOT_EXIST"

class AppointmentPrintingType:
    VIVISION = "Vivision"
    VIVISION_KID = "Vivision Kid"

class FloorEnum:
    NO_CHOICE ="0"
    OBSTETRICS_GYNECOLOGY = "1"
    FAMILY_PLANNING = "2"
    OBSTETRICS_GYNECOLOGY_ULTRASOUND = "3"
    TOOL_HANDLING = "4"
    SAVE_THE_PATIENT = "5"
    CRAFTS_ROOM = "6"


OBJECT_IS_NOT_EXIST = "{} không tồn tại, vui lòng tải lại trang để tiếp tục thao tác"

APPOINTMENT_ERROR_MESSAGE_DICT = {
    AppointmentErrorCode.APPOINTMENT_DOES_NOT_EXIST: OBJECT_IS_NOT_EXIST.format(
        "Lịch hẹn"
    ),
}

APPOINTMENT_TYPE_CHOICES = [
    (AppointmentType.NEW_EXAMINATION, "New examination"),
    (AppointmentType.RE_EXAMINATION, "Re examination"),
]

APPOINTMENT_STATE_CHOICES = [
    (AppointmentState.NOT_YET_ARRIVED, "Not Yet Arrived"),
    (AppointmentState.WAITING, "Waiting"),
    (AppointmentState.EXAMINING, "Examining"),
    (AppointmentState.CONSULT, "Consult"),
    (AppointmentState.FINISHED, "Finished"),
    (AppointmentState.WAITING_FOR_CONCLUDE, "Waiting for conclude"),
    (AppointmentState.CYCLOGYL, "Cyclogyl"),
    (AppointmentState.SUBCLINICAL, "Subclinical"),
    (AppointmentState.EXPIRED, "Expired"),
]

BOOKING_TYPE_CHOICES = [
    (BookingType.BY_DATE, "Date Priority"),
    (BookingType.BY_DOCTOR, "Doctor Priority"),
    (BookingType.BY_TECHNICIAN, "Technician Priority"),
]

APPOINTMENT_SORT_CHOICES = [
    (AppointmentSortKey.START_TIME_DESC, AppointmentSortValue.START_TIME_DESC),
    (AppointmentSortKey.START_TIME_ASC, AppointmentSortValue.START_TIME_ASC),
]

DEFAULT_APPOINTMENT_SORT = AppointmentSortValue.START_TIME_DESC
APPOINTMENT_START_TIME = "time_slot_id.start_time"
APPOINTMENT_SORT_DICT = dict(APPOINTMENT_SORT_CHOICES)

BOOKING_TYPE_VALUES = set(
    getattr(BookingType, attr) for attr in dir(BookingType) if not attr.startswith("_")
)
APPOINTMENT_STATE_VALUES = set(
    getattr(AppointmentState, attr)
    for attr in dir(AppointmentState)
    if not attr.startswith("_")
)

VISIT_STATE_LIST = [
    AppointmentState.EXAMINING,
    AppointmentState.CONSULT,
    AppointmentState.FINISHED,
    AppointmentState.WAITING_FOR_CONCLUDE,
    AppointmentState.CYCLOGYL,
    AppointmentState.SUBCLINICAL,
]


APPOINTMENT_TYPE_DICT = {
    AppointmentType.NEW_EXAMINATION: "Khám mới",
    AppointmentType.RE_EXAMINATION: "Tái khám",
}

APPOINTMENT_STATE_DICT = {
    AppointmentState.NOT_YET_ARRIVED: "Chưa đến",
    AppointmentState.WAITING: "Chờ khám",
    AppointmentState.EXAMINING: "Đang khám",
    AppointmentState.CONSULT: "Tư vấn",
    AppointmentState.FINISHED: "Kết thúc",
    AppointmentState.WAITING_FOR_CONCLUDE: "CBSKL",
    AppointmentState.CYCLOGYL: "Cyclogyl",
    AppointmentState.SUBCLINICAL: "CLS",
    AppointmentState.EXPIRED: "Hết hạn",
}

# Excel style
HEADER_STYLE = "font: bold on, height 240, name Calibri (Body); align: horiz left"
CONTENT_STYLE = "font: height 240, name Calibri (Body); align: horiz left"
DATE_FIELDS = ["create_date", "write_date"]


APPOINTMENT_PRINTING_TYPES = [
    (AppointmentPrintingType.VIVISION, "Vivision"),
    (AppointmentPrintingType.VIVISION_KID, "Vivision Kid")
]

FLOOR_ENUM = [
    (FloorEnum.NO_CHOICE, " "),
    (FloorEnum.OBSTETRICS_GYNECOLOGY, "p.301 PK Sản Phụ Khoa"),
    (FloorEnum.FAMILY_PLANNING, "p.302 PK kế hoạch hóa gia đình"),
    (FloorEnum.OBSTETRICS_GYNECOLOGY_ULTRASOUND, "p.303 P.Siêu âm Sản Phụ Khoa"),
    (FloorEnum.TOOL_HANDLING, "p.401 P.Xử lý dụng cụ"),
    (FloorEnum.SAVE_THE_PATIENT, "p.402 P.Lưu bệnh nhân"),
    (FloorEnum.CRAFTS_ROOM, "p.403 P.Thủ Thuật"),
]


FLOOR_OPT_ENUM = [
    ("0", " "),
    ("1", "Tầng 2"),
    ("2", "Tầng 3"), 
    ("3", "Tầng 4"),
]
