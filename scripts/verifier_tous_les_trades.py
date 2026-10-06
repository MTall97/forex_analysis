#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification de tous les trades d'Amirou, mois par mois (mars 2019 - octobre 2026), en croisant :
1. ce que le canal annonce (registre texte data/trades.csv ; plans lus sur les captures :
   data/trades_simules.csv pour l'OCR, data/revue_trades_simules.csv pour la revue visuelle) ;
2. ce que le canal dit ensuite : messages d'issue (data/trade_events.csv : tp, sl, be, rate,
   profit_flottant) sur la même paire dans les 10 jours suivant l'annonce ;
3. ce que montrent les cours : rejeu du plan quand entrée, stop et objectif sont connus
   (scripts/simuler_trades_dukascopy.py ; les niveaux du registre texte sont lus dans le message).

Fusion : un plan sur capture et une annonce texte sur la même paire, dans le même sens, à moins
de 2 jours, sont un même trade.

Classement (règles de CLAUDE.md) :
- selon le canal : ✅ TP ou gain, ❌ SL, ➖ BE, ⏸ non déclenché (« raté »), ⚠️ gain flottant seulement
  (un gain flottant n'est pas un TP), ❔ aucune issue publiée ;
- selon les cours : ✅ objectif, ❌ stop, ⏸ non déclenché, ⚠️ publié après l'entrée ou incohérent,
  ❔ pas de niveaux ou pas de cours ;
- écart : le canal annonce un TP (ou un gain) alors que les cours donnent le stop, ou l'inverse.
Les septembres ont été vérifiés à la main (analyses/TRADES_SEPTEMBRE.md), qui fait foi en cas d'écart.

Sorties : data/verification_trades.csv (un trade par ligne), data/verification_mensuelle.csv,
analyses/TRADES_TOUS_LES_MOIS.md.
"""
import os
import re
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
import simuler_trades_dukascopy as sim  # noqa: E402

NIV = re.compile(r'(?:\bat|\ba|\bà|@|:)\s*([0-9]+(?:[.,][0-9]+)?)', re.I)
SYMB_CANAL = {'tp': '✅', 'gain': '✅', 'sl': '❌', 'be': '➖', 'rate': '⏸', 'profit_flottant': '⚠️', 'inconnue': '❔'}


def niveaux_texte(t, sens):
    """Entrée, stop, objectif lus dans « sell limit X at 1.2 stop loss at 1.3 take profit at 1.1 »."""
    t = str(t)
    def apres(motif):
        m = re.search('(?:' + motif + r')[^0-9]{0,25}([0-9]+[.,][0-9]+)', t, re.I)
        return float(m.group(1).replace(',', '.')) if m else None
    sl = apres(r'stop[- ]?loss|\bsl\b')
    tp = apres(r'take[- ]?profit|\btp\b')
    m = re.search(r'(?:sell|buy|vend\w*|ach[eè]t\w*)[^0-9]{0,40}?([0-9]+[.,][0-9]+)', t, re.I)
    e = float(m.group(1).replace(',', '.')) if m else None
    if None in (e, sl, tp):
        return None
    achat = sens == 'achat'
    if (achat and not (sl < e < tp)) or (not achat and not (tp < e < sl)):
        return None
    return e, sl, tp


def issue_canal_depuis_evenements(ev, paire, debut, sens=None):
    """Dernier événement décisif publié sur la paire dans les 10 jours (même logique que le registre)."""
    f = ev[(ev['paires'].fillna('').str.contains(paire)) & (ev['date'] > debut) &
           (ev['date'] <= debut + timedelta(days=10))]
    if f.empty:
        return 'inconnue', ''
    for e in ['tp', 'sl', 'be', 'rate', 'profit_flottant']:
        g = f[f['evenement'] == e]
        if not g.empty:
            return e, ' '.join(f'#{i}' for i in g['id_message'].head(3))
    return 'inconnue', ''


def issue_canal_depuis_captures(rv, paire, debut, sens=None, entree=None):
    """Issue montrée en image par le canal (revue visuelle) : « TP atteint », position clôturée en gain ou en perte.
    La capture doit concerner la même position : même sens quand il est lisible, et entrée à moins de 0,15 %
    quand elle est lisible (sinon une capture d'une autre position sur la même paire serait prise pour l'issue)."""
    f = rv[(rv['paire'] == paire) & (rv['date'] > debut) & (rv['date'] <= debut + timedelta(days=10))]
    if sens:
        f = f[f['sens'].isna() | (f['sens'] == sens)]
    if entree and not pd.isna(entree):
        f = f[f['entree'].isna() | ((f['entree'] - entree).abs() / entree < 0.0015)]
    for issue, motif in [('sl', r'perte|clôturé −|clôturé -'), ('tp', r'TP atteint|objectif atteint|clôturé \+'),
                         ('profit_flottant', r'flottant|position .* \+')]:
        g = f[f['note'].fillna('').str.contains(motif, case=False, regex=True)]
        if not g.empty:
            return issue, ' '.join(f'#{i}' for i in g['id_message'].head(3)) + ' (capture)'
    return 'inconnue', ''


JOUR = None


def rejouer_journalier(paire, sens, e, sl, tp, depart):
    """Rejeu sur bougies journalières Dukascopy (2019-2020, paires du registre texte), mêmes règles que
    scripts/simuler_trades_dukascopy.py : ordre au marché si le prix est à moins d'un quart de risque de l'entrée,
    sinon ordre en attente 7 jours ; stop compté si stop et objectif tombent le même jour ; 20 jours de bourse."""
    global JOUR
    if JOUR is None:
        f = 'data/prix/journalier_dukascopy_registre.csv'
        JOUR = pd.read_csv(f, parse_dates=['date']) if os.path.exists(f) else pd.DataFrame(columns=['paire', 'date'])
    d = JOUR[(JOUR['paire'] == paire)].sort_values('date')
    jour0 = pd.Timestamp(depart.date())
    avant, apres = d[d['date'] < jour0], d[d['date'] >= jour0]
    if avant.empty or apres.empty:
        return None
    achat, risque = sens == 'achat', abs(e - sl)
    rr = abs(tp - e) / risque
    prix = apres.iloc[0]['open']
    if (achat and prix <= sl) or (not achat and prix >= sl):
        return dict(statut='incohérent', issue='prix déjà au-delà du stop', r='')
    if (achat and prix >= tp) or (not achat and prix <= tp):
        return dict(statut='après coup', issue='objectif déjà dépassé à la publication', r='')
    en_marche = abs(prix - e) / risque <= 0.25
    entree_i = None
    for i, b in enumerate(apres.itertuples()):
        if en_marche or b.low <= e <= b.high:
            entree_i = i
            break
        if i >= 5:
            break
        if (achat and b.high >= tp) or (not achat and b.low <= tp):
            return dict(statut='annoncé', issue='non déclenché (objectif atteint sans entrée)', r='')
    if entree_i is None:
        return dict(statut='annoncé', issue='non déclenché', r='')
    seq = apres.iloc[entree_i:entree_i + 20]
    for b in seq.itertuples():
        hs = b.low <= sl if achat else b.high >= sl
        ht = b.high >= tp if achat else b.low <= tp
        if hs:
            return dict(statut='annoncé', issue='stop', r=-1.0)
        if ht:
            return dict(statut='annoncé', issue='objectif', r=round(rr, 2))
    der = seq.iloc[-1]['close']
    return dict(statut='annoncé', issue='ouvert après 20 jours', r=round(((der - e) if achat else (e - der)) / risque, 2))


def statut_cours(r):
    if r is None or (isinstance(r, float) and np.isnan(r)):
        return '❔', 'pas de niveaux'
    issue, statut = r['issue_rejeu'], r['statut_rejeu']
    if statut == 'après coup':
        return '⚠️', f"publié après l'entrée ({issue})"
    if statut == 'incohérent':
        return '⚠️', issue
    if issue == 'objectif':
        return '✅', 'objectif'
    if issue == 'stop':
        return '❌', 'stop'
    if str(issue).startswith('non déclenché'):
        return '⏸', issue
    return '❔', issue


# Écarts examinés à la main sur les cours horaires (2024-2026) : id du message d'annonce -> (canal, cours, note)
VERIFIES = {
    10510: ('❔', None, "le « SL » vient du message #10529 mal classé (« imaginez, vous fermez ce soir… ») : aucune issue publiée ; "
                        "les cours donnent l'objectif le 31/01/2024"),
    10513: ('❔', None, "précision de l'objectif du trade #10510 (« mon tp … jusqu'à 95.000 ») ; même « SL » mal classé (#10529)"),
    10853: ('✅', None, "position fermée en gain avant l'objectif (#10865 : +9 900 $ le 03/04/2024) ; le plan publié aurait "
                        "fini au stop le 12/04"),
    13808: ('✅', '✅', "objectif mal lu par l'OCR (1.19593) : la capture #13836 montre l'objectif 1.18722, atteint"),
    15295: ('✅', '⚠️', "stop élargi après la publication (1.97098 -> 1.97, #15315) : le plan publié touche le stop le "
                        "04/09/2026 avant l'objectif ; la version modifiée atteint l'objectif"),
}


def main():
    ev = pd.read_csv('data/trade_events.csv')
    ev['date'] = pd.to_datetime(ev['date_utc'])
    reg = pd.read_csv('data/trades.csv')
    reg['date'] = pd.to_datetime(reg['date_utc'])
    rv = pd.read_csv('data/revue_visuelle_captures.csv')
    rv = rv[rv['categorie'].isin(['resultat', 'trade']) & ~rv['note'].fillna('').str.contains('membre|tiers', case=False)]
    rv['date'] = pd.to_datetime(rv['date'])
    lignes = []
    # 1. registre texte
    for _, t in reg.iterrows():
        niv = niveaux_texte(t['texte_entree'], t['sens'])
        rej = None
        if niv and isinstance(t['paire'], str):
            try:
                rej = sim.simuler(t['paire'], t['sens'], *niv, t['date'].to_pydatetime())
            except Exception:
                rej = None
            if rej is None:
                rej = rejouer_journalier(t['paire'], t['sens'], *niv, t['date'].to_pydatetime())
        lignes.append(dict(date=t['date'], paire=t['paire'], sens=t['sens'], source='texte',
                           id_message=t['id_entree'], issue_canal=t['issue'], ids_issue=t['ids_issue'],
                           entree=niv[0] if niv else np.nan, stop=niv[1] if niv else np.nan,
                           objectif=niv[2] if niv else np.nan,
                           statut_rejeu=rej['statut'] if rej else '', issue_rejeu=rej['issue'] if rej else '',
                           r=rej['r'] if rej else np.nan, texte=str(t['texte_entree'])[:160]))
    # 2. plans sur captures
    for f, src in [('data/trades_simules.csv', 'capture OCR'), ('data/revue_trades_simules.csv', 'capture revue')]:
        s = pd.read_csv(f)
        for _, t in s.iterrows():
            d = pd.Timestamp(t['date_publication'])
            # même trade que dans le registre texte ?
            proche = [l for l in lignes if l['source'] == 'texte' and l['paire'] == t['paire'] and l['sens'] == t['sens']
                      and abs((l['date'] - d).total_seconds()) <= 2 * 86400]
            if proche:
                l = proche[0]
                if not l['statut_rejeu']:
                    l.update(entree=t['entree'], stop=t['stop'], objectif=t['objectif'], statut_rejeu=t['statut'],
                             issue_rejeu=t['issue'], r=pd.to_numeric(t['resultat_r'], errors='coerce'))
                l['source'] = 'texte + capture'
                continue
            ic, ids = issue_canal_depuis_evenements(ev, t['paire'], d)
            if ic in ('inconnue', 'profit_flottant'):
                ic2, ids2 = issue_canal_depuis_captures(rv, t['paire'], d, t['sens'], t['entree'])
                if ic2 != 'inconnue' and not (ic == 'profit_flottant' and ic2 == 'profit_flottant'):
                    ic, ids = ic2, ids2
            lignes.append(dict(date=d, paire=t['paire'], sens=t['sens'], source=src, id_message=t['id_message'],
                               issue_canal=ic, ids_issue=ids, entree=t['entree'], stop=t['stop'],
                               objectif=t['objectif'], statut_rejeu=t['statut'], issue_rejeu=t['issue'],
                               r=pd.to_numeric(t['resultat_r'], errors='coerce'), texte=''))
    v = pd.DataFrame(lignes).sort_values('date').reset_index(drop=True)
    v['r'] = pd.to_numeric(v['r'], errors='coerce')
    v['canal'] = v['issue_canal'].map(SYMB_CANAL).fillna('❔')
    cs = [statut_cours(r if isinstance(r['statut_rejeu'], str) and r['statut_rejeu'] else None) for _, r in v.iterrows()]
    v['cours'] = [c[0] for c in cs]
    v['detail_cours'] = [c[1] for c in cs]
    v['ecart'] = np.where((v['canal'] == '✅') & (v['cours'] == '❌'), 'TP annoncé, stop selon les cours',
                          np.where((v['canal'] == '❌') & (v['cours'] == '✅'), 'SL annoncé, objectif selon les cours',
                                   np.where((v['canal'] == '⚠️') & (v['cours'] == '❌'), 'gain flottant annoncé, stop selon les cours', '')))
    v['note_verification'] = ''
    for mid, (canal, cours, note) in VERIFIES.items():
        k = v['id_message'] == mid
        v.loc[k, 'canal'] = canal
        if cours:
            v.loc[k, 'cours'] = cours
        v.loc[k, 'note_verification'] = note
        v.loc[k, 'ecart'] = ''
    v['resolution'] = np.where(v['date'] >= pd.Timestamp('2023-12-15'), 'horaire', 'journalier')
    v['mois'] = v['date'].dt.strftime('%Y-%m')
    v.to_csv('data/verification_trades.csv', index=False)

    m = v.groupby('mois').apply(lambda g: pd.Series({
        'trades': len(g),
        'canal_tp': int((g['canal'] == '✅').sum()), 'canal_sl': int((g['canal'] == '❌').sum()),
        'canal_be': int((g['canal'] == '➖').sum()), 'canal_non_decl': int((g['canal'] == '⏸').sum()),
        'canal_flottant': int((g['canal'] == '⚠️').sum()), 'canal_rien': int((g['canal'] == '❔').sum()),
        'cours_objectif': int((g['cours'] == '✅').sum()), 'cours_stop': int((g['cours'] == '❌').sum()),
        'cours_non_decl': int((g['cours'] == '⏸').sum()), 'cours_apres_coup': int((g['cours'] == '⚠️').sum()),
        'cours_inconnu': int((g['cours'] == '❔').sum()),
        'r_copiable': round(float(g.loc[g['statut_rejeu'] == 'annoncé', 'r'].sum()), 1),
        'ecarts': int((g['ecart'] != '').sum()),
    })).reset_index()
    m.to_csv('data/verification_mensuelle.csv', index=False)
    print(m.to_string())
    print(v['canal'].value_counts().to_string())
    print(v['cours'].value_counts().to_string())
    print(v[v['ecart'] != ''][['date', 'paire', 'sens', 'source', 'id_message', 'ids_issue', 'ecart']].to_string())


if __name__ == '__main__':
    main()
