# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.account.models.account_move import PAYMENT_STATE_SELECTION

from functools import lru_cache


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    place_id = fields.Many2one("z_place.place", string="Cơ sở", readonly=True)

    _depends = {
        "account.move": [
            "name",
            "state",
            "move_type",
            "partner_id",
            "invoice_user_id",
            "fiscal_position_id",
            "invoice_date",
            "invoice_date_due",
            "invoice_payment_term_id",
            "partner_bank_id",
            "place_id",
        ],
        "account.move.line": [
            "quantity",
            "price_subtotal",
            "price_total",
            "amount_residual",
            "balance",
            "amount_currency",
            "move_id",
            "product_id",
            "product_uom_id",
            "account_id",
            "journal_id",
            "company_id",
            "currency_id",
            "partner_id",
        ],
        "product.product": ["product_tmpl_id", "standard_price"],
        "product.template": ["categ_id"],
        "uom.uom": ["category_id", "factor", "name", "uom_type"],
        "res.currency.rate": ["currency_id", "name"],
        "res.partner": ["country_id"],
    }

    @api.model
    def _select(self):
        return """
            SELECT
                line.id,
                line.move_id,
                line.product_id,
                line.account_id,
                line.journal_id,
                line.company_id,
                line.company_currency_id,
                line.partner_id AS commercial_partner_id,
                account.account_type AS user_type,
                move.state,
                move.move_type,
                move.partner_id,
                move.invoice_user_id,
                move.fiscal_position_id,
                move.payment_state,
                move.invoice_date,
                move.invoice_date_due,
                move.place_id AS place_id,
                uom_template.id                                             AS product_uom_id,
                template.categ_id                                           AS product_categ_id,
                line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                                                                            AS quantity,
                -line.balance * currency_table.rate                         AS price_subtotal,
                line.price_total * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                                                                            AS price_total,
                -COALESCE(
                   -- Average line price
                   (line.balance / NULLIF(line.quantity, 0.0)) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                   -- convert to template uom
                   * (NULLIF(COALESCE(uom_line.factor, 1), 0.0) / NULLIF(COALESCE(uom_template.factor, 1), 0.0)),
                   0.0) * currency_table.rate                               AS price_average,
                CASE
                    WHEN move.move_type NOT IN ('out_invoice', 'out_receipt') THEN 0.0
                    ELSE -line.balance * currency_table.rate - (line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0)) * product_standard_price.value_float
                END
                                                                            AS price_margin,
                line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('out_invoice','in_refund','out_receipt') THEN -1 ELSE 1 END)
                    * product_standard_price.value_float                    AS inventory_value,
                COALESCE(partner.country_id, commercial_partner.country_id) AS country_id,
                line.currency_id                                            AS currency_id
        """
