import json, os
from pathlib import Path

def decide(raw, ci):
    if not isinstance(raw, dict): return 'INCONCLUSIVO'
    findings=raw.get('findings')
    if not isinstance(findings,list): return 'INCONCLUSIVO'
    for f in findings:
        if not isinstance(f,dict) or f.get('priority') not in ['P0','P1','P2','P3'] or not all(f.get(k) for k in ['file','line','scenario','expected','actual','impact','evidence']):
            return 'INCONCLUSIVO'
    if any(f['priority'] in ['P0','P1','P2'] for f in findings): return 'REQUER_DESENVOLVEDOR'
    if ci!='success' or raw.get('complete') is not True or raw.get('limitations'):
        return 'INCONCLUSIVO'
    return 'CONCLUIDO_SEM_ESCALONAMENTO'

def main():
    try: raw=json.loads(Path('review.json').read_text())
    except (OSError,ValueError): raw={'summary':'Revisão não produziu resultado válido.','complete':False,'limitations':['Verifique credenciais e logs do job.'],'findings':[]}
    if not isinstance(raw,dict) or not isinstance(raw.get('findings'),list) or any(not isinstance(f,dict) for f in raw.get('findings',[])):
        raw={'summary':'Saída inválida do revisor.','complete':False,'limitations':['Formato inválido; revisão inconclusiva.'],'findings':[]}
    state=decide(raw,os.environ['CI_RESULT'])
    raw.update(state=state,head=os.environ['HEAD_SHA'],base=os.environ['BASE_SHA'],ci=os.environ['CI_RESULT'])
    Path('review.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2))
    lines=['<!-- kaspper-auto-review -->',f'## Revisão automática — {state}',f'Commit: {raw["head"]}',f'CI: {raw["ci"]}',str(raw.get('summary','')),'']
    for f in raw.get('findings',[]):
        lines += [f'### {f.get("priority","?")} — {f.get("file","?")}:{f.get("line","?")}',*[f'**{k}:** {f.get(k,"não informado")}' for k in ['scenario','expected','actual','impact','evidence']],'']
    lines += ['**Limitações:** '+str(raw.get('limitations',[])), 'Conclusão restrita ao commit acima. Sem merge automático.']
    Path('review.md').write_text('\n'.join(lines))
    with open(os.environ['GITHUB_OUTPUT'],'a') as out: out.write(f'state={state}\nalert={str(state!="CONCLUIDO_SEM_ESCALONAMENTO").lower()}\n')
if __name__=='__main__': main()
