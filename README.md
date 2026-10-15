# Zesty list

Merged, deduplicated Pump and X/Twitter handles from the source exports in the
parent `zestys` folder. This repository contains the generated list and its
source evidence.

## Generated files

- `search_handles.json`: compact handle data for the homepage, regenerated with
  every build, without the full original detail records.
- `master_handles.json`: all handles, original detail records, source locations,
  and the scan report.
- `index.json`: generation timestamp, summary counts, input scan report, and links
  to the alphabetical shards.
- `alphabetized/*.json`: handles grouped by first character (`a`–`z`, `0-9`, or
  `_other`), with up to 500 handles per file and their associated detail records.

Handles are deduplicated by platform and case-insensitive handle. Original
spellings and source evidence are retained. Identical detail records are stored
once with all their source locations. Explicit Pump/X profile columns establish
related handles; mentions alone do not establish an account relationship.

## Rebuild the list

The generator lives at `../build_handles.py`, outside this repository. From the
parent `zestys` folder, run:

```sh
python3 build_handles.py
```

The script uses Python 3's standard library and scans CSV, TSV, JSON, JSONL, and
text exports recursively. By default, it writes directly into this `list`
repository, regardless of the current working directory. It skips hidden paths,
this repository, and the legacy `handles_output` folder so generated data is not
re-ingested.

Optional settings:

```sh
python3 build_handles.py --input /path/to/exports --max-records 500
python3 build_handles.py --output /path/to/another/output
```

Rebuilding replaces the master and index files, refreshes the alphabetical
shards, and removes obsolete generated shards. The command prints a summary and
exits with a nonzero status if any input files could not be read; inspect the
`input_files` scan report for errors before publishing an update.

The output retains original source records, which may include additional profile
data beyond handles. Review the generated files before sharing them.

## Homepage

`index.html` is the project homepage and searchable directory. It supports
contains, starts-with, ends-with, exact, and regular-expression searches, plus
platform, case sensitivity, and related-handle filters. Results
are paginated. Searches match handles only. X handles link to x.com; Pump
handles link to the pump.fun profile URLs retained from source exports. Regex searches run in a separate worker with a timeout so a slow
pattern can be stopped without freezing the page.

To preview from this repository:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000`. The page needs HTTP hosting to load its JSON data;
opening it directly as a local file will not work in most browsers. The files can
also be served by GitHub Pages or another static host.

Barter, paid updates, and earned updates are labeled **Coming soon**. These
programs are not live, and no payment, submission, or credits system is connected.
Their terms and requirements will be provided later.

## Current dataset

The current build scanned 9 source files without errors and contains 10,275
unique handles (8,020 Pump and 2,255 X/Twitter), backed by 11,728 unique detail
records. See `index.json` for the authoritative summary and generation time.

## Pump wallets

Pump entries include `wallet_addresses`, extracted from source
`pump_profile_url` values and validated as base58-encoded 32-byte Solana public
keys. Address case is preserved. `wallet_address` is populated only when exactly
one distinct address is known. If a handle appears with multiple addresses, all
are retained and `wallet_conflict` is true; the homepage displays a notice.
These are source-reported profile associations, not proof of wallet ownership.
X entries do not inherit a wallet from a related Pump entry.

## SOL balance snapshots

Run `python3 update_balances.py` from this repository after rebuilding. It fetches
native SOL balances on mainnet using Solana `getMultipleAccounts` in batches of
100, writes `wallet_balances.json`, and decorates the master, search file, and
alphabetical shards with `wallet_balances`. The generator preserves that cache
on later rebuilds. Use `SOLANA_RPC_URL` for a dedicated provider; its URL is never
written into the output. Public RPC may rate-limit requests. Retry resumes using
successful snapshots younger than one hour; `--max-age-hours 0` refreshes all.

Balances retain exact integer lamports, decimal SOL strings, confirmed slots,
and UTC lookup times. A missing on-chain account has a zero balance. Failed
requests display unavailable or a labeled stale prior balance; they never become
zero. The job stops after three consecutive failed batches and exits nonzero
unless every wallet has a successful snapshot. No token holdings or wallet
ownership verification is included. The page shows per-wallet balances, without
summing wallets for handles with conflicting source associations.

## Live USD valuation

The top banner multiplies the deduplicated native SOL balance snapshots by the
Coinbase public SOL/USD spot rate, fetched in the visitor's browser every 30
seconds. Changes animate between real quotes; no simulated price changes are
used. The banner shows the quote retrieval time and labels stale quotes on
failures. Wallet balances remain snapshots from the balance updater, so this
is an estimate of tracked native SOL holdings, not total personal net worth.
Tokens and other assets are excluded. Reduced-motion preferences are respected.

The directory can sort by handle or native SOL balance ascending/descending.
Balance sorting uses exact lamports, sums distinct linked Pump wallets per row,
and places unavailable balances last in either direction. It applies to the full
filtered result set before pagination.
