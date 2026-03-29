#!/usr/bin/env python3
"""Parse strace-style logs into a viewable HTML table (or CSV) via pandas."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

DEFAULT_PATH_PREFIX = "/home/anurag/opensource/TEST/"

_ERRNO_RE = re.compile(r"^(-?\d+)\s+([A-Z0-9_]+)\s+\((.*)\)\s*$")
_INT_RE = re.compile(r"^-?\d+$")


def _split_syscall_and_args(left: str) -> tuple[str | None, str | None]:
    """Split `name(...)` into syscall name and argument string; handles nested parens."""
    try:
        i = left.index("(")
    except ValueError:
        return None, None
    name = left[:i].strip()
    depth = 0
    for j in range(i, len(left)):
        c = left[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return name, left[i + 1 : j]
    return name, left[i + 1 :]


def parse_strace_line(line: str) -> dict:
    line = line.rstrip("\n\r")
    row: dict = {"raw": line}

    if " = " not in line:
        row["kind"] = "message" if line.strip() else "blank"
        row["syscall"] = None
        row["arguments"] = None
        row["result_raw"] = None
        row["errno"] = None
        row["errno_message"] = None
        return row

    left, right = line.rsplit(" = ", 1)
    right = right.strip()
    syscall, args = _split_syscall_and_args(left)
    row["kind"] = "syscall"
    row["syscall"] = syscall
    row["arguments"] = args

    m = _ERRNO_RE.match(right)
    if m:
        row["result_raw"] = right
        row["errno"] = m.group(2)
        row["errno_message"] = m.group(3)
        return row

    if _INT_RE.match(right):
        row["result_raw"] = right
        row["errno"] = None
        row["errno_message"] = None
        return row

    row["result_raw"] = right
    row["errno"] = None
    row["errno_message"] = None
    return row


def log_to_dataframe(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = [parse_strace_line(line) for line in text.splitlines()]
    df = pd.DataFrame(rows)
    df.insert(0, "line", range(1, len(df) + 1))
    return df


def filter_lines_under_prefix(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Keep only rows whose raw line references ``prefix`` (e.g. filesystem paths)."""
    if not prefix:
        return df
    mask = df["raw"].astype(str).str.contains(prefix, regex=False, na=False)
    return df.loc[mask].reset_index(drop=True)


def dataframe_to_html(df: pd.DataFrame, *, subtitle: str | None = None) -> str:
    """Single-page HTML with a scrollable, sticky-header table."""
    inner = df.to_html(index=False, na_rep="", escape=True, classes="log")
    n = len(df)
    sub = f"<p>{subtitle}</p>\n" if subtitle else ""
    title = f"Strace log ({n} rows)"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: system-ui, "Segoe UI", sans-serif; margin: 0; padding: 12px;
    background: #1a1a1e; color: #e8e8ec; }}
  h1 {{ font-size: 1.1rem; font-weight: 600; margin: 0 0 12px; }}
  .wrap {{ overflow: auto; max-height: calc(100vh - 56px); border: 1px solid #3d3d44;
    border-radius: 6px; }}
  table.log {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
  table.log th, table.log td {{ border: 1px solid #3d3d44; padding: 6px 10px;
    text-align: left; vertical-align: top; }}
  table.log th {{ background: #2a2a30; position: sticky; top: 0; z-index: 1; }}
  table.log tr:nth-child(even) {{ background: #222228; }}
  table.log td {{ word-break: break-word; max-width: 36rem; }}
</style>
</head>
<body>
<h1>Strace log — {n} rows</h1>
{sub}<div class="wrap">
{inner}
</div>
</body>
</html>
"""


def write_output(
    df: pd.DataFrame, path: Path, *, html_subtitle: str | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        df.to_csv(path, index=False)
    else:
        path.write_text(dataframe_to_html(df, subtitle=html_subtitle), encoding="utf-8")


def main() -> None:
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(
        description="Export strace log as a viewable HTML table or CSV."
    )
    p.add_argument(
        "-i",
        "--input",
        type=Path,
        default=here / "out.log",
        help="Input log path (default: %(default)s)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=here / "strace_table.html",
        help="Output path: .html (default) or .csv (default: %(default)s)",
    )
    p.add_argument(
        "--path-prefix",
        default=DEFAULT_PATH_PREFIX,
        metavar="PREFIX",
        help=(
            "Only export lines that contain this path prefix (default: %(default)s). "
            "Pass an empty string to include all lines."
        ),
    )
    args = p.parse_args()

    df = log_to_dataframe(args.input)
    prefix = args.path_prefix
    if prefix:
        before = len(df)
        df = filter_lines_under_prefix(df, prefix)
        print(f"Filtered {before} → {len(df)} rows (prefix {prefix!r})")
    html_note = (
        f"Filtered to lines referencing <code>{prefix}</code>" if prefix else None
    )
    write_output(df, args.output, html_subtitle=html_note)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
