CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE SCHEMA crypto_counter;
CREATE TABLE IF NOT EXISTS crypto_counter.cc_current_price (
    id          uuid PRIMARY KEY DEFAULT uuid_generate_v1(),
    currency    varchar(10) NOT NULL,
    price       numeric NOT NULL,
   	created_at 	timestamp DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crypto_counter.cc_wallet_balance (
    id          uuid PRIMARY KEY DEFAULT uuid_generate_v1(),
    balance     money NOT NULL,
   	created_at 	timestamp DEFAULT NOW()
);