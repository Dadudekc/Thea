-- Prompt Management System Schema

-- Contexts table - Hierarchical context storage
CREATE TABLE IF NOT EXISTS contexts (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    type TEXT NOT NULL,  -- 'strategic', 'project', 'conversation', 'task'
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON for additional data
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    FOREIGN KEY (parent_id) REFERENCES contexts(id) ON DELETE SET NULL
);

-- Context relationships
CREATE TABLE IF NOT EXISTS context_relationships (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- 'depends_on', 'references', 'extends'
    strength FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_id, target_id, relationship_type),
    FOREIGN KEY (source_id) REFERENCES contexts(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES contexts(id) ON DELETE CASCADE
);

-- Prompt templates
CREATE TABLE IF NOT EXISTS prompt_templates (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    type TEXT NOT NULL,  -- 'meta', 'project', 'task', 'utility'
    name TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    variables TEXT,  -- JSON array of required variables
    metadata TEXT,  -- JSON for additional data
    version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    success_rate FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES prompt_templates(id) ON DELETE SET NULL
);

-- Template versions
CREATE TABLE IF NOT EXISTS template_versions (
    template_id TEXT NOT NULL,
    version TEXT NOT NULL,
    content TEXT NOT NULL,
    changes TEXT,  -- Description of changes
    performance_data TEXT,  -- JSON performance metrics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    is_active BOOLEAN DEFAULT true,
    PRIMARY KEY (template_id, version),
    FOREIGN KEY (template_id) REFERENCES prompt_templates(id) ON DELETE CASCADE
);

-- Prompt strategies
CREATE TABLE IF NOT EXISTS prompt_strategies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,  -- 'problem-solving', 'learning', 'creation', 'analysis'
    steps TEXT NOT NULL,  -- JSON array of strategy steps
    templates TEXT NOT NULL,  -- JSON array of template IDs
    context_requirements TEXT,  -- JSON specification of required context
    success_conditions TEXT,  -- JSON success criteria
    fallback_strategy_id TEXT,
    metadata TEXT,  -- JSON for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success_rate FLOAT DEFAULT 0.0,
    FOREIGN KEY (fallback_strategy_id) REFERENCES prompt_strategies(id) ON DELETE SET NULL
);

-- Conversation flows
CREATE TABLE IF NOT EXISTS conversation_flows (
    id TEXT PRIMARY KEY,
    strategy_id TEXT,
    initial_context_id TEXT,
    goal TEXT NOT NULL,
    state TEXT NOT NULL,  -- JSON current state
    history TEXT,  -- JSON conversation history
    metadata TEXT,  -- JSON for additional data
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    success_rate FLOAT,
    FOREIGN KEY (strategy_id) REFERENCES prompt_strategies(id) ON DELETE SET NULL,
    FOREIGN KEY (initial_context_id) REFERENCES contexts(id) ON DELETE SET NULL
);

-- Response analysis
CREATE TABLE IF NOT EXISTS response_analysis (
    id TEXT PRIMARY KEY,
    conversation_flow_id TEXT NOT NULL,
    prompt_template_id TEXT NOT NULL,
    response_text TEXT NOT NULL,
    analysis_results TEXT NOT NULL,  -- JSON analysis data
    quality_score FLOAT,
    relevance_score FLOAT,
    completeness_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_flow_id) REFERENCES conversation_flows(id) ON DELETE CASCADE,
    FOREIGN KEY (prompt_template_id) REFERENCES prompt_templates(id) ON DELETE CASCADE
);

-- Learning patterns
CREATE TABLE IF NOT EXISTS learning_patterns (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- 'success', 'failure', 'optimization'
    pattern_data TEXT NOT NULL,  -- JSON pattern description
    frequency INTEGER DEFAULT 1,
    impact_score FLOAT,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Pattern applications
CREATE TABLE IF NOT EXISTS pattern_applications (
    pattern_id TEXT NOT NULL,
    template_id TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success_score FLOAT,
    notes TEXT,
    PRIMARY KEY (pattern_id, template_id, strategy_id, applied_at),
    FOREIGN KEY (pattern_id) REFERENCES learning_patterns(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES prompt_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (strategy_id) REFERENCES prompt_strategies(id) ON DELETE CASCADE
);

-- Performance metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,  -- 'template', 'strategy', 'flow'
    entity_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'success_rate', 'response_time', 'token_usage'
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(type);
CREATE INDEX IF NOT EXISTS idx_contexts_relevance ON contexts(relevance_score);
CREATE INDEX IF NOT EXISTS idx_templates_type ON prompt_templates(type);
CREATE INDEX IF NOT EXISTS idx_templates_success ON prompt_templates(success_rate);
CREATE INDEX IF NOT EXISTS idx_strategies_type ON prompt_strategies(type);
CREATE INDEX IF NOT EXISTS idx_strategies_success ON prompt_strategies(success_rate);
CREATE INDEX IF NOT EXISTS idx_flows_strategy ON conversation_flows(strategy_id);
CREATE INDEX IF NOT EXISTS idx_analysis_flow ON response_analysis(conversation_flow_id);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON learning_patterns(type);
CREATE INDEX IF NOT EXISTS idx_metrics_entity ON performance_metrics(entity_type, entity_id);

-- Create views
CREATE VIEW IF NOT EXISTS v_active_contexts AS
SELECT c.*, 
       (SELECT COUNT(*) FROM contexts sub WHERE sub.parent_id = c.id) as child_count
FROM contexts c
WHERE c.is_active = true;

CREATE VIEW IF NOT EXISTS v_template_performance AS
SELECT t.id, t.name, t.type,
       t.success_rate,
       t.usage_count,
       COUNT(DISTINCT tv.version) as version_count,
       MAX(tv.created_at) as last_updated
FROM prompt_templates t
LEFT JOIN template_versions tv ON t.id = tv.template_id
WHERE t.is_active = true
GROUP BY t.id;

CREATE VIEW IF NOT EXISTS v_strategy_performance AS
SELECT s.id, s.name, s.type,
       s.success_rate,
       COUNT(DISTINCT cf.id) as flow_count,
       AVG(cf.success_rate) as avg_flow_success
FROM prompt_strategies s
LEFT JOIN conversation_flows cf ON s.id = cf.strategy_id
GROUP BY s.id;

-- Insert default strategies
INSERT OR IGNORE INTO prompt_strategies (id, name, description, type, steps, templates, context_requirements, success_conditions) VALUES
('problem_solving_basic', 'Basic Problem Solving',
'Standard approach for solving programming problems',
'problem-solving',
'[
    {"step": "understand", "description": "Understand the problem fully"},
    {"step": "plan", "description": "Plan the solution approach"},
    {"step": "implement", "description": "Implement the solution"},
    {"step": "verify", "description": "Verify and test the solution"}
]',
'["clarification_template", "planning_template", "implementation_template", "verification_template"]',
'{"required": ["problem_description", "constraints", "examples"]}',
'{"must_have": ["working_solution", "test_cases", "documentation"]}'),

('learning_systematic', 'Systematic Learning',
'Structured approach for learning new technologies',
'learning',
'[
    {"step": "overview", "description": "Get a high-level overview"},
    {"step": "fundamentals", "description": "Learn core concepts"},
    {"step": "practice", "description": "Hands-on practice"},
    {"step": "advanced", "description": "Explore advanced topics"}
]',
'["overview_template", "concept_template", "practice_template", "advanced_template"]',
'{"required": ["learning_goal", "current_knowledge", "time_available"]}',
'{"must_have": ["concept_understanding", "practical_experience", "advanced_exposure"]}');