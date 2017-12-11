
import math
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('ggplot')
pd.set_option('display.max_rows', 500)

def plot_results(plot_df, filename):
	plot_df.index = plot_df.image_id
	plot_df = plot_df.drop(['correct'], axis=1)
	plot_df.plot.bar(rot=0)
	plt.xlabel('Image IDs')
	plt.ylabel('Counts')
	plt.savefig('analysis/' + filename, format="pdf", bbox_inches='tight', dpi=500)
	# plt.show()

image_id_list = range(1,11)

# Get input files
response_df = pd.read_csv('response.csv')
gt_df = pd.read_csv('ground_truth.csv')

response_df = response_df[response_df['username'] != 'manaswi']

gt_df.index = image_id_list
gt_df = gt_df.drop(['image_id'], axis=1)

# Format dataframe to have image_id_list as rows and each question's answer as column

rows = []
for image_id in image_id_list:

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
			
analyze_df = pd.DataFrame(rows, columns=['image_id', 'vote', 'confidence', 'percent_agreement', 'username'])

# To handle 0s in log transformation for SP algo, changing 1.0 agreement to 0.99
# analyze_df.loc[analyze_df['percent_agreement'] == 1.0, 'percent_agreement'] = 0.99
print analyze_df

"""
Method 1: majority voting
"""
results = []
for image_id in image_id_list:

	correct = gt_df.ix[image_id]['correct']

	a_df = analyze_df[analyze_df.image_id == image_id]
	counts = a_df['vote'].value_counts()

	if 'yes' in counts: 
		yes_count = counts['yes']
	else: 
		yes_count = 0
	
	if 'no' in counts: 
		no_count = counts['no'] 
	else: 
		no_count = 0

	# Errs towards yes'
	if yes_count >= no_count:
		selected_answer = 'yes'
	else:
		selected_answer = 'no'

	results.append((image_id, yes_count,no_count, correct, selected_answer))

mj_results = pd.DataFrame(results, columns=['image_id', 'yes', 'no', 'correct','predicted'])
mj_results.index = image_id_list
mj_results = mj_results.drop(['image_id'], axis=1)
mj_results['predicted'] = np.where(mj_results['yes'] > mj_results['no'], 'yes', 'no')
print "\n Majority Voting Results\n", mj_results

# Plot results
# plot_results(mj_results, 'majority_voting.png')

"""
Method 2: Surprisingly Popular (SP) Algorithm
Relies on Bayesian Truth Serum (BTS) score
"""

def take_log_a_by_b(a, b):

	c = math.pow(10, -6)
	return math.log(c + (a / (b + c)))

n = 11 # number of respondents
results = []
for image_id in image_id_list:
	a_df = analyze_df[analyze_df.image_id == image_id]
	
	print "\nImage: ", image_id

	# Only run the algorithm if there are disagreements
	# counts = a_df['vote'].value_counts()
	# if ('yes' in counts and 'no' in counts):

	# Run the algorithm

	# Step 1a: Average mean xk_mean of the votes for each answer choice
	xk_mean_yes = mj_results.ix[image_id]['yes'].astype('double') / n
	xk_mean_no = mj_results.ix[image_id]['no'].astype('double') / n

	print "step1a:", xk_mean_yes, xk_mean_no

	# Step 1b: Geometric mean yk_gmean of the predictions of percent agreement with answer k
	yk_product_yes = 1
	yk_product_no = 1
	for idx, row in a_df.iterrows():

		if row['vote'] == 'yes':
			yk_product_yes *= row['percent_agreement']
			yk_product_no *= 1 - row['percent_agreement']
		else:
			yk_product_yes *= 1 - row['percent_agreement']
			yk_product_no *= row['percent_agreement']

	yk_gmean_yes = yk_product_yes ** (1.0 / n)
	yk_gmean_no = yk_product_no ** (1.0 / n)

	print "step1b:", yk_gmean_yes, yk_gmean_no

	# Step 2: BTS score u_r for each respondent r
	bts_scores = []
	for idx, row in a_df.iterrows():

		if row['vote'] == 'yes':
			first_term = take_log_a_by_b(xk_mean_yes, yk_gmean_yes)
			second_term_yes = xk_mean_yes * take_log_a_by_b(row['percent_agreement'], xk_mean_yes)
			second_term_no = xk_mean_no *  take_log_a_by_b((1 - row['percent_agreement']), xk_mean_no)
		
		else:
			first_term = take_log_a_by_b(xk_mean_no, yk_gmean_no)
			second_term_yes = xk_mean_yes * take_log_a_by_b((1 - row['percent_agreement']), xk_mean_yes)
			second_term_no = xk_mean_no *  take_log_a_by_b(row['percent_agreement'], xk_mean_no)
			
		u_r =  first_term + (second_term_yes + second_term_no)

		bts_scores.append((row['username'], u_r, row['vote']))
	
	bts_r_df = pd.DataFrame(bts_scores, columns=['username', 'bts_score', 'vote'])
	print "step2: BTS Score\n", bts_r_df

	# Step 3: Average BTS score ur_mean_k of all respondents endoring answer k
	# Get yes/no counts
	if (bts_r_df[bts_r_df.vote == 'yes']['bts_score'].sum() == 0):
		ur_mean_yes = 0
	else:
		ur_mean_yes = bts_r_df[bts_r_df.vote == 'yes']['bts_score'].sum()/ (n * xk_mean_yes)
	
	if bts_r_df[bts_r_df.vote == 'no']['bts_score'].sum() == 0:
		ur_mean_no = 0
	else:
		ur_mean_no = bts_r_df[bts_r_df.vote == 'no']['bts_score'].sum()/ (n * xk_mean_no)

	print "step3:", ur_mean_yes, ur_mean_no

	# Step 4: Choose the answer k that has the maximum score
	# Errs towards yes'
	if ur_mean_yes >= ur_mean_no:
		predicted_answer = 'yes'
	else:
		predicted_answer = 'no'

	# else:
	# 	# Select the answer that's endorsed by everyone
	# 	if('yes' in counts):
	# 		predicted_answer = 'yes'
	# 	else:
	# 		predicted_answer = 'no'

	print "image id:", image_id, predicted_answer

	results.append((image_id, gt_df.ix[image_id]['correct'], predicted_answer))

sp_results = pd.DataFrame(results, columns=['image_id', 'correct', 'predicted'])
print "\n Surprisingly Popular (SP) Results\n", sp_results





# Plot results
# plot_results(sp_results, 'surprisingly_popular.pdf')
