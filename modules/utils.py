#!/usr/bin/env python3
"""Utility functions"""

import os
import sys
import platform

def detect_platform():
    """Detect running platform"""
    system = platform.system().lower()
    
    # Check if running in Termux
    is_termux = 'com.termux' in os.environ.get('HOME', '') or \
                os.path.exists('/data/data/com.termux')
    
    if is_termux:
        return 'termux'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'macos'
    else:
        return system

def check_requirements():
    """Check if all requirements are met"""
    checks = {
        'root': os.geteuid() == 0,
        'proc_fs': os.path.exists('/proc/self/maps'),
        'linux': platform.system().lower() == 'linux',
    }
    
    print("\n[+] System Requirements Check:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
    
    return all(checks.values())

def format_bytes(size):
    """Format byte size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"

def scan_pattern_in_memory(data, pattern):
    """Search for byte pattern in data"""
    results = []
    offset = 0
    pattern_bytes = bytes.fromhex(pattern.replace('?', '.').replace(' ', ''))
    
    # Handle wildcards
    if '?' in pattern:
        # Simple pattern matching with wildcards
        import re
        pattern_re = pattern.replace(' ', '').replace('??', '.')
        pattern_re = bytes.fromhex(pattern_re.replace('?', '0'))
        # Actually let's do simple search
        return search_with_wildcard(data, pattern)
    
    while True:
        pos = data.find(pattern_bytes, offset)
        if pos == -1:
            break
        results.append(pos)
        offset = pos + 1
    
    return results

def search_with_wildcard(data, pattern_hex):
    """Search with wildcard bytes (??)"""
    # Split pattern into bytes
    parts = pattern_hex.strip().split()
    results = []
    
    for i in range(len(data) - len(parts) + 1):
        match = True
        for j, part in enumerate(parts):
            if part == '??' or part == '?':
                continue
            try:
                b = int(part, 16)
                if data[i + j] != b:
                    match = False
                    break
            except ValueError:
                match = False
                break
        
        if match:
            results.append(i)
    
    return results
