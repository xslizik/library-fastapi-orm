CREATE TYPE "card_status" AS ENUM (
  'active',
  'deactivated',
  'suspended'
);

CREATE TYPE "publication_format" AS ENUM (
  'book',
  'magazine',
  'e_book'
);

CREATE TYPE "language" AS ENUM (
  'Slovak',
  'English',
  'Czech'
);

CREATE TYPE "publication_status" AS ENUM (
  'offline',
  'lost',
  'online'
);

CREATE TYPE "publication_category" AS ENUM (
  'science',
  'history',
  'science_fiction',
  'fantasy',
  'horror'
);

CREATE TYPE "tag_type" AS ENUM (
  'most_popular_adult',
  'most_popular_children',
  'newest'
);

CREATE TYPE "penalty_type" AS ENUM (
  'late_return',
  'damaged_publication',
  'lost_publication'
);

CREATE TYPE "sentiment" AS ENUM (
  'read',
  'want_to_read',
  'stalled'
);

CREATE TYPE "borrow_status" AS ENUM (
  'returned',
  'borrowed',
  'lost'
);

CREATE TYPE "reservation_status" AS ENUM (
  'claimed',
  'unclaimed',
  'rejected'
);

CREATE TABLE "users" (
  "user_id" varchar(11) UNIQUE PRIMARY KEY NOT NULL,
  "name" varchar(64) NOT NULL,
  "mail" varchar(32) NOT NULL,
  "password" varchar(32) NOT NULL,
  "register_date" date NOT NULL,
  "parent_user_id" varchar(11)
);

CREATE TABLE "user_cards" (
  "card_id" int PRIMARY KEY NOT NULL,
  "user_id" varchar(11) NOT NULL,
  "card_status" card_status NOT NULL
);

CREATE TABLE "publications" (
  "publication_id" int UNIQUE PRIMARY KEY NOT NULL,
  "isbn" varchar(13) UNIQUE NOT NULL,
  "title" varchar(64) NOT NULL,
  "publication_format" publication_format NOT NULL,
  "language" language NOT NULL,
  "release_date" date NOT NULL
);

CREATE TABLE "specific_publications" (
  "specific_publication_id" int PRIMARY KEY NOT NULL,
  "publication_id" int NOT NULL,
  "publication_status" publication_status NOT NULL
);

CREATE TABLE "publication_tags" (
  "tag_id" int NOT NULL,
  "publication_id" int NOT NULL
);

CREATE TABLE "tags" (
  "tag_id" int PRIMARY KEY NOT NULL,
  "tag_type" tag_type UNIQUE NOT NULL
);

CREATE TABLE "publication_authors" (
  "author_id" int NOT NULL,
  "publication_id" int NOT NULL
);

CREATE TABLE "authors" (
  "author_id" int UNIQUE PRIMARY KEY NOT NULL,
  "name" varchar(64) NOT NULL,
  "birth_date" date NOT NULL
);

CREATE TABLE "publication_categories" (
  "category_id" int NOT NULL,
  "publication_id" int NOT NULL
);

CREATE TABLE "categories" (
  "category_id" int PRIMARY KEY NOT NULL,
  "publication_category" UNIQUE publication_category NOT NULL
);

CREATE TABLE "borrowed_publications" (
  "borrowed_publication_id" int PRIMARY KEY NOT NULL,
  "specific_publication_id" int NOT NULL,
  "user_id" varchar(11) NOT NULL,
  "from_date" date NOT NULL,
  "to_date" date NOT NULL,
  "borrow_status" borrow_status NOT NULL
);

CREATE TABLE "penalties" (
  "penalty_id" int PRIMARY KEY NOT NULL,
  "borrowed_publication_id" int NOT NULL,
  "penalty_type" penalty_type NOT NULL,
  "payed_out" boolean NOT NULL,
  "issued_date" date NOT NULL,
  "price" decimal(8,2) NOT NULL
);

CREATE TABLE "reminders" (
  "reminder_id" int PRIMARY KEY NOT NULL,
  "borrowed_publication_id" int NOT NULL,
  "reminder_date" date NOT NULL
);

CREATE TABLE "extensions" (
  "extension_id" int PRIMARY KEY NOT NULL,
  "borrowed_publication_id" int NOT NULL,
  "extension_date" date NOT NULL,
  "approved" boolean NOT NULL
);

CREATE TABLE "reservations" (
  "reservation_id" int PRIMARY KEY NOT NULL,
  "user_id" varchar(11) NOT NULL,
  "specific_publication_id" int NOT NULL,
  "reservation_date" date NOT NULL,
  "reservation_expiration_date" date NOT NULL,
  "reservation_status" reservation_status NOT NULL
);

CREATE TABLE "favorites" (
  "user_id" varchar(11) NOT NULL,
  "publication_id" int NOT NULL,
  "sentiment" sentiment NOT NULL
);

CREATE TABLE "ratings" (
  "rating_id" int PRIMARY KEY NOT NULL,
  "user_id" varchar(11) NOT NULL,
  "publication_id" int NOT NULL
);

CREATE TABLE "reviews" (
  "rating_id" int NOT NULL,
  "review" text NOT NULL,
  "created_at" date NOT NULL
);

CREATE TABLE "comments" (
  "comment_id" int PRIMARY KEY NOT NULL,
  "rating_id" int NOT NULL,
  "comment" text NOT NULL,
  "created_at" date NOT NULL
);

CREATE TABLE "stars" (
  "rating_id" int NOT NULL,
  "star_rating" smallint NOT NULL,
  "created_at" date NOT NULL
);

ALTER TABLE "users" ADD FOREIGN KEY ("parent_user_id") REFERENCES "users" ("user_id");

ALTER TABLE "user_cards" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");

ALTER TABLE "specific_publications" ADD FOREIGN KEY ("publication_id") REFERENCES "publications" ("publication_id");

ALTER TABLE "publication_tags" ADD FOREIGN KEY ("tag_id") REFERENCES "tags" ("tag_id");

ALTER TABLE "publication_tags" ADD FOREIGN KEY ("publication_id") REFERENCES "publications" ("publication_id");

ALTER TABLE "publication_authors" ADD FOREIGN KEY ("author_id") REFERENCES "authors" ("author_id");

ALTER TABLE "publication_authors" ADD FOREIGN KEY ("publication_id") REFERENCES "publications" ("publication_id");

ALTER TABLE "publication_categories" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("category_id");

ALTER TABLE "publication_categories" ADD FOREIGN KEY ("publication_id") REFERENCES "publications" ("publication_id");

ALTER TABLE "borrowed_publications" ADD FOREIGN KEY ("specific_publication_id") REFERENCES "specific_publications" ("specific_publication_id");

ALTER TABLE "borrowed_publications" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");

ALTER TABLE "penalties" ADD FOREIGN KEY ("borrowed_publication_id") REFERENCES "borrowed_publications" ("borrowed_publication_id");

ALTER TABLE "reminders" ADD FOREIGN KEY ("borrowed_publication_id") REFERENCES "borrowed_publications" ("borrowed_publication_id");

ALTER TABLE "extensions" ADD FOREIGN KEY ("borrowed_publication_id") REFERENCES "borrowed_publications" ("borrowed_publication_id");

ALTER TABLE "reservations" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");

ALTER TABLE "reservations" ADD FOREIGN KEY ("specific_publication_id") REFERENCES "specific_publications" ("specific_publication_id");

ALTER TABLE "favorites" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");

ALTER TABLE "favorites" ADD FOREIGN KEY ("publication_id") REFERENCES "publications" ("publication_id");

ALTER TABLE "ratings" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");

ALTER TABLE "ratings" ADD FOREIGN KEY ("publication_id") REFERENCES "publications" ("publication_id");

ALTER TABLE "reviews" ADD FOREIGN KEY ("rating_id") REFERENCES "ratings" ("rating_id");

ALTER TABLE "comments" ADD FOREIGN KEY ("rating_id") REFERENCES "ratings" ("rating_id");

ALTER TABLE "stars" ADD FOREIGN KEY ("rating_id") REFERENCES "ratings" ("rating_id");
