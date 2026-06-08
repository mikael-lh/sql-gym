CREATE TABLE times_archive (
    article_id TEXT PRIMARY KEY,
    uri TEXT,
    pub_date DATE,
    section_name TEXT,
    news_desk TEXT,
    type_of_material TEXT,
    document_type TEXT,
    word_count INTEGER,
    web_url TEXT,
    headline_main TEXT,
    byline_original TEXT,
    abstract TEXT,
    snippet TEXT,
    keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    byline_person JSONB NOT NULL DEFAULT '[]'::jsonb,
    multimedia_count_by_type JSONB
);

CREATE INDEX times_archive_pub_date_idx ON times_archive (pub_date);
CREATE INDEX times_archive_section_name_idx ON times_archive (section_name);
CREATE INDEX times_archive_news_desk_idx ON times_archive (news_desk);
