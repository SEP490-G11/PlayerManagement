import xlwt
import base64
from io import BytesIO
from odoo import _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_appointment.helpers.constants import (
    DEFAULT_APPOINTMENT_SORT,
    APPOINTMENT_START_TIME,
    APPOINTMENT_SORT_DICT,
    APPOINTMENT_STATE_VALUES,
    VISIT_STATE_LIST,
    BOOKING_TYPE_VALUES,
    BookingType,
    HEADER_STYLE,
    CONTENT_STYLE,
    DATE_FIELDS,
)
from odoo.addons.z_hr.helpers.constants import HrErrorCode
from odoo.addons.z_web.helpers.constants import (
    STANDARD_TIME_FORMAT,
    READABLE_DATE_FORMAT,
    EXPORT_DATE_FORMAT,
)
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.validation import ZValidation


class ZAppointmentUtils:
    @staticmethod
    def filter_appointments_or_visits(params, visit_states=None):
        # Initial conditions
        search_domain = [("state", "in", visit_states)] if visit_states else []
        order = DEFAULT_APPOINTMENT_SORT

        # Get params
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        place_id = params.get("place_id")
        search_key = ZUtils.escape_special_characters(params.get("input"))
        sort = ZUtils.get(params, "sort", int)
        customer_ids = ZUtils.parse_to_list_id(params, "customer_ids")
        doctor_ids = ZUtils.parse_to_list_id(params, "doctor_ids")
        technician_ids = ZUtils.parse_to_list_id(params, "technician_ids")
        group_ids = ZUtils.parse_to_list_id(params, "group_ids")
        state = ZUtils.parse_to_list_id(params, "state")

        # Build search domain
        if search_key:
            search_domain += [
                "|",
                "|",
                ("customer_id.name", "ilike", search_key),
                ("customer_id.mobile", "ilike", search_key),
                ("customer_id.z_mobile", "ilike", search_key),
            ]
        if start_date:
            search_domain.append(
                (APPOINTMENT_START_TIME, ">=", start_date + " 00:00:00")
            )
        if end_date:
            search_domain.append((APPOINTMENT_START_TIME, "<=", end_date + " 23:59:59"))
        if doctor_ids:
            search_domain.append(("doctor_id", "in", doctor_ids))
        if technician_ids:
            search_domain.append(("technician_id", "in", technician_ids))
        if customer_ids:
            search_domain.append(("customer_id", "in", customer_ids))
        if group_ids:
            search_domain.append(("customer_id.group_id", "in", group_ids))
        if state:
            search_domain.append(("state", "in", state))
        if place_id:
            search_domain.append(("place_id", "=", int(place_id)))
        if sort:
            order = APPOINTMENT_SORT_DICT.get(sort, DEFAULT_APPOINTMENT_SORT)
        return search_domain, order

    @staticmethod
    def format_appointment_item(row, record, technician):
        return {
            "no": row,
            "id": record.id,
            "customer_id": record.customer_id.id,
            "customer_name": record.customer_id.name,
            "customer_phone_number": record.customer_id.mobile,
            "customer_note": record.customer_id.comment,
            "customer_group": {
                "id": record.customer_id.group_id.id,
                "label": record.customer_id.group_id.name,
            },
            "booking_type": record.booking_type,
            "booking_date": ZUtils.format_datetime(record.time_slot_id.start_time),
            "booking_time": ZUtils.format_datetime(
                record.time_slot_id.start_time, STANDARD_TIME_FORMAT
            ),
            "place_id": record.place_id.id if record.place_id else None,
            "place_name": record.place_id.name if record.place_id else None,
            "type": record.type,
            "state": record.state,
            "overbook": record.overbook,
            "doctor": {
                "id": record.doctor_id.id,
                "name": record.doctor_id.name,
            },
            "has_took_examination": record.has_took_examination,
            "technician": technician,
            "time_slot_id": record.time_slot_id.id,
            "examination_reason": record.examination_reason,
            "note": record.note,
            "create_date": ZUtils.format_datetime(record.create_date),
            "write_date": ZUtils.format_datetime(record.write_date),
            "printing_type": record.printing_type
        }

    @staticmethod
    def format_results(records, offset=0, other_format_func=None):
        results = []
        for row, res in enumerate(records, offset + 1):
            # specialist = res.time_slot_id.employee_id
            # if not specialist.is_doctor:
            #     technician = {
            #         "id": specialist.id,
            #         "name": specialist.name,
            #     }
            # else:
            technician = {
                "id": res.technician_id.id if res.technician_id else None,
                "name": res.technician_id.name if res.technician_id else "",
            }
            item = (
                other_format_func(row, res, technician)
                if other_format_func
                else ZAppointmentUtils.format_appointment_item(row, res, technician)
            )
            results.append(item)
        return results

    @staticmethod
    def validate_required_field(values, is_update=False):
        required_fields = ["booking_type", "customer", "time_slot_id", "doctor_id"]
        if is_update:
            required_fields.append("id")
        ZValidation.validate_required_field(values, required_fields)
        return ZUtils.strip_values(values)

    @staticmethod
    def validate_booking_type(booking_type, values):
        if booking_type not in BOOKING_TYPE_VALUES:
            raise ValidationError("Booking type is invalid.")
        if booking_type == BookingType.BY_TECHNICIAN:
            ZValidation.validate_required_field(values, ["technician_id"])

    @staticmethod
    def validate_appointment_state(state: str, is_visit: bool = False):
        valid_state = APPOINTMENT_STATE_VALUES if not is_visit else VISIT_STATE_LIST
        if state not in valid_state:
            raise ValidationError("State is invalid.")

    @staticmethod
    def check_empty_customer_id_and_info(customer_id, customer_info):
        if not customer_id and not customer_info:
            raise ValidationError(
                "Không thể để trống đồng thời id và thông tin khách hàng"
            )

    @staticmethod
    def check_valid_appointment(time_slot, appointment):
        if (
            appointment
            and time_slot
            and appointment.time_slot_id.id != time_slot.id
            and appointment.time_slot_id.start_time
            <= (ZUtils.now()).replace(tzinfo=None)
        ):
            raise ValidationError(_("Past the rescheduling time"))

    @staticmethod
    def check_overbook(overbook: bool, time_slot, appointment):
        if (
            not overbook
            and time_slot.booked
            and (
                not appointment
                or (
                    appointment
                    and (
                        time_slot.id != appointment.time_slot_id.id
                        or appointment.overbook
                    )
                )
            )
        ):
            raise UserError(HrErrorCode.TIME_SLOT_IS_NOT_AVAILBLE)

    @staticmethod
    def validate_time_slot_by_booking_type(
        appointment_model,
        booking_type: str,
        overbook: bool,
        doctor_id: int,
        technician_id: int,
        time_slot,
        appointment,
    ):
        if booking_type == BookingType.BY_TECHNICIAN:
            if technician_id != time_slot.employee_id.id:
                raise ValidationError(
                    "Vui lòng gửi lên slot của kỹ thuật viên khi đặt lịch ưu tiên Kỹ thuật viên"
                )
            if not overbook:
                msg = "Không thể chọn bác sĩ có lịch hẹn vào giờ này"
                appointment_ids = (
                    appointment_model._get_appointments_by_doctor_id_and_start_time(
                        doctor_id, time_slot.start_time
                    ).mapped("id")
                )
                if appointment_ids and (
                    not appointment
                    or (appointment and appointment.id not in appointment_ids)
                ):
                    raise ValidationError(msg)
        else:
            if time_slot.employee_id.id != doctor_id:
                raise ValidationError(
                    "Vui lòng gửi lên slot của bác sĩ khi đặt lịch ưu tiên Ngày tháng/Bác sĩ"
                )

    @staticmethod
    def get_customer_info(instance, customer_id, customer_info):
        customer_instance = instance.env["res.partner"]
        if customer_id:
            customer = customer_instance._get_customer_by_id(customer_id)
            customer._format_mobile()
            return customer
        else:
            customer = customer_instance.create(customer_info)
            customer._format_mobile()
            return customer

    @staticmethod
    def booking_slots(time_slot_instance, appointment):
        employee_ids = [appointment.doctor_id.id]
        technician_id = appointment.technician_id
        if technician_id:
            employee_ids.append(technician_id.id)
        time_slot_instance._get_time_slots_by_employee_ids_and_start_time(
            employee_ids, appointment.time_slot_id.start_time
        ).write({"booked": True})

    @staticmethod
    def release_slots(time_slot_instance, appointment):
        employee_ids = []
        doctor_id = appointment.doctor_id
        technician_id = appointment.technician_id
        if appointment.overbook:
            if appointment.booking_type == BookingType.BY_TECHNICIAN:
                employee_ids.append(doctor_id.id)
            elif technician_id:
                employee_ids.append(technician_id.id)
        else:
            employee_ids.append(doctor_id.id)
            if technician_id:
                employee_ids.append(technician_id.id)
        if employee_ids:
            time_slot_instance._get_time_slots_by_employee_ids_and_start_time(
                employee_ids, appointment.time_slot_id.start_time
            ).write({"booked": False})

    @staticmethod
    def generate_examination_code(instance, start_time):
        examination_count = instance.env["z_appointment.examination_count"]
        prefix = f"LK{ZUtils.format_datetime(start_time, '%y%m%d')}"

        examination_count_record =  examination_count.search([("prefix","=",prefix)],limit = 1)

        if examination_count_record :
            examination_count_record.count += 1
            return f"{prefix}{examination_count_record.count:04d}"
        else:
            examination_count.create({
                "prefix": prefix,
                "count": 1
            })
            return f"{prefix}{1:04d}"



    @staticmethod
    def create_or_update(instance, values, is_update=False):
        # Validation
        appointment_instance = instance.env["z_appointment.appointment"]
        time_slot_instance = instance.env["z_hr.time_slot"]
        employee_instance = instance.env["hr.employee"]
        appointment = None
        values = ZAppointmentUtils.validate_required_field(values, is_update)
        booking_type = values["booking_type"]
        ZAppointmentUtils.validate_booking_type(booking_type, values)
        if is_update:
            appointment = appointment_instance._get_appointment_by_id(values["id"])
        customer_values = values.get("customer")
        customer_id = customer_values.get("id")
        customer_info = customer_values.get("info")
        if 'date' in customer_info and not customer_info['date']:
            customer_info['date'] = None
        ZAppointmentUtils.check_empty_customer_id_and_info(customer_id, customer_info)

        # Get time_slot, doctor, optom
        doctor_id = values["doctor_id"]
        technician_id = values.get("technician_id")
        time_slot_id = values["time_slot_id"]
        overbook = values.get("overbook", False)

        # Validate old appointment, time slot, overbook state
        time_slot = time_slot_instance._get_enable_time_slot_by_id(
            time_slot_id, is_update
        )
        ZAppointmentUtils.check_valid_appointment(time_slot, appointment)
        ZAppointmentUtils.check_overbook(overbook, time_slot, appointment)
        employee_instance._get_employee_by_id(doctor_id)
        if technician_id:
            employee_instance._get_employee_by_id(technician_id)
        ZAppointmentUtils.validate_time_slot_by_booking_type(
            appointment_instance,
            booking_type,
            overbook,
            doctor_id,
            technician_id,
            time_slot,
            appointment,
        )

        # Get or create customer
        customer = ZAppointmentUtils.get_customer_info(
            instance, customer_id, customer_info
        )
        payload = {
            "booking_type": booking_type,
            "customer_id": customer.id,
            "time_slot_id": time_slot_id,
            "doctor_id": doctor_id,
            "technician_id": technician_id,
            "type": values["type"],
            "overbook": values.get("overbook"),
            "examination_reason": values.get("examination_reason"),
            "note": values.get("note"),
        }
        if appointment is None:
            appointment = appointment_instance.create(payload)
            ZAppointmentUtils.booking_slots(time_slot_instance, appointment)
        else:
            old_technician_id = (
                appointment.technician_id.id if appointment.technician_id else None
            )
            if (
                appointment.time_slot_id.id != time_slot.id
                or appointment.doctor_id.id != doctor_id
                or (old_technician_id != technician_id)
            ):
                ZAppointmentUtils.release_slots(time_slot_instance, appointment)
                appointment.write(payload)
                ZAppointmentUtils.booking_slots(time_slot_instance, appointment)
            else:
                appointment.write(payload)
        return appointment

    @staticmethod
    def format_detail(record):
        res = {
            "id": record.id,
            "customer": record.customer_id.read(
                [
                    "id",
                    "group_id",
                    "name",
                    "code",
                    "gender",
                    "date",
                    "mobile",
                    "job",
                    "comment",
                ]
            )[0],
            "doctor_id": record.doctor_id.id,
            "technician_id": record.technician_id.id if record.technician_id else None,
            "time_slot_id": record.time_slot_id.id,
            "place_id": record.place_id.id if record.place_id else None,
            "type": record.type,
            "state": record.state,
            "booking_type": record.booking_type,
            "booking_date": ZUtils.format_datetime(record.time_slot_id.start_time),
            "booking_time": ZUtils.format_datetime(
                record.time_slot_id.start_time, STANDARD_TIME_FORMAT
            ),
            "overbook": record.overbook,
            "examination_reason": record.examination_reason,
            "note": record.note,
            "create_date": ZUtils.format_datetime(record.create_date),
            "write_date": ZUtils.format_datetime(record.write_date),
        }
        res["customer"]["date"] = ZUtils.format_datetime(res["customer"]["date"])
        return res

    @staticmethod
    def process_excel(
        queryset,
        fields,
        date_fields,
        selection_fields,
        reference_fields,
        condition_fields,
        other_format_times,
        sheet,
        headers,
        header_format,
        content_format,
    ):
        def __get_value(record, field):
            if field in reference_fields.keys():
                ref = [v for v in reference_fields[field].split(".")]
                tmp = record
                for i in ref:
                    try:
                        tmp = tmp[i] or ""
                    except (KeyError, TypeError):
                        tmp = ""
                    if not tmp:
                        continue
                value = tmp
            else:
                value = getattr(record, field, "") or ""
            if field in selection_fields.keys():
                value = selection_fields[field].get(value)
            elif field in date_fields:
                if field in other_format_times.keys():
                    date_format = other_format_times[field]
                else:
                    date_format = READABLE_DATE_FORMAT
                value = ZUtils.format_datetime(value, date_format)
            elif field in condition_fields.keys():
                value = condition_fields[field](record[field])
            return value

        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        for row, record in enumerate(queryset, start=1):
            sheet.write(row, 0, row, content_format)
            for col, field in enumerate(fields, start=1):
                value = __get_value(record, field)
                sheet.write(row, col, value, content_format)

    @staticmethod
    def export_data(
        queryset,
        headers,
        fields,
        filename,
        extra_date_fields=[],
        selection_fields={},
        reference_fields={},
        other_format_times={},
        condition_fields={},
    ):
        workbook = xlwt.Workbook(encoding="utf-8")
        sheet = workbook.add_sheet("Data")
        header_format = xlwt.easyxf(HEADER_STYLE)
        content_format = xlwt.easyxf(CONTENT_STYLE)
        date_fields = DATE_FIELDS + extra_date_fields

        ZAppointmentUtils.process_excel(
            queryset,
            fields,
            date_fields,
            selection_fields,
            reference_fields,
            condition_fields,
            other_format_times,
            sheet,
            headers,
            header_format,
            content_format,
        )

        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)
        excel_content = base64.b64encode(excel_file.read())
        url = "data:application/vnd.ms-excel;base64," + excel_content.decode("utf-8")
        return {
            "url": url,
            "filename": f"{filename}-{ZUtils.format_datetime(ZUtils.now(), EXPORT_DATE_FORMAT)}.xls",
        }
