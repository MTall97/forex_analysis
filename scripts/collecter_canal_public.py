#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Récupère les messages récents du canal public d'Amirou (https://t.me/thehalalwinningteam) par sa version web
(https://t.me/s/thehalalwinningteam), sans export Telegram : les identifiants sont les mêmes que dans l'export
(vérifié : #13798 a le même texte et la même heure UTC dans les deux).

Les messages postérieurs au dernier id de data/telegram_messages.jsonl y sont ajoutés, au même format
(id, date_utc, text, photo, media, reply_to, forwarded_from), avec "source": "web". Les photos sont téléchargées dans
canal_public/photos/<id>.jpg (non suivi par Git, comme les autres photos du canal). Les vidéos sont notées
("media": "video") mais pas téléchargées.

Limites : la version web ne montre ni les réponses (reply_to) de façon fiable ni les messages supprimés ; le texte
est reconstruit depuis le HTML (sauts de ligne conservés).
Usage : python scripts/collecter_canal_public.py
"""
import html
import json
import os
import re
import subprocess
import time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
CANAL = 'thehalalwinningteam'
JSONL = 'data/telegram_messages.jsonl'
PHOTOS = 'canal_public/photos'


def get(url):
    for i in range(4):
        r = subprocess.run(['curl', '-s', '-f', '-L', url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(2 ** i)
    return b''


def texte(fragment):
    fragment = re.sub(r'<br\s*/?>', '\n', fragment)
    fragment = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', lambda m: m.group(2), fragment, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def messages(page):
    blocs = re.split(r'(?=<div class="tgme_widget_message_wrap)', page)
    for b in blocs:
        m = re.search(rf'data-post="{CANAL}/(\d+)"', b)
        if not m:
            continue
        i = int(m.group(1))
        d = re.search(r'<time datetime="([^"]+)"', b)
        t = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', b, re.S)
        fw = re.search(r'tgme_widget_message_forwarded_from_name[^>]*>(?:<span[^>]*>)?(.*?)</', b, re.S)
        photos = re.findall(r"tgme_widget_message_photo_wrap[^>]*background-image:url\('([^']+)'\)", b)
        video = 'tgme_widget_message_video' in b or 'tgme_widget_message_roundvideo' in b
        yield dict(id=i, date_utc=d.group(1)[:19] if d else None, text=texte(t.group(1)) if t else '',
                   photos=photos, video=video, forwarded_from=texte(fw.group(1)) if fw else None)


def main():
    dernier = 0
    for l in open(JSONL, encoding='utf-8'):
        dernier = max(dernier, json.loads(l)['id'])
    os.makedirs(PHOTOS, exist_ok=True)
    nouveaux, apres = {}, dernier
    while True:
        page = get(f'https://t.me/s/{CANAL}?after={apres}').decode('utf-8', 'replace')
        lot = [m for m in messages(page) if m['id'] > apres]
        if not lot:
            break
        for m in lot:
            nouveaux[m['id']] = m
        apres = max(m['id'] for m in lot)
        time.sleep(1)
    lignes = []
    for i in sorted(nouveaux):
        m = nouveaux[i]
        photo = None
        for k, url in enumerate(m['photos'][:1]):
            f = f'{PHOTOS}/{i}.jpg'
            if not os.path.exists(f):
                open(f, 'wb').write(get(url))
            photo = f
        lignes.append(dict(id=i, date_utc=m['date_utc'], text=m['text'], photo=photo,
                           media='video' if m['video'] else None, reply_to=None, forwarded_from=m['forwarded_from'],
                           source='web'))
    with open(JSONL, 'a', encoding='utf-8') as f:
        for x in lignes:
            f.write(json.dumps(x, ensure_ascii=False) + '\n')
    print(f'{len(lignes)} nouveaux messages après #{dernier}' +
          (f" : #{lignes[0]['id']} ({lignes[0]['date_utc']}) → #{lignes[-1]['id']} ({lignes[-1]['date_utc']})" if lignes else ''))


if __name__ == '__main__':
    main()
