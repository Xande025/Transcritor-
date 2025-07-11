import os
import sys
import subprocess
import glob
from pathlib import Path
import msvcrt  # Para Windows
from colorama import Fore, Back, Style, init

# Inicializar colorama para Windows
init(autoreset=True)

class PainelTranscricao:
    def __init__(self):
        self.arquivo_audio = None
        self.modelo = "medium"
        self.idioma = "pt"
        self.traduzir = False
        self.formato = ".txt"
        self.pasta_saida = None  # None = pasta atual, ou caminho específico
        self.modelos_disponiveis = ["tiny", "base", "small", "medium", "large"]
        self.idiomas_disponiveis = {
            "pt": "Português",
            "en": "Inglês", 
            "es": "Espanhol",
            "fr": "Francês",
            "de": "Alemão",
            "it": "Italiano",
            "auto": "Auto-detectar"
        }
        self.formatos_disponiveis = {
            ".txt": "Texto simples",
            ".srt": "Legendas SRT",
            ".vtt": "WebVTT"
        }
        
    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def aguardar_tecla(self, mensagem="Pressione qualquer tecla para continuar..."):
        print(f"\n{Fore.CYAN}{mensagem}")
        msvcrt.getch()
        
    def exibir_cabecalho(self):
        print(f"{Fore.MAGENTA}{'='*70}")
        print(f"{Fore.MAGENTA}🎙️  SISTEMA DE TRANSCRIÇÃO DE ÁUDIO - WHISPER AI  🎙️")
        print(f"{Fore.MAGENTA}{'='*70}")
        print()
        
    def exibir_configuracoes_atuais(self):
        print(f"{Fore.YELLOW}📋 CONFIGURAÇÕES ATUAIS:")
        print(f"{Fore.WHITE}┌─ Arquivo: {Fore.GREEN}{self.arquivo_audio or 'Nenhum selecionado'}")
        print(f"{Fore.WHITE}├─ Modelo: {Fore.GREEN}{self.modelo}")
        print(f"{Fore.WHITE}├─ Idioma: {Fore.GREEN}{self.idiomas_disponiveis.get(self.idioma, self.idioma)}")
        print(f"{Fore.WHITE}├─ Traduzir: {Fore.GREEN}{'Sim' if self.traduzir else 'Não'}")
        print(f"{Fore.WHITE}├─ Formato: {Fore.GREEN}{self.formatos_disponiveis[self.formato]}")
        pasta_display = self.pasta_saida or "Pasta do projeto"
        print(f"{Fore.WHITE}└─ Pasta de saída: {Fore.GREEN}{pasta_display}")
        print()
        
    def menu_principal(self):
        while True:
            self.limpar_tela()
            self.exibir_cabecalho()
            self.exibir_configuracoes_atuais()
            
            print(f"{Fore.CYAN}🔧 MENU PRINCIPAL:")
            opcoes = [
                "1️⃣  Selecionar arquivo de áudio",
                "2️⃣  Configurar modelo Whisper", 
                "3️⃣  Configurar idioma",
                "4️⃣  Configurar tradução",
                "5️⃣  Configurar formato de saída",
                "6️⃣  Configurar pasta de saída",
                "7️⃣  Verificar FFmpeg",
                "8️⃣  🚀 INICIAR TRANSCRIÇÃO",
                "9️⃣  Ver arquivos recentes",
                "0️⃣  Sair"
            ]
            
            for opcao in opcoes:
                cor = Fore.GREEN if "INICIAR" in opcao else Fore.WHITE
                if "Sair" in opcao:
                    cor = Fore.RED
                print(f"{cor}{opcao}")
                
            print(f"\n{Fore.YELLOW}Digite sua opção: ", end="")
            
            try:
                opcao = input().strip()
                if opcao == "1":
                    self.selecionar_arquivo()
                elif opcao == "2":
                    self.configurar_modelo()
                elif opcao == "3":
                    self.configurar_idioma()
                elif opcao == "4":
                    self.configurar_traducao()
                elif opcao == "5":
                    self.configurar_formato()
                elif opcao == "6":
                    self.configurar_pasta_saida()
                elif opcao == "7":
                    self.verificar_ffmpeg()
                elif opcao == "8":
                    self.iniciar_transcricao()
                elif opcao == "9":
                    self.ver_arquivos_recentes()
                elif opcao == "0":
                    self.confirmar_saida()
                    break
                else:
                    print(f"{Fore.RED}❌ Opção inválida!")
                    self.aguardar_tecla()
            except KeyboardInterrupt:
                self.confirmar_saida()
                break
                
    def selecionar_arquivo(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}📁 SELEÇÃO DE ARQUIVO DE ÁUDIO")
        print("="*50)
        
        # Mostrar arquivos de áudio na pasta atual (como opção secundária)
        extensoes_audio = ['*.mp3', '*.wav', '*.m4a', '*.flac', '*.ogg', '*.aac', '*.mp4', '*.avi', '*.mkv']
        arquivos_encontrados = []
        
        for ext in extensoes_audio:
            arquivos_encontrados.extend(glob.glob(ext))
        
        print(f"{Fore.YELLOW}📝 COLE O CAMINHO DO ARQUIVO DE ÁUDIO:")
        print(f"{Fore.WHITE}💡 Dica: Ctrl+V para colar")
        print(f"{Fore.CYAN}Formatos suportados: MP3, WAV, M4A, FLAC, OGG, AAC, MP4, AVI, MKV")
        print()
        
        if arquivos_encontrados:
            print(f"{Fore.GREEN}📂 Ou escolha um arquivo da pasta atual:")
            for i, arquivo in enumerate(arquivos_encontrados, 1):
                tamanho = os.path.getsize(arquivo) / (1024*1024)  # MB
                print(f"{Fore.WHITE}{i:2d}. {Fore.YELLOW}{arquivo} {Fore.CYAN}({tamanho:.1f} MB)")
            print()
        
        print(f"{Fore.YELLOW}Caminho do arquivo: ", end="")
        escolha = input().strip()
        
        # Se digitou um número e há arquivos na pasta
        if escolha.isdigit() and arquivos_encontrados:
            try:
                idx = int(escolha) - 1
                if 0 <= idx < len(arquivos_encontrados):
                    self.arquivo_audio = arquivos_encontrados[idx]
                    print(f"{Fore.GREEN}✅ Arquivo selecionado: {self.arquivo_audio}")
                    self.aguardar_tecla()
                    return
                else:
                    print(f"{Fore.RED}❌ Número inválido!")
                    self.aguardar_tecla()
                    return
            except ValueError:
                pass
        
        # Se não foi um número válido, trata como caminho
        if escolha:
            caminho = escolha.strip().strip('"')
            if os.path.exists(caminho):
                self.arquivo_audio = caminho
                print(f"{Fore.GREEN}✅ Arquivo válido selecionado!")
                print(f"{Fore.CYAN}📁 {os.path.basename(caminho)}")
                self.aguardar_tecla()
            else:
                print(f"{Fore.RED}❌ Arquivo não encontrado!")
                print(f"{Fore.YELLOW}Verifique se o caminho está correto.")
                self.aguardar_tecla()
        else:
            print(f"{Fore.YELLOW}⚠️  Nenhum caminho informado.")
            self.aguardar_tecla()
                
    def configurar_modelo(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}🤖 CONFIGURAÇÃO DO MODELO WHISPER")
        print("="*50)
        
        modelos_info = {
            "tiny": "Muito rápido, menos preciso (~39 MB)",
            "base": "Rápido, precisão básica (~74 MB)", 
            "small": "Equilibrado (~244 MB)",
            "medium": "Boa precisão (~769 MB) - Recomendado",
            "large": "Máxima precisão (~1550 MB)"
        }
        
        print(f"{Fore.YELLOW}Modelos disponíveis:")
        for i, modelo in enumerate(self.modelos_disponiveis, 1):
            cor = Fore.GREEN if modelo == self.modelo else Fore.WHITE
            print(f"{cor}{i}. {modelo.upper()} - {modelos_info[modelo]}")
            
        print(f"\n{Fore.YELLOW}Selecione o modelo (1-5): ", end="")
        try:
            escolha = int(input().strip())
            if 1 <= escolha <= 5:
                self.modelo = self.modelos_disponiveis[escolha - 1]
                print(f"{Fore.GREEN}✅ Modelo alterado para: {self.modelo}")
                self.aguardar_tecla()
            else:
                print(f"{Fore.RED}❌ Opção inválida!")
                self.aguardar_tecla()
        except ValueError:
            print(f"{Fore.RED}❌ Digite um número válido!")
            self.aguardar_tecla()
            
    def configurar_idioma(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}🌍 CONFIGURAÇÃO DE IDIOMA")
        print("="*50)
        
        print(f"{Fore.YELLOW}Idiomas disponíveis:")
        idiomas_lista = list(self.idiomas_disponiveis.items())
        for i, (codigo, nome) in enumerate(idiomas_lista, 1):
            cor = Fore.GREEN if codigo == self.idioma else Fore.WHITE
            print(f"{cor}{i}. {nome} ({codigo})")
            
        print(f"\n{Fore.YELLOW}Selecione o idioma (1-{len(idiomas_lista)}): ", end="")
        try:
            escolha = int(input().strip())
            if 1 <= escolha <= len(idiomas_lista):
                self.idioma = idiomas_lista[escolha - 1][0]
                print(f"{Fore.GREEN}✅ Idioma alterado para: {self.idiomas_disponiveis[self.idioma]}")
                self.aguardar_tecla()
            else:
                print(f"{Fore.RED}❌ Opção inválida!")
                self.aguardar_tecla()
        except ValueError:
            print(f"{Fore.RED}❌ Digite um número válido!")
            self.aguardar_tecla()
            
    def configurar_traducao(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}🔄 CONFIGURAÇÃO DE TRADUÇÃO")
        print("="*50)
        
        print(f"{Fore.YELLOW}Opções de tradução:")
        print(f"{Fore.GREEN if not self.traduzir else Fore.WHITE}1. Apenas transcrever")
        print(f"{Fore.GREEN if self.traduzir else Fore.WHITE}2. Transcrever e traduzir para inglês")
        
        print(f"\n{Fore.YELLOW}Selecione a opção (1-2): ", end="")
        try:
            escolha = int(input().strip())
            if escolha == 1:
                self.traduzir = False
                print(f"{Fore.GREEN}✅ Modo: Apenas transcrição")
            elif escolha == 2:
                self.traduzir = True
                print(f"{Fore.GREEN}✅ Modo: Transcrição + Tradução")
            else:
                print(f"{Fore.RED}❌ Opção inválida!")
            self.aguardar_tecla()
        except ValueError:
            print(f"{Fore.RED}❌ Digite um número válido!")
            self.aguardar_tecla()
            
    def configurar_formato(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}📄 CONFIGURAÇÃO DE FORMATO DE SAÍDA")
        print("="*50)
        
        print(f"{Fore.YELLOW}Formatos disponíveis:")
        formatos_lista = list(self.formatos_disponiveis.items())
        for i, (ext, desc) in enumerate(formatos_lista, 1):
            cor = Fore.GREEN if ext == self.formato else Fore.WHITE
            print(f"{cor}{i}. {desc} ({ext})")
            
        print(f"\n{Fore.YELLOW}Selecione o formato (1-{len(formatos_lista)}): ", end="")
        try:
            escolha = int(input().strip())
            if 1 <= escolha <= len(formatos_lista):
                self.formato = formatos_lista[escolha - 1][0]
                print(f"{Fore.GREEN}✅ Formato alterado para: {self.formatos_disponiveis[self.formato]}")
                self.aguardar_tecla()
            else:
                print(f"{Fore.RED}❌ Opção inválida!")
                self.aguardar_tecla()
        except ValueError:
            print(f"{Fore.RED}❌ Digite um número válido!")
            self.aguardar_tecla()
            
    def configurar_pasta_saida(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}📁 CONFIGURAÇÃO DE PASTA DE SAÍDA")
        print("="*50)
        
        print(f"{Fore.YELLOW}📂 Pasta atual de saída: {Fore.WHITE}{self.pasta_saida or 'Pasta do projeto (padrão)'}")
        print()
        
        print(f"{Fore.WHITE}Opções:")
        print(f"{Fore.GREEN}1 - Pasta do projeto (padrão)")
        print(f"{Fore.CYAN}2 - Desktop do usuário")
        print(f"{Fore.MAGENTA}3 - Pasta Documentos")
        print(f"{Fore.YELLOW}4 - Pasta Downloads")
        print(f"{Fore.BLUE}5 - Escolher pasta personalizada")
        print(f"{Fore.RED}0 - Voltar")
        
        print()
        escolha = input(f"{Fore.YELLOW}Escolha uma opção: ").strip()
        
        if escolha == "1":
            self.pasta_saida = None
            print(f"{Fore.GREEN}✅ Pasta configurada: Pasta do projeto")
        elif escolha == "2":
            self.pasta_saida = os.path.expanduser("~/Desktop")
            print(f"{Fore.GREEN}✅ Pasta configurada: {self.pasta_saida}")
        elif escolha == "3":
            self.pasta_saida = os.path.expanduser("~/Documents")
            print(f"{Fore.GREEN}✅ Pasta configurada: {self.pasta_saida}")
        elif escolha == "4":
            self.pasta_saida = os.path.expanduser("~/Downloads")
            print(f"{Fore.GREEN}✅ Pasta configurada: {self.pasta_saida}")
        elif escolha == "5":
            print(f"\n{Fore.CYAN}📂 Digite o caminho da pasta:")
            print(f"{Fore.WHITE}Exemplo: C:\\Users\\Usuario\\Minhas Transcrições")
            pasta_personalizada = input(f"{Fore.YELLOW}Caminho: ").strip().strip('"')
            
            if pasta_personalizada:
                # Verificar se a pasta existe ou pode ser criada
                try:
                    os.makedirs(pasta_personalizada, exist_ok=True)
                    self.pasta_saida = pasta_personalizada
                    print(f"{Fore.GREEN}✅ Pasta configurada: {self.pasta_saida}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Erro ao configurar pasta: {str(e)}")
                    print(f"{Fore.YELLOW}Mantendo configuração anterior.")
            else:
                print(f"{Fore.YELLOW}⚠️ Operação cancelada.")
        elif escolha == "0":
            return
        else:
            print(f"{Fore.RED}❌ Opção inválida!")
        
        self.aguardar_tecla()

    def verificar_ffmpeg(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}🔧 VERIFICAÇÃO DO FFMPEG")
        print("="*50)
        
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"{Fore.GREEN}✅ FFmpeg está instalado e funcionando!")
                versao = result.stdout.split('\n')[0]
                print(f"{Fore.WHITE}Versão: {versao}")
            else:
                print(f"{Fore.RED}❌ FFmpeg encontrado mas com problemas")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"{Fore.RED}❌ FFmpeg não encontrado!")
            print(f"{Fore.YELLOW}💡 Para instalar o FFmpeg:")
            print(f"{Fore.WHITE}1. Baixe de: https://ffmpeg.org/download.html")
            print(f"{Fore.WHITE}2. Adicione ao PATH do sistema")
            print(f"{Fore.WHITE}3. Reinicie o terminal")
            
        self.aguardar_tecla()
        
    def iniciar_transcricao(self):
        if not self.arquivo_audio:
            self.limpar_tela()
            print(f"{Fore.RED}❌ ERRO: Nenhum arquivo de áudio selecionado!")
            print(f"{Fore.YELLOW}Selecione um arquivo primeiro no menu principal.")
            self.aguardar_tecla()
            return
            
        self.limpar_tela()
        print(f"{Fore.GREEN}🚀 INICIANDO TRANSCRIÇÃO")
        print("="*50)
        
        # Mostrar configurações finais
        print(f"{Fore.YELLOW}📋 Configurações da transcrição:")
        print(f"{Fore.WHITE}Arquivo: {Fore.CYAN}{os.path.basename(self.arquivo_audio)}")
        print(f"{Fore.WHITE}Modelo: {Fore.CYAN}{self.modelo}")
        print(f"{Fore.WHITE}Idioma: {Fore.CYAN}{self.idiomas_disponiveis.get(self.idioma, self.idioma)}")
        print(f"{Fore.WHITE}Traduzir: {Fore.CYAN}{'Sim' if self.traduzir else 'Não'}")
        print(f"{Fore.WHITE}Formato: {Fore.CYAN}{self.formatos_disponiveis[self.formato]}")
        
        print(f"\n{Fore.YELLOW}Deseja continuar? (s/n): ", end="")
        if input().strip().lower() != 's':
            return
            
        # Executar o script de transcrição
        print(f"\n{Fore.CYAN}🎬 Executando transcrição...")
        print(f"{Fore.YELLOW}Aguarde... Isso pode levar alguns minutos.\n")
        
        # Usar função direta para melhor controle
        try:
            from transcrever_audio_melhorado import transcrever_audio
            
            # Preparar parâmetros
            idioma_param = None if self.idioma == "auto" else self.idioma
            
            # Executar transcrição
            arquivo_criado = transcrever_audio(
                self.arquivo_audio,
                self.modelo,
                idioma_param,
                self.traduzir,
                self.formato,
                self.pasta_saida
            )
            
            if arquivo_criado and os.path.exists(arquivo_criado):
                print(f"\n{Fore.GREEN}✅ Transcrição concluída com sucesso!")
                print(f"{Fore.CYAN}📁 Arquivo salvo: {os.path.basename(arquivo_criado)}")
                print(f"{Fore.YELLOW}📂 Localização: {arquivo_criado}")
                
                # Perguntar se quer abrir o arquivo ou pasta
                print(f"\n{Fore.WHITE}Opções:")
                print(f"{Fore.GREEN}A - Abrir arquivo de transcrição")
                print(f"{Fore.CYAN}F - Abrir pasta no Windows Explorer")
                print(f"{Fore.YELLOW}Enter - Continuar")
                
                opcao = input(f"\n{Fore.YELLOW}Escolha: ").strip().upper()
                
                if opcao == "A":
                    try:
                        subprocess.run(['notepad', arquivo_criado], check=True)
                        print(f"{Fore.GREEN}✅ Arquivo aberto no Bloco de Notas!")
                    except:
                        print(f"{Fore.YELLOW}⚠️ Não foi possível abrir automaticamente.")
                elif opcao == "F":
                    try:
                        # Abrir pasta contendo o arquivo
                        pasta_arquivo = os.path.dirname(arquivo_criado)
                        subprocess.run(['explorer', pasta_arquivo], check=True)
                        print(f"{Fore.GREEN}✅ Pasta aberta no Windows Explorer!")
                    except:
                        print(f"{Fore.YELLOW}⚠️ Não foi possível abrir a pasta.")
            else:
                raise Exception("Arquivo de saída não foi criado")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {str(e)}")
            # Fallback para método antigo
            self._executar_transcricao_fallback()
        
        self.aguardar_tecla()
    
    def _executar_transcricao_fallback(self):
        """Método fallback usando subprocess"""
        print(f"{Fore.YELLOW}⚠️ Usando método alternativo...")
        
        cmd = [
            sys.executable, "transcrever_audio_melhorado.py",
            self.arquivo_audio,
            "--modelo", self.modelo,
            "--formato", self.formato
        ]
        
        if self.idioma != "auto":
            cmd.extend(["--idioma", self.idioma])
            
        if self.traduzir:
            cmd.append("--traduzir")
            
        try:
            resultado = subprocess.run(cmd, capture_output=False, text=True)
            if resultado.returncode == 0:
                print(f"\n{Fore.GREEN}✅ Transcrição concluída com sucesso!")
                
                # Determinar nome do arquivo de saída
                nome_base = os.path.splitext(os.path.basename(self.arquivo_audio))[0]
                sufixo = "_traduzido" if self.traduzir else "_transcricao"
                arquivo_saida = f"{nome_base}{sufixo}{self.formato}"
                
                # Se pasta personalizada configurada, mover arquivo
                if self.pasta_saida and os.path.exists(arquivo_saida):
                    try:
                        os.makedirs(self.pasta_saida, exist_ok=True)
                        novo_caminho = os.path.join(self.pasta_saida, arquivo_saida)
                        os.rename(arquivo_saida, novo_caminho)
                        arquivo_saida = novo_caminho
                        print(f"{Fore.CYAN}📁 Arquivo movido para: {arquivo_saida}")
                    except Exception as e:
                        print(f"{Fore.YELLOW}⚠️ Não foi possível mover arquivo: {str(e)}")
                
                # Verificar se o arquivo foi criado
                if os.path.exists(arquivo_saida):
                    print(f"{Fore.CYAN}📁 Arquivo salvo: {os.path.basename(arquivo_saida)}")
                    print(f"{Fore.YELLOW}📂 Localização: {os.path.abspath(arquivo_saida)}")
                    
                    # Perguntar se quer abrir o arquivo ou pasta
                    print(f"\n{Fore.WHITE}Opções:")
                    print(f"{Fore.GREEN}A - Abrir arquivo de transcrição")
                    print(f"{Fore.CYAN}F - Abrir pasta no Windows Explorer")
                    print(f"{Fore.YELLOW}Enter - Continuar")
                    
                    opcao = input(f"\n{Fore.YELLOW}Escolha: ").strip().upper()
                    
                    if opcao == "A":
                        try:
                            subprocess.run(['notepad', arquivo_saida], check=True)
                            print(f"{Fore.GREEN}✅ Arquivo aberto no Bloco de Notas!")
                        except:
                            print(f"{Fore.YELLOW}⚠️ Não foi possível abrir automaticamente.")
                    elif opcao == "F":
                        try:
                            pasta_arquivo = os.path.dirname(os.path.abspath(arquivo_saida))
                            subprocess.run(['explorer', pasta_arquivo], check=True)
                            print(f"{Fore.GREEN}✅ Pasta aberta no Windows Explorer!")
                        except:
                            print(f"{Fore.YELLOW}⚠️ Não foi possível abrir a pasta.")
                else:
                    print(f"{Fore.RED}❌ Erro: Arquivo de saída não encontrado!")
                    self.diagnosticar_problema_arquivo(arquivo_saida)
            else:
                print(f"\n{Fore.RED}❌ Erro durante a transcrição!")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Erro ao executar: {str(e)}")
        
        self.aguardar_tecla()
        
    def ver_arquivos_recentes(self):
        self.limpar_tela()
        print(f"{Fore.CYAN}📚 ARQUIVOS DE TRANSCRIÇÃO RECENTES")
        print("="*50)
        
        # Mostrar pasta atual
        pasta_atual = os.getcwd()
        print(f"{Fore.YELLOW}📂 Pasta atual: {Fore.WHITE}{pasta_atual}")
        print()
        
        # Buscar arquivos de transcrição na pasta atual e em subpastas
        padroes = ['*_transcricao.txt', '*_transcricao.srt', '*_transcricao.vtt', 
                  '*_traduzido.txt', '*_traduzido.srt', '*_traduzido.vtt']
        arquivos_transcricao = []
        
        # Buscar na pasta atual
        for padrao in padroes:
            arquivos_transcricao.extend(glob.glob(padrao))
            
        # Buscar em subpastas outputs/ e uploads/
        for subpasta in ['outputs', 'uploads']:
            if os.path.exists(subpasta):
                for padrao in padroes:
                    arquivos_transcricao.extend(glob.glob(os.path.join(subpasta, padrao)))
            
        # Também buscar arquivos de texto que podem ser transcrições
        todos_txt = glob.glob('*.txt')
        
        # Incluir arquivos com UUIDs (do sistema web)
        import re
        uuid_pattern = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}.*\.txt$')
        arquivos_uuid = [f for f in todos_txt if uuid_pattern.match(f)]
        arquivos_transcricao.extend(arquivos_uuid)
        
        outros_arquivos = [f for f in todos_txt if f not in arquivos_transcricao and 
                          (f.lower().find('transcri') >= 0 or f.lower().find('traduz') >= 0)]
        arquivos_transcricao.extend(outros_arquivos)
        
        # Remover duplicatas
        arquivos_transcricao = list(set(arquivos_transcricao))
            
        if arquivos_transcricao:
            arquivos_transcricao.sort(key=os.path.getmtime, reverse=True)
            print(f"{Fore.GREEN}📄 Arquivos encontrados (mais recentes primeiro):")
            
            for i, arquivo in enumerate(arquivos_transcricao[:10], 1):  # Mostrar apenas os 10 mais recentes
                modificado = os.path.getmtime(arquivo)
                data_modificacao = Path(arquivo).stat().st_mtime
                import datetime
                data_str = datetime.datetime.fromtimestamp(data_modificacao).strftime("%d/%m/%Y %H:%M")
                tamanho = os.path.getsize(arquivo) / 1024  # KB
                
                print(f"{Fore.WHITE}{i:2d}. {Fore.YELLOW}{arquivo}")
                print(f"     {Fore.CYAN}📅 {data_str} | 📦 {tamanho:.1f} KB")
                
            print(f"\n{Fore.WHITE}Digite uma opção:")
            print(f"{Fore.GREEN}[1-{len(arquivos_transcricao)}] - Visualizar arquivo")
            print(f"{Fore.CYAN}F - Abrir pasta no Windows Explorer")
            print(f"{Fore.YELLOW}Enter - Voltar ao menu")
            print(f"\n{Fore.YELLOW}Opção: ", end="")
            
            escolha = input().strip().upper()
            
            if escolha == "F":
                self.abrir_pasta_arquivos()
            elif escolha.isdigit():
                idx = int(escolha) - 1
                if 0 <= idx < len(arquivos_transcricao):
                    self.visualizar_arquivo(arquivos_transcricao[idx])
        else:
            print(f"{Fore.YELLOW}⚠️  Nenhum arquivo de transcrição encontrado.")
            print(f"{Fore.WHITE}💡 Possíveis causas:")
            print(f"{Fore.WHITE}   - Ainda não foi feita nenhuma transcrição")
            print(f"{Fore.WHITE}   - Os arquivos estão em outra pasta")
            print(f"{Fore.WHITE}   - Os nomes dos arquivos são diferentes")
            print()
            print(f"{Fore.WHITE}Opções:")
            print(f"{Fore.GREEN}F - Abrir pasta no Windows Explorer")
            print(f"{Fore.YELLOW}Enter - Voltar ao menu")
            print(f"\n{Fore.YELLOW}Opção: ", end="")
            
            escolha = input().strip().upper()
            if escolha == "F":
                self.abrir_pasta_arquivos()
            
        if escolha != "F":
            self.aguardar_tecla()
        
    def visualizar_arquivo(self, caminho_arquivo):
        self.limpar_tela()
        print(f"{Fore.CYAN}👁️  VISUALIZANDO: {os.path.basename(caminho_arquivo)}")
        print("="*70)
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                
            linhas = conteudo.split('\n')
            print(f"{Fore.YELLOW}📊 Total de linhas: {len(linhas)}")
            print(f"{Fore.YELLOW}📏 Tamanho: {len(conteudo)} caracteres")
            print("\n" + "─"*70)
            
            # Mostrar primeiras 20 linhas
            for i, linha in enumerate(linhas[:20], 1):
                if linha.strip():
                    print(f"{Fore.WHITE}{i:3d}: {linha}")
                    
            if len(linhas) > 20:
                print(f"\n{Fore.CYAN}... e mais {len(linhas) - 20} linhas")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao ler arquivo: {str(e)}")
            
        self.aguardar_tecla()
        
    def confirmar_saida(self):
        self.limpar_tela()
        print(f"{Fore.MAGENTA}👋 ENCERRANDO SISTEMA DE TRANSCRIÇÃO")
        print("="*50)
        print(f"{Fore.YELLOW}Deseja realmente sair? (s/n): ", end="")
        if input().strip().lower() == 's':
            print(f"\n{Fore.GREEN}✅ Obrigado por usar o Sistema de Transcrição!")
            print(f"{Fore.CYAN}🚀 Desenvolvido com Whisper AI")
            return True
        return False
    
    def abrir_pasta_arquivos(self):
        """Abre a pasta atual no Windows Explorer"""
        try:
            pasta_atual = os.getcwd()
            subprocess.run(['explorer', pasta_atual], check=True)
            print(f"{Fore.GREEN}✅ Pasta aberta no Windows Explorer!")
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao abrir pasta: {str(e)}")
            print(f"{Fore.YELLOW}📂 Pasta manual: {os.getcwd()}")
        
        self.aguardar_tecla()
    
    def diagnosticar_problema_arquivo(self, nome_arquivo_esperado):
        """Diagnóstica problemas quando arquivo de saída não é encontrado"""
        print(f"\n{Fore.RED}🔍 DIAGNÓSTICO DO PROBLEMA")
        print(f"{Fore.WHITE}{'='*50}")
        
        print(f"{Fore.YELLOW}📋 Arquivo esperado: {nome_arquivo_esperado}")
        print(f"{Fore.YELLOW}📂 Diretório atual: {os.getcwd()}")
        
        # Listar todos os arquivos na pasta atual
        arquivos_atuais = [f for f in os.listdir('.') if os.path.isfile(f)]
        print(f"\n{Fore.CYAN}📄 Arquivos na pasta atual ({len(arquivos_atuais)}):")
        
        if arquivos_atuais:
            for arquivo in sorted(arquivos_atuais):
                tamanho = os.path.getsize(arquivo) / 1024
                print(f"   - {arquivo} ({tamanho:.1f} KB)")
        else:
            print(f"   {Fore.RED}Nenhum arquivo encontrado!")
        
        # Buscar arquivos com nome similar
        nome_base = os.path.splitext(nome_arquivo_esperado)[0]
        import glob
        
        print(f"\n{Fore.MAGENTA}🔍 Buscando arquivos similares...")
        
        # Padrões de busca
        padroes = [
            f"{nome_base}*",
            "*transcricao*",
            "*traduzido*",
            "*.txt",
            "*.srt",
            "*.vtt"
        ]
        
        arquivos_encontrados = set()
        for padrao in padroes:
            arquivos_encontrados.update(glob.glob(padrao))
        
        if arquivos_encontrados:
            print(f"{Fore.GREEN}✅ Arquivos encontrados:")
            for arquivo in sorted(arquivos_encontrados):
                if os.path.exists(arquivo):
                    stat = os.stat(arquivo)
                    tamanho = stat.st_size / 1024
                    import datetime
                    modificado = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%H:%M:%S")
                    print(f"   - {arquivo} ({tamanho:.1f} KB, modificado às {modificado})")
        else:
            print(f"{Fore.RED}❌ Nenhum arquivo similar encontrado!")
        
        # Verificar subpastas
        subpastas = ['outputs', 'uploads', 'transcricoes']
        print(f"\n{Fore.CYAN}📁 Verificando subpastas...")
        
        for subpasta in subpastas:
            if os.path.exists(subpasta) and os.path.isdir(subpasta):
                arquivos_sub = os.listdir(subpasta)
                if arquivos_sub:
                    print(f"   📂 {subpasta}/: {len(arquivos_sub)} arquivo(s)")
                    for arquivo in arquivos_sub[:3]:  # Mostrar apenas os 3 primeiros
                        print(f"      - {arquivo}")
                    if len(arquivos_sub) > 3:
                        print(f"      ... e mais {len(arquivos_sub) - 3} arquivo(s)")
                else:
                    print(f"   📂 {subpasta}/: (vazia)")
            else:
                print(f"   📂 {subpasta}/: (não existe)")
        
        print(f"\n{Fore.WHITE}{'='*50}")
        self.aguardar_tecla()

def main():
    try:
        painel = PainelTranscricao()
        painel.menu_principal()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Interrompido pelo usuário.")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro inesperado: {str(e)}")
    finally:
        print(f"{Fore.WHITE}\nAté logo! 👋")

if __name__ == "__main__":
    main()
