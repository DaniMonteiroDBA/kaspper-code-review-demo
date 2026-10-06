import unittest
from unittest.mock import patch
import native_alert as n

HEAD='8415db89927d7b8e9328811102d0758f550e72a8'
BOT={'login':n.BOT_LOGIN,'id':n.BOT_ID}
def summary(status='Completed',head=HEAD):
 return dict(id=6020799538,user=BOT,body=n.SUMMARY+'\n| **Code Review** | **'+status+'** | '+chr(96)+head[:7]+chr(96)+' |',
             updated_at='2026-10-06T16:33:10Z')
def finding(priority='P1',head=HEAD):
 return dict(id=1,user=BOT,commit_id=head,body='['+priority+'] Bug',path='orders.py',line=4,html_url='https://github.com/'+n.REPO+'/pull/1#discussion_r1')
def reaction(date='2026-10-06T16:33:12Z'):
 return dict(user=BOT,content='+1',created_at=date)

class ClassificationTests(unittest.TestCase):
 def test_clean_observed_format(self):
  self.assertEqual(n.classify(HEAD,[summary()],[],[],[reaction()])[0],'SEM_ACHADOS_REPORTADOS')
 def test_no_silence_as_clean(self): self.assertEqual(n.classify(HEAD,[],[],[],[])[0],'AGUARDANDO')
 def test_completed_without_reaction(self): self.assertEqual(n.classify(HEAD,[summary()],[],[],[])[0],'AGUARDANDO')
 def test_running(self): self.assertEqual(n.classify(HEAD,[summary('Running')],[],[],[reaction()])[0],'AGUARDANDO')
 def test_old_summary(self): self.assertEqual(n.classify('f'*40,[summary()],[],[],[reaction()])[0],'VERSAO_ANTIGA')
 def test_old_reaction(self): self.assertEqual(n.classify(HEAD,[summary()],[],[],[reaction('2025-01-01')])[0],'AGUARDANDO')
 def test_all_priorities(self):
  for priority in ['P0','P1','P2']:
   self.assertEqual(n.classify(HEAD,[],[],[finding(priority)],[])[0],'ACHADOS')
 def test_badge_priority(self):
  f=finding(); f['body']='**<sub>![P1 Badge](https://example.invalid/badge)</sub>** Defect'
  self.assertEqual(n.classify(HEAD,[],[],[f],[])[0],'ACHADOS')
 def test_dismissed_inline(self):
  f=finding();f['pull_request_review_id']=7
  self.assertEqual(n.classify(HEAD,[],[dict(id=7,state='DISMISSED')],[f],[])[0],'AGUARDANDO')
 def test_old_finding(self): self.assertEqual(n.classify('f'*40,[],[],[finding()],[])[0],'AGUARDANDO')
 def test_wrong_identity(self):
  f=finding();f['user']={'login':n.BOT_LOGIN,'id':123}
  self.assertEqual(n.classify(HEAD,[],[],[f],[])[0],'AGUARDANDO')
 def test_review_submission(self): self.assertEqual(n.classify(HEAD,[],[finding()],[],[])[0],'ACHADOS')
 def test_unversioned_conversation(self): self.assertEqual(n.classify(HEAD,[finding()],[],[],[])[0],'AGUARDANDO')
 def test_failure(self): self.assertEqual(n.classify(HEAD,[summary('Failed')],[],[],[])[0],'FALHA_REVISAO')
 def test_p3_ignored(self): self.assertEqual(n.classify(HEAD,[],[],[finding('P3')],[])[0],'AGUARDANDO')
 def test_receipt_identity(self):
  marker='<!-- key -->'; c=dict(user={'login':'human','id':n.ACTIONS_ID},body=marker+'\nEstado de envio: SMTP_ACEITO')
  self.assertFalse(n.has_receipt([c],marker,'SMTP_ACEITO'))
 def test_missing_smtp_does_not_connect(self):
  with patch.dict(n.os.environ,{},clear=True),patch.object(n.smtplib,'SMTP') as smtp:
   with self.assertRaises(ValueError): n.send_alert(1,HEAD,'ACHADOS',[finding()])
   smtp.assert_not_called()
 def test_smtp_fixed_recipient_and_starttls(self):
  f=dict(priority='P1',path='orders.py',line=4,url='https://github.com/'+n.REPO+'/pull/1')
  with patch.dict(n.os.environ,{'SMTP_USERNAME':'sender@example.invalid','SMTP_PASSWORD':'TEST_ONLY'},clear=True),patch.object(n.smtplib,'SMTP') as smtp:
   smtp.return_value.__enter__.return_value.send_message.return_value={}
   n.send_alert(1,HEAD,'ACHADOS',[f])
   msg=smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
   self.assertEqual(msg['To'],'danibruxinha@gmail.com')
   self.assertNotIn('TEST_ONLY',str(msg))
   smtp.return_value.__enter__.return_value.starttls.assert_called_once()

class FakeGH:
 def __init__(self,comments=None,change_head=False):
  self.comments=comments or []; self.posts=[]; self.reads=0;self.change_head=change_head
 def request(self,path,data=None):
  if data is not None:self.posts.append(data);return dict(id=77)
  self.reads+=1
  return dict(number=1,state='open',draft=False,head={'sha':'f'*40 if self.change_head and self.reads>1 else HEAD})
 def pages(self,path):
  if path=='/pulls?state=open':return [dict(number=1)]
  if path.endswith('/comments') and path.startswith('/issues'):return self.comments
  if path.endswith('/comments') and path.startswith('/pulls'):return [finding()]
  return []

class DeliveryTests(unittest.TestCase):
 def test_once_recorded(self):
  state,fs=n.classify(HEAD,[],[],[finding()],[])
  marker='<!-- kaspper-native-alert:'+n.key_for(1,HEAD,state,fs)+' -->'
  gh=FakeGH([dict(user={'login':'github-actions[bot]','id':n.ACTIONS_ID},body=marker+'\nEstado de envio: SMTP_ACEITO')])
  with patch.object(n,'send_alert') as send:
   self.assertEqual(n.run(gh,{},'schedule')[0]['mail'],'JA_REGISTRADO');send.assert_not_called()
 def test_new_head_before_send(self):
  with patch.object(n,'send_alert') as send:
   self.assertEqual(n.run(FakeGH(change_head=True),{},'schedule')[0]['mail'],'DESCARTADO_NOVO_HEAD');send.assert_not_called()
 def test_failed_send_no_success_receipt(self):
  gh=FakeGH()
  with patch.object(n,'send_alert',side_effect=ValueError('no SMTP')):
   r=n.run(gh,{},'schedule');self.assertIn('PENDENTE',r[0]['mail'])
   self.assertNotIn('SMTP_ACEITO',gh.posts[0]['body'])
 def test_forbidden_audit_prevents_email(self):
  gh=FakeGH(); original=gh.request
  def request(path,data=None):
   if data is not None: raise n.HTTPError('https://api.github.com',403,'Forbidden',{},None)
   return original(path,data)
  gh.request=request
  with patch.object(n,'send_alert') as send:
   result=n.run(gh,{},'schedule')
   self.assertEqual(result[0]['mail'],'BLOQUEADO_REGISTRO_GITHUB');send.assert_not_called()
 def test_event_human_ignored(self):
  gh=FakeGH()
  self.assertEqual(n.run(gh,{'comment':{'user':{'login':'human','id':1}},'issue':{'number':1,'pull_request':{}}},'issue_comment'),[])
if __name__=='__main__':unittest.main()
