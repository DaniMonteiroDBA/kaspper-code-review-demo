"""Consome revisão nativa; não chama modelo nem executa código de PR."""
import hashlib, json, os, re, smtplib, ssl
from pathlib import Path
from email.message import EmailMessage
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BOT_LOGIN = "chatgpt-codex-connector[bot]"
BOT_ID = 199175422
ACTIONS_ID = 41898282
RECIPIENT = "danibruxinha@gmail.com"
SUMMARY = "<!-- codex-pull-request-review-summary -->"
REPO = "DaniMonteiroDBA/kaspper-code-review-demo"

def is_codex(item):
    u = item.get("user") or {}
    return u.get("login") == BOT_LOGIN and u.get("id") == BOT_ID

def classify(head, comments, reviews, inline, reactions):
    findings = []
    dismissed = {r["id"] for r in reviews if r.get("state") == "DISMISSED"}
    for item in reviews + inline:
        if item.get("pull_request_review_id") in dismissed: continue
        if not is_codex(item) or item.get("commit_id") != head: continue
        if item.get("state") in ["DISMISSED", "PENDING"]: continue
        priority = re.search(r"(?:\[P([012])\]|!\[P([012]) Badge\])", item.get("body") or "")
        if priority:
            findings.append(dict(id=item["id"], priority="P"+(priority[1] or priority[2]),
                                 url=item.get("html_url", ""), path=item.get("path", ""),
                                 line=item.get("line"), source="review"))
    for item in comments:
        if not is_codex(item) or SUMMARY in (item.get("body") or ""): continue
        if head not in (item.get("body") or ""): continue
        priority = re.search(r"(?:\[P([012])\]|!\[P([012]) Badge\])", item.get("body") or "")
        if priority:
            findings.append(dict(id=item["id"], priority="P"+(priority[1] or priority[2]),
                                 url=item.get("html_url", ""), path="", line=None, source="comment"))
    if findings: return "ACHADOS", findings
    summaries = [c for c in comments if is_codex(c) and SUMMARY in (c.get("body") or "")]
    if not summaries: return "AGUARDANDO", []
    latest = max(summaries, key=lambda x: x.get("updated_at", ""))
    row = next((line for line in latest["body"].splitlines() if "**Code Review**" in line), "")
    sha = re.search(chr(96)+r"([a-f0-9]{7,40})"+chr(96), row)
    if not sha or not head.startswith(sha[1]): return "VERSAO_ANTIGA", []
    if "**Running**" in row: return "AGUARDANDO", []
    if re.search(r"\*\*(Failed|Error|Cancelled|Canceled)\*\*", row, re.I):
        return "FALHA_REVISAO", []
    if "**Completed**" in row:
        if any(is_codex(r) and r.get("content") == "+1" and
               r.get("created_at", "") >= latest.get("updated_at", "") for r in reactions):
            return "SEM_ACHADOS_REPORTADOS", []
    return "AGUARDANDO", []

def key_for(number, head, state, findings):
    values = [REPO, number, head, state, sorted((f["source"], str(f["id"]), f["priority"]) for f in findings)]
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()

def has_receipt(comments, marker, status):
    return any((c.get("user") or {}).get("id") == ACTIONS_ID and
               (c.get("user") or {}).get("login") == "github-actions[bot]" and
               marker in (c.get("body") or "") and
               f"Estado de envio: {status}" in (c.get("body") or "") for c in comments)

class GitHub:
    def __init__(self, token): self.token = token
    def request(self, path, data=None):
        if not path.startswith("/"): raise ValueError("Expected relative GitHub path")
        headers = {"Authorization":"Bearer "+self.token, "Accept":"application/vnd.github+json",
                   "X-GitHub-Api-Version":"2022-11-28", "User-Agent":"Kaspper-native-review-alert"}
        if data is not None: headers["Content-Type"] = "application/json"
        req = Request("https://api.github.com/repos/"+REPO+path,
                      data=None if data is None else json.dumps(data).encode(), headers=headers)
        with urlopen(req, timeout=30) as response: return json.load(response)
    def pages(self, path):
        result = []
        for page in range(1, 101):
            sep = "&" if "?" in path else "?"
            items = self.request(path+sep+f"per_page=100&page={page}")
            if not isinstance(items, list): raise ValueError("Expected GitHub collection")
            result.extend(items)
            if len(items) < 100: return result
        raise RuntimeError("Pagination bound reached; coverage is incomplete")

def send_alert(number, head, state, findings):
    user, password = os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD")
    if not user or not password: raise ValueError("SMTP credentials absent; not sent")
    message = EmailMessage()
    message["From"] = user
    message["To"] = RECIPIENT
    message["Subject"] = f"[Kaspper] {state} — PR #{number}"
    lines = ["A revisão nativa do Codex requer atenção.", f"Estado: {state}",
             f"Commit: {head}", f"PR: https://github.com/{REPO}/pull/{number}"]
    for f in findings:
        lines.append(f'{f["priority"]} — {f["path"] or "revisão"}:{f["line"] or ""}')
        if f["url"].startswith("https://github.com/"+REPO+"/"): lines.append(f["url"])
    lines.append("Abra o GitHub para ler achados e evidências. Sem merge automático.")
    message.set_content("\n".join(lines))
    with smtplib.SMTP(os.getenv("SMTP_HOST") or "smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(user, password)
        if smtp.send_message(message): raise RuntimeError("SMTP rejected recipient")

def run(gh, event, event_name):
    if event_name == "issue_comment":
        if not is_codex(event.get("comment") or {}) or not (event.get("issue") or {}).get("pull_request"):
            return []
        numbers = [event["issue"]["number"]]
    else:
        numbers = [pr["number"] for pr in gh.pages("/pulls?state=open")]
    results = []
    for number in numbers:
        pr = gh.request(f"/pulls/{number}")
        if pr["state"] != "open" or pr["draft"]: continue
        head = pr["head"]["sha"]
        comments = gh.pages(f"/issues/{number}/comments")
        reviews = gh.pages(f"/pulls/{number}/reviews")
        inline = gh.pages(f"/pulls/{number}/comments")
        reactions = gh.pages(f"/issues/{number}/reactions")
        state, findings = classify(head, comments, reviews, inline, reactions)
        result = dict(pr=number, head=head, state=state, findings=findings, recipient=RECIPIENT)
        results.append(result)
        if state not in ["ACHADOS", "FALHA_REVISAO", "SEM_ACHADOS_REPORTADOS"]: continue
        marker = "<!-- kaspper-native-alert:"+key_for(number,head,state,findings)+" -->"
        needs_mail = state != "SEM_ACHADOS_REPORTADOS"
        final_status = "SMTP_ACEITO" if needs_mail else "NAO_NECESSARIO"
        if has_receipt(comments, marker, final_status):
            result["mail"] = "JA_REGISTRADO"
            continue
        current = gh.request(f"/pulls/{number}")
        if current["head"]["sha"] != head or current["state"] != "open":
            result["mail"] = "DESCARTADO_NOVO_HEAD"
            continue
        if needs_mail:
            # Comprova escrita do recibo antes do envio externo.
            if not has_receipt(comments,marker,"PENDENTE"):
                try:
                    gh.request(f"/issues/{number}/comments",{"body":marker+
                        f"\n## Alerta da revisão nativa\nCommit: {head}\nResultado: {state}"
                        "\nEstado de envio: PENDENTE\nEnvio ainda não confirmado."})
                except HTTPError as exc:
                    result["mail"]="BLOQUEADO_REGISTRO_GITHUB"
                    result["record_error"]=f"GitHub HTTP {exc.code}"
                    continue
            try: send_alert(number,head,state,findings)
            except (ValueError, OSError, smtplib.SMTPException, RuntimeError):
                result["mail"] = "PENDENTE_CONFIGURACAO_OU_FALHA_SMTP"
                continue
        try:
            gh.request(f"/issues/{number}/comments", {"body":marker+
            f"\n## Registro da revisão nativa\nCommit: {head}\nResultado: {state}"
            f"\nEstado de envio: {final_status}"
            f"\nDestinatário: {RECIPIENT if needs_mail else 'não acionado'}"
            "\nSMTP_ACEITO é aceite pelo servidor, não confirmação de recebimento na caixa."})
        except HTTPError as exc:
            result["mail"]="BLOQUEADO_REGISTRO_GITHUB"
            result["record_error"]=f"GitHub HTTP {exc.code}"
            continue
        result["mail"] = final_status
    return results

def main():
    if os.environ.get("GITHUB_REPOSITORY") != REPO: raise SystemExit("Repository out of scope")
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    results = run(GitHub(os.environ["GH_TOKEN"]), event, os.environ["GITHUB_EVENT_NAME"])
    Path("native-alert-result.json").write_text(json.dumps(results,ensure_ascii=False,indent=2))
    with open(os.environ["GITHUB_STEP_SUMMARY"],"a") as summary:
        summary.write("## Revisão nativa — encaminhamento\n\n")
        for r in results: summary.write(f'- PR #{r["pr"]}: {r["state"]}; envio: {r.get("mail","aguardando")}.\n')
    if any(r.get("mail") in ["PENDENTE_CONFIGURACAO_OU_FALHA_SMTP","BLOQUEADO_REGISTRO_GITHUB"] for r in results):
        raise SystemExit("Alerta ou registro pendente: verifique SMTP/permissão de comentário. Entrega não confirmada.")
if __name__ == "__main__": main()
