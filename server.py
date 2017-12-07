from __future__ import print_function
import os
import sys
import requests
import traceback
import inspect
from flask import Flask, render_template, request, url_for


app = Flask(__name__)

@app.route("/<name>", methods=['GET', 'POST'])
def server(name='user1'):

	errors = []

	# Default filename
	filename = 'test1.jpeg'
	filepath = url_for('static', filename='images/' + filename)

	if request.method == "POST":
		try:

			question1 = request.form['question1']
			question2 = request.form['question2']
			question3 = request.form['question3']
			current_image = request.form['current_image']
			
			current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

			# Get next image to load if data submitted is fine
			file_list = sorted(os.listdir(current_dir + url_for('static', filename='images')))

			n_files = len(file_list)

			current_img_idx = ([i for i, x in enumerate(file_list) if x == current_image])[0]
			print("Curr Image Index: ", current_img_idx)

			if (current_img_idx + 1) >= n_files:
				print ("No files left")
				# Render thank you html
			else:
				next_image_idx = current_img_idx + 2
				print("Next image index: ", next_image_idx)
				filename = 'test' + str(next_image_idx) + '.jpeg'
				filepath = url_for('static', filename='images/' + filename)


			print("Question1: " + question1)
			print("Question2: " + question2)
			print("Question3: " + question3)
			print("Current: " + current_image)
			print("Next: " + filename)


		except Exception as ex:
			errors.append(ex.message)
			print(traceback.format_exc())
	
	# Get list of images from the folder and the associated metadata from the database
	

	if len(errors) > 0:
		print("Errors: ", len(errors))
		return render_template('tool.html', name=name, filename=filename, filepath=filepath,
		 errors=errors)
	else:
		return render_template('tool.html', name=name, filename=filename, filepath=filepath)

if __name__ == '__main__':
	app.run()