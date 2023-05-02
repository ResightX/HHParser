CREATE TABLE COMPANY(
    id integer primary key autoincrement,
    name text not null,
    has_awards boolean default(false),
    is_verified boolean default(false),
    is_accredited boolean default(false),
    rating decimal,
    review_count integer
);

CREATE TABLE VACANCY(
    id integer primary key autoincrement,
    title text not null,
    wage integer,
    company_id integer references COMPANY(id)
);