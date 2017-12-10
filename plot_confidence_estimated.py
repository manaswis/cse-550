"""
Plots demonstrating suprisingly popular method
by analyzing the question where majority vote failed
"""

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('ggplot')

# Sub Plots
# fig, axes = plt.subplots(nrows=1, ncols=2)

# Get input files
response_df = pd.read_csv('response.csv')
gt_df = pd.read_csv('ground_truth.csv')

response_df = response_df[response_df['username'] != 'manaswi']

# Get number of votes
r_df = response_df[ (response_df.q_id == 1) & (response_df.img_id == 7) ]
counts = r_df['answer'].value_counts()

if 'yes' in counts: 
	yes_count = counts['yes']
else: 
	yes_count = 0

if 'no' in counts: 
	no_count = counts['no'] 
else: 
	no_count = 0

# Sub-plot 1
n_votes_df = pd.DataFrame([(yes_count, no_count)], columns=['Yes', 'No'])
t_votes_df = n_votes_df.transpose()
# t_votes_df.plot.barh(legend=False)
# plt.xlabel('Votes')
# plt.show()


image_id = '10'
# Get the confidence of respondents who answered yes and no respectively
r_df = response_df[response_df.img_id == int(image_id)]

u_yes_per = []
u_no_per = []
e_yes_per = []
e_no_per = []
for rrow in r_df.groupby('username'):

	df = rrow[1]
	answer = df.ix[df.index[0]]['answer']
	user_confidence = int(df.ix[df.index[1]]['answer'])
	estimated_yes = int(df.ix[df.index[2]]['answer'])

	if (answer == 'yes'):
		u_yes_per.append(user_confidence)
		e_yes_per.append(estimated_yes)
	else:
		u_no_per.append(user_confidence)
		e_no_per.append(estimated_yes)

# u_yes_plot_df = pd.DataFrame({'confidence': u_yes_per}, columns=['confidence'])
# u_no_plot_df = pd.DataFrame({'confidence': u_no_per}, columns=['confidence'])

# e_yes_plot_df = pd.DataFrame({'estimated': e_yes_per}, columns=['estimated'])
# e_no_plot_df = pd.DataFrame({'estimated': e_no_per}, columns=['estimated'])

# Sub-plot 2
# fig, axes = plt.subplots(1,2, sharex=True)
# axes[0,0].hist(u_no_per)
# axes[1,0].hist(u_yes_per)

# plt.hist(u_yes_per)
# plt.xlabel('Confidence %')
# plt.xlim((50,100))

for name in ['Yes', 'No']:
	if name == 'Yes':
		plt.hist(u_yes_per)
	else:
		plt.hist(u_no_per)
	plt.xlabel('Confidence ' + name + '%')
	plt.xlim((50,100))
	plt.savefig('analysis/' + image_id + '_' + name + '_confidence_histogram.pdf', format="pdf", bbox_inches='tight', dpi=500)
	plt.close()

for name in ['yes', 'no']:
	if name == 'yes':
		plt.hist(e_yes_per)
	else:
		plt.hist(e_no_per)
	plt.xlabel('Predicted ' + name + '%')
	plt.xlim((0,100))
	plt.savefig('analysis/' + image_id + '_' + name + '_estimated_histogram.pdf', format="pdf", bbox_inches='tight', dpi=500)
	plt.close()

# plt.show()

# fig, axes = plt.subplots(1,2, sharex=True)
# axes[0,0].hist(e_no_per)
# axes[1,0].hist(e_yes_per)
# plt.xlabel('Predicted yes%')

plt.show()
