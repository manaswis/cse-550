from __future__ import print_function
import os
import sys
import requests
import traceback
import inspect
from flask import Flask, render_template, request, url_for


app = Flask(__name__)

@app.route("/<username>", methods=['GET', 'POST'])
def server(username='user1'):

	# Default filename
	filename = 'test1.jpeg'
	filepath = url_for('static', filename='images/' + filename)

	content = {
		"username": username,
		"errors": [],
		"filename": filename,
		"filepath": filepath
	}
	errors = []
	
	if request.method == "POST":
		try:

			current_image = content['filename'] = request.form['current_image']
			content['filepath'] = url_for('static', filename='images/' + content['filename'])
			if ('question1' in request.form and 
				'question2' in request.form and 
				'question3' in request.form):

				question1 = request.form['question1']
				question2 = request.form['question2']
				question3 = request.form['question3']
				
				current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

				# Get next image to load if data submitted is fine
				file_list = sorted(os.listdir(current_dir + url_for('static', filename='images')))

				n_files = len(file_list)

				current_img_idx = ([i for i, x in enumerate(file_list) if x == current_image])[0]
				print("Curr Image Index: ", current_img_idx)

				if (current_img_idx + 1) >= n_files:
					print ("No files left")
					return render_template('thankyou.html', username=username)
				else:
					next_image_idx = current_img_idx + 2
					print("Next image index: ", next_image_idx)
					content['filename'] = 'test' + str(next_image_idx) + '.jpeg'
					content['filepath'] = url_for('static', filename='images/' + content['filename'])


				print("Question1: " + question1)
				print("Question2: " + question2)
				print("Question3: " + question3)
				print("Current: " + current_image)
				print("Next: " + content['filename'])
			
			else:
				content['errors'].append("Some or all fields are empty!")

		except Exception as ex:
			content['errors'].append(ex.message)
			print(traceback.format_exc())
	
	# TODO: Get the metadata of the image from the database and populate content dict
	content["original_label"] = "Curb Ramp"
	
	return render_template('tool.html', **content)

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':

	if (len(sys.argv) > 1):
		if sys.argv[1] == "initdb":
			print("Initializing database")
			sys.exit(0)
			# init_db()
	else:
		app.run()