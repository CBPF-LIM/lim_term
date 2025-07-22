# LIM Serial

GUI para comunicação serial e visualização de dados em tempo real.

## Características

- **Interface com abas**: Configuração, Dados e Gráficos
- **Comunicação serial**: Conecta a diversas portas seriais
- **Visualização em tempo real**: Gráficos atualizados automaticamente
- **Múltiplos tipos de gráfico**: Linha, Barras, Dispersão
- **Configuração avançada**: Cores, marcadores, limites de eixo
- **Exportação de dados**: Salva dados em arquivos de texto

## Instalação

### Dependências

```bash
pip install tkinter matplotlib pyserial
```

### Execução

```bash
python lim_serial.py
```

## Uso

1. **Configuração**: Selecione a porta serial e baudrate
2. **Conexão**: Clique em "Conectar" para iniciar a comunicação
3. **Visualização**: Os dados aparecerão na aba "Dados"
4. **Gráficos**: Configure as colunas X e Y na aba "Gráfico"
5. **Personalização**: Use "Opções de Gráfico" para customizar a visualização

## Formato dos Dados

Os dados devem ser enviados via serial no formato:
```
coluna1 coluna2 coluna3 ...
valor1  valor2  valor3  ...
```

Exemplo:
```
1.0 2.5 3.2
2.0 2.8 3.5
3.0 3.1 3.8
```

## Desenvolvimento

### Arquitetura

O projeto segue uma arquitetura modular:

- **config.py**: Centralizou todas as configurações
- **core/**: Lógica de negócio (serial e gráficos)
- **gui/**: Interface gráfica separada em componentes
- **utils/**: Utilitários reutilizáveis

### Benefícios da Modularização

1. **Manutenibilidade**: Código organizado e fácil de entender
2. **Reutilização**: Componentes podem ser utilizados independentemente
3. **Testabilidade**: Cada módulo pode ser testado isoladamente
4. **Escalabilidade**: Fácil adição de novas funcionalidades

## Licença

Projeto desenvolvido por CBPF-LIM.
