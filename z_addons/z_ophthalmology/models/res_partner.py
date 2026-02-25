# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime

class ZPartner(models.Model):
    _inherit = "res.partner"
    
    research_ids = fields.Many2many(string="Research", comodel_name="z_ophthalmology.research")

    personal_eye_history = fields.Text("Personal eye history")
    personal_overall_health_history = fields.Text("Personal overall health history")
    family_eye_history = fields.Text("Family eye history")
    family_overall_health_history = fields.Text("Family overall health history")
    allergies_history = fields.Text("Allergies history")
    medication_history = fields.Text("Medication history")
    other_notes = fields.Text("Other notes")
    comprehensive_ids = fields.One2many(
        string="Comprehensive",
        comodel_name="z_ophthalmology.comprehensive",
        inverse_name="customer_id",
    )
    date_join_rs = fields.Date(string="Date join research")
    lens_ids = fields.One2many(
        string="Lens",
        comodel_name="z_ophthalmology.lens",
        inverse_name="customer_id",
    )
    re_lens_ids = fields.One2many(
        string="ReLens",
        comodel_name="z_ophthalmology.re_lens",
        inverse_name="customer_id",
    )
    binocular_vision_ids = fields.One2many(
        string="Lens",
        comodel_name="z_ophthalmology.binocular_vision",
        inverse_name="customer_id",
    )
    vision_ids = fields.One2many(
        string="Vision",
        comodel_name="z_ophthalmology.vision",
        inverse_name="customer_id",
    )

    reexamination_date = fields.Date(
        string="Reexamination date",
        compute="_compute_reexamination_date",
        store=True
    )

    @api.depends("comprehensive_ids", "comprehensive_ids.reexamination_date",
                 "lens_ids", "lens_ids.reexamination_date",
                 "re_lens_ids", "re_lens_ids.reexamination_date",
                 "binocular_vision_ids", "binocular_vision_ids.reexamination_date",
                 "vision_ids", "vision_ids.reexamination_date",
    )
    def _compute_reexamination_date(self):
        for record in self:
            all_dates = (
                    record.comprehensive_ids.mapped('reexamination_date') +
                    record.lens_ids.mapped('reexamination_date') +
                    record.re_lens_ids.mapped('reexamination_date') +
                    record.binocular_vision_ids.mapped('reexamination_date') +
                    record.vision_ids.mapped('reexamination_date')
            )
            valid_dates = []
            for d in all_dates:
                if isinstance(d, str):
                    try:
                        valid_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
                    except ValueError:
                        continue
                elif isinstance(d, date):
                    valid_dates.append(d)
            if valid_dates:
                record.reexamination_date = min(valid_dates)
            else:
                record.reexamination_date = False
    
    @api.onchange("research_ids")
    def onchange_research(self):
        if self.research_ids:
            self.research_ids = [(6, 0, self.research_ids[-1].ids)]
        else:
            self.research_ids = False



