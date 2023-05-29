# -*- coding: utf-8 -*-
import itertools

from odoo import fields, models, api, _, SUPERUSER_ID, exceptions


class BayPlan(models.Model):
    _name = 'bay.plan'
    _rec_name = 'terminal_id'
    _description = 'Bay Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    terminal_id = fields.Many2one('terminal.terminal', string='Terminal',
                                  tracking=True)
    total_teus = fields.Integer(string='Total Terminal Capacity (in TEUs)', tracking=True, readonly=True)
    total_area_acres = fields.Float(string='Total Area (Acres)', tracking=True, readonly=True)

    bay_plan_line_ids = fields.One2many('bay.plan.line', 'bay_plan_id',
                                        string='Bay Plan Line IDs', tracking=True)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        row = None
        col = None
        stack = None
        nums = ['R','C','S']
        combinations = vals.get('bay_plan_line_ids')
        for r in combinations:
            row = r[2].get('row')
            col = r[2].get('col')
            stack = r[2].get('tier')
            row = int(row)
            col = int(col)
            stack = int(stack)
            combination = self.combMatrix(nums, row, col, stack)
            for comb in combination:
                self.env['bay.plan.attribute'].create({
                    'terminal_id': vals.get('terminal_id'),
                    'terminal_service_id': r[2].get('terminal_service_id'),
                    'name': comb
                })
        return res

    def combMatrix(self, m, row, col, stack):
        r = 1
        c = 1
        s = 1
        combination_list = []
        while r <= row:
            c = 1
            while c <= col:
                s = 1
                while s <= stack:
                    combination = ("" + m[0] + str(r) + m[1] + str(c) + m[2] + str(s))
                    combination_list.append(combination)
                    s += 1
                c += 1
            r += 1
        return combination_list

    @api.onchange('terminal_id')
    def get_total_teus_area(self):
        area = 0
        teus = 0
        for rec in self:
            if rec.terminal_id:
                terminal_service_lines_obj = rec.terminal_id.terminal_service_line_ids
                if terminal_service_lines_obj:
                    for ter in terminal_service_lines_obj:
                        area += ter.area_acres
                        teus += ter.terminal_capacity_teus
            rec.total_area_acres = area
            rec.total_teus = teus

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(BayPlan, self).unlink()


class BayPlanLine(models.Model):
    _name = 'bay.plan.line'
    _description = 'Bay Plan'

    bay_plan_id = fields.Many2one('bay.plan', string='Bay Plan ID')
    self_ids = fields.Char(string='IDs')
    terminal_service_id = fields.Many2one('terminal.service', string='Terminal Services')
    name = fields.Char(string='Name')
    row = fields.Char('R')
    col = fields.Char('C')
    tier = fields.Char('S')

