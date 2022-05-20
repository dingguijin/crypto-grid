from odoo import fields, models

class Pnl(models.Model):
    _name = 'mfbot.pnl'

    _rec_name = "id"

    _inherit = ['mail.thread',
                'mail.activity.mixin']

    strategy_id = fields.Many2one('mfbot.strategy', '策略')
    user_id = fields.Many2one('res.users', related='strategy_id.user_id', string='客户', readonly=True)
    sale_id = fields.Many2one('res.users', related='strategy_id.sale_id', string='推荐人', readonly=True)
        
    market = fields.Selection([
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('ADA', 'ADA')], 
        related='strategy_id.market', string='币种', required=True)
    
    price = fields.Float('当前价格', readonly=True)

    side = fields.Selection([
        ('BUY', 'BUY'),
        ('SELL', 'SELL')], 
        string='side', required=True)

    size = fields.Float('持仓量', readonly=True)

    break_even_price = fields.Float('成本价格', readonly=True)
    liquidation_price = fields.Float('清算价格', readonly=True)

    pnl = fields.Float('盈亏', readonly=True)
    date = fields.Datetime('日期', readonly=True)

