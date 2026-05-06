create table if not exists brand_config (
  id                  text primary key default 'main',
  name                text not null,
  handle              text not null,
  audience            text not null,
  voice_brief         text not null,
  strategy_brief      text not null,
  content_territories text[] not null default '{}',
  post_max_chars      int not null default 280,
  formats             jsonb not null default '[]',
  updated_at          timestamptz not null default now()
);
