# Alerta seletivo da revisão nativa — 06/10/2026

Implementado sem OPENAI_API_KEY. O Codex revisa no GitHub; o adaptador lê seu resultado e usa GITHUB_TOKEN automático para registrar o encaminhamento. SMTP é o serviço de envio separado.

## Comportamento
- P0/P1/P2 publicados pelo bot no commit atual: e-mail para danibruxinha@gmail.com.
- Falha explícita da revisão atual: alerta para intervenção.
- Completed no commit atual + reação 👍 posterior pelo bot + sem achados: registra SEM_ACHADOS_REPORTADOS, sem e-mail.
- Revisão em andamento, silêncio ou resultado antigo: aguardando; não significa aprovação.
- P2 não é garantido na revisão nativa, que prioriza P0/P1. O adaptador consome P2 se publicado.
- Nenhum merge automático; este componente encaminha e documenta achados.

O gatilho é o comentário nativo no PR, com conferência periódica a cada 15 minutos como recuperação. A periodicidade é nominal; GitHub pode atrasar execuções. Para perguntas, o time pode mencionar @codex no PR. Para nova revisão manual, comentar @codex review.

## Evidência real
1. PR #1: summary 6020799538, commit 8415db89927d7b8e9328811102d0758f550e72a8, Completed 16:33:10Z e 👍 16:33:12Z. Fundamentou o reconhecimento de revisão concluída sem achados. Após atualização de workflows, revisão do novo head b3a51931dd79c7caa9c3e96990c23b130d904db1 concluiu às 16:45:34Z, com 👍 às 16:45:36Z. A [execução 37498227670](https://github.com/DaniMonteiroDBA/kaspper-code-review-demo/actions/runs/37498227670) terminou com sucesso e [documentou SEM_ACHADOS_REPORTADOS / NAO_NECESSARIO](https://github.com/DaniMonteiroDBA/kaspper-code-review-demo/pull/1#issuecomment-6021030093), sem enviar e-mail.
2. PR #2: commit 5818303dadcf1b96fdf7d4e89651b0c375b3b8a0, achado real P1: remover o filtro de tenant expõe pedidos de outro cliente. [Achado do Codex](https://github.com/DaniMonteiroDBA/kaspper-code-review-demo/pull/2#discussion_r4197993955).
3. [Execução 37497929539](https://github.com/DaniMonteiroDBA/kaspper-code-review-demo/actions/runs/37497929539): 23 testes passaram; o adaptador registrou ACHADOS/PENDENTE no PR #2. A execução terminou com falha intencional porque SMTP_USERNAME e SMTP_PASSWORD estão ausentes. [Registro pendente](https://github.com/DaniMonteiroDBA/kaspper-code-review-demo/pull/2#issuecomment-6020992365). Nenhum e-mail real foi enviado.
4. O comentário histórico INCONCLUSIVO em #1 vem do workflow antigo baseado em API, atualmente pausado em main e nas quatro branches de ensaio. Não é resultado da revisão nativa.

## Ativar remetente
Abrir [Settings → Secrets and variables → Actions](https://github.com/DaniMonteiroDBA/kaspper-code-review-demo/settings/secrets/actions), escolher New repository secret e cadastrar:
| Secret | Valor |
| --- | --- |
| SMTP_USERNAME | E-mail completo da conta remetente |
| SMTP_PASSWORD | Credencial SMTP da conta; para Gmail, senha de app |

Padrão instalado: smtp.gmail.com, porta 587, STARTTLS. Para outro serviço compatível com esse modo, cadastrar a variável SMTP_HOST e suas credenciais. Não colocar senhas no chat, código ou PR.

Gmail: [gerar senha de app](https://myaccount.google.com/apppasswords); exige verificação em duas etapas e disponibilidade desse recurso na conta. [Instruções oficiais](https://support.google.com/mail/answer/185833?hl=pt-BR).
Depois de cadastrar, abrir [Actions](https://github.com/DaniMonteiroDBA/kaspper-code-review-demo/actions/workflows/native-alert.yml), selecionar Run workflow em main. O P1 pendente será reenviado. Conferir SMTP_ACEITO no PR e o recebimento na caixa danibruxinha@gmail.com. Só então o envio real está validado.

## Validação e limites
23 testes cobrem P0/P1/P2 e badges, identidade do bot, head antigo, revisão dismissed, reação antiga, silêncio, revisão em andamento, falta de SMTP, TLS, destinatário, deduplicação, mudança de head e bloqueio da escrita antes do envio. SMTP foi simulado nos testes.

Recibos são por PR, commit e conjunto de achados. SMTP_ACEITO significa aceite pelo servidor, não confirmação de entrega. Uma interrupção entre envio e gravação do recibo pode duplicar o e-mail; não há garantia de exatamente uma entrega. Achados adicionais podem gerar novo alerta.
O workflow executa somente código de main, sem executar código do PR com credenciais SMTP. Resultados JSON ficam como artefatos por 90 dias e os recibos ficam no PR.
