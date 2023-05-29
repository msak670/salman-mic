# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID, exceptions


class BayPlanAttribute(models.Model):
    _name = 'bay.plan.attribute'
    _description = 'Bay Plan Attribute'
    _rec_name = 'name'

    terminal_id = fields.Many2one('terminal.terminal', string='Terminal')
    terminal_service_id = fields.Many2one('terminal.service', string='Terminal Services')
    name = fields.Char(string='Name')
    state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved')
    ], string='State', default='available')

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(BayPlanAttribute, self).unlink()