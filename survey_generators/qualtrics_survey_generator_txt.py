import pandas as pd 

titles = list(pd.read_csv('random_combined.csv', names = ['Title'])['Title'])

desc = """Headline: <br><br>
<b>{}</b>
"""

q1 = 'Does this headline refer to an acquisition?'
q1_choices = [
	'Yes',
	'No',
	'Not sure',
	'Not a headline',
]

q2 = 'ACQUIRER:'

q3 = 'ACQUIRED:'

q4 = """Click here if there is something strange about this headline that we should pay attention to.
"""

q5 = 'Optional notes'

directions = """For each headline, we want you to: <br>
a) identify whether the release is about an acquisition or not <br>
b) if it is, for you to identify and enter (preferably by copy-pasting verbatim) the ACQUIRER and ACQUIRED companies. <br><br>
If the ACQUIRER or ACQUIRED names are not obvious from the headline, please leave the corresponding box blank.
"""

num_q = 1
with open('qualtrics_survey.txt', 'w') as f:
	f.write('[[AdvancedFormat]]\n\n')

	# instruction page
	instr_page = '[[Question:Text]]\n{}\n[[PageBreak]]\n'
	f.write(instr_page.format(directions))

	for curr_title in titles[:5]:
		# acq / non-acq
		curr_desc = desc.format(curr_title)
		curr_page = '[[Question:Text]]\n' + '{}. '.format(num_q) + curr_desc
		curr_page += '[[Question:MC:DropDown]]\n'
		curr_page += q1 + '\n\n'
		curr_page += '[[Choices]]\n'
		for q1_c in q1_choices:
			curr_page += q1_c + '\n'
		curr_page += '\n\n'
		
		# if acq: acquirer
		curr_page += '[[Question:TextEntry:SingleLine]]\n' + q2 + '\n\n'

		# if acq: acquiree
		curr_page += '[[Question:TextEntry:SingleLine]]\n' + q3 + '\n\n'

		# # something strange
		curr_page += '[[Question:MC:MultipleAnswer]]\n\n[[Choices]]\n' + q4 + '\n\n'

		# # optional notes
		curr_page += '[[Question:TextEntry:Essay]]\n' + q5 + '\n\n'
		
		curr_page += '[[PageBreak]]\n'
		f.write(curr_page)
		num_q += 1
