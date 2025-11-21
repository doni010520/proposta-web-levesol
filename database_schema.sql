-- ============================================
-- SCHEMA DO BANCO DE DADOS - SUPABASE
-- Sistema de Propostas Web - LEVESOL
-- ============================================

-- Execute este SQL no seu painel do Supabase
-- SQL Editor > New Query > Cole e Execute

-- ============================================
-- TABELA: propostas
-- Armazena todas as propostas criadas
-- ============================================
CREATE TABLE IF NOT EXISTS propostas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_proposta VARCHAR(50) UNIQUE NOT NULL,
    cliente_nome VARCHAR(255) NOT NULL,
    cliente_cpf_cnpj VARCHAR(20),
    cliente_endereco TEXT,
    cliente_cidade VARCHAR(100),
    cliente_telefone VARCHAR(20),
    dados_sistema JSONB NOT NULL,
    dados_payback JSONB NOT NULL,
    investimento DECIMAL(12,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE propostas IS 'Armazena todas as propostas de energia solar criadas';
COMMENT ON COLUMN propostas.id IS 'UUID único da proposta';
COMMENT ON COLUMN propostas.numero_proposta IS 'Número formatado da proposta (ex: 211124/2024)';
COMMENT ON COLUMN propostas.dados_sistema IS 'JSON com dados técnicos do sistema fotovoltaico';
COMMENT ON COLUMN propostas.dados_payback IS 'JSON com projeção de payback anual';

-- ============================================
-- TABELA: visualizacoes
-- Registra cada vez que uma proposta é aberta
-- ============================================
CREATE TABLE IF NOT EXISTS visualizacoes (
    id SERIAL PRIMARY KEY,
    proposta_id UUID NOT NULL REFERENCES propostas(id) ON DELETE CASCADE,
    visualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT,
    pais VARCHAR(50),
    cidade VARCHAR(100)
);

COMMENT ON TABLE visualizacoes IS 'Registra todas as visualizações das propostas (tracking)';
COMMENT ON COLUMN visualizacoes.proposta_id IS 'Referência à proposta visualizada';
COMMENT ON COLUMN visualizacoes.ip_address IS 'IP do visitante';
COMMENT ON COLUMN visualizacoes.user_agent IS 'Navegador/dispositivo usado';

-- ============================================
-- ÍNDICES para performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_propostas_numero 
    ON propostas(numero_proposta);

CREATE INDEX IF NOT EXISTS idx_propostas_created 
    ON propostas(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_visualizacoes_proposta 
    ON visualizacoes(proposta_id);

CREATE INDEX IF NOT EXISTS idx_visualizacoes_data 
    ON visualizacoes(visualizado_em DESC);

-- ============================================
-- VIEWS úteis para análise
-- ============================================

-- View: Propostas com total de visualizações
CREATE OR REPLACE VIEW vw_propostas_stats AS
SELECT 
    p.id,
    p.numero_proposta,
    p.cliente_nome,
    p.investimento,
    p.created_at,
    COUNT(v.id) as total_visualizacoes,
    MAX(v.visualizado_em) as ultima_visualizacao,
    MIN(v.visualizado_em) as primeira_visualizacao
FROM propostas p
LEFT JOIN visualizacoes v ON p.id = v.proposta_id
GROUP BY p.id, p.numero_proposta, p.cliente_nome, p.investimento, p.created_at
ORDER BY p.created_at DESC;

COMMENT ON VIEW vw_propostas_stats IS 'Resumo de propostas com estatísticas de visualização';

-- ============================================
-- POLÍTICAS DE SEGURANÇA (RLS)
-- Ajuste conforme sua necessidade
-- ============================================

-- Habilitar RLS (Row Level Security)
ALTER TABLE propostas ENABLE ROW LEVEL SECURITY;
ALTER TABLE visualizacoes ENABLE ROW LEVEL SECURITY;

-- Política: Permitir leitura pública de propostas
CREATE POLICY "Propostas podem ser lidas publicamente" 
    ON propostas FOR SELECT 
    USING (true);

-- Política: Permitir inserção de propostas (apenas via service_role)
CREATE POLICY "Propostas podem ser criadas via API" 
    ON propostas FOR INSERT 
    WITH CHECK (true);

-- Política: Permitir registro de visualizações
CREATE POLICY "Visualizações podem ser registradas" 
    ON visualizacoes FOR INSERT 
    WITH CHECK (true);

-- Política: Permitir leitura de visualizações
CREATE POLICY "Visualizações podem ser lidas" 
    ON visualizacoes FOR SELECT 
    USING (true);

-- ============================================
-- FUNÇÕES ÚTEIS
-- ============================================

-- Função: Buscar propostas mais visualizadas
CREATE OR REPLACE FUNCTION get_top_propostas(limit_count INT DEFAULT 10)
RETURNS TABLE (
    proposta_id UUID,
    numero_proposta VARCHAR,
    cliente_nome VARCHAR,
    total_views BIGINT
) 
LANGUAGE SQL
AS $$
    SELECT 
        p.id,
        p.numero_proposta,
        p.cliente_nome,
        COUNT(v.id) as total_views
    FROM propostas p
    LEFT JOIN visualizacoes v ON p.id = v.proposta_id
    GROUP BY p.id, p.numero_proposta, p.cliente_nome
    ORDER BY total_views DESC
    LIMIT limit_count;
$$;

-- ============================================
-- DADOS DE EXEMPLO (opcional - remova em produção)
-- ============================================

-- Inserir proposta de exemplo
INSERT INTO propostas (
    numero_proposta,
    cliente_nome,
    cliente_cpf_cnpj,
    cliente_endereco,
    cliente_cidade,
    cliente_telefone,
    dados_sistema,
    dados_payback,
    investimento
) VALUES (
    'EXEMPLO001/2024',
    'Cliente Exemplo',
    '123.456.789-00',
    'Rua Exemplo, 123',
    'Bauru - SP',
    '(14) 99999-9999',
    '{"num_modulos": 10, "potencia_kwp": "7.0", "investimento": 50000}'::jsonb,
    '[{"ano": 1, "amortizacao": -45000, "economia_mensal": 800}]'::jsonb,
    50000.00
);

-- ============================================
-- VERIFICAÇÃO
-- ============================================

-- Verificar se tudo foi criado corretamente
SELECT 
    'Tabelas criadas' as status,
    COUNT(*) as total
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('propostas', 'visualizacoes');

SELECT 
    'Índices criados' as status,
    COUNT(*) as total
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('propostas', 'visualizacoes');

-- ============================================
-- FIM DO SCRIPT
-- ============================================
