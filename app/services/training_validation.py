"""
Serviço de validação de conteúdo de treinamento
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import openai
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class TrainingValidationService:
    """
    Serviço para validar conteúdo de treinamento da IA
    """
    
    def __init__(self):
        self.ai_service = AIService()
        
        # Palavras e padrões proibidos
        self.prohibited_keywords = [
            # Conteúdo violento
            'suicídio', 'suicidio', 'matar', 'violência', 'violencia', 'agressão', 'agressao',
            'ferimento', 'machucar', 'cortar', 'autolesão', 'autolesao',
            
            # Conteúdo sexual explícito
            'sexo', 'sexual', 'pornografia', 'pornografico', 'erótico', 'erotico',
            
            # Drogas e substâncias
            'droga', 'cocaína', 'cocaina', 'maconha', 'heroína', 'heroina', 'crack',
            'álcool', 'alcool', 'bebida alcoólica', 'bebida alcoolica',
            
            # Discriminação
            'racismo', 'racista', 'homofobia', 'homofóbico', 'homofobico', 
            'transfobia', 'transfóbico', 'transfobico', 'xenofobia',
            
            # Informações médicas específicas
            'diagnóstico', 'diagnostico', 'remédio', 'medicamento', 'prescrição', 'prescricao',
            'dosagem', 'tratamento médico', 'tratamento medico'
        ]
        
        # Padrões regex para detectar conteúdo problemático
        self.prohibited_patterns = [
            r'\b(?:como|onde|quero)\s+(?:comprar|conseguir|obter)\s+(?:droga|drogas)\b',
            r'\b(?:receita|formula|fórmula)\s+(?:caseira|para)\s+(?:droga|drogas|veneno)\b',
            r'\b(?:formas|maneiras|jeitos)\s+de\s+(?:morrer|suicidar|se matar)\b',
            r'\b(?:locais|lugares|sites)\s+(?:para|de)\s+(?:comprar|conseguir)\s+(?:arma|drogas)\b'
        ]
        
        # Temas obrigatórios para aprovação
        self.required_themes = [
            'apoio emocional', 'suporte psicológico', 'bem-estar mental', 'saúde mental',
            'acolhimento', 'escuta ativa', 'empatia', 'resiliência', 'autocuidado',
            'técnicas de relaxamento', 'mindfulness', 'meditação', 'respiração',
            'inteligência emocional', 'gestão de emoções', 'autoestima', 'autoconfiança'
        ]
    
    def validate_content(self, content: str, title: str = "", description: str = "") -> Dict:
        """
        Valida o conteúdo de treinamento
        
        Args:
            content: Conteúdo a ser validado
            title: Título do conteúdo
            description: Descrição do conteúdo
            
        Returns:
            Dict com resultado da validação
        """
        try:
            full_text = f"{title} {description} {content}".lower()
            
            validation_result = {
                'is_valid': True,
                'score': 1.0,
                'issues': [],
                'recommendations': [],
                'detected_themes': []
            }
            
            # 1. Verificar palavras proibidas
            prohibited_found = self._check_prohibited_content(full_text)
            if prohibited_found:
                validation_result['is_valid'] = False
                validation_result['score'] -= 0.5
                validation_result['issues'].extend([
                    f"Conteúdo proibido detectado: {', '.join(prohibited_found)}"
                ])
            
            # 2. Verificar padrões problemáticos
            pattern_issues = self._check_prohibited_patterns(full_text)
            if pattern_issues:
                validation_result['is_valid'] = False
                validation_result['score'] -= 0.3
                validation_result['issues'].extend(pattern_issues)
            
            # 3. Verificar relevância temática
            theme_score = self._check_theme_relevance(full_text)
            validation_result['detected_themes'] = self._detect_themes(full_text)
            
            if theme_score < 0.3:
                validation_result['score'] -= 0.2
                validation_result['recommendations'].append(
                    "Conteúdo tem baixa relevância para suporte emocional. "
                    "Considere incluir mais temas relacionados a bem-estar mental."
                )
            
            # 4. Validação via IA (se disponível)
            ai_validation = self._ai_content_validation(content)
            if ai_validation:
                if not ai_validation['is_appropriate']:
                    validation_result['is_valid'] = False
                    validation_result['score'] -= 0.4
                    validation_result['issues'].append(
                        f"IA detectou conteúdo inadequado: {ai_validation['reason']}"
                    )
                
                validation_result['score'] = min(1.0, validation_result['score'] * ai_validation['quality_score'])
            
            # 5. Verificar qualidade mínima
            if len(content.strip()) < 50:
                validation_result['score'] -= 0.1
                validation_result['recommendations'].append(
                    "Conteúdo muito curto. Recomenda-se pelo menos 50 caracteres."
                )
            
            # Normalizar score
            validation_result['score'] = max(0.0, min(1.0, validation_result['score']))
            
            # Se score muito baixo, marcar como inválido
            if validation_result['score'] < 0.5:
                validation_result['is_valid'] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Erro na validação de conteúdo: {str(e)}")
            return {
                'is_valid': False,
                'score': 0.0,
                'issues': [f"Erro interno na validação: {str(e)}"],
                'recommendations': [],
                'detected_themes': []
            }
    
    def _check_prohibited_content(self, text: str) -> List[str]:
        """Verifica palavras proibidas no texto"""
        found = []
        for keyword in self.prohibited_keywords:
            if keyword in text:
                found.append(keyword)
        return found
    
    def _check_prohibited_patterns(self, text: str) -> List[str]:
        """Verifica padrões problemáticos no texto"""
        issues = []
        for pattern in self.prohibited_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Padrão problemático detectado: {pattern}")
        return issues
    
    def _check_theme_relevance(self, text: str) -> float:
        """Calcula relevância temática do conteúdo"""
        theme_count = 0
        for theme in self.required_themes:
            if theme in text:
                theme_count += 1
        
        return min(1.0, theme_count / len(self.required_themes) * 3)
    
    def _detect_themes(self, text: str) -> List[str]:
        """Detecta temas presentes no texto"""
        detected = []
        for theme in self.required_themes:
            if theme in text:
                detected.append(theme)
        return detected
    
    def _ai_content_validation(self, content: str) -> Optional[Dict]:
        """
        Usa IA para validar conteúdo
        """
        try:
            prompt = f"""
            Você é um especialista em saúde mental e suporte emocional. 
            Analise o seguinte conteúdo de treinamento para um chatbot de suporte emocional:

            CONTEÚDO:
            {content}

            Avalie se este conteúdo é:
            1. Apropriado para suporte emocional
            2. Seguro e não prejudicial
            3. Útil para treinar uma IA de suporte

            Responda em JSON com:
            {{
                "is_appropriate": true/false,
                "quality_score": 0.0-1.0,
                "reason": "explicação breve",
                "suggestions": ["sugestão1", "sugestão2"]
            }}
            """
            
            response = self.ai_service._get_openai_response(prompt)
            
            if response:
                # Tentar extrair JSON da resposta
                import json
                try:
                    # Buscar JSON na resposta
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = response[start:end]
                        return json.loads(json_str)
                except (json.JSONDecodeError, ValueError):
                    logger.warning("Resposta da IA não está em formato JSON válido")
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na validação por IA: {str(e)}")
            return None
    
    def validate_file_content(self, file_path: str, file_type: str) -> Dict:
        """
        Valida conteúdo de arquivo
        
        Args:
            file_path: Caminho do arquivo
            file_type: Tipo do arquivo (pdf, doc, txt, etc.)
            
        Returns:
            Dict com resultado da validação
        """
        try:
            content = self._extract_file_content(file_path, file_type)
            if not content:
                return {
                    'is_valid': False,
                    'score': 0.0,
                    'issues': ['Não foi possível extrair conteúdo do arquivo'],
                    'recommendations': ['Verifique se o arquivo não está corrompido'],
                    'detected_themes': []
                }
            
            return self.validate_content(content)
            
        except Exception as e:
            logger.error(f"Erro na validação de arquivo: {str(e)}")
            return {
                'is_valid': False,
                'score': 0.0,
                'issues': [f"Erro ao processar arquivo: {str(e)}"],
                'recommendations': [],
                'detected_themes': []
            }
    
    def _extract_file_content(self, file_path: str, file_type: str) -> Optional[str]:
        """
        Extrai conteúdo de diferentes tipos de arquivo
        """
        try:
            if file_type.lower() in ['txt', 'text']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_type.lower() == 'pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        return text
                except ImportError:
                    logger.warning("PyPDF2 não disponível para extração de PDF")
                    return None
            
            elif file_type.lower() in ['doc', 'docx']:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    logger.warning("python-docx não disponível para extração de DOC")
                    return None
            
            elif file_type.lower() == 'odt':
                try:
                    from odf import text, teletype
                    from odf.opendocument import load
                    
                    textdoc = load(file_path)
                    allparas = textdoc.getElementsByType(text.P)
                    content = ""
                    for para in allparas:
                        content += teletype.extractText(para) + "\n"
                    return content
                except ImportError:
                    logger.warning("odfpy não disponível para extração de ODT")
                    return None
            
            else:
                logger.warning(f"Tipo de arquivo não suportado: {file_type}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo do arquivo: {str(e)}")
            return None
    
    def get_validation_summary(self, validation_result: Dict) -> str:
        """
        Gera um resumo legível da validação
        """
        if validation_result['is_valid']:
            status = "✅ APROVADO"
        else:
            status = "❌ REJEITADO"
        
        score = validation_result['score']
        score_text = f"Score: {score:.2f}/1.00"
        
        summary = f"{status} - {score_text}\n\n"
        
        if validation_result['issues']:
            summary += "🚨 PROBLEMAS ENCONTRADOS:\n"
            for issue in validation_result['issues']:
                summary += f"• {issue}\n"
            summary += "\n"
        
        if validation_result['recommendations']:
            summary += "💡 RECOMENDAÇÕES:\n"
            for rec in validation_result['recommendations']:
                summary += f"• {rec}\n"
            summary += "\n"
        
        if validation_result['detected_themes']:
            summary += "🎯 TEMAS DETECTADOS:\n"
            for theme in validation_result['detected_themes']:
                summary += f"• {theme}\n"
        
        return summary
