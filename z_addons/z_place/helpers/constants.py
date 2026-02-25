from odoo import _


class PlaceErrorCode:
    PLACE_DOES_NOT_EXIST = "PLACE_DOES_NOT_EXIST"


OBJECT_IS_NOT_EXIST = _("{} does not exist, please reload this page to continue")
PLACE_ERROR_MESSAGE_DICT = {
    PlaceErrorCode.PLACE_DOES_NOT_EXIST: OBJECT_IS_NOT_EXIST.format(_("Place")),
}
