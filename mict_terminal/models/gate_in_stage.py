# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, exceptions


class GateInStage(models.Model):
    _name = 'gate.in.stage'
    _description = 'Gate In Stage'
    _rec_name = 'stage_name'

    stage_name = fields.Char('Stage Name')
    sequence = fields.Integer('Gate In Stage Sequence', default=10)

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(GateInStage, self).unlink()