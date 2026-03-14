#!/usr/bin/env python3
"""
bouncer_check.py — OpenBrain Bouncer Agent

Reviews the classification output from Sorter and decides whether to file it
directly in a category or flag it for human review.

Usage:
    python3 execution/bouncer_check.py '{"domain": "...", "quality_score": "..."}'
    python3 execution/bouncer_check.py --stdin

Output (stdout):
    JSON object with decision and reason.
"""

import sys
import json
import argparse

def evaluate_quality(entry):
    """
    Evaluates the quality of a classified entry.
    Logic:
    - If quality_score is 'low' -> FLAG
    - If summary is too short -> FLAG
    - If domain is 'Clan' and category is 'Inbox Log' (fallback) -> FLAG
    - Else -> PASS
    """
    quality_score = entry.get('quality_score', 'low')
    summary = entry.get('summary', '')
    domain = entry.get('domain', '')
    category = entry.get('category', '')

    if quality_score == 'low':
        return 'flag', "Quality score is too low."
    
    if len(summary.split()) < 3:
        return 'flag', "Summary is too concise/non-descriptive."
    
    if domain == 'Clan' and category == 'Inbox Log':
        return 'flag', "Fallback classification (Clan/Inbox) needs review."

    return 'pass', "Quality threshold met."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain Bouncer — Evaluate quality')
    parser.add_argument('entry', nargs='?', help='Classified JSON entry')
    parser.add_argument('--stdin', action='store_true', help='Read entry from stdin')
    args = parser.parse_args()

    try:
        if args.stdin:
            raw_input = sys.stdin.read().strip()
        elif args.entry:
            raw_input = args.entry
        else:
            print(json.dumps({"error": "No input provided"}, indent=2), file=sys.stderr)
            sys.exit(1)

        entry = json.loads(raw_input)
        decision, reason = evaluate_quality(entry)
        
        print(json.dumps({
            "decision": decision,
            "reason": reason
        }, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)
