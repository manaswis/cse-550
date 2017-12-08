CREATE TABLE ground_truth (
  image_id integer PRIMARY KEY AUTOINCREMENT,
  filename text,
  marked_label text,
  correct text
);

CREATE TABLE response (
  r_id integer PRIMARY KEY AUTOINCREMENT,
  img_id integer,
  q_id integer,
  answer text,
  username text
);


-- To copy data from one table to another
-- INSERT INTO response (q_id, answer , username) SELECT q_id, answer , username FROM response_old;
