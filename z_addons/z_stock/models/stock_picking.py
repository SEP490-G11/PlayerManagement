from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import datetime, time


class ZStockPicking(models.Model):
    _inherit = "stock.picking"

    picking_code = fields.Selection(related="picking_type_id.code", store=True)
    
    approver_ids = fields.Many2many(
        "hr.employee", 
        string="Người phê duyệt", 
        tracking=True,
        domain="[]"
    )
    is_not_approver = fields.Boolean(string="Not Approver", compute='_compute_is_not_approver')
    approver_ids_domain = fields.Char(compute='_compute_approver_ids_domain')

    @api.onchange('location_dest_id')
    def onchange_location_dest_id(self):
        self.approver_ids = False

    @api.depends('location_dest_id', 'location_id')
    def _compute_approver_ids_domain(self):
        for rec in self:
            domain = [
                ('job_id.acronym', '=', 'LT-DS'),
            ]
            if rec.location_dest_id and rec.location_dest_id.place_id:
                domain.append(('place_ids', 'in', [rec.location_dest_id.place_id.id]))
            rec.approver_ids_domain = str(domain)


    origin_so_count = fields.Integer(string="Số SO liên quan", compute='_compute_origin_so_count')
    invoice_count = fields.Integer(string="Số hóa đơn", compute='_compute_invoice_count')
    place_id = fields.Many2one("z_place.place", string="Place", require=True, default=lambda self: self._get_default_place_id())
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True, index=True,
        default=lambda self: self._default_picking_type_id())
    
    
    
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        ctx = dict(self.env.context)
        ctx['user_place_ids'] = self.env.user.place_ids.ids
        res["context"] = ctx
        print("ctx",ctx)
        return res

    @api.depends('approver_ids')
    def _compute_is_not_approver(self):
        current_user = self.env.user
        for rec in self:
            # Get all employees linked to current user (usually 1 value)
            user_employees = current_user.employee_ids
            
            # Check if any of user's employees is in the approver list
            rec.is_not_approver = not bool(user_employees & rec.approver_ids)

    def action_confirm(self):
        if self.picking_type_code == 'internal':
            self._check_approver()
        return super(ZStockPicking, self).action_confirm()

    def _check_approver(self):
        for rec in self:
            if not rec.approver_ids:
                raise ValidationError("Bạn cần điền ít nhất một Người phê duyệt điều chuyển.")

    # def _check_approver(self):
    #     for rec in self:
    #         if not rec.approver_id:
    #             raise ValidationError(_("Please select an approver."))
    @api.onchange("location_id", "location_dest_id")
    def _onchange_location_id(self):
        picking_type_code = self.env.context.get("restricted_picking_type_code")
        allowed_place_ids = self.env.user.place_ids.ids
        if (
            picking_type_code == "incoming"
            and not self.location_dest_id.place_id.id in allowed_place_ids
        ):
            raise ValidationError(
                _("You are not allowed to create a picking in this branch.")
            )
        if (
            picking_type_code == "outgoing"
            and not self.location_id.place_id.id in allowed_place_ids
        ):
            raise ValidationError(
                _("You are not allowed to create a picking in this branch.")
            )

    def _get_default_place_id(self):
        current_user = (
            request.session.uid
            and self.env["res.users"].browse(request.session.uid)
            or self.env.user
        )
        return current_user.place_ids[0].id
    
    def _default_picking_type_id(self):
        picking_type_code = self.env.context.get('restricted_picking_type_code')
        user_place_ids = request.session.uid and self.env["res.users"].browse(request.session.uid).place_ids.ids or self.env.user.place_ids.ids
        
        if picking_type_code:
            picking_types = self.env['stock.picking.type'].search([
                ('code', '=', picking_type_code),
                ('company_id', '=', self.env.company.id),
                ('warehouse_id.place_id', 'in', user_place_ids)
            ])
            return picking_types[:1].id
                    
        
        
    def _compute_origin_so_count(self):
        for rec in self:
            so = self.env['sale.order'].search([('name', '=', rec.origin)])
            rec.origin_so_count = len(so)

    def _compute_invoice_count(self):
        for rec in self:
            so = self.env['sale.order'].search([('name', '=', rec.origin)])
            invoices = self.env['account.move'].search([('invoice_origin', 'in', so.mapped('name'))])
            rec.invoice_count = len(invoices)

    def action_view_origin_so(self):
        self.ensure_one()
        so = self.env['sale.order'].search([('name', '=', self.origin)])
        action = self.env.ref('sale.action_orders').read()[0]
        if len(so) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = so.id
        else:
            action['domain'] = [('id', 'in', so.ids)]
        return action

    def action_view_related_invoices(self):
        self.ensure_one()
        so = self.env['sale.order'].search([('name', '=', self.origin)])
        invoices = self.env['account.move'].search([('invoice_origin', 'in', so.mapped('name'))])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        else:
            action['domain'] = [('id', 'in', invoices.ids)]
        return action

    @api.model_create_multi
    def create(self, vals_list):
        current_user = (
            request.session.uid
            and self.env["res.users"].browse(request.session.uid)
            or self.env.user
        )

        if not current_user.place_ids:
            raise ValidationError(_("You are not allowed to create a picking in any branch."))

        for vals in vals_list:
            place_id = None

            if vals.get("return_id") and vals.get("return_id") != False:
                return_picking = self.env["stock.picking"].search([('id', '=', vals["return_id"])], limit=1)
                if return_picking and return_picking.approver_ids:
                    vals["approver_ids"] = [(6, 0, return_picking.approver_ids.ids)]

            if vals.get("location_id") and vals.get("picking_type_code") == 'incoming':
                location = self.env["stock.location"].browse(vals["location_id"])
                place_id = location.place_id
                if place_id not in current_user.place_ids:
                    raise ValidationError(_("You are not allowed to create a picking in this branch."))
            elif vals.get("location_dest_id") and vals.get("picking_type_code") == 'outgoing':
                location = self.env["stock.location"].browse(vals["location_dest_id"])
                place_id = location.place_id
                if place_id not in current_user.place_ids:
                    raise ValidationError(_("You are not allowed to create a picking in this branch."))
            else:
                place_id = current_user.place_ids[0]

            vals["place_id"] = place_id.id

        return super().create(vals_list)
    
    
    def cron_cancel_ready_stock_pick_daily(self):
        today = fields.Date.context_today(self)
        start_time = datetime.combine(today, time(0, 0))
        end_time = datetime.combine(today, time(23, 50))

        stock_pickings = self.env['stock.picking'].search([
            ('state', '=', 'assigned'),
            ('picking_type_code', '=', 'outgoing'),
            ('create_date', '>=', start_time),
            ('create_date', '<=', end_time)
        ])
        for stock_pick in stock_pickings:
            stock_pick.action_cancel()
