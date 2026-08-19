"""Token-economical serialization for tool return values.

Compact (no indent), non-ASCII-preserving, and size-capped so a single
tool call can never blow past the ~20,000-char budget an agent's context
can reasonably absorb.

Customer Thermometer's own API never returns JSON (its responses are XML
documents, or plain integers/strings), so tool results here are plain
Python `str` values rather than dicts/lists. dump_json_capped() still
applies to them unchanged: it JSON-serializes the string (satisfying the
SOP's "tools return a JSON-serialized string" convention) and, in the rare
case a response exceeds the char budget, falls through to the generic
too-large notice below (the list/dict truncation branches are dead code
for this vendor but kept so this module stays a drop-in match of the
reference implementation).
"""

import json
from typing import Any

MAX_CHARS = 20_000


def _compact(data: Any) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def dump_json_capped(data: Any, max_chars: int = MAX_CHARS) -> str:
    """Serialize data compactly, truncating the largest list field (or the
    top-level list) if the result would exceed max_chars, rather than ever
    returning an unbounded blob.
    """
    s = _compact(data)
    if len(s) <= max_chars:
        return s

    if isinstance(data, list):
        return _truncate_list(data, max_chars, wrap_key="items")

    if isinstance(data, dict):
        list_keys = [k for k, v in data.items() if isinstance(v, list)]
        if list_keys:
            key = max(list_keys, key=lambda k: len(_compact(data[k])))
            items = data[key]
            lo, hi = 0, len(items)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                candidate = dict(data)
                candidate[key] = items[:mid]
                candidate["truncated"] = True
                candidate["truncated_field"] = key
                candidate["original_count"] = len(items)
                if len(_compact(candidate)) <= max_chars:
                    lo = mid
                else:
                    hi = mid - 1
            candidate = dict(data)
            candidate[key] = items[:lo]
            candidate["truncated"] = True
            candidate["truncated_field"] = key
            candidate["original_count"] = len(items)
            return _compact(candidate)

    # Not list-shaped and still too big — return a short notice instead of
    # a giant unbounded string. For this vendor this is the path a huge raw
    # XML/text response falls into: narrowing the query (smaller limit or
    # date range) is the way to get under the cap.
    return _compact(
        {
            "truncated": True,
            "note": f"Result too large ({len(s)} chars) to return in full and not list-shaped; narrow your query.",
        }
    )


def _truncate_list(items: list, max_chars: int, wrap_key: str) -> str:
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        candidate = {wrap_key: items[:mid], "truncated": True, "original_count": len(items)}
        if len(_compact(candidate)) <= max_chars:
            lo = mid
        else:
            hi = mid - 1
    return _compact({wrap_key: items[:lo], "truncated": True, "original_count": len(items)})


def error_envelope(code: str, message: str, retryable: bool) -> str:
    return _compact({"error": {"code": code, "message": message, "retryable": retryable}})
