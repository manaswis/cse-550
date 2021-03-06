from __future__ import print_function
import os
import sys
import requests
import traceback
import inspect
import pandas as pd
from flask import Flask, render_template, request, url_for, g
from db_functions import *

app = Flask(__name__)

@app.route("/initdb")
def init_db():
	print("Initializing database")

	with app.app_context():
		current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
		df = pd.read_csv(current_dir + '/static/labels.csv')
		entries = []
		for idx, row in df.iterrows():
			marked_label = row['marked_label']
			correct = row['correct']
			img_filename = row['img_filename']

			entries.append((img_filename, marked_label, correct))

		print(entries)
		query = "INSERT INTO ground_truth (filename, marked_label, correct) VALUES (?, ?, ?)"
		query_db(query, entries, executemany=True)

"""
Temporary method to fix data in the database
"""
@app.route("/temp")
def temp():
	print("Initializing database")

	pd.set_option('display.max_rows', 500)
	with app.app_context():
		responses = query_db('select * from response where username == ?',['mikey'])
		responses_df = pd.DataFrame(responses, columns=['r_id', 'img_id', 'q_id', 'answer', 'username'])
		# print(responses_df)

		count = 1
		img_id = 1
		for idx, row in responses_df.iterrows():
			responses_df.ix[idx, 'img_id'] = int(img_id)

			r_id = responses_df.ix[idx, 'r_id']

			print(r_id, '=', img_id)
			query = 'UPDATE response SET img_id=? where r_id=?'
			# query_db(query, [int(img_id), int(r_id)])

			if (count == 3):
				count = 1
				
				if(img_id == 10):
					img_id = 1
				else:
					img_id += 1
			else:
				count += 1
		
		print(responses_df)

@app.route("/<username>", methods=['GET', 'POST'])
def server(username='user1'):

	# Default filename
	filename = 'image0.jpeg'
	filepath = url_for('static', filename='images/' + filename)

	content = {
		"username": username,
		"errors": [],
		"filename": filename,
		"filepath": filepath,
		"image_no": 1
	}

	if request.method == "POST":
		try:

			current_image = content['filename'] = request.form['current_image']
			content['filepath'] = url_for('static', filename='images/' + content['filename'])
			if ('question1' in request.form and 
				'question2' in request.form and 
				'question3' in request.form):

				question1 = str(request.form['question1'])
				question2 = str(request.form['question2'])
				question3 = str(request.form['question3'])

				print("\nSubmitted Data\n")
				print("\tQuestion1: " + question1)
				print("\tQuestion2: " + question2)
				print("\tQuestion3: " + question3)
				print("\tCurrent: " + current_image)
				print("\n")

				# Get current image index
				current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
				file_list = sorted([filename for filename in os.listdir(current_dir + url_for('static', filename='images')) 
									if filename.startswith("image")])
				n_files = len(file_list)

				current_img_idx = ([i for i, x in enumerate(file_list) if x == current_image])[0]
				print("Curr Image Index: ", current_img_idx)

				image_id = current_img_idx + 1

				# Build a response
				user = str(username)
				qresponse = [(image_id, 1, question1, user), 
							(image_id, 2, question2, user), 
							(image_id, 3, question3, user)]
				
				# Store responses to the database
				query_db('insert into response (img_id, q_id,answer,username) values (?,?,?,?) ', qresponse, executemany=True)

				# Get next image to load
				if current_img_idx + 1 == n_files:
					print ("No files left")
					return render_template('thankyou.html', username=username)
				else:
					next_image_idx = current_img_idx + 1
					print("Next image index: ", next_image_idx)
					content["image_no"] = next_image_idx + 1
					content['filename'] = 'image' + str(next_image_idx) + '.jpeg'
					content['filepath'] = url_for('static', filename='images/' + content['filename'])

				print("Next Image: " + content['filename'])
			
			else:
				content['errors'].append("Some or all fields are empty!")

		except Exception as ex:
			content['errors'].append(ex.message)
			print(traceback.format_exc())
	
	# TODO: Get the metadata of the image from the database and populate content dict
	
	image_md = query_db('select marked_label from ground_truth where filename = ?',
				[content['filename']], one=True)
	content["original_label"] = image_md['marked_label']
	
	return render_template('tool.html', **content)

if __name__ == '__main__':
	app.run()