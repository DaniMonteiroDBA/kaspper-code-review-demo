# Validação do alerta nativo — 06/10/2026

22 testes locais passaram. Foram cobertos identidade do bot, P0/P1/P2, badge de prioridade, head antigo, revisão dismissed, reação antiga, revisão em andamento, silêncio, falta de SMTP, STARTTLS, destinatário fixo, deduplicação e mudança de head antes do envio. SMTP simulado: nenhum e-mail real enviado.

Observação real: PR #1, summary 6020799538, head 8415db89927d7b8e9328811102d0758f550e72a8, Completed 16:33:10Z e reação +1 do bot 16:33:12Z. O formato fundamenta a classificação sem achados reportados.

Formato de achados inicialmente baseado em fixtures; verificar no PR #2 ao ativar. Envio requer credenciais cadastradas diretamente no GitHub. Revisão nativa não usa OPENAI_API_KEY; adaptador usa o GITHUB_TOKEN automático e SMTP.
