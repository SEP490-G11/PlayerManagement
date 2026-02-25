from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.z_partner.helpers.constants import PartnerErrorCode
from odoo.addons.z_web.helpers.model_utils import ZModelUtils

class Research(models.Model):
    _name = 'z_partner.research'
    _description = 'Research'
    
    date = fields.Date(index=True, tracking=True, string="Date")
    name = fields.Char(string="Name", tracking=True, required=True)
    color = fields.Selection(
        selection=[
            ('red', 'Red'),
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('orange', 'Orange'),
            ('yellow', 'Yellow'),
            ('purple', 'Purple'),
            ('pink', 'Pink'),
            ('brown', 'Brown'),
            ('black', 'Black'),
            ('white', 'White'),
            ('grey', 'Grey'),
            ('cyan', 'Cyan'),
            ('magenta', 'Magenta'),
            ('lime', 'Lime'),
            ('olive', 'Olive'),
        ],
        string="Color",
        tracking=True,
        required=True
    )
    
    def _get_research_by_id(self, group_id):
        return ZModelUtils.get_record_by_id(
            self, group_id, PartnerErrorCode.RESEARCH_DOES_NOT_EXIST
        )

    @api.model
    def create(self, vals):
        existing_colors = self.search([]).mapped('color')
        if vals.get('color') in existing_colors:
            raise ValidationError("This color is already used.")
        if len(existing_colors) >= 15:
            raise ValidationError("Only 15 colors are allowed.")
        return super(Research, self).create(vals)

    @api.model
    def write(self, vals):
        if 'color' in vals:
            existing_colors = self.search([('id', '!=', self.id)]).mapped('color')
            if vals['color'] in existing_colors:
                raise ValidationError("This color is already used.")
            if len(existing_colors) >= 15:
                raise ValidationError("Only 15 colors are allowed.")
        return super(Research, self).write(vals)
