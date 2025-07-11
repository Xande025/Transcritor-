# -*- coding: utf-8 -*-
import os
import sys
import argparse
import whisper
import subprocess

# Configurar codificação para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')

# Configurar ffmpeg para o Whisper
def configurar_ffmpeg():
    """Configura o ffmpeg para o Whisper funcionar corretamente"""
    try:
        # Verificar se ffmpeg está disponível
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("[OK] FFmpeg encontrado e funcionando")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Se não encontrou, tentar caminhos comuns
    caminhos_ffmpeg = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe")
    ]
    
    for caminho in caminhos_ffmpeg:
        if os.path.exists(caminho):
            # Adicionar ao PATH temporariamente
            os.environ['PATH'] = os.path.dirname(caminho) + os.pathsep + os.environ.get('PATH', '')
            print(f"[OK] FFmpeg configurado: {caminho}")
            return True
    
    print("[ERRO] FFmpeg não encontrado. Verifique se está instalado e no PATH.")
    return False

def transcrever_audio(caminho_audio, modelo_nome, idioma, traduzir, formato_saida, pasta_saida=None):
    # Configurar ffmpeg primeiro
    if not configurar_ffmpeg():
        print("[ERRO] Não foi possível configurar o FFmpeg. Abortando.")
        return
    
    # Carrega o modelo
    print(f"[INFO] Carregando modelo Whisper: {modelo_nome}")
    model = whisper.load_model(modelo_nome)

    # Verifica existência do arquivo
    if not os.path.exists(caminho_audio):
        print(f"[ERRO] Arquivo não encontrado: {caminho_audio}")
        return

    # Transcrição
    print(f"[INFO] Transcrevendo: {os.path.basename(caminho_audio)}")
    resultado = model.transcribe(
        caminho_audio,
        language=idioma,
        task='translate' if traduzir else 'transcribe',
        verbose=True
    )

    # Nome de saída - usar pasta específica se fornecida
    nome_base = os.path.splitext(os.path.basename(caminho_audio))[0]
    sufixo = "_traduzido" if traduzir else "_transcricao"
    
    # Se o nome base contém UUID (do sistema web), remover o UUID do nome final
    import re
    uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}_'
    if re.match(uuid_pattern, nome_base):
        nome_limpo = re.sub(uuid_pattern, '', nome_base)
        nome_final = f"{nome_limpo}{sufixo}{formato_saida}"
    else:
        nome_final = f"{nome_base}{sufixo}{formato_saida}"
    
    # Determinar pasta de saída
    if pasta_saida:
        # Usar pasta específica (para sistema web)
        os.makedirs(pasta_saida, exist_ok=True)
        arquivo_saida = os.path.join(pasta_saida, nome_final)
    else:
        # Salvar no diretório atual (para linha de comando)
        arquivo_saida = os.path.abspath(nome_final)
    
    print(f"[INFO] Arquivo será salvo como: {os.path.basename(arquivo_saida)}")
    print(f"[INFO] Caminho completo: {arquivo_saida}")

    try:
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            if formato_saida == ".txt":
                for segmento in resultado["segments"]:
                    f.write(segmento["text"].strip() + "\n")  # type: ignore
            elif formato_saida == ".srt":
                for i, segmento in enumerate(resultado["segments"], 1):
                    f.write(f"{i}\n")
                    f.write(f"{format_tempo(segmento['start'])} --> {format_tempo(segmento['end'])}\n")  # type: ignore
                    f.write(f"{segmento['text'].strip()}\n\n")  # type: ignore
            elif formato_saida == ".vtt":
                f.write("WEBVTT\n\n")
                for segmento in resultado["segments"]:
                    f.write(f"{format_tempo(segmento['start'])} --> {format_tempo(segmento['end'])}\n")  # type: ignore
                    f.write(f"{segmento['text'].strip()}\n\n")  # type: ignore
        
        print(f"\n[OK] Transcrição salva em: {os.path.basename(arquivo_saida)}")
        print(f"[INFO] Caminho completo: {arquivo_saida}")
        
        # Retornar o caminho do arquivo para uso programático
        return arquivo_saida
    except Exception as e:
        print(f"[ERRO] Erro ao salvar: {str(e)}")

def format_tempo(segundos):
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    ms = int((segundos - int(segundos)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def main():
    parser = argparse.ArgumentParser(description="Transcrição de áudio com Whisper.")
    parser.add_argument("audio", help="Caminho do arquivo de áudio")
    parser.add_argument("--modelo", default="medium", choices=["tiny", "base", "small", "medium", "large"],
                        help="Modelo Whisper a usar (padrão: medium)")
    parser.add_argument("--idioma", default="pt", help="Idioma do áudio. Use 'None' para autodetectar")
    parser.add_argument("--traduzir", action="store_true", help="Traduzir para inglês")
    parser.add_argument("--formato", default=".txt", choices=[".txt", ".srt", ".vtt"],
                        help="Formato de saída da transcrição")

    args = parser.parse_args()
    idioma = None if args.idioma.lower() == "none" else args.idioma

    transcrever_audio(args.audio, args.modelo, idioma, args.traduzir, args.formato)

if __name__ == "__main__":
    main() 