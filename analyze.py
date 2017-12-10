
import math
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('ggplot')

def plot_results(plot_df, filename):
	plot_df.index = plot_df.image_id
	plot_df = plot_df.drop(['correct'], axis=1)
	plot_df.plot.bar(rot=0)
	plt.xlabel('Image IDs')
	plt.ylabel('Counts')
	plt.savefig('analysis/' + filename, format="pdf", bbox_inches='tight', dpi=500)
	# plt.show()


# Get input files
response_df = pd.read_csv('response.csv')
gt_df = pd.read_csv('ground_truth.csv')

response_df = response_df[response_df['username'] != 'manaswi']

# Format dataframe to have image_ids as rows and each question's answer as column

image_ids = range(1,11)
rows = []
for image_id in image_ids:

	r_df = response_df[response_df.img_id == image_id]

	for rrow in r_df.groupby('username'):

		username = rrow[0]
		value_df = rrow[1]
		answer = value_df.ix[value_df.index[0]]['answer']
		user_confidence = int(value_df.ix[value_df.index[1]]['answer']) / 100.0
		percent_agreement = estimated_yes = int(value_df.ix[value_df.index[2]]['answer']) / 100.0

		if answer == 'no':
			percent_agreement = 1 - estimated_yes

		rows.append((image_id, answer, user_confidence, percent_agreement, username))
			
analyze_df = pd.DataFrame(rows, columns=['image_id', 'vote', 'confidence', 'per_agreement', 'username'])
print analyze_df

"""
Method 1: majority voting
"""
results = []
for idx, row in gt_df.iterrows():

	image_id = row['image_id']
	correct = row['correct']
	a_df = analyze_df[analyze_df.img_id == image_id]
	counts = a_df['vote'].value_counts()

	if 'yes' in counts: 
		yes_count = counts['yes']
	else: 
		yes_count = 0
	
	if 'no' in counts: 
		no_count = counts['no'] 
	else: 
		no_count = 0

	results.append((image_id, yes_count,no_count, correct))

mj_results = pd.DataFrame(results, columns=['image_id', 'yes', 'no', 'correct'])
mj_results.index = mj_results.image_id
mj_results = mj_results.drop(['image_id'], axis=1)
print mj_results

# Plot results
# plot_results(mj_results, 'majority_voting.png')

"""
Method 2: Surprisingly Popular (SP) Algorithm
Relies on Bayesian Truth Serum (BTS) score
"""

n = 11 # number of respondents
for image_id in image_ids:
	a_df = analyze_df[analyze_df.img_id == image_id]
	
	# Step 1a: Average mean x_k of the votes for each answer choice
	xk_mean_yes = mj_results.ix[image_id]['yes'] / n
	xk_mean_no = mj_results.ix[image_id]['no'] / n

	# Step 1b: Geometric mean y_k of the predictions of percent agreement with answer k
	yk_logsum_yes = 0
	yk_logsum_no = 0
	for idx, row in analyze_df.iterrows():

		if row['vote'] = 'yes':
			yk_logsum_yes += math.log(row['percent_agreement'])
			yk_logsum_no += math.log(1 - row['percent_agreement'])
		else:
			yk_logsum_yes += math.log(1 - row['percent_agreement'])
			yk_logsum_no += math.log(row['percent_agreement'])

	yk_gmean_yes = yk_logsum_yes / n
	yk_gmean_no = yk_logsum_no / n

	# Step 2: BTS score u_r for each respondent r
	bts_scores = []
	for idx, row in analyze_df.iterrows():

		if row['vote'] = 'yes':
			u_r = math.log(xk_mean_yes / yk_gmean_yes) + (xk_mean_yes * math.log(row['percent_agreement'] / xk_mean_yes) + 
														  xk_mean_no *  math.log((1 - row['percent_agreement']) / xk_mean_no))
		else:
			u_r = math.log(xk_mean_no / yk_gmean_no) + (xk_mean_yes * math.log((1 - row['percent_agreement']) / xk_mean_yes) + 
														  xk_mean_no *  math.log(row['percent_agreement'] / xk_mean_no))

		bts_scores.append((row['username'], u_r))
	bts_r_df = pd.DataFrame(bts_scores, columns=['username', 'bts_score'])






# Plot results
# plot_results(sp_results, 'surprisingly_popular.pdf')
