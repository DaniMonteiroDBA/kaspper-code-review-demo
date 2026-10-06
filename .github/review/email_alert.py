"""Alerta contém só status e link. Nunca envia código ou segredos."""
import os, smtplib, ssl
from email.message import EmailMessage

def main():
    user=os.environ.get('SMTP_USERNAME'); password=os.environ.get('SMTP_PASSWORD')
    if not user or not password: raise SystemExit('Configure SMTP_USERNAME e SMTP_PASSWORD nos secrets do GitHub. Alerta NÃO enviado.')
    message=EmailMessage()
    message['From']=user
    message['To']='danibruxinha@gmail.com'
    message['Subject']=f'[Kaspper demo] {os.environ["REVIEW_STATE"]} — PR #{os.environ["PR_NUMBER"]}'
    message.set_content(f'Revisão automática requer atenção.\nEstado: {os.environ["REVIEW_STATE"]}\nCommit: {os.environ["HEAD_SHA"]}\nPR: {os.environ["PR_URL"]}\nExecução: {os.environ["RUN_URL"]}\nAbra o relatório no GitHub para os achados e evidências.\n')
    host=os.environ.get('SMTP_HOST') or 'smtp.gmail.com'
    with smtplib.SMTP(host,587,timeout=30) as smtp:
        smtp.starttls(context=ssl.create_default_context()); smtp.login(user,password); smtp.send_message(message)
    print('Alerta aceito pelo servidor SMTP; entrega na caixa não verificada.')
if __name__=='__main__': main()
