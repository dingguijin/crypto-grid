import os
import json
import time
import urllib.parse
from typing import Optional, Dict, Any, List
import logging

from requests import Request, Session, Response
import hmac
import base64
from ciso8601 import parse_datetime

class BitgetClient:
    _ENDPOINT = 'https://api.bitget.com/'

    def __init__(self, api_key=None, api_secret=None, api_pass_phrase=None) -> None:
        self._session = Session()
        
        self._api_key = api_key
        self._api_secret = api_secret
        self._pass_phrase = api_pass_phrase

        self._latest_order_time = int(time.time())

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        http_proxy = os.getenv("http_proxy")
        https_proxy = os.getenv("https_proxy")
        proxies = {}
        if http_proxy and https_proxy:
            proxies = {
                "http": http_proxy,
                "https": https_proxy
            }
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        # add timeout to catch timeout
        response = self._session.send(request.prepare(), proxies=proxies, timeout=3)        
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()

            
        if prepared.body:
            signature_payload += prepared.body
        
        print("Sign payload", signature_payload)
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256')
        signature = signature.hexdigest()
        signature = bytes.fromhex(signature)
        signature = base64.b64encode(signature)
        
        request.headers['ACCESS-TIMESTAMP'] = str(ts)
        request.headers['ACCESS-KEY'] = self._api_key
        request.headers['ACCESS-SIGN'] = signature
        request.headers['ACCESS-PASSPHRASE'] = self._pass_phrase

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            print(json.dumps(data, indent=2))
            if data['msg'] != 'success':
                raise Exception(data)
            return data['data']

    def list_futures(self) -> List[dict]:
        return self._get('futures')

    def list_markets(self) -> List[dict]:
        return self._get('markets')

    def get_market(self, market: str) -> dict:
        return self._get(f'markets/{market}')

    def get_future(self, future: str) -> dict:
        return self._get(f'futures/{future}')

    def get_symbol(self, symbol: str) -> dict:
        return self._get(f'api/v2/spot/public/symbols', {'symbol': symbol})

    def get_ticker(self, symbol: str) -> dict:
        return self._get(f'api/v2/spot/market/tickers', {'symbol': symbol})


    def get_orderbook(self, market: str, depth: int = None) -> dict:
        return self._get(f'markets/{market}/orderbook', {'depth': depth})

    def get_trades(self, market: str) -> List[dict]:
        return self._get(f'markets/{market}/trades')

    def get_klines(self, market: str, resolution: int, start_time: int, end_time: int) -> dict:
        return self._get(f'markets/{market}/candles', {"resolution": resolution, "start_time": start_time, "end_time": end_time })

    def get_future_stats(self, future: str = None) -> dict:
        return self._get(f'futures/{future}/stats')

    def get_funding_rates(self, future: str = None, start_time: float = None, end_time: float = None):
        return self._get(f'funding_rates', {'future': future, 'start_time': start_time, 'end_time': end_time})

    def get_account_info(self) -> dict:
        return self._get(f'api/v2/account/all-account-balance')

    def get_unfilled_orders(self, symbol: str = None) -> List[dict]:
        return self._get(f'api/v2/spot/trade/unfilled-orders', {'symbol': symbol})

    def get_open_trigger_orders(self, market: str = None) -> List[dict]:
        return self._get(f'conditional_orders', {'market': market})

    def get_order_history(self, market: str = None, side: str = None, order_type: str = None, start_time: float = None, end_time: float = None) -> List[dict]:
        return self._get(f'orders/history', {'market': market, 'side': side, 'orderType': order_type, 'start_time': start_time, 'end_time': end_time})
        
    def get_conditional_order_history(self, market: str = None, side: str = None, type: str = None, order_type: str = None, start_time: float = None, end_time: float = None) -> List[dict]:
        return self._get(f'conditional_orders/history', {'market': market, 'side': side, 'type': type, 'orderType': order_type, 'start_time': start_time, 'end_time': end_time})

    def modify_order(
        self, existing_order_id: Optional[str] = None,
        existing_client_order_id: Optional[str] = None, price: Optional[float] = None,
        size: Optional[float] = None, client_order_id: Optional[str] = None,
    ) -> dict:
        assert (existing_order_id is None) ^ (existing_client_order_id is None), \
            'Must supply exactly one ID for the order to modify'
        assert (price is None) or (size is None), 'Must modify price or size of order'
        path = f'orders/{existing_order_id}/modify' if existing_order_id is not None else \
            f'orders/by_client_id/{existing_client_order_id}/modify'
        return self._post(path, {
            **({'size': size} if size is not None else {}),
            **({'price': price} if price is not None else {}),
            ** ({'clientId': client_order_id} if client_order_id is not None else {}),
        })

    def get_conditional_orders(self, market: str = None) -> List[dict]:
        return self._get(f'conditional_orders', {'market': market})

    def place_order(self, symbol: str, side: str, price: float, size: float, order_type: str = 'limit', client_id: str = None) -> dict:
        self._latest_order_time = int(time.time())
        return self._post('api/v2/spot/trade/place-order', {
            'symbol': symbol,
            'side': side,
            'price': str(price),
            'size': str(size),
            'orderType': order_type,
            'force': "gtc",
            'clientOid': client_id
        })

    def place_conditional_order(
        self, market: str, side: str, size: float, type: str = 'stop',
        limit_price: float = None, reduce_only: bool = False, cancel: bool = True,
        trigger_price: float = None, trail_value: float = None
    ) -> dict:
        """
        To send a Stop Market order, set type='stop' and supply a trigger_price
        To send a Stop Limit order, also supply a limit_price
        To send a Take Profit Market order, set type='trailing_stop' and supply a trigger_price
        To send a Trailing Stop order, set type='trailing_stop' and supply a trail_value
        """
        assert type in ('stop', 'take_profit', 'trailing_stop')
        assert type not in ('stop', 'take_profit') or trigger_price is not None, \
            'Need trigger prices for stop losses and take profits'
        assert type not in ('trailing_stop',) or (trigger_price is None and trail_value is not None), \
            'Trailing stops need a trail value and cannot take a trigger price'

        return self._post('conditional_orders',
                          {'market': market, 'side': side, 'triggerPrice': trigger_price,
                           'size': size, 'reduceOnly': reduce_only, 'type': 'stop',
                           'cancelLimitOnTrigger': cancel, 'orderPrice': limit_price})

    def cancel_order(self, symbol: str, order_id: str) -> dict:
        return self._post(f'api/v2/spot/trade/cancel-order', {'order_id': order_id, 'symbol': symbol})

    def get_historial_prices(self, market: str, interval: int, start_time: float, end_time: float) -> List[dict]:
        # GET /markets/{market_name}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}
        # interval is 15, 60, 300, 900, 3600, 14400, 86400, or any multiple of 86400 up to 30*86400
        # start_time timestamp
        return self._get(f'markets/{market}/candles', {'resolution': interval,
                                                      'start_time': start_time,
                                                      'end_time': end_time})

    def get_fills(self, market: str) -> List[dict]:
        return self._get(f'fills', {'market': market, 'start_time': self._latest_order_time - 1})

    def get_balances(self) -> List[dict]:
        return self._get('wallet/balances')

    def get_deposit_address(self, ticker: str) -> dict:
        return self._get(f'wallet/deposit_address/{ticker}')

    def get_positions(self, show_avg_price: bool = False) -> List[dict]:
        return self._get('positions', {'showAvgPrice': show_avg_price})

    def get_position(self, name: str, show_avg_price: bool = False) -> dict:
        return next(filter(lambda x: x['future'] == name, self.get_positions(show_avg_price)), None)

    def get_all_trades(self, market: str, start_time: float = None, end_time: float = None) -> List:
        ids = set()
        limit = 100
        results = []
        while True:
            response = self._get(f'markets/{market}/trades', {
                'end_time': end_time,
                'start_time': start_time,
            })
            deduped_trades = [r for r in response if r['id'] not in ids]
            results.extend(deduped_trades)
            ids |= {r['id'] for r in deduped_trades}
            print(f'Adding {len(response)} trades with end time {end_time}')
            if len(response) == 0:
                break
            end_time = min(parse_datetime(t['time']) for t in response).timestamp()
            if len(response) < limit:
                break
        return results
