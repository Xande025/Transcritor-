from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import json
import subprocess
import glob
from pathlib import Path
import threading
import uuid
from datetime import datetime
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Criar pastas se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Armazenar status das transcrições
transcription_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    # Verificar se é um arquivo de áudio/vídeo válido
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.mp4', '.avi', '.mkv', '.mov'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Formato {file_ext} não suportado'}), 400
    
    # Salvar arquivo
    task_id = str(uuid.uuid4())
    filename = f"{task_id}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Informações do arquivo
    file_size = os.path.getsize(filepath)
    file_info = {
        'task_id': task_id,
        'filename': file.filename,
        'filepath': filepath,
        'size': file_size,
        'uploaded_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'filename': file.filename,
        'size': file_size
    })

@app.route('/transcribe', methods=['POST'])
def start_transcription():
    data = request.get_json()
    
    task_id = data.get('task_id')
    modelo = data.get('modelo', 'medium')
    idioma = data.get('idioma', 'pt')
    traduzir = data.get('traduzir', False)
    formato = data.get('formato', '.txt')
    
    if not task_id:
        return jsonify({'error': 'ID da tarefa não fornecido'}), 400
    
    # Encontrar arquivo
    upload_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_*"))
    if not upload_files:
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    filepath = upload_files[0]
    
    # Inicializar status
    transcription_status[task_id] = {
        'status': 'processing',
        'progress': 0,
        'message': 'Iniciando transcrição...',
        'started_at': datetime.now().isoformat()
    }
    
    # Executar transcrição em thread separada
    thread = threading.Thread(
        target=run_transcription,
        args=(task_id, filepath, modelo, idioma, traduzir, formato)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'task_id': task_id})

def run_transcription(task_id, filepath, modelo, idioma, traduzir, formato):
    try:
        # Atualizar status
        transcription_status[task_id]['message'] = 'Carregando modelo Whisper...'
        transcription_status[task_id]['progress'] = 10
        
        # Comando para execução
        cmd = [
            'python', 'transcrever_audio_melhorado.py',
            filepath,
            '--modelo', modelo,
            '--formato', formato
        ]
        
        if idioma != 'auto':
            cmd.extend(['--idioma', idioma])
            
        if traduzir:
            cmd.append('--traduzir')
        
        # Atualizar status
        transcription_status[task_id]['message'] = 'Transcrevendo áudio...'
        transcription_status[task_id]['progress'] = 30
        
        # Log do comando para debug
        print(f"[DEBUG] Executando comando: {' '.join(cmd)}")
        print(f"[DEBUG] Diretório de trabalho: {os.getcwd()}")
        print(f"[DEBUG] Arquivo de entrada: {filepath}")
        
        # Importar e usar a função diretamente em vez de subprocess
        import sys
        sys.path.append('.')
        from transcrever_audio_melhorado import transcrever_audio
        
        # Preparar parâmetros
        idioma_param = None if idioma == 'auto' else idioma
        pasta_outputs = app.config['OUTPUT_FOLDER']
        
        # Executar transcrição diretamente
        try:
            arquivo_salvo = transcrever_audio(
                filepath, 
                modelo, 
                idioma_param, 
                traduzir, 
                formato,
                pasta_outputs
            )
            
            if arquivo_salvo and os.path.exists(arquivo_salvo):
                # Renomear arquivo para incluir task_id (primeiros 8 caracteres para legibilidade)
                nome_original = os.path.basename(arquivo_salvo)
                task_short = task_id[:8]  # Usar apenas primeiros 8 caracteres do UUID
                
                # Separar nome e extensão
                nome_sem_ext, extensao = os.path.splitext(nome_original)
                novo_nome = f"{task_short}_{nome_sem_ext}{extensao}"
                novo_caminho = os.path.join(app.config['OUTPUT_FOLDER'], novo_nome)
                
                if arquivo_salvo != novo_caminho:
                    # Se arquivo de destino já existe, adicionar timestamp para garantir unicidade
                    contador = 1
                    novo_caminho_base = novo_caminho
                    while os.path.exists(novo_caminho):
                        nome_com_contador = f"{task_short}_{nome_sem_ext}_{contador}{extensao}"
                        novo_caminho = os.path.join(app.config['OUTPUT_FOLDER'], nome_com_contador)
                        contador += 1
                        
                        # Evitar loop infinito
                        if contador > 100:
                            # Como último recurso, sobrescrever
                            novo_caminho = novo_caminho_base
                            try:
                                os.remove(novo_caminho)
                                print(f"[DEBUG] Arquivo existente sobrescrito: {novo_caminho}")
                            except:
                                pass
                            break
                    
                    try:
                        os.rename(arquivo_salvo, novo_caminho)
                        arquivo_salvo = novo_caminho
                        print(f"[DEBUG] Arquivo renomeado para: {novo_caminho}")
                    except Exception as e:
                        print(f"[DEBUG] Erro ao renomear arquivo: {str(e)}")
                        # Se não conseguir renomear, manter o arquivo original
                        arquivo_salvo = arquivo_salvo
                
                transcription_status[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Transcrição concluída com sucesso!',
                    'output_file': os.path.basename(arquivo_salvo),
                    'completed_at': datetime.now().isoformat()
                })
            else:
                raise Exception("Arquivo de saída não foi criado")
                
        except Exception as e:
            # Fallback para o método antigo com subprocess
            print(f"[DEBUG] Usando fallback subprocess devido a: {str(e)}")
            
            # Executar transcrição
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                # Encontrar arquivo de saída
                original_filename = Path(filepath).stem.split('_', 1)[1]  # Remove task_id prefix
                base_name = Path(original_filename).stem
                sufixo = "_traduzido" if traduzir else "_transcricao"
                output_filename = f"{base_name}{sufixo}{formato}"
                
                # Procurar arquivo de saída apenas na pasta outputs
                possible_paths = [
                    os.path.join(app.config['OUTPUT_FOLDER'], output_filename),
                ]
                
                source_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        source_path = path
                        break
                
                if source_path:
                    # Renomear arquivo para incluir task_id (primeiros 8 caracteres)
                    task_short = task_id[:8]
                    nome_sem_ext, extensao = os.path.splitext(output_filename)
                    novo_nome = f"{task_short}_{nome_sem_ext}{extensao}"
                    dest_path = os.path.join(app.config['OUTPUT_FOLDER'], novo_nome)
                    
                    if source_path != dest_path:
                        # Se arquivo de destino já existe, adicionar contador
                        contador = 1
                        dest_path_base = dest_path
                        while os.path.exists(dest_path):
                            nome_com_contador = f"{task_short}_{nome_sem_ext}_{contador}{extensao}"
                            dest_path = os.path.join(app.config['OUTPUT_FOLDER'], nome_com_contador)
                            contador += 1
                            
                            # Evitar loop infinito
                            if contador > 100:
                                dest_path = dest_path_base
                                try:
                                    os.remove(dest_path)
                                    print(f"[DEBUG] Arquivo existente sobrescrito: {dest_path}")
                                except:
                                    pass
                                break
                        
                        try:
                            os.rename(source_path, dest_path)
                            print(f"[DEBUG] Arquivo renomeado para: {dest_path}")
                        except Exception as e:
                            print(f"[DEBUG] Erro ao renomear arquivo: {str(e)}")
                            dest_path = source_path  # Manter arquivo original se não conseguir renomear
                    
                    transcription_status[task_id].update({
                        'status': 'completed',
                        'progress': 100,
                        'message': 'Transcrição concluída com sucesso!',
                        'output_file': os.path.basename(dest_path),
                        'completed_at': datetime.now().isoformat()
                    })
                else:
                    # Arquivo não encontrado - fazer diagnóstico apenas na pasta outputs
                    import glob
                    output_files = glob.glob(os.path.join(app.config['OUTPUT_FOLDER'], '*'))
                    
                    error_msg = f"Arquivo de saída não encontrado: {output_filename}"
                    if output_files:
                        recent_files = [os.path.basename(f) for f in output_files[-5:]]  # Últimos 5
                        error_msg += f" | Arquivos na pasta outputs: {', '.join(recent_files)}"
                    
                    transcription_status[task_id].update({
                        'status': 'error',
                        'message': error_msg,
                        'completed_at': datetime.now().isoformat()
                    })
            else:
                transcription_status[task_id].update({
                    'status': 'error',
                    'message': f'Erro na transcrição: {result.stderr}',
                    'completed_at': datetime.now().isoformat()
                })
            
    except Exception as e:
        transcription_status[task_id].update({
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'completed_at': datetime.now().isoformat()
        })

@app.route('/status/<task_id>')
def get_status(task_id):
    status = transcription_status.get(task_id, {'status': 'not_found'})
    return jsonify(status)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'Arquivo não encontrado'}), 404

@app.route('/recent')
def get_recent_files():
    files = []
    output_dir = app.config['OUTPUT_FOLDER']
    
    for file_path in glob.glob(os.path.join(output_dir, '*')):
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            files.append({
                'filename': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'download_url': url_for('download_file', filename=os.path.basename(file_path))
            })
    
    # Ordenar por data de modificação (mais recente primeiro)
    files.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify(files[:20])  # Retorna os 20 mais recentes

@app.route('/check_ffmpeg')
def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            return jsonify({'status': 'ok', 'version': version})
        else:
            return jsonify({'status': 'error', 'message': 'FFmpeg com problemas'})
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return jsonify({'status': 'not_found', 'message': 'FFmpeg não encontrado'})

@app.route('/cleanup')
def cleanup_files():
    """Remove arquivos antigos para liberar espaço"""
    try:
        # Remover uploads antigos (mais de 1 hora)
        current_time = datetime.now().timestamp()
        for file_path in glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*')):
            if current_time - os.path.getmtime(file_path) > 3600:  # 1 hora
                os.remove(file_path)
        
        return jsonify({'success': True, 'message': 'Limpeza concluída'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/<task_id>')
def debug_transcription(task_id):
    """Endpoint para debug de problemas de transcrição"""
    try:
        # Informações do diretório atual
        current_dir = os.getcwd()
        
        # Listar arquivos no diretório atual
        current_files = [f for f in os.listdir('.') if os.path.isfile(f)]
        
        # Listar arquivos na pasta uploads
        upload_files = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            upload_files = os.listdir(app.config['UPLOAD_FOLDER'])
        
        # Listar arquivos na pasta outputs
        output_files = []
        if os.path.exists(app.config['OUTPUT_FOLDER']):
            output_files = os.listdir(app.config['OUTPUT_FOLDER'])
        
        # Buscar arquivos relacionados ao task_id
        task_files = [f for f in current_files if task_id in f]
        
        # Status da transcrição
        status = transcription_status.get(task_id, {})
        
        debug_info = {
            'task_id': task_id,
            'current_directory': current_dir,
            'current_files': current_files[:20],  # Limitar para não sobrecarregar
            'upload_files': upload_files,
            'output_files': output_files,
            'task_related_files': task_files,
            'transcription_status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
