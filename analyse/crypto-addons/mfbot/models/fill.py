from odoo import fields, models

class Fill(models.Model):
    _name = 'mfbot.fill'
    _rec_name = "id"
    _order = "date desc"

    _inherit = ['mail.thread',
                'mail.activity.mixin']

    strategy_id = fields.Many2one('mfbot.strategy', '策略')
    strategy = fields.Selection([
        ('GRID', 'GRID'),
        ('FACTOR', 'FACTOR')],
        string='策略', related='strategy_id.strategy')

    user_id = fields.Many2one('res.users', related='strategy_id.user_id', string='客户', readonly=True)
    sale_id = fields.Many2one('res.users', related='strategy_id.sale_id', string='推荐人', readonly=True)
    
    market = fields.Selection([
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('ADA', 'ADA')], 
        related='strategy_id.market', string='币种', required=True)

    side = fields.Selection([
        ('BUY', 'BUY'),
        ('SELL', 'SELL')], 
        string='交易方向', required=True)

    size = fields.Float('size', readonly=True)
    price = fields.Float('price', readonly=True)

    pnl = fields.Float('总盈亏', readonly=True)
    balance = fields.Float('总余额', readonly=True)
    position = fields.Float('总仓位', readonly=True)
    
    break_even_price = fields.Float('成本价格', readonly=True)
    liquidation_price = fields.Float('清算价格', readonly=True)

    date = fields.Datetime('日期', readonly=True)

    long_short = fields.Selection([
        ('LONG', 'LONG'),
        ('SHORT', 'SHORT'),
        ('BOTH', 'BOTH')],                                  
        string='多空偏好', required=False)

    position_action = fields.Selection([
        ('OPEN', 'OPEN'),
        ('CLOSE', 'CLOSE')], 
        string='仓位动作', required=False)

    open_reason = fields.Char(string='开仓信号', required=False)
    close_reason = fields.Char(string='平仓信号', required=False)

