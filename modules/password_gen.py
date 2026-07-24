#!/usr/bin/env python3

"""
Camoro - AI-Powered Password Generator
Generates ~18,000 smart passwords based on gathered intelligence
"""

import json
import os
import sys
import itertools
import random
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
WORDLIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wordlists')

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
NC = '\033[0m'

# Common number suffixes
YEAR_SUFFIXES = ['123', '1234', '12345', '123456', '1', '12', '123!', '123@', '123#',
                 '007', '069', '101', '111', '121', '123', '143', '147', '159', '200',
                 '2020', '2021', '2022', '2023', '2024', '2025', '2026',
                 '21', '22', '23', '24', '25',
                 '246', '247', '258', '321', '333', '357', '369', '404', '420',
                 '456', '555', '666', '777', '888', '999',
                 '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999',
                 '0', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                 '01', '02', '03', '04', '05', '06', '07', '08', '09',
                 '11', '13', '14', '15', '16', '17', '18', '19', '20',
                 '69', '96', '420', '007']

COMMON_PREFIXES = ['', '!', '@', '#', '$', '%', '&', '*', '~', '_', '-', '+', '=']
COMMON_SUFFIXES = ['!', '@', '#', '$', '%', '&', '*', '~', '_', '-', '.', ',', '?', '/', '+', '=', '!!', '!?', '?!', '...', ':)']

# Leetspeak substitutions
LEETSPEAK = {
    'a': ['a', 'A', '4', '@', 'а'],
    'b': ['b', 'B', '8', '6'],
    'c': ['c', 'C', '(', '<', '{', '¢'],
    'e': ['e', 'E', '3', 'е'],
    'g': ['g', 'G', '9', '6'],
    'i': ['i', 'I', '1', '!', '|', 'l'],
    'l': ['l', 'L', '1', '|', 'I', '!'],
    'o': ['o', 'O', '0', '()', '[]', 'о'],
    's': ['s', 'S', '5', '$', 'z'],
    't': ['t', 'T', '7', '+'],
    'z': ['z', 'Z', '2'],
}


def load_info(username):
    """Load gathered information for the target."""
    filepath = os.path.join(RESULTS_DIR, username, 'info.json')
    if not os.path.exists(filepath):
        print(f"{RED}[!] Info file not found for: {username}{NC}")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_common_passwords():
    """Load common passwords wordlist."""
    wordlist_path = os.path.join(WORDLIST_DIR, 'common.txt')
    passwords = []
    if os.path.exists(wordlist_path):
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]
    return passwords


def generate_leet_variations(word):
    """Generate leetspeak variations of a word."""
    if not word or len(word) < 2:
        return [word]
    
    variations = {word, word.lower(), word.upper(), word.capitalize()}
    word_lower = word.lower()
    
    # Common leet substitutions
    for i, char in enumerate(word_lower):
        if char in LEETSPEAK:
            for sub in LEETSPEAK[char]:
                if sub != char:
                    new_word = word_lower[:i] + sub + word_lower[i+1:]
                    variations.add(new_word)
                    variations.add(new_word.upper())
                    variations.add(new_word.capitalize())
    
    # Multiple substitutions
    if len(word) >= 3:
        # E->3, A->4, S->5, O->0
        leet = word_lower
        leet = leet.replace('e', '3').replace('a', '4').replace('s', '5').replace('o', '0')
        variations.add(leet)
        variations.add(leet.upper())
        variations.add(leet.capitalize())
        
        # Another common pattern
        leet2 = word_lower
        leet2 = leet2.replace('e', '3').replace('a', '@').replace('s', '$').replace('o', '0').replace('i', '1')
        variations.add(leet2)
        variations.add(leet2.upper())
        variations.add(leet2.capitalize())
    
    # Reverse
    variations.add(word_lower[::-1])
    variations.add(word[::-1])
    
    return list(variations)


def generate_combined_passwords(base_words, info):
    """Generate smart password combinations based on intelligence."""
    passwords = set()
    
    # Extract key information
    username = info.get('username', '').lower()
    full_name = info.get('full_name', '')
    bio = info.get('biography', '')
    birthday = info.get('birthday', '')
    real_name = info.get('real_name', '')
    partner_name = info.get('partner_name', '')
    hobby = info.get('hobby', '')
    pet = info.get('pet', '')
    city = info.get('city', '')
    fav_number = info.get('fav_number', '')
    keyword = info.get('keyword', '')
    
    # Build keyword list from all sources
    keywords = []
    
    # From username
    keywords.append(username)
    # Try splitting username (e.g., john_doe -> john, doe)
    if '_' in username:
        keywords.extend(username.split('_'))
    if '.' in username:
        keywords.extend(username.split('.'))
    if '-' in username:
        keywords.extend(username.split('-'))
    
    # From full name
    if full_name:
        keywords.append(full_name.lower())
        name_parts = full_name.lower().split()
        keywords.extend(name_parts)
        # First + last combined
        if len(name_parts) >= 2:
            keywords.append(name_parts[0] + name_parts[-1])
            keywords.append(name_parts[-1] + name_parts[0])
    
    # From real name (user provided)
    if real_name:
        keywords.append(real_name.lower())
        for part in real_name.lower().split():
            keywords.append(part)
    
    # From partner name
    if partner_name:
        keywords.append(partner_name.lower())
        keywords.append(f"{username}{partner_name.lower()}")
        keywords.append(f"{partner_name.lower()}{username}")
    
    # From bio
    if bio:
        # Extract words from bio
        bio_words = bio.lower().split()
        keywords.extend([w for w in bio_words if len(w) > 2])
        # Special words in bio
        for word in bio_words:
            if word in ['love', 'life', 'live', 'happy', 'family', 'god', 'king', 'queen', 
                        'boss', 'forever', 'always', 'never', 'faith', 'hope']:
                keywords.append(word)
    
    # From hobby
    if hobby:
        keywords.append(hobby.lower())
    
    # From pet
    if pet:
        keywords.append(pet.lower())
    
    # From city
    if city:
        keywords.append(city.lower())
    
    # From keyword
    if keyword:
        keywords.append(keyword.lower())
    
    # Clean keywords
    keywords = [k.strip() for k in keywords if k.strip() and len(k.strip()) >= 2]
    keywords = list(set(keywords))
    
    print(f"{CYAN}[*] {WHITE}Keywords extracted: {YELLOW}{len(keywords)}{NC}")
    for kw in keywords[:10]:
        print(f"    {CYAN}→{NC} {kw}")
    if len(keywords) > 10:
        print(f"    {CYAN}→{NC} ... and {len(keywords)-10} more")
    
    # ======================================================
    # STAGE 1: Base keyword variations with suffixes
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 1: Keyword variations...{NC}")
    for kw in keywords:
        # The keyword itself
        passwords.add(kw)
        passwords.add(kw.capitalize())
        passwords.add(kw.upper())
        
        # With common suffixes
        for suffix in ['123', '1234', '123456', '1', '12', '!', '@', '#', '123!', '!@#',
                       '2024', '2025', '2026', '21', '22', '23', '24',
                       '.', '_', '-', '!!', '..', '__']:
            passwords.add(f"{kw}{suffix}")
            passwords.add(f"{kw.capitalize()}{suffix}")
            passwords.add(f"{kw.upper()}{suffix}")
            
            # Suffix + keyword
            passwords.add(f"{suffix}{kw}")
            if not suffix.startswith(('2', '1', '0')):
                passwords.add(f"{suffix}{kw.capitalize()}")
    
    # ======================================================
    # STAGE 2: Name combinations
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 2: Name combinations...{NC}")
    name_parts = []
    if full_name:
        name_parts.extend(full_name.lower().split())
    if real_name:
        name_parts.extend(real_name.lower().split())
    
    name_parts = list(set([p for p in name_parts if len(p) >= 2]))
    
    if len(name_parts) >= 2:
        for p1, p2 in itertools.permutations(name_parts, 2):
            passwords.add(f"{p1}{p2}")
            passwords.add(f"{p1}.{p2}")
            passwords.add(f"{p1}_{p2}")
            passwords.add(f"{p1}-{p2}")
            passwords.add(f"{p1}{p2}123")
            passwords.add(f"{p1}{p2}!")
            passwords.add(p1 + p2.capitalize())
            
            # With username
            passwords.add(f"{p1}{username}")
            passwords.add(f"{username}{p1}")
            passwords.add(f"{p1}.{username}")
            passwords.add(f"{username}.{p1}")
    
    # ======================================================
    # STAGE 3: Birthday-based passwords
    # ======================================================
    if birthday:
        print(f"{CYAN}[*] {WHITE}Generating stage 3: Birthday patterns...{NC}")
        date_str = birthday.replace('-', '').replace('/', '')
        if len(date_str) >= 6:
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            
            date_formats = [
                f"{day}{month}{year}", f"{month}{day}{year}",
                f"{day}{month}", f"{month}{day}",
                f"{day}{month[0]}{month[1]}",  # DM
                f"{year}", f"{year[2:]}",  # 2025 -> 25
                f"{day}.{month}.{year}", f"{day}/{month}/{year}",
                f"{day}-{month}-{year}",
            ]
            
            for df in date_formats:
                passwords.add(df)
                for kw in keywords[:5]:
                    passwords.add(f"{kw}{df}")
                    passwords.add(f"{df}{kw}")
                    passwords.add(f"{kw}{df}!")
                    passwords.add(f"{kw}.{df}")
    
    # ======================================================
    # STAGE 4: Favorites (pet, hobby, city, fav_number)
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 4: Personal favorites...{NC}")
    fav_items = [pet, hobby, city, fav_number, partner_name, keyword]
    fav_items = [f for f in fav_items if f and len(str(f).strip()) >= 2]
    
    for i, item in enumerate(fav_items):
        item = str(item).lower().strip()
        passwords.add(item)
        passwords.add(item.capitalize())
        
        for suffix in YEAR_SUFFIXES[:20]:
            passwords.add(f"{item}{suffix}")
            passwords.add(f"{item.capitalize()}{suffix}")
        
        # Combine with username
        passwords.add(f"{username}{item}")
        passwords.add(f"{item}{username}")
        passwords.add(f"{username}_{item}")
        passwords.add(f"{item}_{username}")
        
        # Combine with other fav items
        for j in range(i+1, len(fav_items)):
            other = str(fav_items[j]).lower().strip()
            passwords.add(f"{item}{other}")
            passwords.add(f"{other}{item}")
            passwords.add(f"{item}.{other}")
            passwords.add(f"{item}_{other}")
    
    # ======================================================
    # STAGE 5: Leetspeak variations of top keywords
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 5: Leetspeak variations...{NC}")
    top_keywords = keywords[:15] + name_parts[:10]
    top_keywords = list(set(top_keywords))
    
    for kw in top_keywords:
        leet_variations = generate_leet_variations(kw)
        for lv in leet_variations[:10]:  # Limit to avoid explosion
            passwords.add(lv)
            for suffix in ['123', '!', '@', '#', '2024', '2025', '1', '!@#']:
                passwords.add(f"{lv}{suffix}")
    
    # ======================================================
    # STAGE 6: Username-based patterns (very common)
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 6: Username patterns...{NC}")
    for prefix in COMMON_PREFIXES:
        for suffix in YEAR_SUFFIXES[:30]:
            passwords.add(f"{prefix}{username}{suffix}")
            passwords.add(f"{username}{prefix}{suffix}")
    
    # Username + common words
    for common_word in ['love', 'life', 'baby', 'babe', 'honey', 'sweet', 'cool',
                        'king', 'queen', 'boss', 'star', 'moon', 'sun', 'fire',
                        'forever', 'always', 'never', 'faith', 'hope', 'god',
                        'sexy', 'hot', 'cute', 'pretty', 'handsome']:
        passwords.add(f"{username}{common_word}")
        passwords.add(f"{common_word}{username}")
        passwords.add(f"{username}{common_word}123")
        passwords.add(f"{username}_{common_word}")
        passwords.add(f"{username}.{common_word}")
    
    # ======================================================
    # STAGE 7: Two-word combinations from keywords
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 7: Word combinations...{NC}")
    common_combos = ['love', 'life', 'baby', 'king', 'queen', 'star', 'sun', 'moon',
                     'fire', 'water', 'dream', 'hope', 'faith', 'soul', 'heart',
                     'angel', 'devil', 'heaven', 'hell', 'world', 'time', 'night',
                     'day', 'light', 'dark', 'shadow', 'blood', 'tears', 'smile']
    
    for kw in keywords[:10]:
        for combo in common_combos[:15]:
            passwords.add(f"{kw}{combo}")
            passwords.add(f"{combo}{kw}")
            passwords.add(f"{kw}_{combo}")
            passwords.add(f"{kw}.{combo}")
            passwords.add(f"{kw}{combo}123")
            passwords.add(f"{combo}{kw}123")
    
    # ======================================================
    # STAGE 8: Common passwords list
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 8: Including common passwords...{NC}")
    common_passwords = load_common_passwords()
    for pwd in common_passwords:
        passwords.add(pwd)
    
    # ======================================================
    # STAGE 9: Add number variations to everything
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 9: Number/symbol enrichment...{NC}")
    base_passwords = list(passwords)[:8000]  # Take current set up to 8000
    for pwd in base_passwords:
        if len(pwd) < 6:  # Short passwords need more
            for suffix in ['123', '1234', '!', '@', '#', '1', '99', '007', '2024']:
                passwords.add(f"{pwd}{suffix}")
        # Add number at beginning or end
        for num in ['1', '12', '123', '2024', '2025', '21', '22', '99', '69', '100',
                    '007', '420', '777', '000', '111', '1234', '12345']:
            passwords.add(f"{pwd}{num}")
            passwords.add(f"{num}{pwd}")
    
    # ======================================================
    # STAGE 10: Instagram-specific patterns
    # ======================================================
    print(f"{CYAN}[*] {WHITE}Generating stage 10: Instagram-specific patterns...{NC}")
    ig_patterns = [
        f"instagram", f"insta", f"igram", f"instagrm",
        f"insta{username}", f"{username}insta",
        f"gram{username}", f"{username}gram",
        f"ig_{username}", f"{username}_ig",
        f"follow", f"followers", f"follower",
        f"like4like", f"follow4follow",
        f"instadaily", f"instalove",
        f"{username}gram", f"gram{username}",
    ]
    for pattern in ig_patterns:
        passwords.add(pattern)
        passwords.add(pattern + '1')
        passwords.add(pattern + '123')
        passwords.add(pattern + '!')
        passwords.add(pattern.capitalize())
    
    # Instagram + birthday
    if birthday:
        year = birthday[:4]
        passwords.add(f"insta{year}")
        passwords.add(f"{year}insta")
        passwords.add(f"ig{year}")
        passwords.add(f"gram{year}")
    
    # ======================================================
    # FINAL: Filter and return
    # ======================================================
    # Remove empty and very short/long passwords
    valid_passwords = set()
    for pwd in passwords:
        pwd = str(pwd).strip()
        if 4 <= len(pwd) <= 64:
            valid_passwords.add(pwd)
    
    # Limit to around 18,000
    password_list = list(valid_passwords)
    
    # If we have too many, trim intelligently
    if len(password_list) > 20000:
        # Keep top keywords variations and common passwords
        password_list = password_list[:20000]
    
    # Shuffle to avoid obvious patterns
    random.shuffle(password_list)
    
    # Ensure we have roughly 18000
    if len(password_list) < 18000:
        # Add more enriched variations
        current_count = len(password_list)
        for pwd in password_list[:5000]:
            for suffix in ['2024', '2025', '!@#', '1234', 'pass', 'word']:
                if len(password_list) < 18000:
                    password_list.append(f"{pwd}{suffix}")
    
    password_list = list(set(password_list))
    
    if len(password_list) > 18000:
        password_list = password_list[:18000]
    
    # Shuffle again
    random.shuffle(password_list)
    
    return password_list


def save_passwords(username, passwords):
    """Save generated passwords to file."""
    user_dir = os.path.join(RESULTS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    
    filepath = os.path.join(user_dir, 'passwords.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        for pwd in passwords:
            f.write(pwd + '\n')
    
    return filepath


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Camoro - AI Password Generator')
    parser.add_argument('--username', '-u', required=True, help='Target Instagram username')
    args = parser.parse_args()
    
    print(f"\n{CYAN}╔{'═'*50}╗{NC}")
    print(f"{CYAN}║{' ' * 8}🧠 CAMORO AI PASSWORD GENERATOR{' ' * 8}║{NC}")
    print(f"{CYAN}╚{'═'*50}╝{NC}\n")
    
    info = load_info(args.username)
    if not info:
        sys.exit(1)
    
    print(f"{YELLOW}[*] Target: {WHITE}{args.username}{NC}")
    print(f"{YELLOW}[*] Full Name: {WHITE}{info.get('full_name', 'N/A')}{NC}")
    print(f"{YELLOW}[*] Bio: {WHITE}{info.get('biography', 'N/A')[:50]}{NC}")
    print()
    
    passwords = generate_combined_passwords([], info)
    
    filepath = save_passwords(args.username, passwords)
    
    print(f"\n{GREEN}╔{'═'*50}╗{NC}")
    print(f"{GREEN}║{' ' * 10}✅ PASSWORD GENERATION COMPLETE{' ' * 10}║{NC}")
    print(f"{GREEN}╚{'═'*50}╝{NC}")
    print(f"  {YELLOW}Total passwords generated: {WHITE}{len(passwords)}{NC}")
    print(f"  {YELLOW}Saved to: {WHITE}{filepath}{NC}")
    
    # Show sample
    print(f"\n{CYAN}[*] Sample passwords:{NC}")
    for pwd in passwords[:15]:
        print(f"  {RED}✗{NC} {pwd}")
    print(f"  {CYAN}... and {len(passwords)-15} more{NC}")
