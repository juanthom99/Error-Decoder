"""Explicitly authored troubleshooting cases, not a Cartesian product of templates.

Rows contain title, contextual example, explanation/cause, and actionable fix.
Examples are illustrative diagnostics; exact wording depends on library version.
The context line disambiguates failures that share the same exception message.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def expanded_entries():
    entries = []
    for category in ('python', 'pandas', 'pip', 'fastapi'):
        topic = None
        for line in (ROOT / 'corpus' / f'{category}.txt').read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#'):
                continue
            if line.startswith('@'):
                topic = line[1:]
                continue
            title, diagnostic, explanation, cause, fix = line.split('|')
            assert topic and all((title, diagnostic, explanation, cause, fix)), line
            entries.append({'title': title, 'example_error': diagnostic.replace('\\n', '\n'), 'explanation': explanation, 'likely_cause': cause, 'fix': fix, 'tags': [category, topic], 'example_kind': 'illustrative contextual diagnostic'})
    return entries
