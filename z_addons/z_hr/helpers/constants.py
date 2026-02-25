class TimeSchedule:
    FROM_TIME = "00:00"
    TO_TIME = "23:59"
    SLOT_SIZE = 15
    PERIOD = 90
    MAX_DAYS = 60


class HrErrorCode:
    EMPLOYEE_DOES_NOT_EXIST = "EMPLOYEE_DOES_NOT_EXIST"
    TIME_SLOT_IS_DISABLE = "TIME_SLOT_IS_DISABLE"
    TIME_SLOT_IS_NOT_AVAILBLE = "TIME_SLOT_IS_NOT_AVAILBLE"


OBJECT_IS_NOT_EXIST = "{} không tồn tại, vui lòng tải lại trang để tiếp tục thao tác"
HR_ERROR_MESSAGE_DICT = {
    HrErrorCode.EMPLOYEE_DOES_NOT_EXIST: OBJECT_IS_NOT_EXIST.format("Nhân viên"),
    HrErrorCode.TIME_SLOT_IS_DISABLE: "Time slot không có sẵn",
    HrErrorCode.TIME_SLOT_IS_NOT_AVAILBLE: "Time slot không khả dụng",
}
