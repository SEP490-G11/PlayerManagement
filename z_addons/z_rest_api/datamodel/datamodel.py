from odoo.addons import datamodel
from odoo.addons.datamodel.core import Datamodel
from marshmallow import fields, Schema, validate, ValidationError
from odoo.addons.datamodel import fields


def validate_require(param):
    if not param:
        raise ValidationError("Thiếu thông tin cho trường bắt buộc")


class TokenDatamodel(Datamodel):
    _name = "token.datamodel"

    username = fields.String(validate=validate_require, required=True)
    password = fields.String(validate=validate_require, required=True)

class ListTimeSlot(Datamodel):
    _name = "get.listTimeSlot"

    place_id = fields.Integer(required=False)
    expected_date = fields.String(required=False)

class BookAppointment(Datamodel):
    _name = "book.appointment"

    customer_name = fields.String(validate=validate_require, required=True)
    customer_phonenumber = fields.String(validate=validate_require, required=True)
    customer_gender = fields.String(validate=validate_require, required=True)
    timeslot_id = fields.Integer(validate=validate_require, required=True)
    note = fields.String(required=False,allow_none=True)
    user_id = fields.String(validate=validate_require, required=True)
