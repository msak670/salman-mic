# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID, exceptions


class TerminalTerminal(models.Model):
    _name = 'terminal.terminal'
    _rec_name = 'name'
    _description = 'Terminal'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    city = fields.Char(string='City', tracking=True)
    terminal_service_details = fields.Text(string='Terminal Service Details', tracking=True)
    terminal_capacity_teus = fields.Integer(string='Terminal Capacity (in TEUs)', tracking=True)
    terminal_service_ids = fields.Many2many('terminal.service', string='Terminal Services', tracking=True)
    area_acres = fields.Float(string='Area (Acres)', tracking=True)

    terminal_service_line_ids = fields.One2many('terminal.service.line', 'terminal_id',
                                                 string='Terminal Services Lines', tracking=True)
    location_id = fields.Many2one('pickup.point', string='Location', tracking=True,
                                  domain="[('location_type_id', '=', 'Terminal')]")

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(TerminalTerminal, self).unlink()

class TerminalServiceLine(models.Model):
    _name = 'terminal.service.line'
    _rec_name = 'terminal_service_id'
    _description = 'Terminal Service Line'

    terminal_id = fields.Many2one('terminal.terminal', string='Terminal ID')
    terminal_service_id = fields.Many2one('terminal.service', string='Name')
    area_acres = fields.Float(string='Area (Acres)')
    terminal_capacity_teus = fields.Float(string='Terminal Capacity (in TEUs)')