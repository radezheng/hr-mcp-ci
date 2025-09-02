"""
Run from the repository root:
    uv run examples/snippets/servers/streamable_config.py
"""

from mcp.server.fastmcp import FastMCP
import json
from pathlib import Path
from typing import Any, Dict, List

# Stateful server (maintains session state)
# mcp = FastMCP("StatefulServer")

# Other configuration options:
# Stateless server (no session persistence)
mcp = FastMCP("StatelessServer", stateless_http=True, host="0.0.0.0")

# Stateless server (no session persistence, no sse stream with supported client)
# mcp = FastMCP("StatelessServer", stateless_http=True, json_response=True)


# Add a simple tool to demonstrate the server
@mcp.tool()
def greet(name: str = "World") -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


# Candidate management helpers and tools (persist to data.json in repo root)
DATA_FILE = Path(__file__).parent / "data.json"


def _load_candidates() -> List[Dict[str, Any]]:
    try:
        if not DATA_FILE.exists():
            return []
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_candidates(candidates: List[Dict[str, Any]]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)


def _to_list(val):
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [s.strip() for s in val.split(",") if s.strip()]
    return []


@mcp.tool()
def list_candidates() -> List[Dict[str, Any]]:
    """Return the whole list of candidates."""
    return _load_candidates()


@mcp.tool()
def search_candidates(query: str = "") -> List[Dict[str, Any]]:
    """Search candidates by name, email, skills, or current role."""
    q = (query or "").lower().strip()
    candidates = _load_candidates()
    if not q:
        return candidates
    out: List[Dict[str, Any]] = []
    for c in candidates:
        fullname = c.get("fullname") or f"{c.get('firstname','')} {c.get('lastname','')}".strip()
        skills_str = " ".join(_to_list(c.get("skills", [])))
        fields = [fullname or "", c.get("email", ""), c.get("current_role", ""), skills_str]
        for f in fields:
            if f and q in f.lower():
                out.append(c)
                break
    return out


@mcp.tool()
def add_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new candidate. Candidate must include an 'email'."""
    if not isinstance(candidate, dict):
        return {"error": "candidate must be an object"}
    email = candidate.get("email")
    if not email:
        return {"error": "email required"}

    candidates = _load_candidates()
    if any(c.get("email", "").lower() == email.lower() for c in candidates):
        return {"error": "candidate with this email already exists"}

    firstname = candidate.get("firstname", "")
    lastname = candidate.get("lastname", "")
    fullname = candidate.get("fullname") or f"{firstname} {lastname}".strip()
    languages = _to_list(candidate.get("languages", []))
    skills = _to_list(candidate.get("skills", []))
    new = {
        "firstname": firstname,
        "lastname": lastname,
        "fullname": fullname,
        "email": email,
        "languages": languages,
        "skills": skills,
        "current_role": candidate.get("current_role", ""),
    }
    candidates.append(new)
    _save_candidates(candidates)
    return new


@mcp.tool()
def update_candidate(email: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing candidate by email. 'updates' is a dict of fields to modify."""
    if not email:
        return {"error": "email required"}
    if not isinstance(updates, dict):
        return {"error": "updates must be an object"}

    candidates = _load_candidates()
    for idx, c in enumerate(candidates):
        if c.get("email", "").lower() == email.lower():
            for k, v in updates.items():
                if k in ("languages", "skills"):
                    c[k] = _to_list(v)
                else:
                    c[k] = v
            # recompute fullname if needed
            c["fullname"] = c.get("fullname") or f"{c.get('firstname','')} {c.get('lastname','')}".strip()
            candidates[idx] = c
            _save_candidates(candidates)
            return c
    return {"error": "candidate not found"}


@mcp.tool()
def remove_candidate(email: str) -> Dict[str, Any]:
    """Remove a candidate by email and return the removed record."""
    if not email:
        return {"error": "email required"}
    candidates = _load_candidates()
    for idx, c in enumerate(candidates):
        if c.get("email", "").lower() == email.lower():
            removed = candidates.pop(idx)
            _save_candidates(candidates)
            return removed
    return {"error": "candidate not found"}


# Run server with streamable_http transport
if __name__ == "__main__":
    # Run server with streamable_http transport
    mcp.run(transport="streamable-http")