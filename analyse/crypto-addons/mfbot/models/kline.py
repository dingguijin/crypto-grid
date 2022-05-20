from odoo import fields, models

class Klines(models.Model):
    _name = 'mfbot.kline'

    _rec_name = "id"

    _inherit = ['mail.thread',
                'mail.activity.mixin']

    exchange = fields.Char('exchange')
    market = fields.Char('market')
    resolution = fields.Integer('Resolution')
    start_time = fields.Datetime('start time')
    end_time = fields.Datetime('end time')
    open = fields.Float('open price')
    high = fields.Float('high price')
    low = fields.Float('low price')
    close = fields.Float('close price')
    volume = fields.Float('volume')
    
    

    
