from typing import List
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
import pytz
from odoo import fields
from pytz import timezone, UTC

from odoo.addons.z_hr.helpers.constants import TimeSchedule
from odoo.addons.z_web.helpers.tools import ZTools
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.constants import (
    STANDARD_TIME_FORMAT,
    TIME_SLOT_FORMAT,
    TIME_ZONE,
)


class ZTimeSlotUtils:
    @staticmethod
    def filter_time_slots(instance, params):
        expect_date = params["expect_date"]
        start_at = expect_date + " 00:00:00"
        end_at = expect_date + " 23:59:59"
        place_id = params["place_id"]
        search_domain = [
            ("enable", "=", True),
            ("start_time", ">=", start_at),
            ("start_time", "<=", end_at),
            ("place_id", "=", int(place_id)),
        ]
        employee_id = ZUtils.get(params, "employee_id", int)
        if employee_id:
            search_domain.append(("employee_id", "=", employee_id))
        else:
            search_domain.append(("employee_id.is_doctor", "=", True))

        return instance.env["z_hr.time_slot"].search(
            search_domain, order="start_time asc"
        )

    @staticmethod
    def filter_valid_time_slots(instance, records):
        def _filter_valid_times_from_start_times(start_times: list):
            search_domain = [
                ("start_time", "in", start_times),
                ("enable", "=", True),
                ("employee_id.is_doctor", "=", True),
            ]
            return (
                instance.env["z_hr.time_slot"]
                .search(search_domain)
                .mapped("start_time")
            )

        ids = records.mapped("id")
        start_times = records.mapped("start_time")
        valid_times = _filter_valid_times_from_start_times(start_times)
        return records.search(
            [("id", "in", ids), ("start_time", "in", valid_times)],
            order="start_time asc",
        )

    @staticmethod
    def _bulk_create(instance, values):
        instance.env["z_hr.time_slot"].create(values)

    @staticmethod
    def _get_specific_time_slot(instance, employee_id, attendance, start_time):
        return instance.env["z_hr.time_slot"].search(
            [
                ("employee_id", "=", employee_id),
                ("attendance_id", "=", attendance.id),
                ("start_time", "=", start_time),
            ],
            limit=1,
        )

    @staticmethod
    def _get_time_slot_ids_by_attendances(
        instance, employee_id: int, attendance_ids: List[int]
    ):
        return instance.env["z_hr.time_slot"].search(
            [
                ("employee_id.id", "=", employee_id),
                ("attendance_id.id", "in", attendance_ids),
                ("booked", "=", False),
            ]
        )

    @staticmethod
    def _create_time_slots(instance, employee_id, attendance, time_slots):
        def _prepare_data(start_time):
            # always create new record even though start_time already exists
            return {
                "employee_id": employee_id,
                "attendance_id": attendance.id,
                "start_time": start_time,
                "slot_size": TimeSchedule.SLOT_SIZE,
                "enable": attendance.enable,
                "booked": False,
            }

        values = []
        now = (
            UTC.localize(fields.Datetime.now())
            .astimezone(pytz.timezone(TIME_ZONE) or timezone("UTC"))
            .replace(tzinfo=None)
        )
        for slot in time_slots:
            if now > slot.replace(tzinfo=None):
                continue
            ts = _prepare_data(slot.strftime(TIME_SLOT_FORMAT))
            if ts:
                values.append(ts)
        ZTimeSlotUtils._bulk_create(instance, values)

    @staticmethod
    def delete_old_time_slots_by_attendances(
        instance, employee_id: int, attendance_ids: List[int]
    ):
        if attendance_ids:
            time_slots = ZTimeSlotUtils._get_time_slot_ids_by_attendances(
                instance, employee_id, attendance_ids
            )
            if time_slots:
                time_slots.unlink()

    @staticmethod
    def _process_time_slot_in_attendances(attendance):
        # Each slot size in 15 minutes
        slot_duration = timedelta(minutes=TimeSchedule.SLOT_SIZE)

        # Start time and end time of working in a day
        start_time = ZUtils.str_to_time(TimeSchedule.FROM_TIME)
        end_time = ZUtils.str_to_time(TimeSchedule.TO_TIME)

        # Initial list time slots
        time_slots = []

        # Check each working time in queryset
        from_time = ZUtils.str_to_time(ZUtils.float_to_time(attendance.hour_from))
        to_time = ZUtils.str_to_time(ZUtils.float_to_time(attendance.hour_to))
        current_time = from_time
        while current_time < to_time:
            if current_time >= start_time and current_time + slot_duration <= end_time:
                # Round the time to the nearest even hour
                rounded_time = current_time + timedelta(
                    minutes=(TimeSchedule.SLOT_SIZE - current_time.minute)
                    % TimeSchedule.SLOT_SIZE
                )
                time_slots.append(rounded_time)
            current_time += slot_duration

        return set(time_slots)

    @staticmethod
    def _main_process(instance, employee_id, attendance):
        if attendance.day_period == "lunch":
            return

        today = ZUtils.now().date()
        start_date = (
            today
            if not attendance.date_from or attendance.date_from < today
            else attendance.date_from
        )
        end_date = (
            start_date + timedelta(days=TimeSchedule.PERIOD)
            if not attendance.date_to
            else attendance.date_to
        )

        time_slots = []
        # Prepare data for generate task
        slots = ZTimeSlotUtils._process_time_slot_in_attendances(attendance)
        current_date = start_date
        while current_date <= end_date:
            day_of_week = str(parse(str(current_date)).weekday())
            if day_of_week != attendance.dayofweek:
                current_date += timedelta(days=1)
                continue
            time_slots += [
                datetime.combine(current_date, time_slot.time())
                for time_slot in sorted(slots)
            ]
            current_date += timedelta(days=1)
        ZTimeSlotUtils._create_time_slots(instance, employee_id, attendance, time_slots)

    # @staticmethod
    # def generate_time_slots_after_change_resource_calendar_for_employee(
    #     instance, employee_id: int, new_attendances, old_attendance_ids: List[int]
    # ):
    #     # Delete old timeslots
    #     ZTimeSlotUtils.delete_old_time_slots_by_attendances(
    #         instance, employee_id, old_attendance_ids
    #     )
    #     # Create new timeslots
    #     for attendance in new_attendances:
    #         ZTimeSlotUtils._main_process(instance, employee_id, attendance)

    @staticmethod
    def change_time_slots_after_change_resource_attendances(
        instance,
        employee_id: int,
        updated_attendance_ids: List[int],
        created_attendances,
    ):
        # Delete old timeslots
        ZTimeSlotUtils.delete_old_time_slots_by_attendances(
            instance, employee_id, updated_attendance_ids
        )
        # Create new timeslots
        for attendance in created_attendances:
            ZTimeSlotUtils._main_process(instance, employee_id, attendance)

    # @staticmethod
    # def generate_time_slots_after_change_resource_calendar_for_employee_async(
    #     instance, *args
    # ):
    #     ZTools.async_exec(
    #         instance,
    #         ZTimeSlotUtils.generate_time_slots_after_change_resource_calendar_for_employee,
    #         *args,
    #     )

    @staticmethod
    def change_time_slots_after_change_resource_attendances_async(instance, *args):
        ZTools.async_exec(
            instance,
            ZTimeSlotUtils.change_time_slots_after_change_resource_attendances,
            *args,
        )

    @staticmethod
    def get_slots_results(start_times):
        results = {}
        for start_time in start_times:
            booking_date = ZUtils.format_datetime(start_time)
            booking_time = ZUtils.format_datetime(start_time, STANDARD_TIME_FORMAT)
            if booking_date not in results:
                results[booking_date] = [booking_time]
            else:
                results[booking_date].append(booking_time)
        results = [{"booking_date": k, "booking_time": v} for k, v in results.items()]
        return results

    @staticmethod
    def filter_slots_with_doctors_working(
        instance,
        start_at: str,
        end_at: str,
        place_id: int,
    ):
        search_domain = [
            ("start_time", ">=", start_at),
            ("start_time", "<=", end_at),
            ("enable", "=", True),
            ("employee_id.is_doctor", "=", True),
            ("place_id", "=", place_id),
        ]
        return instance.search(search_domain)
