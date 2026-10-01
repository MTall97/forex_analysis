#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rejoue chaque trade lu sur les captures (data/captures_niveaux.csv) avec les bougies réelles
de Dukascopy, pour savoir ce qu'un abonné aurait obtenu en suivant le plan publié.

Règles de simulation (prix BID, sans spread ni commission) :
1. Dédoublonnage : une même position (paire, entrée et stop identiques à 0,05 % près,
   dans les 10 jours) n'est gardée qu'une fois, à sa première publication.
2. Départ = date de publication lue sur la capture (sinon date du message Telegram).
3. Si, au moment de la publication, le prix est déjà au-delà de l'objectif, du stop, ou en gain
   latent de plus d'un demi-risque, la capture a été faite après l'entrée : trade « après coup »,
   non copiable. On le rejoue depuis le dernier passage à l'entrée pour connaître son issue,
   mais il est exclu des statistiques « copiables ».
4. Sinon, si le prix est à moins d'un quart de risque de l'entrée, c'est un ordre au marché
   (entrée immédiate) ; sinon un ordre en attente qui doit toucher l'entrée (7 jours maximum) :
   - objectif atteint avant l'entrée -> « non déclenché (objectif atteint sans entrée) » ;
   - rien après 5 jours -> « non déclenché ».
5. Une fois déclenché : le premier niveau touché (objectif ou stop) décide. Si les deux sont
   touchés dans la même heure, on descend aux bougies d'une minute ; si c'est encore
   ambigu, on compte le stop (hypothèse prudente). Sans issue après 20 jours de bourse :
   « ouvert », résultat mesuré au dernier prix.
Résultat en R : +gain/risque si objectif, -1 si stop, valeur latente si ouvert.
gain_max_r : meilleur gain latent atteint avant la sortie (sert à estimer l'effet des passages à BE,
que la simulation n'applique pas).

Données : par défaut Yahoo Finance (scripts/prix_yahoo.py) : bougies horaires depuis mi-décembre
2023, journalières avant (colonne « resolution » ; en journalier, une bougie qui touche à la fois
l'objectif et le stop compte comme un stop). Variable SOURCE_PRIX=dukascopy pour utiliser
https://datafeed.dukascopy.com (horaire + minute, mais très limité en débit depuis le cloud).
Sortie : data/trades_simules.csv
"""

import csv
import lzma
import os
import socket
import struct
import time
import urllib.request
from datetime import datetime, timedelta

CACHE = 'data/prix/dukascopy'
socket.setdefaulttimeout(30)
BASE = 'https://datafeed.dukascopy.com/datafeed'


def echelle(paire):
    return 1e3 if paire.endswith('JPY') or paire.startswith('XAU') else 1e5


def telecharger(url, fichier):
    """Télécharge avec un débit réduit (Dukascopy coupe les connexions trop rapprochées)."""
    if os.path.exists(fichier):
        return open(fichier, 'rb').read()
    for essai in range(8):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            os.makedirs(os.path.dirname(fichier), exist_ok=True)
            open(fichier, 'wb').write(data)
            time.sleep(2.5)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                os.makedirs(os.path.dirname(fichier), exist_ok=True)
                open(fichier, 'wb').write(b'')
                return b''
            time.sleep(15 * (essai + 1))
        except Exception:
            time.sleep(15 * (essai + 1))
    print(f"  [!] échec du téléchargement : {url}", flush=True)
    return b''


def decoder(data, debut, paire):
    """Bougies (datetime, ouverture, haut, bas, clôture)."""
    if not data:
        return []
    raw = lzma.decompress(data)
    k = echelle(paire)
    out = []
    for i in range(len(raw) // 24):
        t, o, c, l, h, v = struct.unpack('>5if', raw[i * 24:(i + 1) * 24])
        if v > 0:
            out.append((debut + timedelta(seconds=t), o / k, h / k, l / k, c / k))
    return out


def heures(paire, an, mois):
    f = f"{CACHE}/{paire}/{an}-{mois:02d}_h1.bi5"
    return decoder(telecharger(f"{BASE}/{paire}/{an}/{mois - 1:02d}/BID_candles_hour_1.bi5", f),
                   datetime(an, mois, 1), paire)


def minutes(paire, jour):
    f = f"{CACHE}/{paire}/{jour:%Y-%m-%d}_m1.bi5"
    return decoder(telecharger(f"{BASE}/{paire}/{jour.year}/{jour.month - 1:02d}/{jour.day:02d}/BID_candles_min_1.bi5", f),
                   datetime(jour.year, jour.month, jour.day), paire)


SOURCE = os.environ.get('SOURCE_PRIX', 'yahoo')  # « yahoo » (par défaut) ou « dukascopy »


def serie_horaire(paire, debut, fin):
    """Bougies horaires (journalières avant mi-décembre 2023 avec Yahoo)."""
    if SOURCE == 'yahoo':
        import prix_yahoo
        return prix_yahoo.bougies(paire, debut, fin)
    out, d = [], datetime(debut.year, debut.month, 1)
    while d <= fin:
        out += heures(paire, d.year, d.month)
        d = (d + timedelta(days=32)).replace(day=1)
    return [b for b in out if debut <= b[0] <= fin]


def touche(b, niveau):
    return b[3] <= niveau <= b[2]


def simuler(paire, sens, e, sl, tp, depart):
    achat = sens == 'achat'
    risque = abs(e - sl)
    if risque == 0:
        return None
    rr = abs(tp - e) / risque
    avant = serie_horaire(paire, depart - timedelta(hours=72), depart)
    apres = serie_horaire(paire, depart, depart + timedelta(days=40))
    if resolution_prix(paire, depart) == '1d':
        # bougie journalière : celle du jour de publication contient des prix postérieurs
        avant = [b for b in avant if b[0] + timedelta(days=1) <= depart]
        apres = serie_horaire(paire, datetime(depart.year, depart.month, depart.day), depart + timedelta(days=40))
    if not apres or not avant:
        return None
    prix = avant[-1][4]                       # dernier prix connu à la publication
    if resolution_prix(paire, depart) == '1d' and apres:
        prix = apres[0][1]                    # en journalier : ouverture du jour de publication
    gain_latent = ((prix - e) if achat else (e - prix)) / risque
    deja_tp = (prix >= tp) if achat else (prix <= tp)
    deja_sl = (prix <= sl) if achat else (prix >= sl)
    statut = 'annoncé'
    touche_recent = any(touche(b, e) for b in avant if b[0] >= depart - timedelta(hours=12))
    if deja_sl:
        return dict(statut='incohérent', issue='prix déjà au-delà du stop', r='', rr=rr, entree_utc='', sortie_utc='', mfe_r='')
    if deja_tp or (touche_recent and gain_latent > 0.5):
        # le prix a déjà dépassé l'entrée de plus d'un demi-risque : capture faite après l'entrée
        statut = 'après coup'
        entree_t = next((b[0] for b in reversed(avant) if touche(b, e)), None)
        if entree_t is None and deja_tp:
            return dict(statut=statut, issue='objectif déjà dépassé à la publication', r='', rr=rr,
                        entree_utc='', sortie_utc='', mfe_r='')
        if entree_t is None:
            return dict(statut=statut, issue='entrée antérieure aux données', r='', rr=rr, entree_utc='', sortie_utc='')
        seq = [b for b in avant if b[0] >= entree_t] + apres
    else:
        entree_t = None
        en_marche = abs(gain_latent) <= 0.25  # ordre au prix du marché
        limite = depart + timedelta(days=7)
        for b in apres:
            if en_marche:
                entree_t = depart
                break
            if b[0] > limite:
                break
            if touche(b, e):
                entree_t = b[0]
                break
            if (achat and b[2] >= tp) or (not achat and b[3] <= tp):
                return dict(statut=statut, issue='non déclenché (objectif atteint sans entrée)', r='', rr=rr,
                            entree_utc='', sortie_utc=b[0].isoformat())
        if entree_t is None:
            return dict(statut=statut, issue='non déclenché', r='', rr=rr, entree_utc='', sortie_utc='')
        seq = [b for b in apres if b[0] >= entree_t]
    fin = entree_t + timedelta(days=28)
    mfe = 0.0
    for b in seq:
        if b[0] > fin:
            break
        hit_tp = (b[2] >= tp) if achat else (b[3] <= tp)
        hit_sl = (b[3] <= sl) if achat else (b[2] >= sl)
        if hit_tp and hit_sl and SOURCE == 'dukascopy':
            for m in minutes(paire, b[0]):
                if not (b[0] <= m[0] < b[0] + timedelta(hours=1)):
                    continue
                mt = (m[2] >= tp) if achat else (m[3] <= tp)
                ms = (m[3] <= sl) if achat else (m[2] >= sl)
                if ms:
                    hit_tp = False
                    break
                if mt:
                    hit_sl = False
                    break
        if hit_tp and hit_sl:
            hit_tp = False  # ambigu dans la même bougie : hypothèse prudente
        if hit_sl:
            return dict(statut=statut, issue='stop', r=-1.0, rr=rr, entree_utc=entree_t.isoformat(),
                        sortie_utc=b[0].isoformat(), mfe_r=round(mfe, 2))
        if hit_tp:
            return dict(statut=statut, issue='objectif', r=round(rr, 2), rr=rr, entree_utc=entree_t.isoformat(),
                        sortie_utc=b[0].isoformat(), mfe_r=round(rr, 2))
        mfe = max(mfe, ((b[2] - e) if achat else (e - b[3])) / risque)
    dernier = [b for b in seq if b[0] <= fin][-1]
    latent = ((dernier[4] - e) if achat else (e - dernier[4])) / risque
    return dict(statut=statut, issue='ouvert après 20 jours', r=round(latent, 2), rr=rr,
                entree_utc=entree_t.isoformat(), sortie_utc=dernier[0].isoformat(), mfe_r=round(mfe, 2))


def resolution_prix(paire, date):
    if SOURCE == 'yahoo':
        import prix_yahoo
        return prix_yahoo.resolution(paire, date)
    return '1h'


def main():
    lignes = list(csv.DictReader(open('data/captures_trades.csv', encoding='utf-8')))
    vus, trades = [], []
    for l in lignes:
        if not (l['paire'] and l['entree'] and l['stop'] and l['objectif'] and l['sens']):
            continue
        e, sl, tp = float(l['entree']), float(l['stop']), float(l['objectif'])
        achat = l['sens'] == 'achat'
        if (achat and not (sl < e < tp)) or (not achat and not (tp < e < sl)):
            continue  # lecture incohérente
        depart = datetime.fromisoformat(l['publication_utc'] or l['date_message'])
        if abs((depart - datetime.fromisoformat(l['date_message'])).days) > 3:
            depart = datetime.fromisoformat(l['date_message'])  # date OCR douteuse
        doublon = any(v[0] == l['paire'] and abs(v[1] - e) / e < 5e-4 and abs(v[2] - sl) / e < 5e-4
                      and abs((depart - v[3]).days) <= 10 for v in vus)
        if doublon:
            continue
        vus.append((l['paire'], e, sl, depart))
        trades.append((l, e, sl, tp, depart))
    out = []
    for n, (l, e, sl, tp, depart) in enumerate(trades, 1):
        try:
            res = simuler(l['paire'], l['sens'], e, sl, tp, depart)
        except Exception as ex:  # données manquantes
            res = None
        if res:
            out.append({'date_publication': depart.isoformat(), 'id_message': l['id_message'], 'paire': l['paire'],
                        'sens': l['sens'], 'entree': e, 'stop': sl, 'objectif': tp, 'ratio_rr': round(res['rr'], 2),
                        'statut': res['statut'], 'resolution': resolution_prix(l['paire'], depart), 'issue': res['issue'], 'resultat_r': res['r'], 'gain_max_r': res.get('mfe_r', ''),
                        'entree_utc': res['entree_utc'], 'sortie_utc': res['sortie_utc'], 'capture': l['fichier']})
        if n % 50 == 0:
            print(f"  {n}/{len(trades)}", flush=True)
    with open('data/trades_simules.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} trades simulés -> data/trades_simules.csv")


if __name__ == '__main__':
    main()
