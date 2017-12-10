
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('ggplot')

def plot_results(plot_df):
	plot_df.index = plot_df.image_id
	plot_df = plot_df.drop(['image_id', 'correct'], axis=1)
	plot_df.plot.bar(rot=0)
	plt.xlabel('Image IDs')
	plt.ylabel('Counts')
	plt.savefig('analysis/ majority_voting.png', format="png", bbox_inches='tight', dpi=500)
	# plt.show()


# Get input files
response_df = pd.read_csv('response.csv')
gt_df = pd.read_csv('ground_truth.csv')

response_df = response_df[response_df['username'] != 'manaswi']
"""
Method 1: majority voting
"""
results = []
for idx, row in gt_df.iterrows():

	image_id = row['image_id']
	correct = row['correct']
	r_df = response_df[ (response_df.q_id == 1) & (response_df.img_id == image_id) ]
	counts = r_df['answer'].value_counts()

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
print mj_results

# Plot results
# plot_results(mj_results)

"""
Method 2: surprisingly popular
"""
results = []
for idx, row in gt_df.iterrows():

	image_id = row['image_id']
	correct = row['correct']
	r_df = response_df[response_df.img_id == image_id]

	yes_per = 0
	no_per = 0
	for rrow in r_df.groupby('username'):

		df = rrow[1]
		answer = df.ix[df.index[0]]['answer']
		user_confidence = int(df.ix[df.index[1]]['answer']) / 100.0
		estimated_yes = int(df.ix[df.index[2]]['answer']) / 100.0
		# print (answer, user_confidence, estimated_yes)

		if (answer == 'yes'):
			if (estimated_yes < 0.5):
				yes_per += user_confidence * (1 - estimated_yes)
			else:
				yes_per += user_confidence * estimated_yes
		else:
			if (estimated_yes > 0.5):
				no_per += user_confidence * (1 - estimated_yes)
			else:
				no_per += user_confidence * estimated_yes
	results.append((image_id, yes_per,no_per, correct))

sp_results = pd.DataFrame(results, columns=['image_id', 'yes_confidence', 'no_confidence', 'correct'])
print sp_results

# Plot results
plot_results(sp_results)
