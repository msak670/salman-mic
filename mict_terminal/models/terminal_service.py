# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID, exceptions


class TerminalService(models.Model):
    _name = 'terminal.service'
    _rec_name = 'name'
    _description = 'Terminal Service'

    name = fields.Char(string='Name', required=True)
    # area_acres = fields.Float(string='Area (Acres)')
    # terminal_capacity_teus = fields.Float(string='Terminal Capacity (in TEUs)')

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(TerminalService, self).unlink()

