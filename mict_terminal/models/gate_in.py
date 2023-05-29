# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID, exceptions
from odoo.exceptions import ValidationError


class GateIn(models.Model):
    _name = 'gate.in'
    _rec_name = 'container_no'
    _description = 'Gate In'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    container_no = fields.Many2one('container.information', string='Container #', tracking=True)
    gate_in_type = fields.Selection([
        ('booking', 'Terminal Booking'),
        ('train_booking', 'Booking'),
        ('cross_stuff', 'Cross Stuff'),
        ('from_train', 'From Train'),
        ('from_truck', 'From Truck')
    ], string='Gate In Type', tracking=True)
    container_status = fields.Selection([
        ('empty', 'Empty'),
        ('laden', 'Laden')
    ], string='Container Status', tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    port_of_loading = fields.Many2one('pickup.point', string='Port of Loading', tracking=True)
    booking_type = fields.Many2one('booking.type', string='Booking Type', tracking=True)
    remarks = fields.Text(string='Remarks', tracking=True)
    eir_document = fields.Binary(string='Print EIR Document', tracking=True)
    pickup_point_id = fields.Many2one('pickup.point', string='Loading Station', tracking=True)
    port_of_discharge = fields.Many2one('pickup.point', string='Unloading Station', tracking=True)
    container_type_id = fields.Many2one('container.type', string='Container Type', tracking=True)
    gate_in_datetime = fields.Datetime(string='Gate In Date & Time')

    terminal_booking_id = fields.Many2one('terminal.booking', string='Terminal Booking', tracking=True)
    train_booking_id = fields.Many2one('booking.module', string='Booking', tracking=True)
    train_id = fields.Many2one('basic.train', string='Train', tracking=True)
    active = fields.Boolean(string='Active', default=True)
    terminal_id = fields.Many2one('terminal.terminal', string='Terminal', tracking=True)

    seal_no = fields.Char(string='Seal No.', related='container_no.seal_no', tracking=True)
    container_size_id = fields.Many2one('container.size', related='container_no.container_size_id',
                                        string='Container Size', tracking=True)
    container_stage = fields.Selection(string='Container Stage', related='container_no.state', tracking=True)

    def _default_gate_in_stage(self):
        return self.env['gate.in.stage'].search([('stage_name', '=', 'Draft')], limit=1).id

    gate_in_stage_id = fields.Many2one('gate.in.stage',
                                     group_expand='_read_group_gate_in_stage_ids',
                                     string='Gate In Stages',
                                     default=_default_gate_in_stage)

    stage_name = fields.Char(related='gate_in_stage_id.stage_name', string='Stage Name')

    @api.model
    def _read_group_gate_in_stage_ids(self, stages, domain, order):
        # search_domain = [('id', 'in', stages.ids)]
        search_domain = ['|', ('id', 'in', stages.ids), ('id', 'not in', stages.ids)]
        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.onchange('container_no')
    def onchange_container_no(self):
        for rec in self:
            if rec.gate_in_type:
                container_obj = self.env['container.information'].search([
                    ('container_no', '=', rec.container_no.container_no)
                ])
                freight_obj = container_obj.frieght_id
                rec.booking_type = freight_obj.booking_type_id.id
                rec.pickup_point_id = freight_obj.pickup_point_id.id
                rec.port_of_discharge = freight_obj.dropoff_point_id.id
                rec.container_type_id = container_obj.container_type_id.id

    # @api.onchange('gate_in_stage_id')
    # def change_gate_in_stage_id(self):
    def action_gatein(self):
        for rec in self:
            previous_mile_list = []
            rec.gate_in_stage_id = self.env['gate.in.stage'].search([('stage_name', '=', 'Gate IN')]).id
            if rec.gate_in_stage_id.stage_name == 'Gate IN':
                if not rec.gate_in_datetime:
                    raise ValidationError('Gate In Date Time should be present!')
                ## if it is in draft state
                if rec.container_no.state == 'draft':
                    raise ValidationError(
                        _('You cannot gate in as this container is in Draft State!'))
                ## check if container is present in any gate in, then don't proceed to gate in
                if rec.container_no.state not in ['ready_middle_mile']:
                    ## check if no future cargo planning
                    miles = rec.container_no.mile_ids
                    ## if no Middle Mile
                    if not any(mile.mile_type_id.name == 'Middle Mile' for mile in miles):
                        raise ValidationError(
                            _('You cannot gate in as this container has no Middle Mile!'))
                    for mil in miles:
                        current_mile = miles.search([('mile_type_id.name', '=', 'Middle Mile'),
                                                     ('id', '=', mil.id)])
                        previous_miles = miles.search([('id', '<', current_mile.id),
                                                     ('id', 'in', miles.ids),
                                                  ('mile_check', '=', False)], order='id desc')
                        for i in previous_miles:
                            previous_mile_list.append(i)
                        ## check if all previous miles are completed
                        for pre in previous_mile_list:
                            if pre.mile_check == False:
                                raise ValidationError(_('You cannot gate in as this container has its previous miles not completed!'))
                        next_mile = miles.search([('id', '>', current_mile.id),
                                                     ('id', 'in', miles.ids),
                                                  ('mile_check', '=', False)], limit=1)
                        if next_mile:
                            # if next_mile.fcp == False:
                            #     raise ValidationError(
                            #         'It cannot proceed to gate in now. Please complete other miles first!')
                            # else:
                            rec.container_no.state = 'gate_in'
                            ## for making draft of container stacking
                            terminal_obj = self.env['terminal.terminal'].search(
                                [('location_id', '=', rec.pickup_point_id.id)])
                            if terminal_obj:
                                container_stacking_obj = self.env['container.stacking']
                                container_stacking_obj.create({
                                    'container_no': rec.container_no.id,
                                    'terminal_id': terminal_obj.id,
                                    'container_status': rec.container_status
                                })
                ## check if container is present in any gate in, then don't proceed to gate in
                else:
                    rec.container_no.state = 'gate_in'
                    ## for making draft of container stacking
                    terminal_obj = self.env['terminal.terminal'].search([('location_id', '=', rec.pickup_point_id.id)])
                    if terminal_obj:
                        container_stacking_obj = self.env['container.stacking']
                        container_stacking_obj.create({
                            'container_no': rec.container_no.id,
                            'terminal_id': terminal_obj.id,
                            'container_status': rec.container_status
                        })

    def action_print_report(self):
        for rec in self:
            if rec.terminal_booking_id.booking_type_id:
                return self.env.ref('mict_terminal.action_report_equipment_interchange').report_action(self)
            # if rec.terminal_booking_id.booking_type_id.name == 'Domestic':
            #     return self.env.ref('mict_terminal.action_report_equipment_interchange').report_action(self)
            # elif rec.terminal_booking_id.booking_type_id.name == 'Import':
            #     return self.env.ref('mict_terminal.action_report_equipment_interchange_import').report_action(self)
            # elif rec.terminal_booking_id.booking_type_id.name == 'Export':
            #     return self.env.ref('mict_terminal.action_report_equipment_interchange_export').report_action(self)

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(GateIn, self).unlink()