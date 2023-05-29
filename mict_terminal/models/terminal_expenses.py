# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class TerminalExpenses(models.Model):
    _name = 'terminal.expenses'
    _description = 'Terminal Expenses'

    gate_out_id = fields.Many2one('gate.out', string='Gate Out')
    name = fields.Char(string="Description")
    location_id = fields.Many2one("pickup.point", string='Location')
    expense_date = fields.Datetime("Date & Time")
    currency_id = fields.Many2one("res.currency", required=False)
    expense_amount = fields.Monetary("Amount", currency_field="currency_id")
    attachment = fields.Binary('Attachment')
    expense_type_id = fields.Many2one('expense.type', string='Expense Type', domain="[('module_type', '=', 'terminal')]")
