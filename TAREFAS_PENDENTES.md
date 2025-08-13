# Tarefas Pendentes ForYou (por Etapa)

## Dashboard Administrativo
- [ ] Implementar frontend para exibir alertas críticos em tempo real usando o novo endpoint `/admin/api/critical-alerts`.
- [ ] Garantir que todos os endpoints de exportação/análise estejam documentados e acessíveis via interface administrativa.

## Chat
- [x] Revisar e/ou implementar endpoints REST para gerenciamento de sessões de chat (listar, buscar, exportar, encerrar, etc).
- [x] Implementar endpoints REST para envio/recebimento de mensagens do chat e persistência do histórico.
- [x] Padronizar endpoints para `/api/chat/send` e `/api/chat/receive`.
- [x] Garantir uso exclusivo do OpenAI (fallback para outros LLMs removido - tarefa pendente abaixo).
- [ ] Implementar painel de monitoramento de chats ativos para admin/voluntários.
- [ ] Integrar IA e lógica de triagem automática no chat (se ainda não estiver 100%).
- [ ] Garantir anonimização e LGPD no histórico de chat exportado.
- [ ] [Pendente] Adicionar fallback para outros LLMs (spaCy, BERT, etc) caso necessário futuramente.

## Voluntários/Profissionais
- [ ] Implementar painel de atribuição de casos para voluntários/profissionais (se aplicável).
- [ ] Criar endpoint para feedback/revisão de atendimentos realizados por voluntários.

## Cliente/Usuário Final
- [ ] Garantir que o dashboard do cliente exiba corretamente métricas e histórico pessoal.
- [ ] Revisar fluxo de onboarding e consentimento LGPD.

## Documentação e Testes
- [ ] Documentar todos os endpoints REST/JSON disponíveis.
- [ ] Adicionar testes automatizados para os principais fluxos (login, dashboard, chat, exportação).

---

Se desejar detalhar ou priorizar alguma etapa, me avise!
