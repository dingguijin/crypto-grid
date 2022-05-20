from odoo import fields, models, api

class Stategy(models.Model):
    _name = 'mfbot.strategy'

    _inherit = ['mail.thread',
                'mail.activity.mixin']

    _rec_name = "id"

    exchange = fields.Selection([
        ('FTX', "FTX"),
        ('DYDX', "DYDX")], 
        default='FTX', string='交易所', required=True, help='Select a exchange.')

    market = fields.Selection([
        ('BTC', "BTC"),
        ('ETH', "ETH"),
        ('GRT', "GRT"),
        ('DOGE', "DOGE"),
        ('ADA', "ADA")], 
        default='BTC', string='币种', required=True, help='Select a coin.')

    invest = fields.Float('初始投入', track_visibility='onchange')
    
    balance = fields.Float('总余额', readonly=True)
    pnl = fields.Float('总盈亏', compute='_compute_pnl', readonly=True)
    position = fields.Float('总仓位', readonly=True)

    strategy = fields.Selection([
        ('GRID', 'GRID'),
        ('FACTOR', 'FACTOR')],
        default='GRID', string='策略', required=True, help='Select a strategy.')

    grid_gap = fields.Float('网格间隔', track_visibility='onchange')
    grid_size = fields.Float('网格每手大小', track_visibility='onchange')
    
    user_id = fields.Many2one('res.users', string='客户')
    sale_id = fields.Many2one('res.users', string='推荐人')

    platform_profit_ratio = fields.Float('平台盈利比例', track_visibility='onchange')
    sale_profit_ratio = fields.Float('推荐人盈利比例', track_visibility='onchange')
    customer_profit_ratio = fields.Float('客户盈利比例', track_visibility='onchange')

    platform_profit = fields.Float('平台盈利', compute='_compute_platform_profit', readonly=True)
    sale_profit = fields.Float('推荐人盈利', compute='_compute_sale_profit', readonly=True)
    customer_profit = fields.Float('客户盈利', compute='_compute_customer_profit', readonly=True)

    subaccount = fields.Char('交易子账号')

    fill_lines = fields.One2many('mfbot.fill', 'strategy_id', string='成交列表')
    pnl_lines = fields.One2many('mfbot.pnl', 'strategy_id', string='盈亏列表')
    misc = fields.Text('其它')

    start_date = fields.Datetime('启动日期', track_visibility='onchange')

    able_to_modify = fields.Boolean('Able to modify', compute='_compute_able_to_modify')
    
    @api.model
    def create(self, vals):
        if vals.get("invest"):
            vals["balance"] = vals.get("invest")
        return super().create(vals)

    @api.depends('invest', 'balance')
    def _compute_pnl(self):
        for record in self:
            if record.balance == 0.0:
                record.pnl = 0.0
            else:
                record.pnl = record.balance - record.invest

    @api.depends('pnl', 'platform_profit_ratio')
    def _compute_platform_profit(self):
        for record in self:
            if record.pnl <= 0.0:
                record.platform_profit = 0.0
            else:
                record.platform_profit = record.platform_profit_ratio * record.pnl

    @api.depends('pnl', 'sale_profit_ratio')
    def _compute_sale_profit(self):
        for record in self:
            if record.pnl <= 0.0:
                record.sale_profit = 0.0
            else:
                record.sale_profit = record.sale_profit_ratio * record.pnl

    @api.depends('pnl', 'customer_profit_ratio')
    def _compute_customer_profit(self):
        for record in self:
            if record.pnl <= 0.0:
                record.customer_profit = 0.0
            else:
                record.customer_profit = record.customer_profit_ratio * record.pnl

    def _compute_able_to_modify(self):
        for record in self:
            record.able_to_modify = self.env.user.has_group('mfbot.group_mfbot_manager')
