# Kaspper — Code Review sem chave API

Ensaio privado, código Python e dados sintéticos. O caminho atual é a integração nativa Codex ↔ GitHub, usando o acesso e os limites disponíveis no plano ChatGPT. Não exige OPENAI_API_KEY.

## Ativar
1. Abra o Codex e suas configurações de revisão de código.
2. Conecte/autorize este repositório na integração Codex, se não aparecer. O acesso do conector deste chat não comprova habilitação do serviço de review.
3. Habilite Automatic review / Review code para DaniMonteiroDBA/kaspper-code-review-demo e configure as preferências/gatilhos.
4. Abra o PR #1 e clique Ready for review. Confirme que o Codex realmente reage e publica resultado.
5. Para teste manual, comente @codex review no PR.

## Cenários
- PR #1: alteração limpa.
- PR #2: isolamento entre clientes.
- PR #3: paginação — P2 esperado no relatório local; pode não aparecer na revisão nativa do GitHub, que documenta somente P0/P1.
- PR #4: perda de registros sob a hipótese de substituição integral do conjunto persistido.

AGENTS.md contém critérios propostos. Os PRs são rascunhos, não fazer merge. Ausência de comentários não significa que revisão rodou ou que não há defeitos.

## Perguntas
Abra o PR no Code Review do aplicativo ChatGPT/Codex e faça perguntas no chat associado. Não use /review-question: esse comando pertencia ao workflow com API e está pausado. @codex com texto diferente de review inicia outra tarefa na integração; não presumir que toda pergunta tem o mesmo comportamento da revisão nativa.

## O que falta comprovar
- Execução nativa do caso com erro e teste de recebimento de e-mail.
- Formato de resultado da mudança limpa e documentação disponível.
- Encaminhamento sem revisão humana conforme política da fábrica.
- Recebimento real do alerta em danibruxinha@gmail.com após configurar SMTP.

Notificações comuns do GitHub não equivalem ao alerta seletivo por defeito. Um adaptador pode enviar SMTP a partir de achados do bot sem chamar a API OpenAI; requer identificar o evento/resultado real e configurar remetente. Destinatário não é credencial de envio. O adaptador foi instalado; envio real depende de SMTP configurado e validação.

## Fluxos anteriores
review.yml e question.yml dependem de API e tiveram gatilhos automáticos removidos. Estão preservados somente como referência com execução manual; não acioná-los neste ensaio. Scripts de SMTP/normalização permanecem como candidatos não integrados à revisão nativa. Não cadastrar chave API para o caminho atual.

## Evidências
10 testes baseline e 5 de decisão passaram localmente; SMTP foi simulado, nenhum e-mail enviado. Um workflow real do PR draft foi reconhecido e skipped. Em 06/10/2026 o PR #1 teve revisão nativa Completed e reação 👍 confirmadas.

## Fontes oficiais
https://learn.chatgpt.com/docs/third-party/github
https://learn.chatgpt.com/docs/code-review

## Alerta seletivo sem API OpenAI — instalado
O workflow native-alert.yml lê os eventos e resultados da revisão nativa. Só aceita o bot chatgpt-codex-connector[bot] com id 199175422, observado no PR #1, e achados P0/P1/P2 associados ao head atual. Comentários humanos, P3, revisões em andamento e achados antigos não enviam e-mail.

Eventos issue_comment criado/editado iniciam a verificação; uma reconciliação a cada 15 minutos cobre atraso entre conclusão, achados e reação. Agendamentos GitHub podem atrasar. Também é possível Actions → Alerta seletivo da revisao nativa → Run workflow. Tudo executa a partir de main, sem checkout ou execução do código candidato e sem chave OpenAI.

Cadastre em Settings → Secrets and variables → Actions:
- SMTP_USERNAME: e-mail da conta remetente.
- SMTP_PASSWORD: credencial SMTP do remetente; Gmail usa senha de app, se disponível.
- SMTP_HOST (variável opcional): padrão smtp.gmail.com, porta 587 STARTTLS.
Destinatário fixo: danibruxinha@gmail.com. Nunca cole senha no chat. Sem remetente configurado, um achado fica PENDENTE e o job falha, sem fingir envio.

Revisão concluída + reação 👍 do bot posterior à conclusão + ausência de achados reportados no head: registra SEM_ACHADOS_REPORTADOS sem e-mail. Isso não aprova merge, não certifica ausência de bugs e não substitui CI.

Achados ou falha explícita de revisão geram alerta. O comentário de recibo evita reenvio para o mesmo conjunto de achados no mesmo head quando SMTP_ACEITO está registrado. Há limite: falha após aceite SMTP mas antes do recibo pode causar duplicação; não há garantia exactly-once. Novos achados geram nova chave. Achados dismissed são ignorados; resolução de threads não é interpretada como nova aprovação. E-mail leva prioridade, arquivo/linha e links, sem corpo do código.

Formato de falhas/achados ainda precisa ser corroborado em resultado real; formato Completed + 👍 foi observado no PR #1. Mudança no formato do bot pode exigir ajuste. 22 testes passaram com fixtures e SMTP simulado. Nenhum envio real confirmado.
