from odoo import _
from odoo.addons.z_appointment.helpers.utils import ZAppointmentUtils
from odoo.addons.z_obstetric.helpers.constants import (
    APPOINTMENT_STATE_VALUES,
    VISIT_STATE_LIST,
)
from odoo.addons.z_web.helpers.constants import (
    STANDARD_TIME_FORMAT,
)
from odoo.exceptions import ValidationError
from odoo.addons.z_web.helpers.utils import ZUtils


class ZAppointmentUtilsExtend(ZAppointmentUtils):
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
        if "date" in customer_info and not customer_info["date"]:
            customer_info["date"] = None
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
            "approach_channel": values.get("approach_channel"),
            "date_assign": values.get("date_assign"),
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
    # update list state validate
    @staticmethod
    def validate_appointment_state(state: str, is_visit: bool = False):
        valid_state = APPOINTMENT_STATE_VALUES if not is_visit else VISIT_STATE_LIST
        if state not in valid_state:
            raise ValidationError("State is invalid.")


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
        "printing_type": record.printing_type,
        "approach_channel": record.approach_channel,
    }


ZAppointmentUtils.format_appointment_item = staticmethod(format_appointment_item)
