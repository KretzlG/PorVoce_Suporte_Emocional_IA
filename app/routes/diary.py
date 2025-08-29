# COMO EU PLANEJO FAZER A ESTRUTURA DISSO:

# 1. Importar as bibliotecas necessárias
# 2. Definir o blueprint para as rotas do diário
# 3. Criar a rota para adicionar uma nova entrada no diário
# 4. Criar a rota para visualizar todas as entradas do diário do usuário
# 5. Criar a rota para visualizar uma entrada específica do diário


# QUESTÕES TÉCNICAS

# Ao enviar um Diario, ele será convertido em jSON
# este JSON sera enviado para IA analisar
# a IA retornará um JSON com os dados analisados e aplicar as informações necessárias no banco de dados do usuário
# Exemplo de JSON que a IA retornará:
# {
#     "sentiment_score": 0.75,
#     "risk_level": "low",
#     "risk_factors": ["stress", "anxiety"],
#     "keywords": ["work", "family", "health"],
#     "mood_level": 4,
#     "emotions": ["happy", "relieved"]
# }

# Todo JSON enviado para a IA será armazenado no banco de dados do usuário com algumas propriedades básicas como data, hora, id do usuário, etc.
# Exemplo de JSON que será armazenado no banco de dados do usuário:
# {
#     "user_id": 1,
#     "entry_id": 1,
#     "timestamp": "2023-10-01T12:00:00Z",
#     "diary_entry": {
#         "title": "Meu dia no trabalho",
#         "content": "Hoje foi um dia estressante no trabalho...",
#         "is_private": true,
#         "visible_to_volunteers": false
#     },
#     "analysis": {
#         "sentiment_score": 0.75,
#         "risk_level": "low",
#         "risk_factors": ["stress", "anxiety"],
#         "keywords": ["work", "family", "health"],
#         "mood_level": 4,
#         "emotions": ["happy", "relieved"]
#     }