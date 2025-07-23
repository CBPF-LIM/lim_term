# LIM Serial - Comunicação Serial & Visualização de Dados

**README em:** [English](../README.md) | [Português](README_pt-br.md) | [Español](README_es.md) | [Deutsch](README_de.md) | [Français](README_fr.md)

---

## Visão Geral

LIM Serial é uma aplicação amigável para comunicação serial e visualização de dados em tempo real. Conecte-se a Arduino ou outros dispositivos seriais, colete dados e crie gráficos dinâmicos com recursos de visualização profissionais. Disponível em 5 idiomas com salvamento automático de preferências.

![LIM Serial Screenshot](shot.png)

![LIM Serial Screenshot](shot_stacked.png)

## Recursos

### 🌍 **Múltiplos Idiomas**
- Disponível em inglês, português, espanhol, alemão e francês
- Altere o idioma pelo menu (requer reinicialização)
- Todas as configurações preservadas ao trocar idiomas

### 📡 **Conexão Serial Fácil**
- Conecte a dispositivos seriais reais (Arduino, sensores, etc.)
- Modo de simulação integrado para testes sem hardware
- Detecção automática de portas com atualização em um clique
- Compatibilidade completa com taxas de transmissão do Arduino IDE (300-2000000 bps)

### 📊 **Visualização de Dados Profissional**
- **Gráficos de Série Temporal**: Plote até 5 colunas de dados simultaneamente
- **Gráficos de Área Empilhada**: Compare dados como valores absolutos ou porcentagens
- **Aparência Personalizável**: Escolha cores, marcadores e tipos de linha para cada série de dados
- **Atualizações em Tempo Real**: Taxas de atualização configuráveis (1-30 FPS)
- **Exportação**: Salve gráficos como imagens PNG de alta qualidade
- **Controles Interativos**: Pause/retome coleta de dados, zoom e panorâmica

### 💾 **Gerenciamento Inteligente de Dados**
- **Salvar/Carregar Manual**: Exporte e importe seus dados a qualquer momento
- **Backup Automático**: Salvamento automático opcional com nomes de arquivo com timestamp
- **Segurança de Dados**: Limpe dados com confirmações
- **Todas as Configurações Salvas**: Preferências automaticamente preservadas entre sessões

## Primeiros Passos

### Requisitos
- Python 3.7 ou mais recente
- Conexão com a internet para instalação de dependências

### Instalação
```bash
# Instalar pacotes necessários
pip install matplotlib pyserial PyYAML

# Baixar e executar LIM Serial
cd lim_term
python lim_serial.py
```

### Primeiros Passos
1. **Idioma**: Escolha seu idioma no menu Idioma
2. **Conexão**: Vá para a aba Configuração, selecione sua porta serial e taxa de transmissão
3. **Dados**: Mude para a aba Dados para ver dados recebidos
4. **Visualização**: Use a aba Gráfico para criar gráficos dos seus dados

## Como Usar

### Aba Configuração
- **Modo**: Escolha "Hardware" para dispositivos reais, "Simulado" para testes
- **Porta**: Selecione sua porta serial (clique em Atualizar para atualizar a lista)
- **Taxa de Transmissão**: Defina a velocidade de comunicação (combine com as configurações do seu dispositivo)
- **Conectar**: Clique para começar a receber dados

### Aba Dados
- **Ver Dados**: Veja dados recebidos em formato de tabela em tempo real
- **Salvar Dados**: Exporte dados atuais para um arquivo de texto
- **Carregar Dados**: Importe arquivos de dados salvos anteriormente
- **Limpar Dados**: Redefina o conjunto de dados atual (com confirmação)
- **Salvamento Automático**: Ative/desative backup automático com nomes de arquivo com timestamp

### Aba Gráfico
- **Escolher Colunas**: Selecione eixo X e até 5 colunas do eixo Y dos seus dados
- **Tipos de Gráfico**:
  - **Série Temporal**: Gráficos de linha/dispersão individuais para cada série de dados
  - **Área Empilhada**: Gráficos em camadas mostrando dados cumulativos ou porcentagens
- **Personalizar**: Expanda "Mostrar Opções Avançadas" para alterar cores, marcadores, taxa de atualização
- **Exportar**: Salve seus gráficos como imagens PNG
- **Controle**: Pause/retome atualizações em tempo real a qualquer momento

### Menu Idioma
- **Trocar Idioma**: Selecione entre 5 idiomas disponíveis
- **Reinicialização Necessária**: A aplicação solicitará reinicialização para mudança de idioma
- **Configurações Preservadas**: Todas as suas preferências são mantidas ao trocar idiomas

## Formato de Dados

Seu dispositivo serial deve enviar dados em formato de texto simples:

```
# Linha de cabeçalho opcional
timestamp voltage current temperature

# Linhas de dados (separadas por espaço ou tab)
1.0 3.3 0.125 25.4
2.0 3.2 0.130 25.6
3.0 3.4 0.122 25.2
```

**Formatos suportados:**
- Colunas separadas por espaço ou tab
- Números em qualquer coluna
- Linha de cabeçalho opcional (será detectada automaticamente)
- Streaming em tempo real ou carregamento de dados em lote

## Solução de Problemas

**Problemas de Conexão:**
- Certifique-se de que seu dispositivo está conectado e ligado
- Verifique se nenhum outro programa está usando a porta serial
- Tente diferentes taxas de transmissão se os dados aparecerem corrompidos
- Use o modo Simulado para testar a interface sem hardware

**Problemas de Dados:**
- Certifique-se de que os dados estão separados por espaço ou tab
- Verifique se os números estão em formato padrão (use . para decimais)
- Verifique se seu dispositivo está enviando dados continuamente
- Tente salvar e recarregar dados para verificar o formato

**Performance:**
- Diminua a taxa de atualização se os gráficos estiverem lentos
- Reduza o tamanho da janela de dados para melhor performance
- Feche outros programas se o sistema ficar lento

## Desenvolvimento

Esta aplicação é construída com Python e usa tkinter para a interface e matplotlib para gráficos.

**Para desenvolvedores:**
- A base de código usa uma arquitetura modular com componentes separados para GUI, gerenciamento de dados e visualização
- Traduções são armazenadas em arquivos YAML no diretório `languages/`
- A configuração usa um sistema de preferências hierárquico salvo em `config/prefs.yml`
- O sistema de atualização de gráficos é desacoplado da chegada de dados para performance ótima

## Licença

Desenvolvido por CBPF-LIM (Centro Brasileiro de Pesquisas Físicas - Laboratório de Luz e Matéria).

---

**LIM Serial** - Comunicação serial e visualização de dados profissionais simplificadas.