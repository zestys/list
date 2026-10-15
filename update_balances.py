#!/usr/bin/env python3
"""Snapshot native SOL balances for known Pump wallets; no keys or signatures needed."""
import argparse
import json
import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent


def write(path, value):
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temp.replace(path)


def decorate(root, balances):
    for path in [root / 'master_handles.json', root / 'search_handles.json', *sorted((root / 'alphabetized').glob('*.json'))]:
        payload = json.loads(path.read_text())
        for row in payload['handles']:
            row['wallet_balances'] = [balances.get(address, {'address': address, 'status': 'unavailable'})
                                      for address in row.get('wallet_addresses', [])]
        write(path, payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rpc-url', default=os.environ.get('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com'))
    parser.add_argument('--delay', type=float, default=1.1, help='Seconds between batches (default 1.1)')
    parser.add_argument('--max-age-hours', type=float, default=1, help='Reuse recent successful lookups')
    args = parser.parse_args()
    if args.delay < 0 or args.max_age_hours < 0:
        parser.error('Delay and maximum age must be nonnegative')
    rows = json.loads((ROOT / 'search_handles.json').read_text())['handles']
    addresses = sorted({a for r in rows for a in r.get('wallet_addresses', [])})
    cache_path = ROOT / 'wallet_balances.json'
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {'network': 'mainnet-beta', 'asset': 'native SOL', 'commitment': 'confirmed', 'balances': {}}
    balances = cache['balances']
    now = datetime.now(timezone.utc)
    pending = [a for a in addresses if balances.get(a, {}).get('status') != 'ok' or
               (now - datetime.fromisoformat(balances[a]['checked_at'])).total_seconds() >= args.max_age_hours * 3600]
    consecutive_failures = 0
    for start in range(0, len(pending), 100):
        batch = pending[start:start + 100]
        body = {'jsonrpc': '2.0', 'id': 1, 'method': 'getMultipleAccounts', 'params': [batch,
                {'encoding': 'base64', 'dataSlice': {'offset': 0, 'length': 0}, 'commitment': 'confirmed'}]}
        checked = datetime.now(timezone.utc).isoformat()
        try:
            request = Request(args.rpc_url, json.dumps(body).encode(), {'Content-Type': 'application/json'})
            with urlopen(request, timeout=25) as response:
                result = json.load(response)
            if 'error' in result:
                raise ValueError('RPC returned an error')
            values = result['result']['value']
            slot = result['result']['context']['slot']
            if len(values) != len(batch):
                raise ValueError('Incomplete RPC response')
            records = {}
            for address, value in zip(batch, values):
                lamports = value['lamports'] if value is not None else 0
                if not isinstance(lamports, int) or isinstance(lamports, bool) or lamports < 0:
                    raise ValueError('Invalid lamport balance')
                records[address] = {'address': address, 'status': 'ok', 'lamports': lamports,
                    'sol': str(Decimal(lamports) / Decimal(1_000_000_000)), 'checked_at': checked,
                    'slot': slot, 'account_exists': value is not None}
            balances.update(records)
            consecutive_failures = 0
        except Exception as exc:
            # Never replace a known balance with zero after a failed request.
            consecutive_failures += 1
            for address in batch:
                previous = balances.get(address, {})
                balances[address] = {**previous, 'address': address, 'status': 'error',
                                     'last_attempt_at': checked, 'error': type(exc).__name__}
        cache['updated_at'] = checked
        write(cache_path, cache)
        print(f'Processed {min(start + 100, len(pending))}/{len(pending)} wallets', flush=True)
        if consecutive_failures >= 3:
            print('Stopped after three failed batches. Retry later or set SOLANA_RPC_URL.', flush=True)
            break
        if start + 100 < len(pending):
            time.sleep(args.delay)
    decorate(ROOT, balances)
    ok = sum(balances.get(a, {}).get('status') == 'ok' for a in addresses)
    print(f'{ok}/{len(addresses)} wallets have successful balance snapshots.')
    return 0 if ok == len(addresses) else 1


if __name__ == '__main__':
    raise SystemExit(main())
