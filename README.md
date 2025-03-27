# PasswordForge

A powerful tool for transforming wordlists using customizable and instance specific character replacement rules.

## Introduction

PasswordForge was born out of necessity when I discovered a limitation in existing password cracking tools like hashcat. While hashcat offers powerful rule-based transformations, I found it challenging to target specific instances of characters within a password—for example, changing only the third occurrence of a particular letter.

As a curious security researcher I wanted to test some of my basic on-the-fly passwords. I noticed that my personal password creation patterns consistently evaded standard hashcat rulesets, even when I attempted to create custom rules.

Rather than a replacement for tools like hashcat, PasswordForge serves as a complementary utility that excels at instance-specific transformations. It's especially valuable for further refining wordlists already generated by other tools, allowing for more targeted password cracking attempts.

I welcome feedback and suggestions from the security community as we all work toward better security testing methodologies. Whether I missed something in hashcat or created something genuinely new, I hope this tool proves useful to fellow security professionals.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Rule Syntax](#rule-syntax)
  - [Character Replacement](#character-replacement)
  - [Case Transformation](#case-transformation)
  - [Multiple Rules and Escaping](#multiple-rules-and-escaping)
- [Command Line Options](#command-line-options)
- [Example Transformations](#example-transformations)
- [Output Formats](#output-formats)
- [Interactive Mode](#interactive-mode)
- [Use Cases](#use-cases)
- [Tips and Best Practices](#tips-and-best-practices)

## Overview

PasswordForge is a Python utility designed to transform wordlists using customizable rules. It's particularly useful for:

- Creating variations of passwords for security testing
- Generating wordlists for dictionary attacks
- Creating custom wordlists for specific scenarios

By applying rule-based transformations, you can easily convert simple wordlists into targeted, customized variations.

## Installation

PasswordForge doesn't require any external dependencies beyond Python 3.x:

```bash
# Download the script
# Make it executable (Linux/macOS)
chmod +x passwordForge.py

## Basic Usage

The basic syntax for using PasswordForge is:

```bash
python passwordForge.py --wordlist your_wordlist.txt --rules your_rules.pfrule --output transformed_words.txt
```

Or using the short form:

```bash
python passwordForge.py -w your_wordlist.txt -r your_rules.pfrule -o transformed_words.txt
```

## Rule Syntax

### Character Replacement

The most basic form of rule is character replacement:

```
char instance replacement
```

Where:
- `char` is the character to replace
- `instance` is which occurrence to replace (a number or "all")
- `replacement` is what to replace it with

Examples:

```
o 1 0        # Replace first 'o' with '0'
e all 3      # Replace all 'e's with '3'
a 2 @        # Replace second 'a' with '@'
```

### Case Transformation

PasswordForge supports two types of case transformations:

**Position-based transformation:**
```
pos position upper/lower
```

Examples:
```
pos 1 upper  # Capitalize the first character
pos 3 lower  # Lowercase the third character
```

**Character-based transformation:**
```
char instance upper/lower
```

Examples:
```
o 2 upper    # Uppercase the second 'o'
e 1 lower    # Lowercase the first 'e'
```

You can use shorthand `u` for upper and `l` for lower:
```
e 1 u        # Same as 'e 1 upper'
```

### Multiple Rules and Escaping

You can combine multiple rules on a single line using the `||` delimiter:

```
o 1 0 || e all 3 || s 2 $
```

This will:
1. Replace the first 'o' with '0'
2. Replace all 'e's with '3'
3. Replace the second 's' with '$'

If you need to use the `||` characters as a replacement, escape them with a backslash:

```
t 1 \||      # Replace first 't' with '||'
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--wordlist` | `-w` | Input wordlist file |
| `--rules` | `-r` | File containing transformation rules |
| `--output` | `-o` | Output file for transformed words |
| `--detail` | | Include detailed transformation information in output |
| `--case-insensitive` | `-i` | Make character matching case-insensitive |

## Example Transformations

Given a word like "password":

| Rule | Result | Explanation |
|------|--------|-------------|
| `a 1 @` | `p@ssword` | First 'a' becomes '@' |
| `o 1 0 \|\| r 1 R` | `passw0Rd` | First 'o' becomes '0', first 'r' becomes 'R' |
| `pos 1 upper` | `Password` | First character capitalized |
| `s 1 $ \|\| s 2 5` | `pa$5word` | First 's' becomes '$', second 's' becomes '5' |

## Output Formats

PasswordForge offers two output formats:

### Standard Output

By default, PasswordForge outputs just the transformed words:

```
p@ssword
passw0rd
Password
```

### Detailed Output

With the `--detail` flag, you get more information:

```
# Generated words by ruleset:
# Ruleset 1: a 1 @
# Ruleset 2: o 1 0
# Ruleset 3: pos 1 upper
#
p@ssword | Ruleset 1
passw0rd | Ruleset 2
Password | Ruleset 3
```

Additionally, a summary file is created with the `.summary.txt` extension:

```
Original Word | Transformed Word | Ruleset
------------- | --------------- | ------
password | p@ssword | a 1 @
password | passw0rd | o 1 0
password | Password | pos 1 upper
```

## Interactive Mode

If you don't provide a rule file, PasswordForge enters interactive mode:

```bash
python passwordForge.py --wordlist words.txt
```

This allows you to enter rules one by one and see the results immediately:

```
No ruleset provided. Entering interactive mode.
Enter rules in format: 'char instance replacement'
  - 'char' is the character to replace
  - 'instance' is the occurrence (1, 2, etc.) or 'all'
  - 'replacement' is what to replace it with
Example: 'o 1 0' replaces first 'o' with '0'
You can also define multiple rules on one line using '||' as a delimiter
Example: 'o 1 0 || e all 3 || s 2 $'
Use backslash to escape the delimiter: 'text \|| more'
Each line you enter will be treated as a separate ruleset.

Enter a ruleset (or 'done' to finish): 
```

## Use Cases

1. **Password Auditing**
   - Create variations of existing passwords to test password policies
   - Generate common password variations to improve security awareness

2. **Penetration Testing**
   - Generate targeted wordlists for specific organizations
   - Create custom dictionaries for brute-force attacks

3. **Data Generation**
   - Create test data with specific patterns
   - Generate username variations for discovery

4. **Language Processing**
   - Create variations of words for natural language processing
   - Generate phonetic alternatives for words

## Tips and Best Practices

1. **Start Simple**
   - Begin with single transformations, then combine them
   - Test your rules on a small sample wordlist first

2. **Use Case-Insensitive Matching When Appropriate**
   - The `-i` flag makes character matching case-insensitive
   - Useful when you want to transform both uppercase and lowercase variants

3. **Organize Rules Logically**
   - Group related rules together in your rule file
   - Use comments (`#`) to explain complex transformations

4. **Watch for Edge Cases**
   - Be aware of how rules interact with different word lengths
   - Test transformations on varied wordlists

5. **Save Useful Rulesets**
   - Create libraries of reusable rules for common transformations
   - Name your rule files descriptively (e.g., `leet_speak.pfrule`, `capitalization.pfrule`)

---

PasswordForge makes it easy to create targeted wordlist variations with minimal effort. By mastering the rule syntax and combining transformations, you can generate sophisticated password variations to improve your security testing process.
```markdown
