import pandas as pd 
import json
import math
import numpy as np

# The Mturk question: In order to get paid for the work you have done on this survey, you need to enter the following code in the box at the bottom of the Mechanical Turk page where you started once you close this survey.

# Please write this down so you don't forget:

# ${rand://int/10000:99999}

np.random.seed(0)

# survey settings
all_titles = list(pd.read_csv("ra_data.csv", encoding = 'utf8')["Headline"])

num_headlines = 30 # unique titles to be classified
num_students = 4 # number of people taking this survey version
overlap = 0.2 # percent of headlines assigned to 1 respondent that will be duplicated
training_length = 5 # number of training titles
training_headlines = ["Training headline {}".format(i) for i in range(training_length)]
block_size = 10 # number of questions in a block (between attention-check)

conditional = False

survey_name = "MTurk Trial"
assignments_name = "mturk_assignments.json"
qsf_name = "mturk_trial.qsf"

titles = list(all_titles)

# determine indices for headlines assigned to each student
titles_per_student = math.ceil(num_headlines / ((1 - overlap) * num_students))
uniques_per_student = math.floor(num_headlines / num_students)
print(titles_per_student, uniques_per_student)

attention_check_length = 5 # number of questions in an attention-check block
attention_check_headlines = [["Attention check headline {}".format(i) for i in range(attention_check_length)] for j in range(math.floor(titles_per_student / block_size))]

uniques_left = num_headlines - num_students * uniques_per_student
uniques = [uniques_per_student for i in range(num_students)]
idx = 0
while uniques_left:
	uniques[idx] += 1
	idx = (idx + 1) % num_students
	uniques_left -= 1

student_assignments = {}
idx_set = set(range(num_headlines))
for i in range(num_students):
	unique_selection = np.random.choice(list(idx_set), size = uniques[i], replace = False)
	idx_set = idx_set - set(unique_selection)
	student_assignments[i] = list(unique_selection)

dup_selection_lst = []
for i in range(num_students):
	dup_selection = np.random.choice(list(student_assignments[(i - 1) % num_students]), size = titles_per_student - uniques[i], replace = False)
	dup_selection_lst.append(list(dup_selection))

for i in range(num_students):
	student_assignments[i].extend(dup_selection_lst[i])

student_assignments_json = {}
for student, assignments in student_assignments.items():
	student_assignments_json[str(student)] = [titles[a] for a in assignments]

with open(assignments_name, 'w') as f:
	json.dump(student_assignments_json, f, ensure_ascii = False, indent = 2)

survey_info = {}
survey_info["SurveyEntry"] = {
	"SurveyID": "SV_eLnpGNWb3hM31cy",
	"SurveyName": survey_name,
	"SurveyDescription": None,
	"SurveyOwnerID": "UR_3WUHDMGK0A1YPvo",
	"SurveyBrandID": "ucdavis",
	"DivisionID": "DV_bCz0vLDEYcivdHv",
	"SurveyLanguage": "EN",
	"SurveyActiveResponseSet": "RS_dgMRsbI5TIbBjLw",
	"SurveyStatus": "Inactive",
	"SurveyStartDate": "0000-00-00 00:00:00",
	"SurveyExpirationDate": "0000-00-00 00:00:00",
	"SurveyCreationDate": "2021-09-02 21:33:29",
	"CreatorID": "UR_3WUHDMGK0A1YPvo",
	"LastModified": "2021-09-02 21:35:33",
	"LastAccessed": "0000-00-00 00:00:00",
	"LastActivated": "0000-00-00 00:00:00",
	"Deleted": None,
}

# survey_info["SurveyElements"] = [
# 	{
# 		"SurveyID": "SV_eLnpGNWb3hM31cy",
# 		"Element": "BL",
# 		"PrimaryAttribute": "Survey Blocks",
# 		"SecondaryAttribute": None,
# 		"TertiaryAttribute": None,
# 	},
# 	{
#       "SurveyID": "SV_eLnpGNWb3hM31cy",
#       "Element": "FL",
#       "PrimaryAttribute": "Survey Flow",
#       "SecondaryAttribute": None,
#       "TertiaryAttribute": None,
#       "Payload": {
#         "Flow": [
#           {
#             "ID": "BL_0NURAV8QJNtGHEq",
#             "Type": "Standard",
#             "FlowID": "FL_3"
#           }
#         ],
#         "Properties": {
#           "Count": 3
#         },
#         "FlowID": "FL_1",
#         "Type": "Root"
#       }
#     },
#     {
#       "SurveyID": "SV_eLnpGNWb3hM31cy",
#       "Element": "SO",
#       "PrimaryAttribute": "Survey Options",
#       "SecondaryAttribute": None,
#       "TertiaryAttribute": None,
#       "Payload": {
#         "BackButton": "false",
#         "SaveAndContinue": "true",
#         "SurveyProtection": "PublicSurvey",
#         "BallotBoxStuffingPrevention": "false",
#         "NoIndex": "Yes",
#         "SecureResponseFiles": "true",
#         "SurveyExpiration": "None",
#         "SurveyTermination": "DefaultMessage",
#         "Header": "",
#         "Footer": "",
#         "ProgressBarDisplay": "Text",
#         "PartialData": "+1 week",
#         "ValidationMessage": None,
#         "PreviousButton": "",
#         "NextButton": "",
#         "SurveyTitle": "Qualtrics Survey | Qualtrics Experience Management",
#         "SkinLibrary": "ucdavis",
#         "SkinType": "MQ",
#         "Skin": "ucdavis2",
#         "NewScoring": 1,
#         "EOSMessage": None,
#         "ShowExportTags": "false",
#         "CollectGeoLocation": "false",
#         "SurveyMetaDescription": "The most powerful, simple and trusted way to gather experience data. Start your journey to experience management and try a free account today.",
#         "PasswordProtection": "No",
#         "AnonymizeResponse": "No",
#         "RefererCheck": "No",
#         "UseCustomSurveyLinkCompletedMessage": None,
#         "SurveyLinkCompletedMessage": None,
#         "SurveyLinkCompletedMessageLibrary": None,
#         "ResponseSummary": "No",
#         "EOSMessageLibrary": None,
#         "EOSRedirectURL": None,
#         "EmailThankYou": "false",
#         "ThankYouEmailMessageLibrary": None,
#         "ThankYouEmailMessage": None,
#         "ValidateMessage": "false",
#         "ValidationMessageLibrary": None,
#         "InactiveSurvey": None,
#         "PartialDeletion": None,
#         "PartialDataCloseAfter": "LastActivity",
#         "InactiveMessageLibrary": None,
#         "InactiveMessage": None,
#         "AvailableLanguages": {
#           "EN": []
#         }
#       }
#     },
# ]

survey_info["SurveyElements"] = [
	{
		"SurveyID": "SV_eLnpGNWb3hM31cy",
		"Element": "BL",
		"PrimaryAttribute": "Survey Blocks",
		"SecondaryAttribute": None,
		"TertiaryAttribute": None,
	},
	{
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "FL",
      "PrimaryAttribute": "Survey Flow",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
      	"Type": "Root",
      	"FlowID": "FL_1",
        "Flow": [
          {
          	"ID": "BL_0NURAV8QJNtGHEq",
            "Type": "Standard",
            "FlowID": "FL_4",
          }
        ],
        "Properties": {
          "Count": 3,
        },
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "SO",
      "PrimaryAttribute": "Survey Options",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
        "BackButton": "false",
        "SaveAndContinue": "true",
        "SurveyProtection": "PublicSurvey",
        "BallotBoxStuffingPrevention": "false",
        "NoIndex": "Yes",
        "SecureResponseFiles": "true",
        "SurveyExpiration": "None",
        "SurveyTermination": "DefaultMessage",
        "Header": "",
        "Footer": "",
        "ProgressBarDisplay": "Text",
        "PartialData": "+1 week",
        "ValidationMessage": None,
        "PreviousButton": "",
        "NextButton": "",
        "SurveyTitle": "Qualtrics Survey | Qualtrics Experience Management",
        "SkinLibrary": "ucdavis",
        "SkinType": "MQ",
        "Skin": "ucdavis2",
        "NewScoring": 1,
        "EOSMessage": None,
        "ShowExportTags": "false",
        "CollectGeoLocation": "false",
        "SurveyMetaDescription": "The most powerful, simple and trusted way to gather experience data. Start your journey to experience management and try a free account today.",
        "PasswordProtection": "No",
        "AnonymizeResponse": "No",
        "RefererCheck": "No",
        "UseCustomSurveyLinkCompletedMessage": None,
        "SurveyLinkCompletedMessage": None,
        "SurveyLinkCompletedMessageLibrary": None,
        "ResponseSummary": "No",
        "EOSMessageLibrary": None,
        "EOSRedirectURL": None,
        "EmailThankYou": "false",
        "ThankYouEmailMessageLibrary": None,
        "ThankYouEmailMessage": None,
        "ValidateMessage": "false",
        "ValidationMessageLibrary": None,
        "InactiveSurvey": None,
        "PartialDeletion": None,
        "PartialDataCloseAfter": "LastActivity",
        "InactiveMessageLibrary": None,
        "InactiveMessage": None,
        "AvailableLanguages": {
          "EN": []
        }
      }
    },
]

survey_info["SurveyElements"][0]["Payload"] = {
	"1": {
		"Type": "Trash",
		"Description": "Trash / Unused Questions",
		"ID": "BL_3JCZSrANuFazQ7I",
		"Options": {
		"BlockLocking": "false",
		"RandomizeQuestions": "false",
		"BlockVisibility": "Expanded"
		},
		"BlockElements": [],
	}
}

# insert key 2 into payload
survey_info["SurveyElements"][0]["Payload"]["2"] = {
	"Type": "Standard",
	"SubType": "",
	"Description": "Survey Body",
	"ID": "BL_2",
	"BlockElements": [],
	"Options": {
		"BlockLocking": "false",
		"RandomizeQuestions": "false",
		"BlockVisibility": "Collapsed",
	}
}

survey_elements = survey_info["SurveyElements"]
block_elements = survey_elements[0]["Payload"]["2"]["BlockElements"]

# description of survey
block_elements.append({
	"Type": "Question",
	"QuestionID": "QID1"
})

# student ID question
block_elements.append({
	"Type": "Question",
	"QuestionID": "QID2"
})

# page break
block_elements.append({
	"Type": "Page Break",
})

directions = """For each headline, we want you to: 
a) Identify whether the headline is about an acquisition or merger. 
b) if it is, for you to identify and enter (preferably by copy-pasting verbatim) the ACQUIRER and ACQUIRED companies. 
c) If the ACQUIRER or ACQUIRED names are not obvious from the headline, please leave the corresponding box blank. 
d) If there are two company names, but you don't know who acquired whom (as in the case of a merger), please still enter the names in either field. 
e) If you are not sure if the headline refers to an acquisition, or if the text does not look like a headline, please mark "not sure" or "This is not a headline". You can still enter company names if relevant.

To increase speed, we suggest using the keyboard to navigate the response:
- "Tab" moves to the next field
- You can use "Y" or "N" keys to select the corresponding drop-down field

Student ID Assignments
- Jahanvi: 0
- Meghna: 1
- Sanjana: 2
- Karina: 3\n\n
"""

qid = "QID{}".format(1)
# survey_elements.append({
# 	"SurveyID": "SV_eLnpGNWb3hM31cy",
# 	"Element": "SQ",
# 	"PrimaryAttribute": qid,
# 	"SecondaryAttribute": directions,
# 	"TertiaryAttribute": None,
# 	"Payload": {
# 	"QuestionText": directions,
# 	"QuestionID": qid,
# 	"QuestionType": "DB",
# 	"Selector": "TB",
# 	"QuestionDescription": directions,
# 	"Validation": {
# 	  "Settings": {
# 	    "Type": "None"
# 	  }
# 	},
# 	"Language": [],
# 	"DataExportTag": qid
# 	}
# })

# add student ID question
qid = "QID{}".format(0)
student_qid = qid
sid_choices = {}
for i in range(num_students):
	sid_choices[str(i)] = { "Display": str(i) }

sort_sid_choices = list(sid_choices.keys())
sort_sid_choices.sort()
block_elements = survey_info["SurveyElements"][0]["Payload"]["2"]["BlockElements"]
block_elements.append({
	"Type": "Question",
    "QuestionID": "QID0"
	})
block_elements.append({
	"Type": "Page Break",
	})

elem = {
	"QuestionText": "Student ID\n\n",
	"QuestionID": qid,
	"QuestionType": "MC",
	"Selector": "DL",
	"QuestionDescription": "Student ID",
	"Choices": sid_choices,
	"Validation": {
		"Settings": {
			"ForceResponse": "ON",
			"ForceResponseType": "ON",
			"Type":"None"
		}
	},
	"Language": [],
	"DataExportTag": qid,
	"SubSelector": "TX",
	"DataVisibility": {
		"Private": False,
		"Hidden": False
	},
	"Configuration": {
		"QuestionDescriptionOption": "UseText"
	},
	"ChoiceOrder": sort_sid_choices,
	"NextChoiceId": str(int(sort_sid_choices[len(sort_sid_choices) - 1]) + 1),
	"NextAnswerId": 1,
}
survey_elements.append(elem)

block_elements.append({
	"Type": "Page Break"
})

i = 3
offset = 3
num_subparts = 5
counter = 3
block_counter = 3

title_to_student = {}
for student, title_idxs in student_assignments.items():
	for t in title_idxs:
		if t in title_to_student:
			title_to_student[t].append(student)
		else:
			title_to_student[t] = [student]

def add_cond_display(student_qid, sids):
	q_cond_display = {
		"Type": "BooleanExpression",
		"inPage": False
	}

	q_cond_display["0"] = {"Type": "If"}
	conj = "If"
	for s in range(len(sids)):
		sid = sids[s]
		q_cond_display["0"][str(s)] = {
			"LogicType": "Question",
			"QuestionID": student_qid,
			"QuestionIsInLoop": "no",
			"ChoiceLocator": "q://{}/SelectableChoice/{}".format(student_qid, sid),
			"Operator": "Selected",
			"QuestionIDFromLocator": student_qid,
			"LeftOperand": "q://{}/SelectableChoice/{}".format(student_qid, sid),
			"Type": "Expression",
			"Description": "<span class=\"ConjDesc\">{}</span> <span class=\"QuestionDesc\">Student ID</span> <span class=\"LeftOpDesc\">{}</span> <span class=\"OpDesc\">Is Selected</span> ".format(conj, sid)
		}
		if s > 0:
			q_cond_display["0"][str(s)]["Conjunction"] = "Or"
		conj = "Or"
	return q_cond_display

displayed_titles = training_headlines
valid_titles = titles[:num_headlines]
at_count = len(attention_check_headlines)
val_block_count = math.ceil(len(valid_titles) / block_size)
i = 0
while val_block_count and at_count:
	displayed_titles.extend(valid_titles[block_size * i:block_size * (i + 1)])
	displayed_titles.extend(attention_check_headlines[i])
	val_block_count -= 1
	at_count -= 1
	i += 1

if val_block_count:
	displayed_titles.extend(valid_titles[block_size * i:block_size * (i + 1)])
elif at_count:
	displayed_titles.extend(attention_check_headlines[i:])

print(len(displayed_titles))

for curr_title in displayed_titles:
	# add to block elements
	req_qid = "QID{}".format(i + 1)
	disp_students = title_to_student[counter - 3]

	# insert key 2 into payload
	survey_info["SurveyElements"][0]["Payload"][str(counter)] = {
		"Type": "Standard",
		"SubType": "",
		"Description": "Block {}".format(block_counter),
		"ID": "BL_{}".format(block_counter),
		"BlockElements": [],
		"Options": {
			"BlockLocking": "false",
			"RandomizeQuestions": "false",
			"BlockVisibility": "Collapsed",
		}
	}
	# survey_info["SurveyElements"][1]["Payload"]["Flow"][0]["Flow"].append({
	# 	"Type": "Block",
	# 	"ID": "BL_{}".format(block_counter),
	# 	"FlowID": "FL_{}".format(block_counter),
	# 	"Autofill": [],
	# 	})
	block_elements = survey_info["SurveyElements"][0]["Payload"][str(counter)]["BlockElements"]

	for subpart in range(num_subparts):
		curr = i + subpart
		qid = "QID{}".format(curr)

		block_elements.append({
			"Type": "Question",
			"QuestionID": qid,
		})

		if subpart == 0:
			elem = {
		      "SurveyID": "SV_eLnpGNWb3hM31cy",
		      "Element": "SQ",
		      "PrimaryAttribute": qid,
		      "SecondaryAttribute": "{}. Headline: {}".format(counter, curr_title),
		      "TertiaryAttribute": None,
		      "Payload": {
		        "QuestionText": "{}. Headline: <br><br>\n<b>{}</b>\n".format(counter, curr_title),
		        "QuestionID": qid,
		        "QuestionType": "DB",
		        "Selector": "TB",
		        "QuestionDescription": "{}. Headline: {}".format(counter, curr_title),
		        "Validation": {
		          "Settings": {
		            "Type": "None"
		          }
		        },
		        "Language": [],
		        "DataExportTag": qid
		      }
			}
		elif subpart == 1:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "Do you think that this headline refers to an acquisition or merger?",
				"TertiaryAttribute": None,
				"Payload": {
				"QuestionText": "Do you think that this headline refers to an acquisition or merger?\n\n",
				"QuestionID": qid,
				"QuestionType": "MC",
				"Selector": "DL",
				"QuestionDescription": "Do you think that this headline refers to an acquisition or merger?",
				"Choices": {
					"1": {
					"Display": "Yes"
					},
					"2": {
					"Display": "No"
					},
					"3": {
					"Display": "Not sure"
					},
					"4": {
					"Display": "Not a headline"
					}
				},
				"Validation": {
					"Settings": {
						"ForceResponse": "ON",
						"ForceResponseType": "ON",
						"Type":"None"
					}
				},
				"Language": [],
				"DataExportTag": qid,
				},
			}
		elif subpart == 2:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "ACQUIRER (leave blank if not indicated or unclear):",
				"TertiaryAttribute": None,
				"Payload": {
				"QuestionText": "ACQUIRER (leave blank if not indicated or unclear):\n\n",
				"QuestionID": qid,
				"QuestionType": "TE",
				"Selector": "SL",
				"QuestionDescription": "ACQUIRER (leave blank if not indicated or unclear):",
				"Validation": {
					"Settings": {
					"Type": "None"
					}
				},
				"Language": [],
				"SearchSource": {
					"AllowFreeResponse": "false"
				},
				"DataExportTag": qid,
				}
		    }
		elif subpart == 3:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "ACQUIRED (leave blank if not indicated or unclear):",
				"TertiaryAttribute": None,
				"Payload": {
				"QuestionText": "ACQUIRED (leave blank if not indicated or unclear):\n\n",
				"QuestionID": qid,
				"QuestionType": "TE",
				"Selector": "SL",
				"QuestionDescription": "ACQUIRED (leave blank if not indicated or unclear):",
				"Validation": {
					"Settings": {
					"Type": "None"
					}
				},
				"Language": [],
				"SearchSource": {
					"AllowFreeResponse": "false"
				},
				"DataExportTag": qid,
				}
		    }
		elif subpart == 4:
			elem = {
		      "SurveyID": "SV_b1uuK02TDahcMrs",
		      "Element": "SQ",
		      "PrimaryAttribute": qid,
		      "SecondaryAttribute": "Timing",
		      "TertiaryAttribute": None,
		      "Payload": {
		        "QuestionText": "Timing",
		        "DefaultChoices": False,
		        "DataExportTag": qid,
		        "QuestionType": "Timing",
		        "Selector": "PageTimer",
		        "Configuration": {
		          "QuestionDescriptionOption": "UseText",
		          "MinSeconds": "0",
		          "MaxSeconds": "0"
		        },
		        "QuestionDescription": "Timing",
		        "Choices": {
		          "1": {
		            "Display": "First Click"
		          },
		          "2": {
		            "Display": "Last Click"
		          },
		          "3": {
		            "Display": "Page Submit"
		          },
		          "4": {
		            "Display": "Click Count"
		          }
		        },
		        "GradingData": [],
		        "Language": [],
		        "NextChoiceId": "QID{}".format(i - 3),
		        "NextAnswerId": 1,
		        "QuestionID": qid
		      }
		    }

		elem["Payload"]["DisplayLogic"] = add_cond_display(student_qid, disp_students)
		elem["Payload"]["NextChoiceId"] = 1
		elem["Payload"]["NextAnswerId"] = 1
		survey_elements.append(elem)

	block_elements.append({
		"Type": "Page Break"
	})
	
	i += num_subparts
	counter += 1
	block_counter += 1

	print(curr_title)

with open(qsf_name, 'w') as f:
	json.dump(survey_info, f, ensure_ascii = False, indent = 2)
