# 🎧 Sistema de Transcrição de Áudio

Um sistema completo de transcrição de áudio usando **Whisper AI** da OpenAI, com múltiplas interfaces de usuário e suporte a vários formatos de saída.

## 📋 Funcionalidades

### 🔧 **Núcleo de Transcrição**
- **Modelos Whisper**: tiny, base, small, medium, large
- **Múltiplos idiomas**: Português, Inglês, Espanhol, etc.
- **Tradução automática**: Transcreve e traduz para inglês
- **Formatos de saída**: TXT, SRT (legendas), VTT (WebVTT)
- **Compatibilidade**: MP3, WAV, MP4, M4A, FLAC, AAC

### 🖥️ **Interface Terminal Interativa**
- Menu colorido e intuitivo
- Seleção de arquivos com suporte a arrastar e soltar
- Configuração de parâmetros em tempo real
- Monitoramento de progresso
- Integração com Windows Explorer

### 🌐 **Interface Web Moderna**
- Upload por arrastar e soltar
- Configuração visual de parâmetros
- Monitoramento em tempo real
- Download automático de resultados
- Design responsivo e moderno

### ⚙️ **Linha de Comando**
- Automação e scripts
- Processamento em lote
- Integração com outros sistemas

## 🛠️ Instalação

### **Pré-requisitos**
- Python 3.8+
- FFmpeg instalado no sistema

### **1. Clone o projeto**
```bash
git clone <url-do-repositorio>
cd Transcritor
```

### **2. Instale as dependências**
```bash
pip install whisper flask colorama
```

### **3. Instale o FFmpeg**
- **Windows**: Baixe de https://ffmpeg.org/download.html
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

## 🚀 Como Usar

### **Opção 1: Interface Terminal Interativa** ⭐ *Recomendado*
```bash
python painel_interativo.py
```

**Funcionalidades:**
- Menu principal com opções numeradas
- Arrastar arquivo para o terminal ou colar caminho
- Configurar modelo, idioma e formato
- Visualizar progresso em tempo real

### **Opção 2: Interface Web**
```bash
python app.py
```
Depois acesse: http://127.0.0.1:5000

**Funcionalidades:**
- Arrastar arquivos para upload
- Configuração visual
- Monitoramento em tempo real
- Download direto dos resultados

### **Opção 3: Linha de Comando**
```bash
# Uso básico
python transcrever_audio_melhorado.py "audio.mp3"

# Com configurações personalizadas
python transcrever_audio_melhorado.py "audio.mp3" --modelo medium --idioma pt --formato .srt

# Traduzir para inglês
python transcrever_audio_melhorado.py "audio.mp3" --traduzir
```

## 📖 Parâmetros de Configuração

### **Modelos Disponíveis**
| Modelo | Tamanho | Velocidade | Qualidade |
|--------|---------|------------|-----------|
| `tiny` | ~39 MB | Muito rápido | Básica |
| `base` | ~74 MB | Rápido | Boa |
| `small` | ~244 MB | Médio | Muito boa |
| `medium` | ~769 MB | Lento | Excelente |
| `large` | ~1550 MB | Muito lento | Máxima |

### **Idiomas Suportados**
- `pt` - Português
- `en` - Inglês
- `es` - Espanhol
- `fr` - Francês
- `de` - Alemão
- `it` - Italiano
- `None` - Autodetectar

### **Formatos de Saída**
- **`.txt`** - Texto simples
- **`.srt`** - Legendas para vídeos
- **`.vtt`** - WebVTT para web

## 📂 Estrutura do Projeto

```
Transcritor/
├── transcrever_audio_melhorado.py  # Núcleo de transcrição
├── painel_interativo.py            # Interface terminal
├── app.py                          # Servidor web Flask
├── templates/
│   └── index.html                  # Interface web
├── uploads/                        # Arquivos enviados (web)
├── outputs/                        # Resultados (web)
├── .venv/                          # Ambiente virtual
└── README.md                       # Este arquivo
```

## 🎯 Exemplos de Uso

### **Transcrição Básica**
```bash
python transcrever_audio_melhorado.py "minha_reuniao.mp3"
# Resultado: minha_reuniao_transcricao.txt
```

### **Legendas para Vídeo**
```bash
python transcrever_audio_melhorado.py "video.mp4" --formato .srt
# Resultado: video_transcricao.srt
```

### **Tradução para Inglês**
```bash
python transcrever_audio_melhorado.py "audio_pt.wav" --traduzir
# Resultado: audio_pt_traduzido.txt
```

### **Modelo Específico**
```bash
python transcrever_audio_melhorado.py "audio.mp3" --modelo large --idioma pt
# Usa o modelo mais preciso em português
```

## 🔧 Solução de Problemas

### **Erro de FFmpeg**
```
[ERRO] FFmpeg não encontrado
```
**Solução**: Instale o FFmpeg e adicione ao PATH do sistema.

### **Erro de Memória**
```
CUDA out of memory
```
**Solução**: Use um modelo menor (tiny, base, small).

### **Arquivo não suportado**
```
[ERRO] Formato não suportado
```
**Solução**: Converta o arquivo para MP3, WAV ou MP4.

## 🆘 Ajuda Rápida

### **Parâmetros da Linha de Comando**
```bash
python transcrever_audio_melhorado.py --help
```

### **Teste de Funcionamento**
```bash
python transcrever_audio_melhorado.py --help
# Se mostrar a ajuda, tudo está funcionando!
```

## 📝 Notas Importantes

- **Primeira execução**: O Whisper baixará o modelo automaticamente
- **Processamento**: Arquivos grandes podem demorar alguns minutos
- **Qualidade**: Modelos maiores são mais precisos mas mais lentos
- **Idioma**: Para melhor precisão, especifique o idioma correto

## 🎉 Começando Agora

1. **Para usuários iniciantes**: Use `python painel_interativo.py`
2. **Para desenvolvedores**: Use a linha de comando
3. **Para demonstrações**: Use a interface web com `python app.py`

---

**🔥 Dica**: O painel interativo é a forma mais fácil de começar! Apenas execute `python painel_interativo.py` e siga as instruções na tela.