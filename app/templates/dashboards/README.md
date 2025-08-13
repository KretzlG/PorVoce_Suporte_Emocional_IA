# ForYou - Sistema de Dashboards

Este diretório contém o sistema completo de dashboards para a plataforma ForYou, desenvolvido com base no modelo de dashboard profissional fornecido, mas totalmente adaptado às cores e identidade visual do projeto.

## 📁 Estrutura de Arquivos

```
app/dashboards/
├── static/
│   ├── css/
│   │   └── dashboard-base.css     # Estilos base para todos os dashboards
│   └── js/
│       └── dashboard-base.js      # JavaScript base com funcionalidades comuns
├── templates/
│   ├── dashboard-base.html        # Template base para todos os dashboards
│   ├── admin/
│   │   └── dashboard.html         # Dashboard específico do administrador
│   ├── client/
│   │   └── dashboard.html         # Dashboard específico do cliente
│   └── volunteer/
│       └── dashboard.html         # Dashboard específico do voluntário
└── README.md                      # Esta documentação
```

## 🎨 Paleta de Cores

O sistema utiliza a paleta rose profissional do ForYou:

- **Primary**: `#be0049` (Rose Dark)
- **Secondary**: `#ff348e` (Rose Medium)  
- **Accent**: `#ff97ca` (Rose Light)
- **Light**: `#ffffff` (White)
- **Dark**: `#770021` (Rose Darker)

## 🏗️ Componentes Base

### Layout Principal
- **Sidebar**: 280px de largura (80px colapsada)
- **Header**: 75px de altura
- **Content**: Responsivo com grid system

### Sistema de Grid
- `grid-cols-1` a `grid-cols-4`
- Gap de 24px entre elementos
- Totalmente responsivo

### Cards e Componentes
- **Stats Cards**: Para exibição de métricas
- **Dashboard Cards**: Containers principais
- **Action Cards**: Para ações rápidas
- **Empty States**: Estados vazios elegantes

## 📱 Responsividade

### Breakpoints
- **Desktop**: 1024px+
- **Tablet**: 768px - 1023px
- **Mobile**: < 768px

### Comportamentos Responsivos
- Sidebar colapse automático em mobile
- Grid adapta colunas automaticamente
- Componentes se reorganizam verticalmente
- Textos e espaçamentos se ajustam

## 🚀 Funcionalidades JavaScript

### Classe ForYouDashboard
- **Toggle Sidebar**: Colapsar/expandir menu lateral
- **Navigation**: Gerenciamento de navegação ativa
- **Animations**: Sistema de animações suaves
- **Notifications**: Sistema de notificações
- **API Helpers**: Funções para requisições
- **Formatters**: Formatação de números, datas e valores

### Principais Métodos
```javascript
// Alterar status da sidebar
toggleSidebar()

// Exibir notificação
showNotification(message, type)

// Atualizar estatísticas com animação
updateStats(elementId, value, animation)

// Realizar requisição API
makeRequest(url, options)
```

## 🎯 Dashboards Específicos

### 1. Dashboard Administrador (`admin/dashboard.html`)
**Funcionalidades:**
- Visão geral completa do sistema
- Gestão de usuários e voluntários
- Monitoramento de conversas
- Análise de riscos
- Relatórios e estatísticas
- Configurações do sistema

**Navegação:**
- Visão Geral
- Gerenciar Usuários
- Voluntários
- Conversas
- Diários
- Relatórios
- Análise de Risco
- Configurações
- Logs do Sistema

### 2. Dashboard Cliente (`client/dashboard.html`)
**Funcionalidades:**
- Interface amigável e acolhedora
- Acesso rápido a nova conversa
- Sistema de humor diário
- Histórico de conversas
- Diário pessoal
- Recursos de apoio
- Acesso a emergência

**Navegação:**
- Início
- Nova Conversa
- Conversas Anteriores
- Escrever no Diário
- Minhas Entradas
- Materiais de Apoio
- Ajuda de Emergência
- Meu Perfil

**Componentes Únicos:**
- **Mood Selector**: Sistema de registro de humor
- **Welcome Card**: Card de boas-vindas personalizado
- **Quick Actions**: Ações rápidas para recursos

### 3. Dashboard Voluntário (`volunteer/dashboard.html`)
**Funcionalidades:**
- Toggle de disponibilidade
- Fila de atendimento em tempo real
- Gestão de conversas ativas
- Estatísticas de voluntariado
- Recursos de treinamento
- Sistema de notificações

**Navegação:**
- Visão Geral
- Fila de Atendimento
- Conversas Ativas
- Histórico
- Treinamentos
- Diretrizes
- Meu Perfil
- Disponibilidade

**Componentes Únicos:**
- **Status Toggle**: Controle de disponibilidade
- **Queue Management**: Gestão da fila de atendimento
- **Real-time Updates**: Atualizações em tempo real

## ⚙️ Configuração e Uso

### 1. Incluir os Assets Base
```html
<!-- CSS Base -->
<link rel="stylesheet" href="{{ url_for('static', filename='../dashboards/static/css/dashboard-base.css') }}">

<!-- JavaScript Base -->
<script src="{{ url_for('static', filename='../dashboards/static/js/dashboard-base.js') }}"></script>
```

### 2. Estender Template Base
```html
{% extends "dashboards/templates/dashboard-base.html" %}

{% block title %}Meu Dashboard{% endblock %}
{% block page_title %}Título da Página{% endblock %}

{% block sidebar_nav %}
<!-- Navegação específica -->
{% endblock %}

{% block content %}
<!-- Conteúdo específico -->
{% endblock %}
```

### 3. Personalizar Estilos
```html
{% block extra_css %}
<style>
/* Estilos específicos */
</style>
{% endblock %}
```

### 4. Adicionar JavaScript
```html
{% block extra_js %}
<script>
// JavaScript específico
</script>
{% endblock %}
```

## 🔧 Personalização

### Cores Customizadas
Para alterar cores específicas, sobrescreva as variáveis CSS:

```css
:root {
    --dashboard-primary-custom: #your-color;
    --dashboard-secondary-custom: #your-color;
}
```

### Componentes Adicionais
Para criar novos componentes, siga o padrão:

```css
.my-component {
    background: var(--dashboard-white);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-fast);
}
```

## 📊 Sistema de Stats

### Cards de Estatísticas
```html
<div class="stats-card">
    <div class="stats-icon primary">
        <!-- SVG Icon -->
    </div>
    <div class="stats-value" id="uniqueId">123</div>
    <div class="stats-label">Label</div>
</div>
```

### Atualização Dinâmica
```javascript
// Atualizar com animação
window.forYouDashboard.updateStats('uniqueId', 456, true);

// Atualizar sem animação
window.forYouDashboard.updateStats('uniqueId', 456, false);
```

## 🌟 Boas Práticas

### 1. Acessibilidade
- Sempre usar labels descritivos
- Implementar navegação por teclado
- Manter contraste adequado
- Usar semantic HTML

### 2. Performance
- Lazy loading para componentes pesados
- Debounce em inputs de busca
- Virtualization para listas grandes
- Otimização de imagens

### 3. UX/UI
- Feedback visual imediato
- Loading states consistentes
- Mensagens de erro claras
- Progressão natural de tarefas

### 4. Responsividade
- Mobile-first approach
- Touch-friendly targets
- Readable text sizes
- Adequate spacing

## 🔮 Extensões Futuras

### Funcionalidades Planejadas
- [ ] Dark mode completo
- [ ] Widgets personalizáveis
- [ ] Drag & drop para reorganização
- [ ] Exportação de relatórios
- [ ] Notificações push
- [ ] Temas personalizados
- [ ] Dashboard builder
- [ ] Integração com BI tools

### APIs Planejadas
- [ ] WebSocket para tempo real
- [ ] GraphQL endpoints
- [ ] Métricas avançadas
- [ ] Export/Import de configurações

## 📝 Notas de Desenvolvimento

### Compatibilidade
- **Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Frameworks**: Flask/Jinja2 templates
- **CSS**: Modern CSS (Grid, Flexbox, CSS Variables)
- **JavaScript**: ES6+ features

### Performance Targets
- **First Paint**: < 1.5s
- **Interactive**: < 3s
- **Bundle Size**: CSS < 50kb, JS < 100kb

### Manutenção
- Atualizar documentação com mudanças
- Testar em múltiplos devices
- Validar acessibilidade regularmente
- Monitorar performance metrics

---

**Desenvolvido para ForYou** - Sistema de apoio emocional com foco em design centrado no usuário e acessibilidade.
