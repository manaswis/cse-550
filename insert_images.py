import os
import pandas as pd

"""
# Generate the csv for the selected iamges
df = pd.read_csv("static/filtered_labels.csv")
file_list = sorted(os.listdir('static/selected_images'))

df = df[df['img_filename'].isin(file_list)]
print df
df.to_csv("static/final_labels.csv",index=False)
"""

df = pd.read_csv("static/labels.csv")
print(df)

# Rename the image name to be of the form "image<index>.jpeg"
for idx, row in df.iterrows():
	old_img_filename = row['img_filename']
	new_img_filename = 'image' + str(idx) + '.jpeg'

	# Rename the file in the folder
	os.rename("static/images/" + old_img_filename, "static/images/" + new_img_filename)
	df.ix[idx, 'img_filename'] = new_img_filename

print(df)
df.to_csv("static/labels.csv",index=False)
