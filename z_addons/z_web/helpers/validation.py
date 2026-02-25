import datetime
import phonenumbers
from odoo import _
from odoo.exceptions import ValidationError
from odoo.addons.z_web.helpers.utils import ZUtils


class ZValidation:
    @staticmethod
    def validate_required_field(values, required_fields):
        for field in required_fields:
            value = values.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                raise ValidationError(f"{field.capitalize()} is required.")

    @staticmethod
    def validate_phone_number(phone_number):
        msg = _("Invalid phone number format, please enter again.")
        try:
            parsed_phone_number = phonenumbers.parse(phone_number, "VN")
            if not phonenumbers.is_valid_number(parsed_phone_number):
                raise ValidationError(msg)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(msg)

    @staticmethod
    def validate_dob(dob):
        if type(dob) == str:
            dob = ZUtils.str_to_date(dob)
        if not dob or dob > datetime.date.today():
            raise ValidationError(_("Birthday must be earlier than the current date."))
