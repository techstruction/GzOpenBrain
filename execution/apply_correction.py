#!/usr/bin/env python3
"""
apply_correction.py — OpenBrain Fix Button

Processes human-in-the-loop corrections to classifications.
Updates the entry in Affine and logs the correction to improve future Sorter/Bouncer accuracy.

Usage:
    python3 execution/apply_correction.py --msg_id ID --domain NEW_DOMAIN
"""

import sys
import json
import argparse

def apply_fix(msg_id, domain=None, category=None):
    """
    Simulates a fix. In production, this would:
    1. Look up the entry in Affine by msg_id.
    2. Update the domain/category fields.
    3. Log the 'Correction' in a special feedback table for Sorter reinforcement.
    """
    return True, f"Corrected entry {msg_id} to Domain: {domain}, Category: {category}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain — Apply Correction')
    parser.add_argument('--msg_id', required=True, help='ID of the message/entry to fix')
    parser.add_argument('--domain', help='New domain')
    parser.add_argument('--category', help='New category')
    args = parser.parse_args()

    success, message = apply_fix(args.msg_id, args.domain, args.category)
    
    print(json.dumps({
        "success": success,
        "message": message
    }, indent=2))
