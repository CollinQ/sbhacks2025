-- Create users table
create table if not exists users (
    id uuid references auth.users on delete cascade primary key,
    email text unique,
    full_name text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create items table
create table if not exists items (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references users(id) on delete cascade not null,
    title text not null,
    description text,
    price decimal(10,2) not null,
    condition text not null,
    image_url text,
    status text default 'available' not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create conversations table
create table if not exists conversations (
    id uuid default gen_random_uuid() primary key,
    item_id uuid references items(id) on delete cascade not null,
    seller_id uuid references users(id) not null,
    potential_buyer_id uuid references users(id) not null,
    status text default 'pending' not null, -- pending, scheduled, completed, cancelled
    last_message_at timestamp with time zone default timezone('utc'::text, now()) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create RLS policies
alter table users enable row level security;
alter table items enable row level security;
alter table conversations enable row level security;

-- Users policies
create policy "Users can view their own profile"
    on users for select
    using (auth.uid() = id);

create policy "Users can update their own profile"
    on users for update
    using (auth.uid() = id);

-- Items policies
create policy "Anyone can view available items"
    on items for select
    using (status = 'available');

create policy "Users can create their own items"
    on items for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own items"
    on items for update
    using (auth.uid() = user_id);

-- Conversations policies
create policy "Users can view their own conversations"
    on conversations for select
    using (auth.uid() = seller_id or auth.uid() = potential_buyer_id);

create policy "Users can create conversations for available items"
    on conversations for insert
    with check (
        auth.uid() = potential_buyer_id and
        exists (
            select 1 from items
            where items.id = item_id
            and items.status = 'available'
        )
    );

create policy "Users can update their own conversations"
    on conversations for update
    using (auth.uid() = seller_id or auth.uid() = potential_buyer_id);

-- Create indexes for better performance
create index if not exists items_user_id_idx on items(user_id);
create index if not exists items_status_idx on items(status);
create index if not exists conversations_seller_id_idx on conversations(seller_id);
create index if not exists conversations_buyer_id_idx on conversations(potential_buyer_id);
create index if not exists conversations_item_id_idx on conversations(item_id);
create index if not exists conversations_status_idx on conversations(status);
create index if not exists conversations_last_message_idx on conversations(last_message_at);