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