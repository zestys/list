# Zesty list

Merged, deduplicated Pump and X/Twitter handles from the source exports in the
parent `zestys` folder. This repository contains the generated list and its
source evidence.

## Generated files

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

## Current dataset

The current build scanned 9 source files without errors and contains 10,275
unique handles (8,020 Pump and 2,255 X/Twitter), backed by 11,728 unique detail
records. See `index.json` for the authoritative summary and generation time.
