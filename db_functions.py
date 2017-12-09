
import sqlite3
from flask import g
from flask import Flask

app = Flask(__name__)
DATABASE = 'cse550proj.db'

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
	db.row_factory = sqlite3.Row
	return db

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def query_db(query, args=(), one=False, executemany=False):
	cur = ''
	if (executemany):
		cur = get_db().executemany(query, args)
	else:
		cur = get_db().execute(query, args)
	get_db().commit()
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()