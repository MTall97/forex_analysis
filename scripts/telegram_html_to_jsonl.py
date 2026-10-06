#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertit un export HTML Telegram (messages*.html) en un fichier JSONL
(un message par ligne), sans dépendance externe.

Champs : id, date_utc, text, photo, media, reply_to, forwarded_from

Usage :
    python scripts/telegram_html_to_jsonl.py ChatExport_2026-10-01 data/telegram_messages.jsonl
"""

import glob
import json
import os
import re
import sys
from datetime import datetime
from html.parser import HTMLParser


class TelegramExportParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.messages = []
        self.cur = None
        self.capture = None      # 'text' | 'forwarded' | None
        self.depth = 0           # profondeur de <div> à l'intérieur du bloc capturé
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '') or ''
        if tag == 'div' and cls.startswith('message default'):
            self.cur = {'id': int(a['id'].replace('message', '')), 'date_utc': None, 'text': '',
                        'photo': None, 'media': None, 'reply_to': None, 'forwarded_from': None}
            self.messages.append(self.cur)
            return
        if tag == 'div' and cls.startswith('message service'):
            self.cur = None
            return
        if self.cur is None:
            return
        if self.capture:
            if tag == 'div':
                self.depth += 1
            elif tag == 'br':
                self.buf.append('\n')
            return
        if tag == 'div' and 'date details' in cls and a.get('title') and self.cur['date_utc'] is None:
            m = re.match(r'(\d\d)\.(\d\d)\.(\d{4}) (\d\d:\d\d:\d\d)', a['title'])
            if m:
                self.cur['date_utc'] = f"{m.group(3)}-{m.group(2)}-{m.group(1)}T{m.group(4)}"
        elif tag == 'div' and cls == 'text':
            self.capture, self.depth, self.buf = 'text', 0, []
        elif tag == 'div' and cls == 'from_name' and self.cur.get('_fwd'):
            self.capture, self.depth, self.buf = 'forwarded', 0, []
        elif tag == 'div' and cls == 'forwarded body':
            self.cur['_fwd'] = True
        elif tag == 'a' and 'photo_wrap' in cls:
            self.cur['photo'] = a.get('href')
        elif tag == 'div' and cls.startswith('media clearfix'):
            self.cur['media'] = cls.split()[-1].replace('media_', '')
        elif tag == 'a' and a.get('href', '').startswith('#go_to_message'):
            self.cur['reply_to'] = int(a['href'].replace('#go_to_message', ''))

    def handle_endtag(self, tag):
        if self.capture and tag == 'div':
            if self.depth == 0:
                txt = ''.join(self.buf).strip()
                txt = re.sub(r'[ \t]*\n[ \t]*', '\n', txt)
                if self.capture == 'text':
                    self.cur['text'] = (self.cur['text'] + '\n' + txt).strip()
                else:
                    self.cur['forwarded_from'] = re.sub(r'\s+', ' ', txt)
                self.capture = None
            else:
                self.depth -= 1

    def handle_data(self, data):
        if self.capture:
            self.buf.append(data)


def page_key(path):
    m = re.search(r'messages(\d*)\.html$', path)
    return int(m.group(1) or 1)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'ChatExport_2026-10-01'
    out = sys.argv[2] if len(sys.argv) > 2 else 'data/telegram_messages.jsonl'
    parser = TelegramExportParser()
    for f in sorted(glob.glob(os.path.join(src, 'messages*.html')), key=page_key):
        with open(f, encoding='utf-8') as fh:
            parser.feed(fh.read())

    # Les messages "joined" n'ont pas toujours d'horodatage complet : on hérite du précédent
    last = None
    for m in parser.messages:
        m.pop('_fwd', None)
        if m['date_utc'] is None:
            m['date_utc'] = last
        last = m['date_utc']

    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        for m in parser.messages:
            fh.write(json.dumps(m, ensure_ascii=False) + '\n')
    print(f"{len(parser.messages)} messages -> {out} "
          f"({parser.messages[0]['date_utc']} .. {parser.messages[-1]['date_utc']})")


if __name__ == '__main__':
    main()
