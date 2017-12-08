CREATE TABLE ground_truth (
  image_id integer PRIMARY KEY AUTOINCREMENT,
  filename text,
  marked_label text,
  correct text
);

CREATE TABLE response (
  r_id integer PRIMARY KEY AUTOINCREMENT,
  q_id integer,
  answer text,
  username text
);
