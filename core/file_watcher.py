import os
import time
from typing import List, Dict, Any, Callable, Optional, Tuple
from core.xml_parser import parse_xml_file, compute_file_hash
from core.database import insert_xmls_bulk, delete_xml_by_path, get_indexed_paths_and_hashes

def scan_directory(directory_path: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[int, int, int]:
    """
    Varre recursivamente um diretório para encontrar novos, alterados e removidos arquivos XML.
    Sincroniza os dados com o SQLite de forma otimizada.
    Retorna uma tupla: (inseridos/atualizados, removidos, total_erros)
    """
    if not os.path.exists(directory_path):
        return 0, 0, 0

    print(f"Iniciando varredura em: {directory_path}")
    
    # 1. Obter todos os arquivos XML no disco recursivamente
    disk_files = []
    for root_dir, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.xml'):
                disk_files.append(os.path.abspath(os.path.join(root_dir, file)))

    total_disk_files = len(disk_files)
    print(f"Total de XMLs encontrados no disco: {total_disk_files}")

    # 2. Obter mapeamento dos arquivos indexados no banco
    indexed_files = get_indexed_paths_and_hashes() # caminhos absolutos -> hash

    # 3. Detectar arquivos que foram excluídos do disco
    deleted_paths = []
    for indexed_path in indexed_files.keys():
        # Se não estiver no disco, foi deletado
        if not os.path.exists(indexed_path):
            deleted_paths.append(indexed_path)

    # Remover do banco em lote/sequencial
    removed_count = 0
    for del_path in deleted_paths:
        if delete_xml_by_path(del_path):
            removed_count += 1
            
    print(f"Arquivos removidos do banco (não encontrados no disco): {removed_count}")

    # 4. Processar novos ou alterados
    to_parse = []
    for idx, filepath in enumerate(disk_files):
        # Callback para relatar progresso de varredura prévia
        if progress_callback:
            # Etapa preliminar: 0% a 10%
            progress_callback(idx + 1, total_disk_files)
            
        current_hash = None
        # Verifica se o arquivo já está no banco e se o hash bate
        if filepath in indexed_files:
            # Para evitar recalcular hash de 50.000 arquivos a cada segundo:
            # Podemos comparar o tamanho e mtime do arquivo como otimização, 
            # mas o hash direto também é viável se o volume for moderado.
            # Vamos usar o hash MD5, que para XMLs pequenos (<50KB) é extremamente rápido.
            try:
                # Otimização: Só calcula hash se mtime ou tamanho diferir? 
                # Como não guardamos mtime/size no banco, vamos direto calcular o hash.
                # Um hash de 10k arquivos pequenos no SSD leva cerca de 1 a 2 segundos.
                current_hash = compute_file_hash(filepath)
                if indexed_files[filepath] == current_hash:
                    # Sem alteração, ignora
                    continue
            except Exception:
                # Se der erro ao ler arquivo, passa reto
                continue
                
        to_parse.append((filepath, current_hash))

    total_to_parse = len(to_parse)
    print(f"Arquivos novos ou alterados detectados para leitura: {total_to_parse}")

    # 5. Ler metadados em lotes e inserir no banco
    inserted_count = 0
    error_count = 0
    batch_size = 500
    batch_docs = []

    for idx, (filepath, cached_hash) in enumerate(to_parse):
        try:
            doc = parse_xml_file(filepath)
            if doc:
                # Se já calculamos o hash no passo anterior, aproveita ele
                if cached_hash:
                    doc["hash_arquivo"] = cached_hash
                batch_docs.append(doc)
            else:
                error_count += 1
        except Exception as e:
            print(f"Erro ao processar {filepath}: {e}")
            error_count += 1

        # Insere em lotes para otimizar transação SQLite
        if len(batch_docs) >= batch_size or idx == total_to_parse - 1:
            if batch_docs:
                try:
                    insert_xmls_bulk(batch_docs)
                    inserted_count += len(batch_docs)
                    batch_docs = []
                except Exception as e:
                    print(f"Erro na gravação em lote: {e}")
                    error_count += len(batch_docs)
                    batch_docs = []

        # Relata progresso real da leitura pesada
        if progress_callback:
            # Mapeia de 10% a 100% o progresso real de leitura dos arquivos pendentes
            progress_callback(idx + 1, total_to_parse)

    print(f"Sincronização concluída. Inseridos/Alterados: {inserted_count}, Erros: {error_count}")
    return inserted_count, removed_count, error_count
