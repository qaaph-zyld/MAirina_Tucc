import argparse
from pathlib import Path
from rhyme_engine import RhymeEngine
import sys


def main():
    parser = argparse.ArgumentParser(description="RimerSR CLI - Serbian rhyme suggester")
    parser.add_argument('word', nargs='?', help='Word to find rhymes for')
    parser.add_argument('--file', type=str, help='Path to lyrics file')
    parser.add_argument('--syllables', type=int, default=2, help='Number of syllables from end (1-3)')
    parser.add_argument('--max', type=int, default=50, help='Maximum number of results')
    parser.add_argument('--dict', type=str, help='Custom dictionary path')
    parser.add_argument('--cyrillic', action='store_true', help='Show Cyrillic output')
    
    args = parser.parse_args()
    
    if not args.word and not args.file:
        parser.print_help()
        sys.exit(1)
    
    dict_path = Path(args.dict) if args.dict else None
    engine = RhymeEngine(dict_path)
    
    try:
        engine.load_dictionary()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.word:
        process_word(engine, args.word, args.syllables, args.max, args.cyrillic)
    
    if args.file:
        process_file(engine, args.file, args.syllables, args.max, args.cyrillic)


def process_word(engine, word, syllables, max_results, show_cyrillic):
    print(f"Finding rhymes for: {word}")
    print(f"Syllables: {syllables}, Max results: {max_results}")
    print("-" * 60)
    
    rhymes = engine.find_rhymes(word, syllables=syllables, max_results=max_results)
    
    if not rhymes:
        print("No rhymes found.")
        return
    
    print(f"Found {len(rhymes)} rhymes:\n")
    
    if show_cyrillic:
        print(f"{'Latin':<30} {'Cyrillic':<30}")
        print("=" * 60)
        for rhyme in rhymes:
            cyrillic = engine.transliterate_to_cyrillic(rhyme)
            print(f"{rhyme:<30} {cyrillic:<30}")
    else:
        for rhyme in rhymes:
            print(rhyme)


def process_file(engine, filepath, syllables, max_results, show_cyrillic):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing file: {filepath}")
    print(f"Syllables: {syllables}, Max results: {max_results}")
    print("=" * 60)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        words = line.split()
        if not words:
            continue
        
        last_word = words[-1]
        
        print(f"\nLine: {line}")
        print(f"Last word: {last_word}")
        print("-" * 60)
        
        rhymes = engine.find_rhymes(last_word, syllables=syllables, max_results=max_results)
        
        if rhymes:
            display_rhymes = rhymes[:10]
            if show_cyrillic:
                latin_str = ", ".join(display_rhymes)
                cyrillic_rhymes = [engine.transliterate_to_cyrillic(r) for r in display_rhymes]
                cyrillic_str = ", ".join(cyrillic_rhymes)
                print(f"Latin:    {latin_str}")
                print(f"Cyrillic: {cyrillic_str}")
            else:
                print(", ".join(display_rhymes))
        else:
            print("No rhymes found.")


if __name__ == "__main__":
    main()
