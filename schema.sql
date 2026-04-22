DROP TABLE venues;
CREATE TABLE venues (
-- CREATE TABLE IF NOT EXISTS venues (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name     TEXT    NOT NULL,
    location       TEXT    NOT NULL,
    num_tables     INTEGER NOT NULL DEFAULT 1,
    price_per_game TEXT    NOT NULL,
    bathroom_type  TEXT    NOT NULL,
    rating         INTEGER NOT NULL DEFAULT 1 CHECK(rating BETWEEN 0 AND 5),
    notes          TEXT,
    photo_URL      TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    1,
    'The Mule Bar',
    'Portland, OR',
    1,
    '$0.50',
    'Gendered',
    3,
    'ATM and Bar for quarters. No hand chalk. Good lighting. Table is level.',
    -- 'img/mulebar.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    2,
    'Bare Bones',
    'Portland, OR',
    1,
    '$0.75',
    'Gender-Neutral',
    3,
    'Sticks and felt in moderate condition. Has hand chalk. ATM & quarter machine.',
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    3,
    'Belmont Inn',
    'Portland, OR',
    2,
    '$0.50',
    'Gendered',
    4,
    'Free days Sun-Tuesday. Sticks and felt in great condition. Has hand chalk. Great lighting. ATM & Quarter machine.',
    'img/belmontinn.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    4,
    'Ship Ahoy Tavern',
    'Portland, OR',
    1,
    '$0.50',
    'Gendered',
    2,
    'Free Day Sunday. Sticks and felt in poor condition. Decent lighting. Hand chalk. ATM.',
    'img/shipahoy.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    5,
    'Reel M Inn',
    'Portland, OR',
    1,
    '$0.00',
    'Gendered',
    2,
    'Sticks in great condition. Felt in mid-condition. Hand chalk. Decent lighting. Individual bathroom stalls.',
    'img/reelminn.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    6,
    'Clinton Street Pub',
    'Portland, OR',
    1,
    '$0.25',
    'Gendered',
    3,
    'Sticks and felt in great condition. Hand chalk. No pool light. Individual bathroom stalls. ATM & Quarter machine',
    -- 'img/clintonstreetpub.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    7,
    'Hungry Tiger',
    'Portland, OR',
    1,
    '$1.00',
    'Gender-Neutral',
    2,
    'No hand chalk. Centered pool light. ATM.',
    -- 'img/hungrytiger.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    8,
    'Clubhouse Bar & Grill',
    'Portland, OR',
    1,
    '$0.75',
    'Gendered',
    2,
    'Individual stalls. Stick and felt in good condition. No hand chalk. Centered great lighting. ATM. Very straight sports bar vibes.',
    -- 'img/clubhouse.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    9,
    'Dublin Pub',
    'Beaverton, OR',
    3,
    '$0.00',
    'Gendered',
    0,
    'Stick and felt in awful condition. No hand chalk. Centered mediocre lighting. ATM. Gross bathrooms.',
    -- 'img/dublinpub.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    10,
    'LaVernes',
    'Portland, OR',
    1,
    '$0.75',
    'Gender-Neutral',
    4,
    'Sticks and felt in great condition. No hand chalk. ATM.',
    -- 'img/lavernes.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    11,
    'Crow Bar',
    'Portland, OR',
    1,
    '$1.00',
    'Gender-Neutral',
    3,
    'Sticks and felt in great condition. No hand chalk. Centered good lighting.',
    -- 'img/crowbar.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    11,
    'Slingshot Lounge',
    'Portland, OR',
    2,
    '$1.00',
    'Gender-Neutral',
    3,
    'Sticks and felt in decent condition. No hand chalk. Centered good lighting. ATM & quarter machine.',
    -- 'img/slingshot.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    12,
    'Thunderbird',
    'Portland, OR',
    1,
    '$0.00',
    'Gender-Neutral',
    0,
    'Sticks and felt in awful condition. Missing a ball. hand chalk. Centered poor lighting.',
    -- 'img/thunderbird.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    13,
    'Bear Paw Inn',
    'Portland, OR',
    2,
    'By the Hour',
    'Gendered',
    3,
    'Sticks and felt in decent condition. hand chalk. Centered good lighting. ATM & quarter machine.',
    -- 'img/bearpaw.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    14,
    'Roadside Attraction',
    'Portland, OR',
    1,
    '$0.00',
    'Gendered',
    1,
    'Individual stalls. stick and felt in poor condition. Hand chalk. centered decent lighting. ATM.',
    -- 'img/roadside.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    15,
    'Joes Cellar',
    'Portland, OR',
    3,
    '$0.00',
    'Gendered',
    3,
    'Stick and felt in good condition. Hand chalk. centered good lighting. ATM & quarter machine.',
    -- 'img/joes.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    16,
    'Panther Club PDX',
    'Portland, OR',
    2,
    '$0.75',
    'Gender-Neutral',
    4,
    'Stick and felt in great condition. no hand chalk. table is level. ATM & quarters at bar.',
    -- 'img/pantherclub.png'
    'img/barebones.png'
);

INSERT OR IGNORE INTO venues (id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url)
VALUES (
    17,
    'Sit Tite',
    'Portland, OR',
    1,
    '$1.00',
    'Gender-Neutral',
    4,
    'Sticks & felt great condition. No hand chalk. Great lighting. Table is level. ATM & Quarter machine.',
    -- 'img/sittite.png'
    'img/barebones.png'
);