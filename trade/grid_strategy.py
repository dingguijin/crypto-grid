import time
import datetime
import logging
import requests

from trade_side import TradeSide
from trade_type import TradeType

class GridStrategy():
    def __init__(self, grid_exchange, market, size, open_price, grid_gap_ratio, strategy_id, stop_price):
        self.market = market
        self.size = size
        
        self.stop_price = stop_price
        self.grid_exchange = grid_exchange
        self.open_price = open_price
        self.grid_gap_ratio = grid_gap_ratio
        self.base_grid_gap_ratio = grid_gap_ratio

        self.placed_orders = []
        self.position_sizes = []

        self.sleep_seconds = 0
        self.grid_step_ratio_sleep = 0

        self.update_odoo_pnl_sleep = 0
        self.update_odoo_pnl_time = datetime.datetime.now()

        self.strategy_id = strategy_id
        _precision = self.grid_exchange.get_float_precision(self.open_price.get("bid_price"))
        self.precision = _precision
        return

    def open_initial_position(self):
        _buy_price = self.open_price.get("bid_price")*(1.0-self.grid_gap_ratio)
        _sell_price = self.open_price.get("ask_price")*(1.0+self.grid_gap_ratio)

        _buy_price = self.grid_exchange.convert_to_precision(_buy_price, self.precision)
        _sell_price = self.grid_exchange.convert_to_precision(_sell_price, self.precision)

        self.place_grid_buy_order(_buy_price)
        self.place_grid_sell_order(_sell_price)
        return

    def get_next_sell_price(self, position_price):
        _sell_price = position_price.get("ask_price")*(1.0+self.grid_gap_ratio)
        _sell_price = self.grid_exchange.convert_to_precision(_sell_price, self.precision)
        return _sell_price

    def get_next_buy_price(self, position_price):
        _buy_price = position_price.get("bid_price")*(1.0-self.grid_gap_ratio)
        _buy_price = self.grid_exchange.convert_to_precision(_buy_price, self.precision)
        return _buy_price

    def place_grid_sell_order(self, price, order_type=TradeType.LIMIT):
        placed_order = None
        if order_type == TradeType.LIMIT:
            placed_order = self.grid_exchange.place_limit_order(self.market, self.size, "sell", price)
        if order_type == TradeType.MARKET:
            placed_order = self.grid_exchange.place_market_order(self.market, self.size, "sell", price)
        if placed_order != None:
            self.placed_orders.append(placed_order)
        return placed_order

    def place_grid_buy_order(self, price, order_type=TradeType.LIMIT):
        trade_side = "buy"
        placed_order = None
        if order_type == TradeType.LIMIT:
            placed_order = self.grid_exchange.place_limit_order(self.market, self.size, trade_side, price)
        if order_type == TradeType.MARKET:
            placed_order = self.grid_exchange.place_market_order(self.market, self.size, trade_side, price)
        if placed_order != None:
            self.placed_orders.append(placed_order)
        return placed_order

    def _find_lastest_fill_orders(self, fills):
        order_ids = set()
        for fill in fills:
            order_ids.add(fill.get("order_id"))
        filled_orders = list(filter(lambda x: x.get("order_id") in order_ids, self.placed_orders))
        unfilled_orders = list(filter(lambda x: x.get("order_id") not in order_ids, self.placed_orders))
        return filled_orders, unfilled_orders
    
    def on_fills_update(self, fills):
        return self.placed_orders

    def cancel_orders(self, cancel_ids):
        if not cancel_ids:
            return
        logging.info("cancel all unfilled orders: %s" % cancel_ids)
        cancelled_ids = self.grid_exchange.cancel_orders(self.market, cancel_ids)
        return cancelled_ids

    def replace_grid_orders(self):
        self.sleep_seconds = 0

        last_price = self.grid_exchange.get_last_trade(self.market)
        buy_price = self.get_next_buy_price(last_price)
        sell_price = self.get_next_sell_price(last_price)

        if self.stop_price and sell_price > self.stop_price:
            print("Sell price > stop_price", sell_price, self.stop_price)
            return

        logging.info("get filled: %s buy: %s, sell: %s" % (last_price, buy_price, sell_price))
        # FIXME: if next price overflow the pricelist, dangerous!!!
        if buy_price != None:
            self.place_grid_buy_order(buy_price)
        if sell_price != None:
            self.place_grid_sell_order(sell_price)
        return
        
    def sleep_strategy(self, seconds):
        time.sleep(seconds)
        self.sleep_seconds = self.sleep_seconds + seconds
        self.grid_step_ratio_sleep = self.grid_step_ratio_sleep + seconds
        self.update_odoo_pnl_sleep = self.update_odoo_pnl_sleep + seconds
        return self.sleep_seconds

    def check_wrong_orders(self):
        # reset sleep seconds when place order
        if self.sleep_seconds < 5.0:
            return
        self.sleep_seconds = 0

        time.sleep(0.4)
        open_orders = self.grid_exchange.get_open_orders(self.market) or []
        #prices = []
        if len(open_orders) == 2:
            #prices.append(float(open_orders[0].get("priceAvg")))
            #prices.append(float(open_orders[1].get("priceAvg")))
            logging.info("orders is right 2, keep waiting %s" % self.sleep_seconds)
            return

        logging.error("open orders != 2 %s, waiting: %s" % (open_orders, self.sleep_seconds))
        if open_orders:
            cancel_ids = list(map(lambda x: x.get("order_id"), open_orders))
            time.sleep(0.4)
            self.cancel_orders(cancel_ids)
        # reinit
        self.placed_orders = []
        self.replace_grid_orders()
        return
    
    def caculate_grid_step_ratio(self):
        if True:
            self.grid_gap_ratio = self.base_grid_gap_ratio
            return

        # comments other code
        if self.grid_step_ratio_sleep < 60.0:
            return
        self.grid_step_ratio_sleep = 0

        positions = self.grid_exchange.get_open_positions(self.market)
        if not positions:
            return

        logging.info("positions ... %s" % positions)
        positions = list(filter(lambda x: x.get("size") > 0.0, positions))
        if not positions:
            return

        position = positions[0]
        logging.info("position ... %s" % position)
        # if position.get("pnl") > 0.0:
        #     return

        account_balance = self.grid_exchange.get_account_balance()
        if not account_balance:
            logging.info("no account balance")
            return

        total_value = account_balance.get("total_value")
        total_position = account_balance.get("total_position")

        logging.info("account balance: %s" % account_balance)
        
        # less than 80%
        if total_value * 0.80 >= total_position:
            self.grid_gap_ratio = self.base_grid_gap_ratio
            logging.info("grid gap ratio 1x %s" % self.grid_gap_ratio)
            return

        # between 80% - 100%
        if total_value * 0.80 < total_position and total_value >= total_position:
            self.grid_gap_ratio = 1.5*self.base_grid_gap_ratio
            logging.info("grid gap ratio 2x %s" % self.grid_gap_ratio)
            return

        # between 100% - 200%
        if total_value < total_position and total_value*2.0 >= total_position:
            self.grid_gap_ratio = 2.0*self.base_grid_gap_ratio
            logging.info("grid gap ratio 4x %s" % self.grid_gap_ratio)
            return

        # larger than 200%
        if total_value*2.0 < total_position:
            self.grid_gap_ratio = 3.0*self.base_grid_gap_ratio
            logging.info("grid gap ratio 8x %s" % self.grid_gap_ratio)
            return

        logging.info("keep grid gap ratio ?x %s" % self.grid_gap_ratio)
        return

    def update_odoo_pnl(self):
        if self.strategy_id == -1:
            # ignore trade record
            return

        if self.update_odoo_pnl_sleep < 36.0:
            return
        self.update_odoo_pnl_sleep = 0.0
        
        # now = datetime.datetime.now()
        # if now.hour != 0:
        #     logging.info("skip now: %s" % now)
        #     return

        positions = self.grid_exchange.get_open_positions(self.market)
        if not positions:
            return

        positions = list(filter(lambda x: x.get("size") > 0.0, positions))
        if not positions:
            return

        position = positions[0]
        if position.get("pnl") > 0.0:
            return

        position["price"] = position["entry_price"]

        account_balance = self.grid_exchange.get_account_balance()
        if not account_balance:
            logging.info("no account balance")
            return

        # total_value = account_balance.get("total_value")

        data = {
            "strategy_id": self.strategy_id,
            "balance": account_balance,
            "position": position
        }
        rest = requests.post("http://localhost:8069/cryptocurrency/update_pnl", json=data)
        logging.info("res %s for %s" % (res.text, data))

    def create_odoo_fill(self, fill):
        account_balance = self.grid_exchange.get_account_balance()
        if not account_balance:
            logging.info("no account balance")
            return

        balance = account_balance.get("total_value")

        positions = self.grid_exchange.get_open_positions(self.market)
        position = {}
        if positions:
            position = positions[0]

        logging.info("fill send: %s" % fill)

        data = {
            "strategy_id": self.strategy_id,
            "size": fill.get("size"),
            "price": fill.get("price"),
            "side": fill.get("side"),
            "balance": balance,
            "position": position.get("net_size"),
            "break_even_price": position.get("break_even_price"),
            "liquidation_price": position.get("liquidation_price")
        }
        res = requests.post("http://localhost:8069/cryptocurrency/create_fill", json=data)
        logging.info("res %s for %s" % (res.text, data))


