#!/usr/bin/env python3
"""
A script to transform wordlists based on custom character replacement rules.
"""

import argparse
import sys
import re

def apply_rules(word, rules, case_insensitive=False):
    """
    Apply the specified rules to the word.
    
    If case_insensitive is True, character matching will ignore case.
    """
    result = word
    for rule in rules:
        if rule["type"] == "replace":
            # Standard replacement rule
            char = rule["char"]
            instance = rule["instance"]
            replacement = rule["replacement"]
            
            if instance == "all":
                if case_insensitive:
                    # Case-insensitive replacement for all instances
                    pattern = re.compile(re.escape(char), re.IGNORECASE)
                    result = pattern.sub(replacement, result)
                else:
                    # Case-sensitive replacement
                    result = result.replace(char, replacement)
            else:
                # Find the nth instance of the character
                count = 0
                new_result = ""
                
                if case_insensitive:
                    # For case-insensitive matching, we'll compare lowercase versions
                    char_lower = char.lower()
                    for c in result:
                        if c.lower() == char_lower:
                            count += 1
                            if count == instance:
                                new_result += replacement
                            else:
                                new_result += c
                        else:
                            new_result += c
                else:
                    # Case-sensitive matching (original behavior)
                    for c in result:
                        if c == char:
                            count += 1
                            if count == instance:
                                new_result += replacement
                            else:
                                new_result += c
                        else:
                            new_result += c
                        
                result = new_result
        elif rule["type"] == "case_transform":
            # Case transformation rule (upper/lower)
            operation = rule["operation"]
            
            if rule["target_type"] == "position":
                # Transform character at specific position
                position = rule["position"]
                
                if position <= len(result):
                    # Apply the case transformation
                    chars = list(result)
                    if operation == "upper":
                        chars[position-1] = chars[position-1].upper()
                    elif operation == "lower":
                        chars[position-1] = chars[position-1].lower()
                    result = ''.join(chars)
            else:  # target_type == "character"
                # Transform specific instance of a character
                char = rule["char"]
                instance = rule["instance"]
                
                # Find the nth instance of the character
                count = 0
                new_result = ""
                
                if case_insensitive and char:
                    # Case-insensitive matching
                    char_lower = char.lower()
                    for c in result:
                        if c.lower() == char_lower:
                            count += 1
                            if count == instance:
                                if operation == "upper":
                                    new_result += c.upper()
                                elif operation == "lower":
                                    new_result += c.lower()
                            else:
                                new_result += c
                        else:
                            new_result += c
                elif char:  # Case-sensitive matching
                    for c in result:
                        if c == char:
                            count += 1
                            if count == instance:
                                if operation == "upper":
                                    new_result += c.upper()
                                elif operation == "lower":
                                    new_result += c.lower()
                            else:
                                new_result += c
                        else:
                            new_result += c
                
                if count > 0:  # Only update if the character was found
                    result = new_result
    
    return result

def split_escaped_delimiters(text, delimiter="||"):
    """Split a string by delimiter, respecting escape sequences."""
    # Use regex to split by delimiter but not when preceded by backslash
    # Using negative lookbehind (?<!\\) to ensure the || is not preceded by \
    parts = re.split(r'(?<!\\)\|\|', text)
    # Replace escaped delimiters with the actual delimiter
    return [part.replace(f"\\{delimiter}", delimiter).strip() for part in parts]

def parse_single_rule(rule_text):
    """Parse a single rule definition."""
    parts = rule_text.split()
    
    # Check for position-based case transformation: "pos X upper/lower"
    if len(parts) == 3 and parts[0].lower() == "pos":
        try:
            position = int(parts[1])
            operation = parts[2].lower()
            
            if operation in ["upper", "u", "lower", "l"]:
                # Normalize operation name
                if operation in ["u", "upper"]:
                    operation = "upper"
                else:
                    operation = "lower"
                
                return {
                    "type": "case_transform",
                    "target_type": "position",
                    "position": position,
                    "operation": operation
                }
            else:
                print(f"Warning: Invalid operation: {operation}")
                return None
        except ValueError:
            print(f"Warning: Invalid position value: {parts[1]}")
            return None
    
    # Check for character-based case transformation: "char instance upper/lower"
    elif len(parts) == 3 and parts[2].lower() in ["upper", "u", "lower", "l"]:
        char = parts[0]
        instance_str = parts[1]
        operation = parts[2].lower()
        
        # Normalize operation name
        if operation in ["u", "upper"]:
            operation = "upper"
        else:
            operation = "lower"
        
        if instance_str.lower() == "all":
            print("Warning: 'all' not supported for case transformation. Use multiple rules instead.")
            return None
        else:
            try:
                instance = int(instance_str)
                return {
                    "type": "case_transform",
                    "target_type": "character",
                    "char": char,
                    "instance": instance,
                    "operation": operation
                }
            except ValueError:
                print(f"Warning: Invalid instance value: {instance_str}")
                return None
    
    # Standard replacement rule: "char instance replacement"
    elif len(parts) >= 3:
        char = parts[0]
        instance = parts[1]
        replacement = parts[2]
        
        if instance.lower() == "all":
            return {
                "type": "replace",
                "char": char,
                "instance": "all",
                "replacement": replacement
            }
        else:
            try:
                instance = int(instance)
                return {
                    "type": "replace",
                    "char": char,
                    "instance": instance,
                    "replacement": replacement
                }
            except ValueError:
                print(f"Warning: Invalid instance value: {instance}")
                return None
    else:
        print(f"Warning: Invalid rule format: {rule_text}")
        return None

def read_rules(rule_file):
    """Read rules from a file, treating each line as a separate ruleset."""
    rulesets = []
    try:
        with open(rule_file, "r") as f:
            for line in f:
                # Skip comments and empty lines
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Split line by || delimiter (respecting escape sequences)
                rule_parts = split_escaped_delimiters(line)
                
                # Process each rule part for this ruleset
                ruleset = []
                for rule_text in rule_parts:
                    rule = parse_single_rule(rule_text)
                    if rule:
                        ruleset.append(rule)
                
                if ruleset:
                    rulesets.append(ruleset)
    except FileNotFoundError:
        print(f"Error: Rule file '{rule_file}' not found.")
        sys.exit(1)
    
    return rulesets

def main():
    parser = argparse.ArgumentParser(description="Apply rules to a wordlist.")
    parser.add_argument("--wordlist", "-w", help="The wordlist file")
    parser.add_argument("--rules", "-r", help="File containing rules")
    parser.add_argument("--output", "-o", help="Output file for generated words")
    parser.add_argument("--detail", action="store_true", 
                        help="Include detailed transformation information in output")
    parser.add_argument("--case-insensitive", "-i", action="store_true",
                        help="Make character matching case-insensitive")
    args = parser.parse_args()
    
    # Read wordlist
    try:
        with open(args.wordlist, "r") as f:
            words = [word.strip() for word in f.readlines()]
    except FileNotFoundError:
        print(f"Error: Wordlist file '{args.wordlist}' not found.")
        sys.exit(1)
    
    # Read or define rulesets
    if args.rules:
        rulesets = read_rules(args.rules)
    else:
        # Interactive mode
        print("No ruleset provided. Entering interactive mode.")
        rulesets = []
        print("Enter rules in format: 'char instance replacement'")
        print("  - 'char' is the character to replace")
        print("  - 'instance' is the occurrence (1, 2, etc.) or 'all'")
        print("  - 'replacement' is what to replace it with")
        print("Example: 'o 1 0' replaces first 'o' with '0'")
        print("You can also define multiple rules on one line using '||' as a delimiter")
        print("Example: 'o 1 0 || e all 3 || s 2 $'")
        print("Use backslash to escape the delimiter: 'text \\|| more'")
        print("Each line you enter will be treated as a separate ruleset.")
        
        while True:
            rule_input = input("Enter a ruleset (or 'done' to finish): ")
            if rule_input.lower() == "done":
                break
            
            # Split by delimiter and parse each rule for this ruleset
            ruleset = []
            rule_parts = split_escaped_delimiters(rule_input)
            for rule_text in rule_parts:
                rule = parse_single_rule(rule_text)
                if rule:
                    ruleset.append(rule)
            
            if ruleset:
                rulesets.append(ruleset)
    
    # Apply each ruleset to all words
    all_generated_words = []
    ruleset_descriptions = []
    
    for ruleset_index, ruleset in enumerate(rulesets, 1):
        # Create a description of this ruleset for output
        ruleset_desc = []
        for rule in ruleset:
            if rule["type"] == "replace":
                char = rule["char"]
                instance = rule["instance"]
                replacement = rule["replacement"]
                ruleset_desc.append(f"{char} {instance} {replacement}")
            elif rule["type"] == "case_transform":
                operation = rule["operation"]
                if rule["target_type"] == "position":
                    position = rule["position"]
                    ruleset_desc.append(f"pos {position} {operation}")
                else:  # target_type == "character"
                    char = rule["char"]
                    instance = rule["instance"]
                    ruleset_desc.append(f"{char} {instance} {operation}")
        
        ruleset_description = " || ".join(ruleset_desc)
        ruleset_descriptions.append(ruleset_description)
        
        # Apply this ruleset to each word
        for word in words:
            new_word = apply_rules(word, ruleset, case_insensitive=args.case_insensitive)
            all_generated_words.append({
                "original": word,
                "transformed": new_word,
                "ruleset_index": ruleset_index,
                "ruleset": ruleset_description
            })
    
    # Output results
    if args.output:
        try:
            with open(args.output, "w") as f:
                # If detail flag is set, include ruleset information
                if args.detail:
                    # Write header with ruleset information
                    f.write("# Generated words by ruleset:\n")
                    for idx, desc in enumerate(ruleset_descriptions, 1):
                        f.write(f"# Ruleset {idx}: {desc}\n")
                    f.write("#\n")
                    
                    # Write all generated words with original word and ruleset info
                    for item in all_generated_words:
                        f.write(f"{item['transformed']} | Ruleset {item['ruleset_index']}\n")
                else:
                    # Just write the transformed words without additional info
                    for item in all_generated_words:
                        f.write(f"{item['transformed']}\n")
                
                # Only create summary file if detail flag is set
                if args.detail:
                    summary_file = args.output + ".summary.txt"
                    with open(summary_file, "w") as sf:
                        sf.write("Original Word | Transformed Word | Ruleset\n")
                        sf.write("------------- | --------------- | ------\n")
                        for item in all_generated_words:
                            sf.write(f"{item['original']} | {item['transformed']} | {item['ruleset']}\n")
                    print(f"Generated words written to {args.output}")
                    print(f"Summary information written to {summary_file}")
                else:
                    print(f"Generated words written to {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
    else:
        # Print to console - adjust format based on detail flag
        if args.detail:
            for idx, desc in enumerate(ruleset_descriptions, 1):
                print(f"\nRuleset {idx}: {desc}")
                print("-" * 40)
                
                # Print words for this ruleset with details
                for item in all_generated_words:
                    if item["ruleset_index"] == idx:
                        print(f"{item['original']} -> {item['transformed']}")
        else:
            # Just print the transformed words
            for item in all_generated_words:
                print(item['transformed'])

if __name__ == "__main__":
    main()
