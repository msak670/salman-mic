# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID, exceptions
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ContainerStacking(models.Model):
    _name = 'container.stacking'
    _rec_name = 'container_no'
    _description = 'Container Stacking'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    container_no = fields.Many2one('container.information', string='Container #', tracking=True,
                                   domain="[('state', '=', 'gate_in')]")
    coc = fields.Boolean(string='COC', tracking=True)
    terminal_id = fields.Many2one('terminal.terminal', string='Terminal', tracking=True)
    container_status = fields.Selection([
        ('empty', 'Empty'),
        ('laden', 'Laden')
    ], string='Container Status', tracking=True)
    reach_stacker = fields.Char(string='Reach Stacker', tracking=True)
    moves = fields.Char(string='Moves', tracking=True)
    note = fields.Text(string='Note', tracking=True)

    terminal_service_id = fields.Many2one('terminal.service', string='Terminal Services', tracking=True)
    bay_plan_attribute_id = fields.Many2many('bay.plan.attribute', string='Location', domain="[('terminal_id', '=', terminal_id),"
                                                                                            "('terminal_service_id', '=', terminal_service_id),"
                                                                                            "('state', '=', 'available')]", tracking=True)
    active = fields.Boolean(string='Active', default=True)

    seal_no = fields.Char(string='Seal No.', related='container_no.seal_no', tracking=True)
    container_size_id = fields.Many2one('container.size', related='container_no.container_size_id',
                                        string='Container Size', tracking=True)
    container_stage = fields.Selection(string='Container Stage', related='container_no.state', tracking=True)

    def _default_container_stacking_stage(self):
        return self.env['container.stacking.stage'].search([('stage_name', '=', 'Draft')], limit=1).id

    container_stacking_stage_id = fields.Many2one('container.stacking.stage',
                                       group_expand='_read_group_container_stacking_stage_ids',
                                       string='Container Stacking Stages',
                                       default=_default_container_stacking_stage)

    stage_name = fields.Char(related='container_stacking_stage_id.stage_name', string='Stage Name')

    @api.model
    def _read_group_container_stacking_stage_ids(self, stages, domain, order):
        # search_domain = [('id', 'in', stages.ids)]
        search_domain = ['|', ('id', 'in', stages.ids), ('id', 'not in', stages.ids)]
        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.onchange('bay_plan_attribute_id')
    def change_bay_plan_attribute_id(self):
        location_list = []
        for rec in self:
            if rec.bay_plan_attribute_id:
                ## limit locations based on the size of container
                if rec.container_size_id.name == '20':
                    if len(rec.bay_plan_attribute_id) > 1:
                        raise ValidationError(_('You are only allowed to select only one location!'))
                elif rec.container_size_id.name == '40' or rec.container_size_id.name == '45':
                    if len(rec.bay_plan_attribute_id) > 2:
                        raise ValidationError(_('You are only allowed to select only two locations!'))
                ## now for correct sequence of locations
                for loc in rec.bay_plan_attribute_id:
                    location_name = loc.name
                    s = int(location_name[-1]) - 1
                    if location_name:
                        location_list.append(location_name)
                        up_location_name = "" + location_name[:-1] + str(s)
                        bay_plan_attribute_obj = self.env['bay.plan.attribute'].search([('name', '=', up_location_name),
                                                                                        ('terminal_id', '=', rec.terminal_id.id),
                                                                                        ('terminal_service_id', '=', rec.terminal_service_id.id)])
                        container_stacking_obj = self.env['container.stacking'].search([('bay_plan_attribute_id', '=', bay_plan_attribute_obj.id)])
                        if not container_stacking_obj and s != 0 and up_location_name not in location_list:
                            loc = False
                            raise ValidationError(_('' + up_location_name + " should be selected first!"))

    kanban_text = fields.Text(compute='get_kanban_text')

    def get_kanban_text(self):
        for rec in self:
            text = ''
            if rec.bay_plan_attribute_id:
                for location in rec.bay_plan_attribute_id:
                    text += '<center>Container Placed at <b> ' + location.name + '</b></center></b><br/>'
            ## code by nida
            rec.kanban_text = text

    @api.model
    def create(self, vals):
        res = super(ContainerStacking, self).create(vals)
        if vals.get('bay_plan_attribute_id'):
            res.container_stacking_stage_id = self.env['container.stacking.stage'].search([('stage_name', '=', 'Stacked')], limit=1).id
            res.bay_plan_attribute_id.state = 'reserved'
        return res

    @api.onchange('container_no')
    def get_container_details(self):
        for rec in self:
            gate_in_obj = self.env['gate.in'].search([('container_no', '=', rec.container_no.id)])
            if gate_in_obj:
                rec.container_status = gate_in_obj.container_status

    ## in case of auto
    # @api.onchange('container_stacking_stage_id')
    # def change_container_stacking_stage_id(self):
    def action_stacked(self):
        for rec in self:
            rec.container_stacking_stage_id = self.env['container.stacking.stage'].search([('stage_name', '=', 'Stacked')]).id
            if rec.container_stacking_stage_id.stage_name == 'Stacked':
                if rec.bay_plan_attribute_id:
                    locations = self.env['bay.plan.attribute'].search([('id', 'in', rec.bay_plan_attribute_id.ids)])
                    for record in locations:
                        record.state = 'reserved'

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(ContainerStacking, self).unlink()

class TrainLoadingLines(models.Model):
    _inherit = 'train.loading.lines'

    bay_plan_attribute_id = fields.Many2many('bay.plan.attribute', string='Stacking Location')

