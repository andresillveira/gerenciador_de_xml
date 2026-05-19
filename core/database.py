import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_FILE = os.path.expanduser("~/.gerenciador_xml/data.db")

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco de dados SQLite, criando as pastas necessárias."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados e cria os índices necessários."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela principal de documentos fiscais
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS xml_documents (
            chave_acesso TEXT PRIMARY KEY,
            numero INTEGER,
            serie INTEGER,
            modelo INTEGER,
            data_emissao TEXT,
            cnpj_emitente TEXT,
            nome_emitente TEXT,
            cnpj_destinatario TEXT,
            nome_destinatario TEXT,
            valor_total REAL,
            tipo_nf INTEGER, -- 0 = Entrada, 1 = Saída, NULL = CT-e / Outros
            caminho_arquivo TEXT UNIQUE,
            hash_arquivo TEXT,
            tags TEXT,
            data_indexacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Índices para otimizar pesquisas e filtros (essencial para performance com 50.000+ itens)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cnpj_emitente ON xml_documents(cnpj_emitente)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cnpj_destinatario ON xml_documents(cnpj_destinatario)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_emissao ON xml_documents(data_emissao)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tipo_nf ON xml_documents(tipo_nf)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_modelo ON xml_documents(modelo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_numero ON xml_documents(numero)")
    
    conn.commit()
    conn.close()

def insert_or_replace_xml(doc: Dict[str, Any]) -> bool:
    """Insere ou atualiza um XML indexado no banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO xml_documents (
                chave_acesso, numero, serie, modelo, data_emissao,
                cnpj_emitente, nome_emitente, cnpj_destinatario, nome_destinatario,
                valor_total, tipo_nf, caminho_arquivo, hash_arquivo, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.get("chave_acesso"),
            doc.get("numero"),
            doc.get("serie"),
            doc.get("modelo"),
            doc.get("data_emissao"),
            doc.get("cnpj_emitente"),
            doc.get("nome_emitente"),
            doc.get("cnpj_destinatario"),
            doc.get("nome_destinatario"),
            doc.get("valor_total"),
            doc.get("tipo_nf"),
            doc.get("caminho_arquivo"),
            doc.get("hash_arquivo"),
            doc.get("tags")
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir XML {doc.get('caminho_arquivo')}: {e}")
        return False
    finally:
        conn.close()

def insert_xmls_bulk(docs: List[Dict[str, Any]]):
    """Insere múltiplos XMLs em lote para máxima performance (uso de transações)."""
    if not docs:
        return
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.executemany("""
            INSERT OR REPLACE INTO xml_documents (
                chave_acesso, numero, serie, modelo, data_emissao,
                cnpj_emitente, nome_emitente, cnpj_destinatario, nome_destinatario,
                valor_total, tipo_nf, caminho_arquivo, hash_arquivo, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                d.get("chave_acesso"),
                d.get("numero"),
                d.get("serie"),
                d.get("modelo"),
                d.get("data_emissao"),
                d.get("cnpj_emitente"),
                d.get("nome_emitente"),
                d.get("cnpj_destinatario"),
                d.get("nome_destinatario"),
                d.get("valor_total"),
                d.get("tipo_nf"),
                d.get("caminho_arquivo"),
                d.get("hash_arquivo"),
                d.get("tags")
            ) for d in docs
        ])
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro na inserção em lote: {e}")
        raise e
    finally:
        conn.close()

def delete_xml_by_path(caminho: str) -> bool:
    """Remove um documento do banco de dados pelo seu caminho de arquivo."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM xml_documents WHERE caminho_arquivo = ?", (caminho,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao deletar XML do banco: {e}")
        return False
    finally:
        conn.close()

def delete_xml_by_key(chave: str) -> bool:
    """Remove um documento do banco de dados pela chave de acesso."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM xml_documents WHERE chave_acesso = ?", (chave,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao deletar XML por chave: {e}")
        return False
    finally:
        conn.close()

def get_indexed_paths_and_hashes() -> Dict[str, str]:
    """Retorna um dicionário mapeando caminho_arquivo -> hash_arquivo de todos os XMLs indexados."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT caminho_arquivo, hash_arquivo FROM xml_documents")
        return {row["caminho_arquivo"]: row["hash_arquivo"] for row in cursor.fetchall()}
    except Exception as e:
        print(f"Erro ao obter caminhos indexados: {e}")
        return {}
    finally:
        conn.close()

def search_documents(filters: Dict[str, Any]) -> List[sqlite3.Row]:
    """
    Busca documentos no banco aplicando filtros dinâmicos.
    Filtros suportados:
    - 'search': termo de busca global (pesquisa na chave, cnpj, razão social ou número)
    - 'cnpj_emitente': CNPJ exato do emitente
    - 'cnpj_destinatario': CNPJ exato do destinatário
    - 'tipo_nf': 0 (Entrada), 1 (Saída)
    - 'modelo': 55 (NF-e), 65 (NFC-e), 57 (CT-e)
    - 'data_inicio': data no formato 'YYYY-MM-DD'
    - 'data_fim': data no formato 'YYYY-MM-DD'
    - 'valor_min': valor total mínimo
    - 'valor_max': valor total máximo
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM xml_documents WHERE 1=1"
    params = []
    
    if filters.get("cnpj_emitente"):
        query += " AND cnpj_emitente = ?"
        params.append(filters["cnpj_emitente"])
        
    if filters.get("cnpj_destinatario"):
        query += " AND cnpj_destinatario = ?"
        params.append(filters["cnpj_destinatario"])
        
    if filters.get("tipo_nf") is not None:
        query += " AND tipo_nf = ?"
        params.append(filters["tipo_nf"])
        
    if filters.get("modelo"):
        query += " AND modelo = ?"
        params.append(filters["modelo"])
        
    if filters.get("data_inicio"):
        # Trata dhEmi que pode ter timezone, comparando os primeiros 10 caracteres (data)
        query += " AND substr(data_emissao, 1, 10) >= ?"
        params.append(filters["data_inicio"])
        
    if filters.get("data_fim"):
        query += " AND substr(data_emissao, 1, 10) <= ?"
        params.append(filters["data_fim"])
        
    if filters.get("valor_min") is not None:
        query += " AND valor_total >= ?"
        params.append(filters["valor_min"])
        
    if filters.get("valor_max") is not None:
        query += " AND valor_total <= ?"
        params.append(filters["valor_max"])
        
    if filters.get("search"):
        search_term = f"%{filters['search']}%"
        query += """ AND (
            chave_acesso LIKE ? 
            OR numero LIKE ? 
            OR cnpj_emitente LIKE ? 
            OR nome_emitente LIKE ? 
            OR cnpj_destinatario LIKE ? 
            OR nome_destinatario LIKE ?
        )"""
        params.extend([search_term] * 6)
        
    # Ordenar por data de emissão decrescente por padrão
    query += " ORDER BY data_emissao DESC"
    
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro na busca de documentos: {e}")
        return []
    finally:
        conn.close()

def get_stats() -> Dict[str, Any]:
    """Retorna estatísticas gerais do banco de dados (totais, valores, contagens)."""
    conn = get_connection()
    cursor = conn.cursor()
    stats = {}
    try:
        # Total de registros
        cursor.execute("SELECT COUNT(*), SUM(valor_total) FROM xml_documents")
        row = cursor.fetchone()
        stats["total_documentos"] = row[0] or 0
        stats["valor_total"] = row[1] or 0.0
        
        # Por modelo
        cursor.execute("SELECT modelo, COUNT(*) FROM xml_documents GROUP BY modelo")
        stats["por_modelo"] = {r[0]: r[1] for r in cursor.fetchall()}
        
        # Por tipo (Entrada/Saída)
        cursor.execute("SELECT tipo_nf, COUNT(*) FROM xml_documents GROUP BY tipo_nf")
        stats["por_tipo"] = {("Entrada" if r[0] == 0 else "Saída" if r[0] == 1 else "Outros"): r[1] for r in cursor.fetchall()}
        
        return stats
    except Exception as e:
        print(f"Erro ao obter estatísticas: {e}")
        return {}
    finally:
        conn.close()

def get_unique_emitentes() -> List[Dict[str, str]]:
    """Retorna lista de emitentes únicos (CNPJ e Nome) para preencher combos de filtro."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT cnpj_emitente, nome_emitente FROM xml_documents WHERE cnpj_emitente IS NOT NULL ORDER BY nome_emitente")
        return [{"cnpj": r["cnpj_emitente"], "nome": r["nome_emitente"]} for r in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao obter emitentes: {e}")
        return []
    finally:
        conn.close()

def get_unique_destinatarios() -> List[Dict[str, str]]:
    """Retorna lista de destinatários únicos (CNPJ e Nome) para preencher combos de filtro."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT cnpj_destinatario, nome_destinatario FROM xml_documents WHERE cnpj_destinatario IS NOT NULL ORDER BY nome_destinatario")
        return [{"cnpj": r["cnpj_destinatario"], "nome": r["nome_destinatario"]} for r in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao obter destinatários: {e}")
        return []
    finally:
        conn.close()
