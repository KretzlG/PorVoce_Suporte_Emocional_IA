#!/usr/bin/env python3
"""
Script para corrigir referências ao CVV 188 no ai_prompt.py
"""

import re

# Ler o arquivo atual
with open('app/services/ai_prompt.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituições para focar na triagem interna
replacements = [
    # Fallback responses - critical
    (r'preciso que você busque ajuda AGORA\. "\s*"Ligue 188 \(CVV\) ou vá ao hospital\. Sua vida importa! 🚨"',
     'SITUAÇÃO CRÍTICA DETECTADA! "\n                "Nossa equipe especializada foi acionada para te apoiar. 🚨"'),
    
    (r'situação séria! CVV: 188 \(24h\) ou hospital IMEDIATAMENTE\. "\s*"Você merece viver e ser feliz! ⚠️"',
     'TRIAGEM EMERGENCIAL ATIVADA! "\n                "Um profissional entrará em contato imediatamente. ⚠️"'),
    
    (r'URGENTE: ligue 188 ou procure ajuda médica AGORA\. "\s*"Não espere, você é importante! 🆘"',
     'VOCÊ NÃO ESTÁ SOZINHO! "\n                "Nossa equipe de crise está organizando seu atendimento AGORA. 🆘"'),
    
    # Fallback responses - high
    (r'hora de buscar ajuda profissional\. "\s*"CVV: 188 está disponível 24h\. Você consegue superar isso! .*?"',
     'nossa triagem especializada irá te atender. "\n                "Você merece todo o suporte que podemos oferecer! 💪"'),
    
    (r'conversar com um psicólogo pode mudar tudo\. "\s*"CVV: 188 para emergências\. Você tem força! 🌟"',
     'conectando você com nossa equipe de profissionais. "\n                "Juntos vamos encontrar soluções. Você tem força! 🌟"'),
    
    (r'procure ajuda profissional hoje mesmo\. "\s*"CVV: 188 sempre disponível\. Dias melhores vão chegar! ☀️"',
     'acionando protocolo de apoio intensivo. "\n                "Nossa plataforma está aqui para você. Dias melhores vão chegar! ☀️"'),
    
    # Emergency prompts
    (r'- Mencione CVV: 188 \(24 horas\)',
     '- Ative triagem emergencial interna'),
    
    (r"'cvv': \"CVV - Centro de Valorização da Vida: 188 \(24h\)\"",
     "'triagem_interna': \"Triagem Especializada - Equipe interna disponível 24h\""),
]

# Aplicar substituições
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Salvar arquivo corrigido
with open('app/services/ai_prompt.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Correções aplicadas no ai_prompt.py")
