#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction du playbook Notion d'Amirou (page publique) par l'API publique de notion.site, puis rendu en texte.

Usage : python scripts/collecter_playbook_notion.py [nombre max de pages, 150 par défaut]
Le modèle contient des centaines de sous-pages vides (journal par mois, fiches de trade) : 150 pages suffisent à
couvrir tout le contenu rempli. Sortie : data/playbook_notion/playbook.txt (le JSON brut reste dans /tmp).
"""
import json, os, re, sys, time
BASE='https://conscious-dirt-ada.notion.site/api/v3/'
OUT='/tmp/playbook_notion.json'
MAX=int(sys.argv[1]) if len(sys.argv)>1 else 150
RACINE_PAGE='b1f86292-44e0-4274-aeeb-d97e1a624a90'
blocks, colls, views = {}, {}, {}
TRIED=set()
def post(ep, body):
    for i in range(2):
        try:
            import subprocess
            o=subprocess.run(['curl','-s','-f','-X','POST',BASE+ep,'-H','content-type: application/json','--data-binary',json.dumps(body)],capture_output=True,timeout=90)
            if o.returncode: raise RuntimeError(o.returncode)
            return json.loads(o.stdout)
        except Exception as e:
            print('err',ep,e,file=sys.stderr); time.sleep(1)
    return {}
def V(x):
    v=x.get('value',{}); return v.get('value',v)
def merge(rm):
    for k,dst in [('block',blocks),('collection',colls),('collection_view',views)]:
        for i,x in rm.get(k,{}).items():
            if V(x): dst[i]=V(x)
def load_page(pid):
    cursor={'stack':[]}
    for _ in range(20):
        j=post('loadCachedPageChunkV2',{'page':{'id':pid},'limit':500,'cursor':cursor,'verticalColumns':False})
        merge(j.get('recordMap',{}))
        cs=j.get('cursors') or []
        if not cs: break
        cursor=cs[0]
def missing(ids):
    for i in ids:
        if i not in blocks and i not in TRIED:
            TRIED.add(i); load_page(i)
def query(b):
    cid=b.get('collection_id') or (b.get('format',{}).get('collection_pointer') or {}).get('id')
    vid=(b.get('view_ids') or [None])[0]
    if not cid or not vid: return
    j=post('queryCollection',{'collection':{'id':cid,'spaceId':b.get('space_id')},'collectionView':{'id':vid,'spaceId':b.get('space_id')},
        'loader':{'type':'reducer','reducers':{'collection_group_results':{'type':'results','limit':500}},'searchQuery':'','userTimeZone':'UTC'}})
    merge(j.get('recordMap',{}))
    ids=j.get('result',{}).get('reducerResults',{}).get('collection_group_results',{}).get('blockIds',[])
    b['_rows']=ids
seen=set(); todo=[RACINE_PAGE]
while todo and len(seen) < MAX:
    p=todo.pop(0)
    if p in seen: continue
    seen.add(p); load_page(p)
    # parcours de l'arbre de la page
    st=[p]
    while st:
        x=st.pop()
        if x not in blocks: missing([x])
        b=blocks.get(x)
        if not b: continue
        if b.get('type') in ('collection_view_page','collection_view') and '_rows' not in b:
            query(b)
            for r in b.get('_rows',[]): todo.append(r)
        for c in b.get('content',[]) or []:
            cb=blocks.get(c)
            if cb is None: missing([c]); cb=blocks.get(c)
            if cb and cb.get('type')=='page' and c!=p: todo.append(c)
            else: st.append(c)
    print('page',p,len(blocks),len(todo),file=sys.stderr)
    if len(seen)%50==0: json.dump({'blocks':blocks,'collections':colls,'views':views},open(OUT,'w'))
json.dump({'blocks':blocks,'collections':colls,'views':views},open(OUT,'w'))
print('pages',len(seen),'blocs',len(blocks))


# ---- rendu en texte
B=blocks; C=colls
def txt(p):
    if not p: return ''
    out=''
    for x in p:
        s=x[0]
        if len(x)>1:
            for a in x[1]:
                if a[0]=='d' and isinstance(a[1],dict): s=a[1].get('start_date','')
                if a[0]=='a': s=f'{s} <{a[1]}>'
        out+=s
    return out
def props(b):
    p=b.get('properties',{}) or {}
    par=b.get('parent_id'); sch=None
    if b.get('parent_table')=='collection' and par in C: sch=C[par].get('schema',{})
    if sch:
        return ' | '.join(f"{sch.get(k,{}).get('name',k)}: {txt(v)}" for k,v in p.items() if txt(v))
    return txt(p.get('title'))
def render(bid,depth,out,seen):
    if bid in seen: return
    seen.add(bid)
    b=B.get(bid)
    if not b: out.append('  '*depth+'[non chargé]'); return
    t=b.get('type')
    if t=='table_row':
        out.append('  '*depth+'| '+' | '.join(txt(v) for v in (b.get('properties') or {}).values())+' |')
    elif t in ('image','file','pdf','video','bookmark','embed'):
        out.append('  '*depth+f"[{t}] {txt((b.get('properties') or {}).get('source'))} {txt((b.get('properties') or {}).get('caption'))}")
    elif t in ('collection_view','collection_view_page'):
        cid=b.get('collection_id'); name=txt(C.get(cid,{}).get('name')) if cid in C else ''
        out.append('  '*depth+f"[base {name}] {len(b.get('_rows',[]))} lignes")
        for r in b.get('_rows',[]): render(r,depth+1,out,seen)
        return
    else:
        s=props(b)
        if s or t not in ('text','divider','column','column_list'): out.append('  '*depth+(f'[{t}] ' if t not in ('text',) else '')+s)
    for c in b.get('content',[]) or []: render(c,depth+1,out,seen)
out=[]; render(RACINE_PAGE,0,out,set())
lignes=[];prev=None
for l in out:
    s=l.strip()
    if re.fullmatch(r'\| \d+h-\d+h \|',s) or s in('|  |','[table]','[copy_indicator]','[non chargé]') or re.fullmatch(r'\[base [^\]]*\] 0 lignes',s): continue
    if l==prev: continue
    lignes.append(l); prev=l
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs('data/playbook_notion',exist_ok=True)
open('data/playbook_notion/playbook.txt','w').write('\n'.join(lignes)); print(len(lignes),'lignes')
