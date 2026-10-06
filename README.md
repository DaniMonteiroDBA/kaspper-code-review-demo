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
- Ativação e execução do review nativo na sua conta.
- Formato de resultado da mudança limpa e documentação disponível.
- Encaminhamento sem revisão humana conforme política da fábrica.
- E-mail seletivo para danibruxinha@gmail.com.

Notificações comuns do GitHub não equivalem ao alerta seletivo por defeito. Um adaptador pode enviar SMTP a partir de achados do bot sem chamar a API OpenAI; requer identificar o evento/resultado real e configurar remetente. Destinatário não é credencial de envio. Não há envio seletivo ativo nesta versão.

## Fluxos anteriores
review.yml e question.yml dependem de API e tiveram gatilhos automáticos removidos. Estão preservados somente como referência com execução manual; não acioná-los neste ensaio. Scripts de SMTP/normalização permanecem como candidatos não integrados à revisão nativa. Não cadastrar chave API para o caminho atual.

## Evidências
10 testes baseline e 5 de decisão passaram localmente; SMTP foi simulado, nenhum e-mail enviado. Um workflow real do PR draft foi reconhecido e skipped. Não confundir esses resultados com revisão nativa já executada.

## Fontes oficiais
https://learn.chatgpt.com/docs/third-party/github
https://learn.chatgpt.com/docs/code-review
