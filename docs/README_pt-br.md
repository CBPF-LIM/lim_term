# LIM Serial - GUI de Comunicação Serial e Visualização de Dados

**README em:** [English](/README.md) | [Português](README_pt-br.md) | [Español](README_es.md) | [Deutsch](README_de.md) | [Français](README_fr.md)

---

## Visão Geral

LIM Serial é uma aplicação GUI moderna e internacionalizada para comunicação serial e visualização de dados em tempo real. Construída com Python/Tkinter e matplotlib, oferece uma interface amigável para conectar a dispositivos seriais, coletar dados e criar gráficos dinâmicos.

![Captura de Tela do LIM Serial](shot.png)

## Características

### 🌍 **Internacionalização**
- **5 Idiomas**: Inglês, Português (Brasil), Espanhol, Alemão, Francês
- **Troca em Tempo Real**: Altere o idioma sem reiniciar
- **Preferências Persistentes**: Seleção de idioma salva automaticamente
- **Traduções em YAML**: Fácil de estender com novos idiomas

### 📡 **Comunicação Serial**
- **Modo Hardware**: Conecte a portas seriais reais
- **Modo Simulado**: Porta virtual integrada com geração de dados
- **Detecção Automática**: Descoberta e atualização automática de portas
- **Baudrate Flexível**: Suporte para todos os baudrates padrão
- **Status em Tempo Real**: Informações de conexão com feedback visual

### 📊 **Visualização de Dados**
- **Múltiplos Tipos de Gráfico**: Linha e Dispersão
- **Plotagem Multi-Séries**: Plotar até 5 séries Y (Y1-Y5) simultaneamente
- **Configuração Individual de Séries**: Cores, marcadores e tipos personalizados por série
- **Atualizações em Tempo Real**: Plotagem de dados ao vivo com atualização configurável
- **Suporte a Legenda**: Legenda automática para gráficos multi-séries
- **Aparência Customizável**: Mais de 20 cores, mais de 10 tipos de marcadores
- **Controle de Eixos**: Limites manuais do eixo Y e janelamento
- **Exportação PNG**: Salve gráficos como imagens de alta qualidade
- **Pausar/Retomar**: Controle o fluxo de dados sem desconectar

### 💾 **Gerenciamento de Dados**
- **Salvar/Carregar**: Exportar e importar dados em formato texto
- **Salvamento Automático**: Backup automático de dados com confirmação do usuário
- **Função Limpar**: Resetar dados com prompts de segurança
- **Configurações Persistentes**: Todas as preferências salvas entre sessões

### 🎨 **Interface do Usuário**
- **Interface com Abas**: Abas organizadas de Configuração, Dados e Gráfico
- **Design Responsivo**: Layout adaptativo com dimensionamento adequado de widgets
- **Feedback Visual**: Indicadores de status e informações de progresso
- **Acessibilidade**: Rotulagem clara e navegação intuitiva

## Instalação

### Requisitos
- Python 3.7+
- tkinter (geralmente incluído com Python)
- matplotlib
- pyserial
- PyYAML

### Instalar Dependências
```bash
pip install matplotlib pyserial PyYAML
```

### Início Rápido
```bash
# Clone ou baixe o projeto
cd lim_serial

# Execute a aplicação
python lim_serial.py
```

## Guia de Uso

### 1. Aba de Configuração
- **Seleção de Modo**: Escolha entre modo Hardware ou Simulado
- **Seleção de Porta**: Selecione entre portas seriais disponíveis (auto-atualizadas)
- **Baudrate**: Configure a velocidade de comunicação
- **Conectar/Desconectar**: Estabeleça ou feche a conexão serial

### 2. Aba de Dados
- **Exibição em Tempo Real**: Visualize dados recebidos em formato tabular
- **Salvar Dados**: Exporte o conjunto de dados atual para arquivo texto
- **Carregar Dados**: Importe dados salvos anteriormente
- **Limpar Dados**: Resete o conjunto de dados atual
- **Salvamento Automático**: Backup automático com confirmação do usuário

### 3. Aba de Gráfico
- **Seleção de Colunas**: Escolha coluna X e até 5 colunas Y (Y1-Y5) para plotagem
- **Suporte Multi-Séries**: Plote múltiplas séries de dados simultaneamente com legenda
- **Configuração Individual**: Defina tipo de gráfico, cor e marcador para cada série Y
- **Tipos de Gráfico**: Selecione gráfico de Linha ou Dispersão por série
- **Customização**: Cores, marcadores, limites de eixo, tamanho da janela (padrão: 50 pontos)
- **Exportar**: Salve gráficos como imagens PNG
- **Pausar/Retomar**: Controle atualizações em tempo real

### 4. Menu de Idiomas
- **Seleção de Idioma**: Disponível na barra de menu principal
- **Troca em Tempo Real**: Mudanças aplicadas imediatamente
- **Persistente**: Preferência de idioma salva automaticamente

## Formato dos Dados

Dados seriais devem ser enviados em colunas separadas por espaço:

```
# Cabeçalho (opcional)
timestamp voltage current temperature

# Linhas de dados
1.0 3.3 0.125 25.4
2.0 3.2 0.130 25.6
3.0 3.4 0.122 25.2
```

**Características:**
- Valores separados por espaço ou tab
- Detecção automática de colunas
- Análise de dados numéricos
- Suporte a linha de cabeçalho (ignorada durante plotagem)

## Arquitetura do Projeto

### Gerenciamento de Configuração
- **Preferências do Usuário**: Armazenadas em `config/prefs.yml`
- **Configurações Específicas de Aba**: Organizadas por seção da interface
- **Persistência de Idioma**: Memória automática de seleção de idioma
- **Padrões Seguros**: Valores de fallback para todas as preferências

### Sistema de Tradução
- **Baseado em YAML**: Arquivos de tradução legíveis em `languages/`
- **Chaves Hierárquicas**: Organizadas por componente da UI e contexto
- **Suporte a Fallback**: Traduções faltando voltam para o inglês
- **Atualizações em Tempo Real**: Interface atualiza imediatamente na mudança de idioma

## Desenvolvimento

### Adicionando Novos Idiomas
1. Crie novo arquivo YAML no diretório `languages/`
2. Siga a estrutura dos arquivos de idioma existentes
3. Teste todas as strings da interface
4. Envie pull request

### Estendendo Funcionalidade
- **Protocolos Seriais**: Estenda `SerialManager` para protocolos customizados
- **Tipos de Gráfico**: Adicione novos tipos de plot em `GraphManager`
- **Formatos de Dados**: Implemente parsers customizados em `utils/`
- **Componentes de UI**: Crie novas abas seguindo padrões existentes

## Arquivos de Configuração

### Preferências do Usuário (`config/prefs.yml`)
```yaml
language: pt-br
tabs:
  config:
    mode: Hardware
    port: "/dev/ttyUSB0"
    baudrate: "9600"
  graph:
    type: Line
    color: Blue
    marker: circle
    window_size: "100"
    x_column: "1"
    y_column: "2"
```

### Arquivos de Idioma (`languages/*.yml`)
Arquivos de tradução estruturados com organização hierárquica por componente da UI.

## Contribuindo

1. Faça fork do repositório
2. Crie uma branch de feature
3. Faça suas alterações
4. Teste completamente (especialmente internacionalização)
5. Envie um pull request

### Áreas para Contribuição
- Novas traduções de idiomas
- Tipos de gráfico adicionais
- Protocolos seriais aprimorados
- Melhorias de UI/UX
- Melhorias de documentação

## Licença

Desenvolvido por CBPF-LIM (Centro Brasileiro de Pesquisas Físicas - Laboratório de Luz e Matéria).

## Suporte

Para problemas, solicitações de recursos ou dúvidas:
- Verifique a documentação existente
- Revise arquivos de tradução para strings da UI
- Teste com diferentes idiomas e configurações
- Reporte bugs com passos detalhados de reprodução

---

**LIM Serial** - Comunicação serial moderna simplificada com acessibilidade internacional.
