# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID

class BookingContainer(models.Model):
    _name = 'booking.container'
    _rec_name = 'container_id'
    _description = 'Container Stacking'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    container_id = fields.Many2one('container.information', string='Container No.', tracking=True)
    coc = fields.Boolean(string='COC', tracking=True)
    container_size_id = fields.Many2one('container.size', related='container_id.container_size_id',
                                        string='Container Size', tracking=True)
    container_type_id = fields.Many2one('container.type', related='container_id.container_type_id',
                                        string='Container Type', tracking=True)
    seal_no = fields.Char(related='container_id.seal_no', string='Seal No.', tracking=True)
    cro_no = fields.Char(related='container_id.cro_no', string='CRO No.', tracking=True)
    weight = fields.Float(related='container_id.weight', string='Weight')

    mile_ids = fields.One2many('miles.miles', related='container_id.mile_ids',
                               string='Miles', tracking=True)