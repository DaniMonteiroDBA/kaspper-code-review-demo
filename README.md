# Kaspper — revisão automática no GitHub
Laboratório privado, Python com dados sintéticos. Sem merge automático.
PR pronto no mesmo repositório → contratos do baseline + Codex → relatório no PR e artefatos. Sem defeito material e com verificações completas, conclui sem review humano. Defeito P0/P1/P2 ou resultado inconclusivo envia alerta para danibruxinha@gmail.com.
## Ativar
Settings → Secrets and variables → Actions → New repository secret:
- OPENAI_API_KEY: chave API OpenAI; cobrança separada do ChatGPT. Defina limite de gasto no projeto API.
- SMTP_USERNAME: endereço da conta remetente.
- SMTP_PASSWORD: credencial SMTP (Gmail: senha de aplicativo, se disponível).
Variável opcional SMTP_HOST; padrão smtp.gmail.com, porta 587 STARTTLS.
Nunca envie chaves/senhas pelo chat nem as coloque no código. Este pacote não cadastrou credenciais.
## Demonstrar
Torne cada PR draft pronto com Ready for review, um por vez:
- Limpo: renomeia variável corretamente.
- P1: remove isolamento entre clientes.
- P2: aceita page=0 quebrando contrato.
- P0: esvazia migração; P0 pressupõe substituição integral dos registros.
Confira Actions → jobs contracts, codex e document; abra o comentário no PR. No caso com erro, confirme também o recebimento do e-mail.
## Perguntas do time
No comentário do PR: /review-question Por que esta alteração pode gerar bug? Cite o cenário e as linhas.
Colaboradores com escrita/admin podem perguntar; o Codex consulta o diff e responde no PR. Cada pergunta usa a API. Workflow de perguntas precisa estar em main.
## Limites
Critérios em AGENTS.md são propostas do ensaio. P2 também pode ser bug. Não há garantia de detecção ou prioridade exata. Mudanças fora de orders.py são inconclusivas nesta versão.
Contratos do baseline não podem ser relaxados pelo PR. Job de testes não recebe OpenAI/SMTP nem token de escrita. Codex lê candidato sem executar código, em sandbox read-only. Documentação e SMTP ficam em job separado com código do baseline.
Novo commit antes da publicação invalida resultado antigo. Reexecuções intencionais podem gerar novo comentário e e-mail; não há garantia de entrega exactly-once.
Relatórios JSON/MD ficam como artefatos 90 dias; comentários permanecem no PR. Para auditoria corporativa, integrar destino durável oficial.
Sem credenciais, revisão não roda corretamente e envio não é realizado; isso não é tratado como aprovação. Aceite SMTP não comprova entrega na caixa.
Gate document fica vermelho para defeito/inconclusivo. Configure proteção de main exigindo o check se quiser bloquear merge; as proteções não são criadas pelo código.
## Validação
python3 -m unittest -v
python3 -m unittest discover -s .github/review -p 'test_*.py' -v
Validação local em docs/VALIDACAO.md. API, email e conversa ainda precisam de validação ponta a ponta após secrets.
## Fontes
https://learn.chatgpt.com/docs/github-action
https://learn.chatgpt.com/docs/code-review
