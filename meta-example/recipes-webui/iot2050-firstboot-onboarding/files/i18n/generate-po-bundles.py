#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

import argparse
import json
from pathlib import Path


def render_bundle(locale_spec):
    language = locale_spec['language']
    direction = locale_spec['languageDirection']
    plural_forms = locale_spec['pluralForms']
    messages = locale_spec.get('messages', {})
    message_items = sorted(messages.items())

    lines = [
        '(function (root) {',
        '  root.cockpit.locale({',
        '    "": {',
        f'      "language": {json.dumps(language, ensure_ascii=False)},',
        f'      "language-direction": {json.dumps(direction, ensure_ascii=False)},',
        f'      "plural-forms": {plural_forms}',
    ]

    if message_items:
        lines.append('    },')
    else:
        lines.append('    }')

    for index, (message_id, translation) in enumerate(message_items):
        comma = ',' if index < len(message_items) - 1 else ''
        lines.append(
            f'    {json.dumps(message_id, ensure_ascii=False)}: [null, {json.dumps(translation, ensure_ascii=False)}]{comma}'
        )

    lines.extend([
        '  });',
        '}(window));',
        '',
    ])

    return '\n'.join(lines)


def write_bundles(source_path, output_dir):
    catalog = json.loads(source_path.read_text(encoding='utf-8'))
    locales = catalog.get('locales', {})
    output_dir.mkdir(parents=True, exist_ok=True)

    for existing_bundle in output_dir.glob('po.*.js'):
        existing_bundle.unlink()

    for locale_name, locale_spec in sorted(locales.items()):
        bundle_path = output_dir / f'po.{locale_name}.js'
        bundle_path.write_text(render_bundle(locale_spec), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Generate po.<locale>.js bundles from a single catalog source.')
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()

    write_bundles(args.source, args.output_dir)


if __name__ == '__main__':
    main()
