from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users",

    z_birthday = fields.Date("Date of Birth")
    z_mobile_phone = fields.Char("Work Mobile")
    place_ids = fields.Many2many("z_place.place", string="Places", tracking=True)
    job_id = fields.Many2one("hr.job", string="Job Position")

    def create(self, vals):
        z_birthday = vals.get("z_birthday")
        z_mobile_phone = vals.get("z_mobile_phone")
        place_ids = vals.get("place_ids")
        job_id = vals.get("job_id")

        if not z_birthday or not z_mobile_phone or not place_ids or not job_id:
            raise ValidationError(
                _(
                    "It is necessary to provide complete information: date of birth, phone number, job and job position."
                )
            )
        user = super(ResUsers, self.with_context(create_employee=True)).create(vals)
        employee_vals = {
            "name": user.name,
            "birthday": z_birthday,
            "mobile_phone": z_mobile_phone,
            "place_ids": place_ids,
            "job_id": job_id,
            "user_id": user.id
        }
        self.env["hr.employee"].create(employee_vals)
        message_infor = {
            "message": (_("Create employee completed successfully.")),
            "title": (_("Success")),
            "action": None,
        }
        self.env.user.notify_info(**message_infor)
        return user
