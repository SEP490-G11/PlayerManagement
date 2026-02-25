CUSTOMER_RECORD_LIMIT = 999999


class PartnerErrorCode:
    # System errors
    CUSTOMER_QUANTITY_LIMIT_EXCEEDED = "CUSTOMER_QUANTITY_LIMIT_EXCEEDED"

    # Does not exist errors
    CUSTOMER_DOES_NOT_EXIST = "CUSTOMER_DOES_NOT_EXIST"
    GROUP_DOES_NOT_EXIST = "GROUP_DOES_NOT_EXIST"
    RESEARCH_DOES_NOT_EXIST = "RESEARCH_DOES_NOT_EXIST"
    DUPLICATE_CUSTOMER_ERROR = "DUPLICATE_CUSTOMER_ERROR"


OBJECT_IS_NOT_EXIST = "{} không tồn tại, vui lòng tải lại trang để tiếp tục thao tác"
PARTNER_ERROR_MESSAGE_DICT = {
    PartnerErrorCode.CUSTOMER_QUANTITY_LIMIT_EXCEEDED: "Số lượng khách hàng trên hệ thống đã vượt quá giới hạn, vui lòng liên hệ Admin để được hỗ trợ!",
    PartnerErrorCode.CUSTOMER_DOES_NOT_EXIST: OBJECT_IS_NOT_EXIST.format("Khách hàng"),
    PartnerErrorCode.GROUP_DOES_NOT_EXIST: OBJECT_IS_NOT_EXIST.format("Nhóm"),
    PartnerErrorCode.RESEARCH_DOES_NOT_EXIST: OBJECT_IS_NOT_EXIST.format("Nghiên cứu"),
}
