from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.z_partner.helpers.constants import PartnerErrorCode
from odoo.addons.z_web.helpers.model_utils import ZModelUtils

class Research(models.Model):
    _name = 'z_ophthalmology.research'
    _description = 'Research'
    
    name = fields.Char(string="Name", tracking=True, required= True)
    color_tag = fields.Integer("Color Tag", required= True)
    
    def _get_research_by_id(self, group_id):
        return ZModelUtils.get_record_by_id(
            self, group_id, PartnerErrorCode.RESEARCH_DOES_NOT_EXIST
        )

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if len(self.search([("name", "=", rec.name)])) > 1:
                raise ValidationError(_("This name is already used."))

    @api.model
    def create(self, vals):
        existing_colors = self.search([]).mapped('color_tag')
        if vals.get('color_tag') in existing_colors:
            raise ValidationError(_("This color is already used."))
        if len(existing_colors) >= 15:
            raise ValidationError(_("Only 15 colors are allowed."))
        return super(Research, self).create(vals)

    @api.model
    def write(self, vals):
        if 'color_tag' in vals:
            existing_colors = self.search([('id', '!=', self.id)]).mapped('color_tag')
            if vals['color_tag'] in existing_colors:
                raise ValidationError(_("This color is already used."))
            if len(existing_colors) >= 15:
                raise ValidationError(_("Only 15 colors are allowed."))
        return super(Research, self).write(vals)
