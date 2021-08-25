# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    
    _inherit = 'account.move'

    def action_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        #if any(not move.is_invoice(include_receipts=True) for move in self):
        #    raise UserError(_("Only invoices could be printed."))

        self.filtered(lambda inv: not inv.invoice_sent).write({'invoice_sent': True})
        if self.user_has_groups('account.group_account_invoice'):
            return self.env.ref('account.account_invoices').report_action(self)
        else:
            return self.env.ref('account.account_invoices_without_payment').report_action(self)
        
        
    def _get_report_base_filename(self):
        #if any(not move.is_invoice() for move in self):
        #    raise UserError(_("Only invoices could be printed."))
        return self._get_move_display_name()