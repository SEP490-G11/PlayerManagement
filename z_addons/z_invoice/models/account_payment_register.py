from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ZAccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"
    
    place_id = fields.Many2one("z_place.place", string="Place", compute="_compute_from_lines", store=True)
    

    @api.depends(
        "can_edit_wizard",
        "source_amount",
        "source_amount_currency",
        "source_currency_id",
        "company_id",
        "currency_id",
        "payment_date",
    )
    def _compute_amount(self):
        for wizard in self:
            if (
                not wizard.journal_id
                or not wizard.currency_id
                or not wizard.payment_date
            ):
                wizard.amount = wizard.amount
            elif wizard.source_currency_id and wizard.can_edit_wizard:
                wizard.amount = (
                    wizard._get_total_amount_in_wizard_currency_to_full_reconcile(
                        wizard._get_batches()[0]
                    )[0]
                )
            else:
                # The wizard is not editable so no partial payment allowed and then, 'amount' is not used.
                wizard.amount = None
                
    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
      
        payment_values = batch_result['payment_values']
        lines = batch_result['lines']
        company = lines[0].company_id._accessible_branches()[:1]
        

        source_amount = abs(sum(lines.mapped('amount_residual')))
        if payment_values['currency_id'] == company.currency_id.id:
            source_amount_currency = source_amount
        else:
            source_amount_currency = abs(sum(lines.mapped('amount_residual_currency')))

        return {
            'company_id': company.id,
            'partner_id': payment_values['partner_id'],
            'partner_type': payment_values['partner_type'],
            'place_id': lines[0].move_id.place_id.id,
            'payment_type': payment_values['payment_type'],
            'source_currency_id': payment_values['currency_id'],
            'source_amount': source_amount,
            'source_amount_currency': source_amount_currency,
        }

    @api.depends('line_ids')
    def _compute_from_lines(self):
        ''' Load initial values from the account.moves passed through the context. '''
        for wizard in self:
            batches = wizard._get_batches()
            batch_result = batches[0]
            wizard_values_from_batch = wizard._get_wizard_values_from_batch(batch_result)

            if len(batches) == 1:
                # == Single batch to be mounted on the view ==
                wizard.update(wizard_values_from_batch)

                wizard.can_edit_wizard = True
                wizard.can_group_payments = len(batch_result['lines']) != 1
            else:
                # == Multiple batches: The wizard is not editable  ==
                wizard.update({
                    'company_id': batches[0]['lines'][0].company_id._accessible_branches()[:1].id,
                    'place_id': batches[0]['lines'][0].move_id.place_id.id,
                    'partner_id': False,
                    'partner_type': False,
                    'payment_type': wizard_values_from_batch['payment_type'],
                    'source_currency_id': False,
                    'source_amount': False,
                    'source_amount_currency': False,
                })

                wizard.can_edit_wizard = False
                wizard.can_group_payments = any(len(batch_result['lines']) != 1 for batch_result in batches)
    


    @api.constrains("amount")
    def _check_amount(self):
        for wizard in self:
            batch_amount = (
                wizard._get_total_amount_in_wizard_currency_to_full_reconcile(
                    wizard._get_batches()[0]
                )[0]
            )
            if wizard.amount > batch_amount:
                raise ValidationError(
                    _(
                        "Amount of payment is greater than amount of due amount's payment"
                    )
                )
    
    
    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals.update(
            {
                "place_id": self.place_id.id,
            }
        )
        return payment_vals
