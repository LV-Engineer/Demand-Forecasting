CREATE TABLE train (
    id          INTEGER PRIMARY KEY,
    date        DATE NOT NULL,
    store_nbr   SMALLINT NOT NULL,
    family      TEXT NOT NULL,
    sales       DOUBLE PRECISION NOT NULL,
    onpromotion INTEGER NOT NULL
);

CREATE TABLE stores (
    store_nbr SMALLINT PRIMARY KEY,
    city      TEXT,
    state     TEXT,
    type      TEXT,
    cluster   SMALLINT
);

CREATE TABLE oil (
    date       DATE PRIMARY KEY,
    dcoilwtico DOUBLE PRECISION
);

CREATE TABLE holidays (
    date        DATE,
    type        TEXT,
    locale      TEXT,
    locale_name TEXT,
    description TEXT,
    transferred BOOLEAN
);

CREATE TABLE transactions (
    date         DATE,
    store_nbr    SMALLINT,
    transactions INTEGER,
    PRIMARY KEY (date, store_nbr)
);