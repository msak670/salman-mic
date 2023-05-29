# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID, exceptions
from odoo.exceptions import ValidationError


class GateOut(models.Model):
    _name = 'gate.out'
    _rec_name = 'container_no'
    _description = 'Gate Out'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    container_no = fields.Many2one('container.information', string='Container #', tracking=True)
    train_id = fields.Many2one('basic.train', string='Train #', tracking=True)
    truck_id = fields.Char(string='Truck #', tracking=True)
    reach_stacker = fields.Char(string='Reach Stacker', tracking=True)
    moves = fields.Char(string='Moves', tracking=True)
    out_datetime = fields.Datetime(string='Out Date & Time', tracking=True)
    eir_document = fields.Binary(string='Print EIR Document', tracking=True)
    remarks = fields.Text(string='Remarks', tracking=True)

    train_booking_id = fields.Many2one('booking.module', string='Booking', tracking=True)
    terminal_id = fields.Many2one('terminal.terminal', string='Terminal', tracking=True)

    seal_no = fields.Char(string='Seal No.', related='container_no.seal_no', tracking=True)
    container_size_id = fields.Many2one('container.size', related='container_no.container_size_id',
                                        string='Container Size', tracking=True)
    container_stage = fields.Selection(string='Container Stage', related='container_no.state', tracking=True)

    # expense_ids = fields.Many2many("terminal.expenses",
    #                                relation='terminal_expense_amount_rel',
    #                                column1='terminal_id',
    #                                column2='expense_id',
    #                                string='Expenses')
    expense_ids = fields.One2many("terminal.expenses",
                                   'gate_out_id',
                                   string='Expenses')

    def _default_gate_out_stage(self):
        return self.env['gate.out.stage'].search([('stage_name', '=', 'Draft')], limit=1).id

    gate_out_stage_id = fields.Many2one('gate.out.stage',
                                     group_expand='_read_group_gate_out_stage_ids',
                                     string='Gate Out Stages',
                                     default=_default_gate_out_stage)

    stage_name = fields.Char(related='gate_out_stage_id.stage_name', string='Stage Name')

    @api.model
    def _read_group_gate_out_stage_ids(self, stages, domain, order):
        # search_domain = [('id', 'in', stages.ids)]
        search_domain = ['|', ('id', 'in', stages.ids), ('id', 'not in', stages.ids)]
        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    # @api.onchange('gate_out_stage_id')
    # def change_gate_out_stage_id(self):
    def action_gateout(self):
        mile_list = []
        for rec in self:
            rec.gate_out_stage_id = self.env['gate.out.stage'].search([('stage_name', '=', 'Gate Out')]).id
            if rec.gate_out_stage_id.stage_name == 'Gate Out':
                if not rec.out_datetime:
                    raise ValidationError('Gate Out Date Time should be present!')
                gate_in_obj = self.env['gate.in'].search([('container_no', '=', rec.container_no.id)])
                if gate_in_obj:
                    gate_in_obj.active = False
                    ## also remove from container stacking
                container_stacking_obj = self.env['container.stacking'].search(
                    [('container_no', '=', rec.container_no.id)])
                if container_stacking_obj:
                    ## remove stacking
                    bay_plan_attribute_ids = container_stacking_obj.bay_plan_attribute_id
                    for loc in bay_plan_attribute_ids:
                        loc.state = 'available'
                    container_stacking_obj.active = False
                rec.container_no.state = 'middle_mile_trip'
                ## for making container available
                state = rec.container_no.state
                if state == 'empty_pickup_trip':
                    mile = 'Empty Pickup'
                elif state == 'first_mile_trip':
                    mile = 'First Mile'
                elif state == 'fm_pickup_trip':
                    mile = 'FM Pickup'
                elif state == 'middle_mile_trip':
                    mile = 'Middle Mile'
                elif state == 'last_mile_trip':
                    mile = 'Last Mile'
                elif state == 'long_haul_trip':
                    mile = 'Long Haul'
                elif state == 'short_haul_trip':
                    mile = 'Short Haul'
                elif state == 'lm_dropoff_trip':
                    mile = 'LM Dropoff'
                elif state == 'empty_dropoff_trip':
                    mile = 'Empty Dropoff'

                miles = rec.container_no.mile_ids
                for mil in miles:
                    if mil.mile_type_id.name == mile:
                        current_mile = miles.search([('mile_type_id.name', '=', mile),
                                                     ('id', '=', mil.id),
                                                     ('mile_check', '=', False)])
                        ## making current mile check that it is completed
                        if current_mile:
                            current_mile.mile_check = True
                        next_mile = miles.search([('id', '>', current_mile.id),
                                                  ('id', 'in', miles.ids),
                                                  ('mile_check', '=', False)], limit=1)
                        if next_mile:
                            mile_list.append(next_mile)
                            break

                for mi in mile_list:
                    if mi.mile_type_id.name == 'Empty Pickup':
                        if mi.fcp == True:
                            rec.container_no.state = 'empty_pickup_trip'
                        else:
                            rec.container_no.state = 'ready_empty_pickup'
                    elif mi.mile_type_id.name == 'FM Pickup':
                        if mi.fcp == True:
                            rec.container_no.state = 'fm_pickup_trip'
                        else:
                            rec.container_no.state = 'ready_fm_pickup'
                    elif mi.mile_type_id.name == 'First Mile':
                        if mi.fcp == True:
                            rec.container_no.state = 'first_mile_trip'
                        else:
                            rec.container_no.state = 'ready_first_mile'
                    elif mi.mile_type_id.name == 'Middle Mile':
                        if mi.fcp == True:
                            rec.container_no.state = 'middle_mile_trip'
                        else:
                            rec.container_no.state = 'ready_middle_mile'
                    elif mi.mile_type_id.name == 'Last Mile':
                        if mi.fcp == True:
                            rec.container_no.state = 'last_mile_trip'
                        else:
                            rec.container_no.state = 'ready_last_mile'
                    elif mi.mile_type_id.name == 'Long Haul':
                        if mi.fcp == True:
                            rec.container_no.state = 'long_haul_trip'
                        else:
                            rec.container_no.state = 'ready_long_haul'
                    elif mi.mile_type_id.name == 'Short Haul':
                        if mi.fcp == True:
                            rec.container_no.state = 'short_haul_trip'
                        else:
                            rec.container_no.state = 'ready_short_haul'
                    elif mi.mile_type_id.name == 'LM Dropoff':
                        if mi.fcp == True:
                            rec.container_no.state = 'lm_dropoff_trip'
                        else:
                            rec.container_no.state = 'ready_lm_dropoff'
                    elif mi.mile_type_id.name == 'Empty Dropoff':
                        if mi.fcp == True:
                            rec.container_no.state = 'empty_dropoff_trip'
                        else:
                            rec.container_no.state = 'ready_empty_dropoff'
                mile_list = []

                ref = ''
                ## make journal entry from expenses
                if self.expense_ids:
                    # create a dictionary to store the total amount and fd_lines for each expense type
                    expense_totals = {}
                    for expense in self.expense_ids:
                        if expense.expense_type_id in expense_totals:
                            expense_totals[expense.expense_type_id]['total_amount'] += expense.expense_amount
                            expense_totals[expense.expense_type_id][
                                'fd_lines'] = expense.expense_type_id.fd_lines
                        else:
                            expense_totals[expense.expense_type_id] = {'total_amount': expense.expense_amount,
                                                                       'fd_lines': expense.expense_type_id.fd_lines}

                    if self.terminal_id:
                        ref += 'Terminal: ' + str(self.terminal_id.name) + ', '
                    if self.train_id:
                        ref += 'Train: ' + str(self.train_id.name) + ', '
                    if self.truck_id:
                        ref += 'Truck #: ' + str(self.truck_id) + ', '
                    if self.train_booking_id:
                        ref += 'Booking: ' + str(self.train_booking_id.name) + ', '
                    if self.container_no:
                        ref += 'Container: ' + str(self.container_no.name) + ', '
                    if self.container_size_id:
                        ref += 'Container Size: ' + str(self.container_size_id.name) + ', '
                    if self.reach_stacker:
                        ref += 'Reach Stacker: ' + str(self.reach_stacker) + ', '
                    if self.moves:
                        ref += 'Moves: ' + str(self.moves) + ', '
                    if self.remarks:
                        ref += 'Remarks: ' + str(self.remarks) + ', '

                    journal_entry_obj = self.env['account.move']
                    for expense_type, data in expense_totals.items():
                        debit_account_id = expense_type.debit.id
                        credit_account_id = expense_type.credit.id
                        total_amount = data['total_amount']
                        fd_lines = data['fd_lines']

                        vals = {
                            'ref': ref,
                            'journal_id': self.env['account.journal'].search(
                                [('name', '=', 'Miscellaneous Operations')],
                                limit=1).id,
                            'line_ids': [(0, 0, {
                                'account_id': debit_account_id,
                                'name': expense_type.name,
                                'debit': total_amount,
                                'credit': 0,
                            }), (0, 0, {
                                'account_id': credit_account_id,
                                'name': expense_type.name,
                                'debit': 0,
                                'credit': total_amount,
                            })],
                        }
                        for fd in fd_lines:
                            vals.update({'fd_lines': [(0, 0, {
                                'segment': fd.segment.id,
                                'status': fd.status.id,
                                'region': fd.region.id,
                                'city': fd.city.id,
                                'loading_points': fd.loading_points.id,
                                'analytic_account_id': fd.analytic_account_id.id
                            })]})

                        journal_entry = journal_entry_obj.create(vals)

    @api.onchange('container_no')
    def _onchange_container_id(self):
        container_list = []
        container_stacking_obj = self.env['container.stacking'].search([('container_stacking_stage_id.stage_name', '=', 'Stacked')])
        if container_stacking_obj:
            for rec in container_stacking_obj:
                container_list.append(rec.container_no.id)
        domain = [('id', 'in', container_list)]
        return {'domain': {'container_no': domain}}

    @api.onchange('container_no')
    def get_container_details(self):
        for rec in self:
            gate_in_obj = self.env['gate.in'].search([('container_no', '=', rec.container_no.id)])
            if gate_in_obj:
                rec.train_id = gate_in_obj.train_id.id
                rec.terminal_id = gate_in_obj.terminal_id.id
                rec.train_booking_id = gate_in_obj.train_booking_id.id

    def unlink(self):
        if self.env.user.has_group('mict_finance.group_delete_restriction'):
            raise exceptions.UserError("You are not allowed delete this record!")
        else:
            return super(GateOut, self).unlink()