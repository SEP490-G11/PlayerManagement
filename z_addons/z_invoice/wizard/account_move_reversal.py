# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from markupsafe import Markup


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"
    
    reason = fields.Char(string='Reason', required=True)

    def reverse_moves(self, is_modify=False):
        self.ensure_one()
        moves = self.move_ids

        # Create default values.
        partners = moves.company_id.partner_id + moves.commercial_partner_id

        bank_ids = self.env["res.partner.bank"].search(
            [
                ("partner_id", "in", partners.ids),
                ("company_id", "in", moves.company_id.ids + [False]),
            ],
            order="sequence DESC",
        )
        partner_to_bank = {bank.partner_id: bank for bank in bank_ids}
        default_values_list = []
        for move in moves:
            if move.is_outbound():
                partner = move.company_id.partner_id
            else:
                partner = move.commercial_partner_id
            default_values_list.append(
                {
                    "partner_bank_id": partner_to_bank.get(
                        partner, self.env["res.partner.bank"]
                    ).id,
                    **self._prepare_default_reversal(move),
                }
            )

        batches = [
            [
                self.env["account.move"],
                [],
                True,
            ],  # Moves to be cancelled by the reverses.
            [self.env["account.move"], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = default_vals.get("auto_post") != "no"
            is_cancel_needed = not is_auto_post and (
                is_modify or self.move_type == "entry"
            )
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

            moves_to_redirect = self.env["account.move"]
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(
                default_values_list, cancel=is_cancel_needed
            )
            new_moves.write(
                {
                    "misa_state": "draft",
                    "misa_inv_no": False,
                    "misa_inv_code": False,
                    "misa_transaction_id": False,
                    "misa_template_id": False,
                    "misa_url": False,
                    "publish_misa_invoice_date": False
                }
            )
            if is_modify:
                new_moves.write({"is_cancel_misa_inv": False})

            moves._message_log_batch(
                bodies={
                    move.id: Markup("Hóa đơn đã được điều chỉnh giảm bởi %s") % reverse._get_html_link(title=_("hóa đơn"))
                    for move, reverse in zip(moves, new_moves)
                }
            )

            if is_modify:
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    data = move.copy_data(self._modify_default_reverse_values(move))[0]
                    data["line_ids"] = [
                        line
                        for line in data["line_ids"]
                        if line[2]["display_type"]
                        in ("product", "line_section", "line_note")
                    ]
                    # Gán origin_move_id là id của hóa đơn gốc
                    data["origin_move_id"] = move.id
                    data["misa_state"] = "draft"
                    data["misa_inv_no"] = False
                    data["misa_inv_code"] = False
                    data["misa_transaction_id"] = False
                    data["misa_template_id"] = False
                    data["misa_url"] = False
                    data["cancel_attach_move_id"] = new_moves[0].id 
                    data["ref"] = self.reason
                    data["publish_misa_invoice_date"] = False
                    moves_vals_list.append(data)
                new_moves = self.env["account.move"].create(moves_vals_list)
                
                moves._message_log_batch(
                bodies={
                    move.id: Markup("Hóa đơn đã được thay thế bởi %s") % replace._get_html_link(title=_("hóa đơn"))
                    for move, replace in zip(moves, new_moves)
                }
            )

            moves_to_redirect |= new_moves

        self.new_move_ids = moves_to_redirect

        # Create action.
        action = {
            "name": _("Reverse Moves"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
        }
        if len(moves_to_redirect) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": moves_to_redirect.id,
                    "context": {"default_move_type": moves_to_redirect.move_type},
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form",
                    "domain": [("id", "in", moves_to_redirect.ids)],
                }
            )
            if len(set(moves_to_redirect.mapped("move_type"))) == 1:
                action["context"] = {
                    "default_move_type": moves_to_redirect.mapped("move_type").pop()
                }
        return action


    def _modify_default_reverse_values(self, origin_move):
        return {
            'date': self.date
        }