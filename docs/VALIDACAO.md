# Validação local — 06/10/2026

10 contratos baseline e 5 testes de decisão passaram. Ambos workflows YAML parseados. Os defeitos sintéticos foram corroborados no ensaio anterior: perda de dados, isolamento e paginação. API OpenAI, postagem no PR, SMTP e resposta automática ainda não foram executados; dependem de secrets e de tornar um PR pronto.

SMTP simulado: destinatário, STARTTLS, ausência da senha no corpo e rejeição sem credenciais verificados; nenhum e-mail enviado. Workflow real do primeiro PR foi reconhecido pelo GitHub e ficou skipped por ser draft.
