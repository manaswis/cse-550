CREATE TABLE ground_truth (
  image_id integer PRIMARY KEY AUTOINCREMENT,
  filename text,
  label_type text
);

CREATE TABLE response (
  r_id integer PRIMARY KEY AUTOINCREMENT,
  q_id integer,
  answer text,
  username text
);

-- Sample Data
INSERT INTO ground_truth (filename, label_type)
VALUES ('test1.jpeg', 'Curb Ramp');

INSERT INTO ground_truth (filename, label_type)
VALUES ('test2.jpeg', 'Obstacle in Path');

