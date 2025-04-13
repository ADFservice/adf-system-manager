# ADF System Manager

## Sobre o Projeto
ADF System Manager é uma ferramenta de gerenciamento e monitoramento de sistemas que oferece diversas funcionalidades para administração de computadores Windows.

Versão Atual: 1.0.4

## Funcionalidades Principais
- Monitoramento de recursos do sistema (CPU, memória, disco)
- Gerenciamento de backups
- Verificação e instalação de atualizações
- Gerenciamento de software instalado
- Suporte a múltiplos idiomas (pt_BR, en_US)
- Temas claro e escuro
- Interface moderna e intuitiva
- Geração de relatórios detalhados
- Backup automático de configurações

## Requisitos do Sistema
- Windows 10 ou superior
- 4GB de RAM (mínimo)
- 100MB de espaço em disco
- Resolução mínima: 1024x768

## Instalação
1. Baixe o instalador mais recente do [GitHub Releases](https://github.com/ADFservice/adf-system-manager/releases)
2. Execute o instalador e siga as instruções
3. Inicie o ADF System Manager pelo atalho criado

Para desenvolvedores:
```bash
git clone https://github.com/ADFservice/adf-system-manager.git
cd adf-system-manager
pip install -r requirements.txt
python main.py
```

## Atualizações Automáticas
O ADF System Manager verifica automaticamente por atualizações ao iniciar. Quando uma nova versão está disponível:

1. O sistema notifica o usuário sobre a atualização
2. O usuário pode escolher baixar e instalar automaticamente
3. A atualização é baixada em segundo plano
4. O sistema é reiniciado após a instalação

Para verificar manualmente:
1. Acesse o menu "Ajuda" > "Verificar Atualizações"
2. Ou use a aba "Atualizações" no programa

## Estrutura do Projeto
```
adf-system-manager/
├── assets/
│   ├── icons/         # Ícones da aplicação
│   ├── images/        # Imagens e logos
│   └── translations/  # Arquivos de tradução
├── src/
│   ├── gui/          # Interface gráfica
│   │   └── tabs/     # Abas da interface
│   └── utils/        # Utilitários e funções auxiliares
├── tests/            # Testes unitários
├── docs/            # Documentação
└── requirements.txt  # Dependências do projeto
```

## Desenvolvimento
- Siga as diretrizes de código no arquivo RULES.md
- Execute os testes antes de submeter alterações
- Mantenha a documentação atualizada
- Use branches para novas funcionalidades

## Releases
Para criar uma nova release:
1. Atualize a versão em `src/version.py`
2. Atualize o CHANGELOG.md
3. Crie e envie uma tag: `git tag v1.x.x && git push origin v1.x.x`
4. O GitHub Actions criará automaticamente a release

## Suporte
Para suporte técnico ou dúvidas:
- Email: adfservicosmarilia@gmail.comr


## Licença
© 2024 ADF Serviços de Informática. Todos os direitos reservados. 
