-- Digital Dreamscape - Memory Nexus Schema
-- The sacred runes that bind the Memory Core

-- Conversations table - The main chronicles
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    source TEXT DEFAULT 'chatgpt',
    status TEXT DEFAULT 'active',
    conversation_metadata TEXT, -- JSON for additional data (renamed from metadata)
    tags TEXT -- JSON array of tag IDs
);

-- Messages table - The individual scrolls within each chronicle
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_index INTEGER NOT NULL, -- Order within conversation
    word_count INTEGER DEFAULT 0,
    token_estimate INTEGER DEFAULT 0,
    message_metadata TEXT, -- JSON for additional data (renamed from metadata)
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Tags table - The classification runes
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#007bff',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- Conversation-Tags junction table - The binding runes
CREATE TABLE IF NOT EXISTS conversation_tags (
    conversation_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (conversation_id, tag_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Analysis results table - The insight crystals
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    analysis_type TEXT NOT NULL, -- 'summary', 'sentiment', 'topics', 'custom'
    result_data TEXT NOT NULL, -- JSON result
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    template_used TEXT, -- Which template was used
    processing_time REAL, -- Time taken in seconds
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Templates table - The Jinja Forge artifacts
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    template_content TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- Settings table - The configuration scrolls
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task tracking system tables
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL,  -- LOW, MEDIUM, HIGH, CRITICAL
    status TEXT NOT NULL,    -- TODO, IN_PROGRESS, BLOCKED, COMPLETED, ARCHIVED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    parent_task_id TEXT,
    quest_id TEXT,           -- Link to MMORPG quest
    xp_reward INTEGER DEFAULT 0,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (quest_id) REFERENCES dreamscape_quests(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (task_id, tag),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_skill_rewards (
    task_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    points INTEGER NOT NULL,
    PRIMARY KEY (task_id, skill_name),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    field_name TEXT NOT NULL,  -- Which field was changed
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    default_tags TEXT,        -- Comma-separated tags
    default_skill_rewards TEXT,-- JSON string of skill:points pairs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    PRIMARY KEY (task_id, depends_on_task_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_metadata (
    task_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (task_id, key),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Create indexes for performance - The speed runes
CREATE INDEX IF NOT EXISTS idx_conversations_url ON conversations(url);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_source ON conversations(source);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_analysis_conversation_id ON analysis_results(conversation_id);
CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);

-- Insert default templates - The foundation artifacts
INSERT OR IGNORE INTO templates (name, description, template_content, category, is_default) VALUES
('Basic Summary', 'Generate a basic summary of the conversation', 
'Please provide a concise summary of this conversation, highlighting the key points and main takeaways.

Conversation Title: {{ conversation.title }}
Message Count: {{ conversation.message_count }}', 'summary', 1),

('Topic Analysis', 'Extract main topics and themes from the conversation',
'Analyze this conversation and identify the main topics, themes, and key concepts discussed.

Conversation Title: {{ conversation.title }}
Please provide:
1. Main topics (3-5 key areas)
2. Important themes
3. Key insights or conclusions', 'analysis', 1),

('Action Items', 'Extract action items and next steps from the conversation',
'Review this conversation and identify any action items, tasks, or next steps mentioned.

Conversation Title: {{ conversation.title }}
Please list:
1. Action items with assignees (if mentioned)
2. Deadlines or timeframes
3. Dependencies or blockers
4. Priority levels', 'actions', 1);

-- Insert default settings - The configuration foundation
INSERT OR IGNORE INTO settings (key, value, description) VALUES
('database_version', '1.0', 'Current database schema version'),
('max_conversations', '10000', 'Maximum number of conversations to store'),
('auto_analyze', 'false', 'Automatically analyze new conversations'),
('default_template', '1', 'Default template ID for new analyses'),
('backup_enabled', 'true', 'Enable automatic database backups'),
('backup_interval_hours', '24', 'Hours between automatic backups');

-- Insert task-related settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
('task_auto_archive_days', '30', 'Days after completion before tasks are archived'),
('task_default_template', 'basic_task', 'Default task template ID'),
('task_xp_multiplier', '1.0', 'Multiplier for task XP rewards'),
('task_skill_multiplier', '1.0', 'Multiplier for task skill rewards'),
('task_notifications_enabled', 'true', 'Enable task notifications'),
('task_daily_summary_time', '09:00', 'Time to send daily task summary');

-- Insert default task templates
INSERT OR IGNORE INTO task_templates (id, name, description, category, priority, default_tags, default_skill_rewards) VALUES
('bug_hunt', 'Bug Hunt Quest', 
'Track down and eliminate bugs in the system', 
'debugging', 'HIGH',
'bug,fix,debug',
'{"Execution Velocity": 3, "System Convergence": 1}'),

('feature_raid', 'Feature Raid Mission',
'Implement new features and capabilities',
'development', 'MEDIUM',
'feature,implement,develop',
'{"System Convergence": 3, "Strategic Intelligence": 1}'),

('system_quest', 'System Convergence Quest',
'Design and integrate system components',
'architecture', 'HIGH',
'system,architecture,design',
'{"System Convergence": 4, "Strategic Intelligence": 2}'),

('knowledge_quest', 'Knowledge Expedition',
'Research and learn new technologies',
'learning', 'MEDIUM',
'research,learn,explore',
'{"Strategic Intelligence": 3, "Domain Stabilization": 1}'),

('workflow_quest', 'Workflow Optimization',
'Improve and optimize development workflows',
'optimization', 'MEDIUM',
'workflow,optimize,improve',
'{"Execution Velocity": 2, "Domain Stabilization": 2}');

-- Create trigger to update conversation metadata when messages change
CREATE TRIGGER IF NOT EXISTS update_conversation_metadata
AFTER INSERT ON messages
BEGIN
    UPDATE conversations 
    SET message_count = (
        SELECT COUNT(*) FROM messages WHERE conversation_id = NEW.conversation_id
    ),
    word_count = (
        SELECT COALESCE(SUM(word_count), 0) FROM messages WHERE conversation_id = NEW.conversation_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
END;

-- Create trigger to update tag usage count
CREATE TRIGGER IF NOT EXISTS update_tag_usage_count
AFTER INSERT ON conversation_tags
BEGIN
    UPDATE tags 
    SET usage_count = (
        SELECT COUNT(*) FROM conversation_tags WHERE tag_id = NEW.tag_id
    )
    WHERE id = NEW.tag_id;
END;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_quest ON tasks(quest_id);
CREATE INDEX IF NOT EXISTS idx_task_history_task ON task_history(task_id);
CREATE INDEX IF NOT EXISTS idx_templates_category ON task_templates(category);

-- Views for common queries
CREATE VIEW IF NOT EXISTS v_active_tasks AS
SELECT t.*, GROUP_CONCAT(tt.tag) as tags
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
WHERE t.status IN ('TODO', 'IN_PROGRESS')
GROUP BY t.id;

CREATE VIEW IF NOT EXISTS v_overdue_tasks AS
SELECT t.*, GROUP_CONCAT(tt.tag) as tags
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
WHERE t.due_date < CURRENT_TIMESTAMP
AND t.status NOT IN ('COMPLETED', 'ARCHIVED')
GROUP BY t.id;

CREATE VIEW IF NOT EXISTS v_task_full_details AS
SELECT 
    t.*,
    GROUP_CONCAT(DISTINCT tt.tag) as tags,
    GROUP_CONCAT(DISTINCT tsr.skill_name || ':' || tsr.points) as skill_rewards,
    GROUP_CONCAT(DISTINCT td.depends_on_task_id) as dependencies,
    COUNT(DISTINCT tc.id) as subtask_count,
    SUM(CASE WHEN tc.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_subtasks
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN task_skill_rewards tsr ON t.id = tsr.task_id
LEFT JOIN task_dependencies td ON t.id = td.task_id
LEFT JOIN tasks tc ON t.id = tc.parent_task_id
GROUP BY t.id;

-- Create trigger to update task metadata on status change
CREATE TRIGGER IF NOT EXISTS update_task_history_on_status
AFTER UPDATE OF status ON tasks
BEGIN
    INSERT INTO task_history (task_id, field_name, old_value, new_value)
    VALUES (OLD.id, 'status', OLD.status, NEW.status);
END;

-- Create trigger to update task metadata on priority change
CREATE TRIGGER IF NOT EXISTS update_task_history_on_priority
AFTER UPDATE OF priority ON tasks
BEGIN
    INSERT INTO task_history (task_id, field_name, old_value, new_value)
    VALUES (OLD.id, 'priority', OLD.priority, NEW.priority);
END;

-- Create trigger to update parent task completion status
CREATE TRIGGER IF NOT EXISTS update_parent_task_status
AFTER UPDATE OF status ON tasks
WHEN NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED'
BEGIN
    UPDATE tasks
    SET status = CASE
        WHEN NOT EXISTS (
            SELECT 1 FROM tasks sub
            WHERE sub.parent_task_id = NEW.parent_task_id
            AND sub.status != 'COMPLETED'
        ) THEN 'COMPLETED'
        ELSE status
    END
    WHERE id = NEW.parent_task_id;
END; 