# -*- coding: utf-8 -*-
"""Varre os .lua de monstros e NPCs do servidor e gera uma pagina HTML
pesquisavel com nome -> LookType (o ID do outfit no Canary Studio)."""
import os
import re
import json
import html

BASE = r"C:\dev\canary_run\data-otservbr-global"
MON = os.path.join(BASE, "monster")
NPC = os.path.join(BASE, "npc")
OUT = r"C:\Users\lleo_\OneDrive\Área de Trabalho\CODE\TIBIA BAGUA\REFERENCIA-MONSTROS.html"

RE_NAME_MON = re.compile(r'createMonsterType\(\s*"([^"]+)"')
# NPCs quase sempre passam uma variavel: local internalNpcName = "A Beggar"
RE_NAME_NPC = re.compile(
    r'createNpcType\(\s*"([^"]+)"'
    r'|internalNpcName\s*=\s*"([^"]+)"'
    r'|npcConfig\.name\s*=\s*"([^"]+)"'
    r'|createHirelingType\(\s*"([^"]+)"'
)


def first_group(m):
    """Devolve o primeiro grupo nao-vazio de um match com alternativas."""
    for g in m.groups():
        if g:
            return g
    return None
RE_LOOKTYPE = re.compile(r'lookType\s*=\s*(\d+)')
RE_LOOKTYPEEX = re.compile(r'lookTypeEx\s*=\s*(\d+)')
RE_EXP = re.compile(r'\.experience\s*=\s*(\d+)')
RE_HP = re.compile(r'\.health\s*=\s*(\d+)')
RE_CLASS = re.compile(r'class\s*=\s*"([^"]+)"')
RE_STARS = re.compile(r'Stars\s*=\s*(\d+)')


def scan(folder, kind, name_re):
    rows = []
    if not os.path.isdir(folder):
        return rows
    for root, _dirs, files in os.walk(folder):
        for fn in files:
            if not fn.endswith(".lua"):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    src = fh.read()
            except OSError:
                continue
            m = name_re.search(src)
            if not m:
                continue
            nome = first_group(m)
            if not nome:
                continue
            lt = RE_LOOKTYPE.search(src)
            ltex = RE_LOOKTYPEEX.search(src)
            rel = os.path.relpath(path, BASE).replace("\\", "/")
            grupo = rel.split("/")[1] if "/" in rel[len(kind):].lstrip("/") else ""
            parts = rel.split("/")
            grupo = parts[1] if len(parts) > 2 else "-"
            rows.append({
                "nome": nome,
                "tipo": kind,
                "look": int(lt.group(1)) if lt else (
                    -int(ltex.group(1)) if ltex else None),
                "item": bool(ltex and not lt),
                "classe": (RE_CLASS.search(src).group(1) if RE_CLASS.search(src) else ""),
                "estrelas": int(RE_STARS.search(src).group(1)) if RE_STARS.search(src) else None,
                "exp": int(RE_EXP.search(src).group(1)) if RE_EXP.search(src) else None,
                "hp": int(RE_HP.search(src).group(1)) if RE_HP.search(src) else None,
                "grupo": grupo,
                "arquivo": rel,
            })
    return rows


mon = scan(MON, "monstro", RE_NAME_MON)
npc = scan(NPC, "npc", RE_NAME_NPC)
rows = sorted(mon + npc, key=lambda r: r["nome"].lower())

com_look = sum(1 for r in rows if r["look"] and r["look"] > 0)
print(f"monstros: {len(mon)}  npcs: {len(npc)}  total: {len(rows)}  com lookType: {com_look}")

data_json = json.dumps(rows, ensure_ascii=False)

PAGE = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Referência de monstros e NPCs - TIBIA BAGUA</title>
<style>
:root{--bg:#14161a;--card:#1c2027;--line:#2c323c;--ink:#e8eaed;--mut:#9aa3af;--acc:#7aa2f7;--warn:#e0af68}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);
       padding:16px 20px 12px;z-index:5}
h1{margin:0 0 2px;font-size:19px}
.sub{color:var(--mut);font-size:12.5px;margin-bottom:12px}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
input[type=search],select{background:var(--card);border:1px solid var(--line);color:var(--ink);
       border-radius:8px;padding:9px 12px;font-size:14px;outline:none}
input[type=search]{flex:1;min-width:260px}
input[type=search]:focus,select:focus{border-color:var(--acc)}
.count{color:var(--mut);font-size:12.5px;white-space:nowrap}
main{padding:0 20px 40px}
table{width:100%;border-collapse:collapse;margin-top:14px}
th{position:sticky;top:112px;background:var(--bg);text-align:left;font-size:12px;
   text-transform:uppercase;letter-spacing:.04em;color:var(--mut);
   padding:8px 10px;border-bottom:1px solid var(--line);cursor:pointer;user-select:none}
th:hover{color:var(--ink)}
td{padding:8px 10px;border-bottom:1px solid #23272f}
tr:hover td{background:#191d24}
.look{font-weight:700;color:var(--acc);font-variant-numeric:tabular-nums}
.look.none{color:#5b6472;font-weight:400}
.look.item{color:var(--warn)}
.badge{font-size:11px;padding:2px 7px;border-radius:99px;border:1px solid var(--line);color:var(--mut)}
.path{color:#6b7280;font-size:11.5px;font-family:ui-monospace,Consolas,monospace}
.hint{background:var(--card);border-left:3px solid var(--acc);padding:11px 14px;
      border-radius:6px;margin-top:14px;font-size:13px}
.num{font-variant-numeric:tabular-nums;color:var(--mut)}
mark{background:#3d4b6b;color:#fff;border-radius:3px;padding:0 2px}
</style></head><body>
<header>
  <h1>Referência de monstros e NPCs</h1>
  <div class="sub">O <b>LookType</b> é o número do outfit. Use ele no Canary Studio:
     Editor de Assets &rarr; Outfits &rarr; <b>Ir para ID</b> &rarr; aba <b>Textura</b> &rarr; <b>&darr; PNG</b>.</div>
  <div class="controls">
    <input type="search" id="q" placeholder="Digite o nome (ex.: cyclops, dragon, rat) ou o LookType..." autofocus>
    <select id="tipo">
      <option value="">Monstros e NPCs</option>
      <option value="monstro">Só monstros</option>
      <option value="npc">Só NPCs</option>
    </select>
    <select id="temlook">
      <option value="">Todos</option>
      <option value="sim">Só com LookType</option>
    </select>
    <span class="count" id="count"></span>
  </div>
</header>
<main>
  <div class="hint">Clique no cabeçalho de qualquer coluna para ordenar.
    LookType em <b style="color:#e0af68">amarelo</b> significa que a criatura usa a aparência de
    um <b>item</b> (lookTypeEx) em vez de um outfit — esses não aparecem na lista de Outfits.</div>
  <table>
    <thead><tr>
      <th data-k="nome">Nome</th>
      <th data-k="look">LookType</th>
      <th data-k="tipo">Tipo</th>
      <th data-k="classe">Classe</th>
      <th data-k="estrelas">Dific.</th>
      <th data-k="exp">Exp</th>
      <th data-k="hp">Vida</th>
      <th data-k="arquivo">Arquivo</th>
    </tr></thead>
    <tbody id="tb"></tbody>
  </table>
</main>
<script>
const DATA = __DATA__;
const tb=document.getElementById('tb'), q=document.getElementById('q'),
      tipo=document.getElementById('tipo'), temlook=document.getElementById('temlook'),
      count=document.getElementById('count');
let sortK='nome', sortDir=1;
const esc=s=>String(s??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function hl(t,term){ if(!term) return esc(t);
  const i=String(t).toLowerCase().indexOf(term); if(i<0) return esc(t);
  return esc(String(t).slice(0,i))+'<mark>'+esc(String(t).slice(i,i+term.length))+'</mark>'+esc(String(t).slice(i+term.length)); }
function render(){
  const term=q.value.trim().toLowerCase(), t=tipo.value, tl=temlook.value;
  let rows=DATA.filter(r=>{
    if(t && r.tipo!==t) return false;
    if(tl==='sim' && !(r.look>0)) return false;
    if(!term) return true;
    return r.nome.toLowerCase().includes(term) || String(r.look??'')===term
        || (r.classe||'').toLowerCase().includes(term);
  });
  rows.sort((a,b)=>{ let x=a[sortK],y=b[sortK];
    if(x==null)x=sortDir>0?Infinity:-Infinity; if(y==null)y=sortDir>0?Infinity:-Infinity;
    if(typeof x==='string')return sortDir*x.localeCompare(y); return sortDir*(x-y); });
  count.textContent=rows.length+' de '+DATA.length;
  tb.innerHTML=rows.slice(0,4000).map(r=>{
    let lk, cls='look';
    if(r.look==null){ lk='—'; cls+=' none'; }
    else if(r.look<0){ lk='item '+(-r.look); cls+=' item'; }
    else lk=r.look;
    return '<tr><td>'+hl(r.nome,term)+'</td>'
      +'<td class="'+cls+'">'+lk+'</td>'
      +'<td><span class="badge">'+r.tipo+'</span></td>'
      +'<td>'+esc(r.classe)+'</td>'
      +'<td class="num">'+(r.estrelas??'')+'</td>'
      +'<td class="num">'+(r.exp??'')+'</td>'
      +'<td class="num">'+(r.hp??'')+'</td>'
      +'<td class="path">'+esc(r.arquivo)+'</td></tr>'; }).join('');
}
document.querySelectorAll('th').forEach(th=>th.onclick=()=>{
  const k=th.dataset.k; sortDir = (k===sortK)? -sortDir : 1; sortK=k; render(); });
[q,tipo,temlook].forEach(el=>el.addEventListener('input',render));
render();
</script></body></html>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(PAGE.replace("__DATA__", data_json))
print("gerado:", OUT, os.path.getsize(OUT), "bytes")
