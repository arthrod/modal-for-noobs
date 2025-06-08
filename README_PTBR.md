# 🚀 modal-for-noobs

**CLI de deploy de apps Gradio para Modal - fácil para leigos e async-first!**

Faça deploy dos seus apps Gradio no Modal com configuração zero. Perfeito para noobs que só querem que as coisas funcionem! 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## ✨ Funcionalidades

- 🚀 **Deploy sem configuração** - Só aponte para seu app Gradio e vá!
- ⚡ **--time-to-get-serious** - Migre HuggingFace Spaces para Modal em segundos
- 🔄 **Async-first** - Construído com padrões modernos Python async/await usando uvloop
- 🎯 **Três modos**: Minimum (CPU), Optimized (GPU + ML), Gra-Jupy (Jupyter + Gradio)
- 🔐 **Auto-autenticação** - Cuida da configuração do Modal automaticamente
- 🪝 **Detecção inteligente** - Encontra sua interface Gradio automaticamente
- 📦 **Magia de dependências** - Auto-instala requirements de HF Spaces ou pasta drop
- 🧙‍♂️ **Assistente interativo** - Orientação passo-a-passo para deploy
- 🥛 **Ordenha de logs** - Visualização linda de logs com --milk-logs
- 💀 **Matador de deploys** - Limpeza fácil com --kill-a-deployment
- 🌐 **Explorador de Exemplos Modal** - Navegue e faça deploy da galeria de exemplos do Modal
- 💚 **Interface linda** - Tema verde assinatura do Modal em tudo
- 🇧🇷 **Modo brasileiro** - Suporte completo ao português brasileiro com --br-huehuehue

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clone e instale
git clone https://github.com/arthrod/modal-for-noobs.git
cd modal-for-noobs
uv sync

# Ou instale diretamente (futuro)
pip install modal-for-noobs
```

### 2. Faça Deploy do Seu App Gradio

```bash
# 🚀 MODO SUPER FÁCIL - Use nossos scripts de launcher!

# Unix/Linux/macOS
./mn.sh app.py                    # Deploy rápido (CPU)
./mn.sh app.py --optimized        # GPU + bibliotecas ML
./mn.sh                           # Modo assistente (padrão)

# Windows
mn.bat app.py                     # Deploy rápido (CPU)
mn.bat app.py --optimized         # GPU + bibliotecas ML
mn.bat                            # Modo assistente (padrão)

# 💡 Instale alias permanente 'mn' para usar de qualquer lugar!
./mn.sh --install-alias           # Unix/Linux/macOS
mn.bat --install-alias            # Windows

# Depois use só 'mn' de qualquer lugar:
mn app.py --optimized
mn --milk-logs                    # Ver logs do deployment

# Alternativa: Uso direto da CLI (se instalado via pip)
modal-for-noobs deploy meu_app.py --dry-run
modal-for-noobs deploy meu_app.py --wizard          # Assistente interativo
modal-for-noobs deploy meu_app.py --gra-jupy        # Combo Jupyter + Gradio
```

## 📖 Exemplos Detalhados

### 🎯 App Gradio Simples
Crie um arquivo `meu_app.py`:
```python
import gradio as gr

def cumprimentar(nome):
    return f"Olá {nome}! 🚀"

demo = gr.Interface(fn=cumprimentar, inputs="text", outputs="text")

if __name__ == "__main__":
    demo.launch()
```

Faça o deploy:
```bash
./mn.sh meu_app.py --optimized
```

### 🧠 App de Modelo ML com Requirements Customizados
1. Crie `drop-ur-precious-stuff-here/requirements.txt`:
```
transformers==4.35.0
torch>=2.0.0
accelerate
```

2. Crie seu app ML:
```python
import gradio as gr
from transformers import pipeline

# O assistente vai detectar e incluir seus requirements automaticamente!
classificador = pipeline("sentiment-analysis")

def analisar_sentimento(texto):
    resultado = classificador(texto)
    return f"Sentimento: {resultado[0]['label']} ({resultado[0]['score']:.2f})"

demo = gr.Interface(
    fn=analisar_sentimento,
    inputs="text",
    outputs="text",
    title="🧠 Análise de Sentimento com Modal-for-noobs!"
)

if __name__ == "__main__":
    demo.launch()
```

3. Deploy com assistente:
```bash
./mn.sh app_ml.py --wizard
```

### 🇧🇷 Modo Brasileiro Completo
```bash
./mn.sh meu_app.py --optimized --br-huehuehue
# Saída tudo em português com humor brasileiro! Huehuehue! 😄
```

## 🛠️ Comandos Avançados

### 🥛 Ordenhar os Logs (Ver Logs do Deployment)
```bash
mn --milk-logs                           # Listar todos os apps
mn --milk-logs meu-app                   # Ver logs de app específico
mn --milk-logs meu-app --follow          # Seguir logs em tempo real
mn --milk-logs meu-app --br-huehuehue    # Logs modo brasileiro! 🇧🇷
```

### 💀 Matar Deployments
```bash
mn --kill-a-deployment                   # Listar deployments ativos
mn --kill-a-deployment meu-app-id        # Matar deployment específico
mn --kill-a-deployment --br-huehuehue    # Modo exterminador brasileiro! 💀
```

### 🔍 Verificação de Sanidade
```bash
mn --sanity-check                        # Verificar o que está deployado
mn --sanity-check --br-huehuehue         # Verificação de sanidade brasileira! 🧠
```

### 💪 Hora de Ficar SÉRIO! (Migração HuggingFace)

```bash
# A opção nuclear - migre HuggingFace Spaces! 🚀
modal-for-noobs time-to-get-serious https://huggingface.co/spaces/usuario/nome-do-space

# Também funciona em modo brasileiro!
modal-for-noobs time-to-get-serious https://huggingface.co/spaces/usuario/nome --br-huehuehue
```

## 🎯 Deployment Modes

### 🔥 Minimum (Padrão)
- **CPU apenas** - Rápido e barato
- **Pacotes básicos**: gradio, fastapi, uvicorn, httpx, markdown2
- **Perfeito para**: Apps simples, protótipos, demos

### ⚡ Optimized
- **GPU + CPU** - Poderoso para ML
- **Pacotes ML**: torch, transformers, accelerate, diffusers, pillow, numpy, pandas
- **Perfeito para**: Modelos de ML, IA generativa, processamento pesado

### 🔬 Gra-Jupy 
- **Jupyter + Gradio** - Notebooks interativos
- **Pacotes científicos**: jupyter, matplotlib, plotly, seaborn, pandas, numpy
- **Perfeito para**: Análise de dados, pesquisa, experimentação

## 🇧🇷 Recursos Brasileiros Especiais

O modal-for-noobs tem suporte completo ao português brasileiro com o modo `--br-huehuehue`!

### O que muda:
- 🗣️ **Todas as mensagens em português** - Interface 100% brasileira
- 😄 **Humor brasileiro** - Huehuehue em tudo!
- 🎉 **Mensagens personalizadas** - "Você oficialmente NÃO é mais um noob!"
- 🇧🇷 **Terminologia local** - "Ordenhar logs", "Matador de deployments"

### Exemplos brasileiros:
```bash
# Deploy básico brasileiro
./mn.sh meu_app.py --br-huehuehue

# Assistente em português
./mn.sh meu_app.py --wizard --br-huehuehue

# Ordenhar logs fresquinhos! 🥛
mn --milk-logs meu-app --br-huehuehue

# Matar deployments! 💀
mn --kill-a-deployment --br-huehuehue
```

## 🏗️ Estrutura do Projeto

```
modal-for-noobs/
├── 🚀 mn.sh                    # Launcher Unix/Linux/macOS  
├── 🪟 mn.bat                   # Launcher Windows
├── 📁 drop-ur-precious-stuff-here/  # Pasta para seus arquivos
│   ├── requirements.txt       # Suas dependências
│   └── README.md              
├── 📦 src/modal_for_noobs/     # Código principal
│   ├── cli.py                 # Interface de linha de comando
│   ├── modal_deploy.py        # Lógica de deploy
│   ├── github_api.py          # Integração GitHub
│   └── examples/              # Apps exemplo
└── 🎓 gradio-modal-deploy/     # Pacote PyPI separado
```

## 🤝 Contribuição

1. Faça fork do projeto
2. Crie sua feature branch (`git checkout -b feature/MinhaFeatureIncrivel`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeatureIncrivel'`)
4. Push para a branch (`git push origin feature/MinhaFeatureIncrivel`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Modal Labs** - Pela plataforma incrível de computação serverless
- **Gradio Team** - Pelo framework fantástico de interfaces ML
- **Comunidade Python** - Por todas as bibliotecas incríveis
- **Neurotic Coder** - Pelo desenvolvimento apaixonado
- **Claude** - Pela assistência na programação

## 🎯 Roadmap

- [ ] 🐳 Suporte Docker nativo
- [ ] 🔄 Auto-redeploy em mudanças de arquivo
- [ ] 📊 Dashboard de monitoramento
- [ ] 🔗 Integração com mais plataformas
- [ ] 🤖 Assistente IA para otimização de código
- [ ] 🌍 Mais idiomas (Espanhol, Francês, etc.)

---

💚 **Feito com <3 pelo [Neurotic Coder](https://github.com/arthrod) e assistido pelo Beloved Claude** ✨

🇧🇷 **Orgulhosamente brasileiro! Huehuehue!** 🇧🇷