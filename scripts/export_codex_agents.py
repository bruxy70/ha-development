#!/usr/bin/env python3
"""Convert Claude role Markdown into project-scoped Codex agents, without model bindings."""
import argparse
import json
from pathlib import Path
import re
import tomllib

def convert(source, destination, prefix=''):
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in sorted(source.glob('*.md')):
        parts = path.read_text().split('---', 2)
        if len(parts) != 3:
            raise ValueError(f'Missing role frontmatter: {path}')
        front, body = parts[1], parts[2].strip()
        # Descriptions may contain unquoted YAML colons or Claude examples.
        match = re.search(r'^description:\s*(.*)$', front, re.M)
        description = match[1].split(' Examples:')[0].strip().strip('"') if match else path.stem
        name = prefix + path.stem.replace('-', '_')
        body = body.replace('TaskCreate/TaskUpdate tools', 'the available task planner or a Markdown checklist')
        body = ('Use the current Codex tools and the project AGENTS.md/CLAUDE.md invariants. '
                'Claude-specific tool labels refer to equivalent current-host capabilities; never invoke Claude. '
                'Use the installed skills by name and preserve project validation and release gates.\n\n' + body)
        text = '\n'.join(f'{k} = {json.dumps(v, ensure_ascii=False)}' for k,v in {
            'name':name, 'description':description, 'developer_instructions':body}.items()) + '\n'
        tomllib.loads(text)
        (destination/(name+'.toml')).write_text(text)
        count += 1
    return count

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('destination',type=Path)
    parser.add_argument('--prefix',default='')
    args=parser.parse_args()
    print(f'Exported {convert(args.source,args.destination,args.prefix)} Codex agents to {args.destination}')
