"""
Computed incident hierarchy model.
Classifies Failure Atlas entries as ROOT_CAUSE, DERIVED, or CONSEQUENCE
based on their failure_type, signature, and relationship to other entries.
No schema changes required — hierarchy is computed at query time.
"""

from typing import Dict, Any, List, Optional, Tuple

INCIDENT_ROLE_ROOT_CAUSE = "ROOT_CAUSE"
INCIDENT_ROLE_DERIVED = "DERIVED"
INCIDENT_ROLE_CONSEQUENCE = "CONSEQUENCE"
INCIDENT_ROLE_UNCLASSIFIED = "UNCLASSIFIED"

# Entry types that represent root causes
ROOT_CAUSE_TYPES = {
    "CROSS_TOOL_DRC_DISAGREEMENT",
}

# Entry types that are derived (same root, different detection path)
DERIVED_TYPES = {
    "DRC_SPACING",
    "DRC_WIDTH",
    "DRC_ENCLOSURE",
    "DRC_ANTENNA",
    "DRC_DENSITY",
}

# Entry types that are consequences (downstream effects)
CONSEQUENCE_TYPES = {
    "SIGNOFF_FAILURE",
    "PIPELINE_FAILURE",
}


def classify_entry_role(entry: Dict[str, Any]) -> str:
    """Classify a single entry's role without reference to other entries.

    This is a best-effort classification based only on the entry's own fields.
    For the most accurate classification, use classify_run_entries() which
    considers inter-entry relationships.
    """
    failure_type = entry.get("failure_type", "")
    domain = entry.get("domain", "")
    category = entry.get("category", "")
    signature = entry.get("signature", "")

    if failure_type in ROOT_CAUSE_TYPES:
        return INCIDENT_ROLE_ROOT_CAUSE

    if failure_type in DERIVED_TYPES:
        return INCIDENT_ROLE_DERIVED

    if failure_type in CONSEQUENCE_TYPES:
        return INCIDENT_ROLE_CONSEQUENCE

    return INCIDENT_ROLE_UNCLASSIFIED


def classify_run_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Classify all entries for a run, considering inter-entry relationships.

    Rules:
    1. If a CROSS_TOOL_DRC_DISAGREEMENT exists, it is the ROOT_CAUSE.
    2. Any DRC_* failure_type entries are DERIVED (same violations, different detector).
    3. SIGNOFF_FAILURE and PIPELINE_FAILURE entries are CONSEQUENCE.
    4. Entries with no relationship to any root cause remain UNCLASSIFIED.

    Each entry dict is returned with an 'incident_role' key added.
    """
    results = []
    has_root_cause = any(
        e.get("failure_type") in ROOT_CAUSE_TYPES for e in entries
    )

    for entry in entries:
        annotated = dict(entry)
        failure_type = entry.get("failure_type", "")

        if failure_type in ROOT_CAUSE_TYPES:
            annotated["incident_role"] = INCIDENT_ROLE_ROOT_CAUSE

        elif failure_type in DERIVED_TYPES and has_root_cause:
            annotated["incident_role"] = INCIDENT_ROLE_DERIVED

        elif failure_type in CONSEQUENCE_TYPES and has_root_cause:
            annotated["incident_role"] = INCIDENT_ROLE_CONSEQUENCE

        elif failure_type in DERIVED_TYPES and not has_root_cause:
            annotated["incident_role"] = INCIDENT_ROLE_ROOT_CAUSE

        else:
            annotated["incident_role"] = classify_entry_role(entry)

        results.append(annotated)

    return results


def build_hierarchy(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build a hierarchy tree from classified entries.

    Returns a list of root cause entries, each with a 'children' list
    containing derived and consequence entries.
    """
    classified = classify_run_entries(entries)

    roots = []
    children = []

    for entry in classified:
        if entry["incident_role"] == INCIDENT_ROLE_ROOT_CAUSE:
            root = dict(entry)
            root["children"] = []
            roots.append(root)
        else:
            children.append(entry)

    for root in roots:
        for child in children:
            root["children"].append(child)

    if not roots and children:
        wrapper = {
            "failure_type": "UNCLASSIFIED_ROOT",
            "incident_role": INCIDENT_ROLE_ROOT_CAUSE,
            "title": f"Unclassified incidents ({len(children)} entries)",
            "children": children,
        }
        roots.append(wrapper)

    return roots


def get_root_summary(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize a run's failure atlas entries by root cause.

    Returns:
        root_count: Number of distinct root causes
        total_entries: Total entries
        consequence_count: Number of consequence entries
        derived_count: Number of derived entries
    """
    classified = classify_run_entries(entries)
    summary = {
        "root_count": sum(1 for e in classified if e["incident_role"] == INCIDENT_ROLE_ROOT_CAUSE),
        "total_entries": len(classified),
        "consequence_count": sum(1 for e in classified if e["incident_role"] == INCIDENT_ROLE_CONSEQUENCE),
        "derived_count": sum(1 for e in classified if e["incident_role"] == INCIDENT_ROLE_DERIVED),
        "unclassified_count": sum(1 for e in classified if e["incident_role"] == INCIDENT_ROLE_UNCLASSIFIED),
    }
    return summary
