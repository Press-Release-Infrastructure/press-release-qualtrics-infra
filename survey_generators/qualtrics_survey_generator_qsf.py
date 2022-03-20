import pandas as pd 
import json
import math
import sys
import numpy as np
import copy
import configparser
from survey_flow_directions import pg1, pg1_alt, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9, pg10, pg11, pg12, pg13, pg14

seed = 0
np.random.seed(seed)
rate = 120 # expected rate of problem solving per hour

# survey settings
config = configparser.ConfigParser()
config.read("qualtrics_survey_controls.txt")

all_titles = list(pd.read_csv(config["settings"]["all_titles_filename"], encoding = 'utf8')["Headline"].unique())

num_headlines = int(config["settings"]["num_headlines"]) # unique titles to be classified
num_students = int(config["settings"]["num_students"]) # number of people taking this survey version
overlap = float(config["settings"]["overlap"]) # percent of headlines assigned to 1 respondent that will be duplicated
training_length = int(config["settings"]["training_length"]) # number of training titles
block_size = int(config["settings"]["block_size"]) # number of questions in a block (between attention-check)
attention_check_length = int(config["settings"]["attention_check_length"]) # number of questions in an attention-check block
follow_up_flag = bool(int(config["settings"]["follow_up_flag"]))
# print(follow_up_flag)

training_thresh_mc = float(config["settings"]["training_thresh_mc"])
training_thresh_te = float(config["settings"]["training_thresh_te"])
attention_thresh_mc = float(config["settings"]["attention_thresh_mc"])
attention_thresh_te = float(config["settings"]["attention_thresh_te"])

training_mc_weight = training_thresh_mc / (training_thresh_mc + 2 * training_thresh_te)
training_te_weight = training_thresh_te / (training_thresh_mc + 2 * training_thresh_te)
attention_mc_weight = attention_thresh_mc / (attention_thresh_mc + 2 * attention_thresh_te)
attention_te_weight = attention_thresh_te / (training_thresh_mc + 2 * training_thresh_te)

survey_name = config["settings"]["survey_name"]
assignments_name = config["settings"]["assignments_name"]
qsf_name = config["settings"]["qsf_name"]

eos_redirect_url = config["settings"]["eos_redirect_url"]

training_headlines_df = pd.read_csv(config["settings"]["training_headlines_filename"], encoding = 'utf8').sample(frac = 1, random_state = seed)
training_flow_headlines_df = pd.read_csv(config["settings"]["training_flow_headlines_filename"], encoding = 'utf8')
training_headlines_df = training_headlines_df.where(pd.notnull(training_headlines_df), "")
training_headlines = list(training_headlines_df["Title"][:training_length])
training_answers = training_headlines_df[["Acq_Status", "Company 1", "Company 2"]].to_records(index = False)[:training_length]

titles = np.array(all_titles)

# determine indices for headlines assigned to each student
titles_per_student = math.ceil(num_headlines / ((1 - overlap) * num_students))
# titles_per_student = math.ceil(num_headlines * 2 / num_students)
uniques_per_student = math.floor(num_headlines / num_students)

att_headlines_df = pd.read_csv(config["settings"]["att_headlines_filename"], encoding = 'utf8').sample(frac = 1, random_state = seed)
att_headlines_df = att_headlines_df.where(pd.notnull(att_headlines_df), "")
attention_check_headlines = []

# pick groups of att length headlines from att_headlines_df without replacement
all_att_idxes = set(np.arange(0, len(att_headlines_df)))
attention_check_answers = {}
for j in range(math.ceil(titles_per_student / block_size)):
	curr_idxes = np.random.choice(list(all_att_idxes), size = attention_check_length, replace = False)
	curr_att = att_headlines_df.iloc[curr_idxes]
	for c in curr_idxes:
		all_att_idxes = list(set(all_att_idxes) - set(curr_idxes))
	curr_att_headlines = []
	for _, c in curr_att.iterrows():
		curr_att_headlines.append(str(c["Title"]))
		attention_check_answers[str(c["Title"])] = [int(c["Acq_Status"]), str(c["Company 1"]), str(c["Company 2"])]
	attention_check_headlines.append(curr_att_headlines)

uniques_left = num_headlines - num_students * uniques_per_student
uniques = [uniques_per_student for i in range(num_students)]
idx = 0
while uniques_left:
	uniques[idx] += 1
	idx = (idx + 1) % num_students
	uniques_left -= 1

student_assignments = {}
curr_idx = 0
idx_set = range(num_headlines)
for i in range(num_students):
	unique_selection = idx_set[curr_idx:(curr_idx + uniques[i])]
	student_assignments[i] = list(unique_selection)
	curr_idx += len(unique_selection)

used_headlines = set()
prev_student_headlines = student_assignments[num_students - 1]
for i in range(num_students):
	curr_student_headlines = student_assignments[i]
	dup_headlines = prev_student_headlines[-int(max(len(curr_student_headlines), len(prev_student_headlines))):].copy()
	prev_student_headlines = student_assignments[i].copy()
	student_assignments[i] = list(set(np.concatenate([student_assignments[i], dup_headlines])))

# check that each headline is assigned twice
headline_dict = {}
for k, v in student_assignments.items():
	for h in v:
		if h in headline_dict:
			headline_dict[h] += 1
		else:
			headline_dict[h] = 1

for v in headline_dict.values():
	assert(v == 2)

student_assignments_json = {}
titles_to_classify = []
for student, assignments in student_assignments.items():
	student_assignments_json[str(student)] = [titles[a] for a in assignments]
	titles_to_classify.extend(student_assignments_json[str(student)])

with open(assignments_name, 'w') as f:
	json.dump(student_assignments_json, f, ensure_ascii = False, indent = 2)

survey_info = {}

# args needed: flow id, right operand, right operand
branch_logic_template = {
	"Type": "Branch",
	"FlowID": "",
	"Description": "New Branch",
	"BranchLogic": {
		"0": {
			"0": {
				"LogicType": "EmbeddedField",
				"LeftOperand": "Score",
				"Operator": "LessThan",
				"RightOperand": "",
				"_HiddenExpression": False,
				"Type": "Expression",
				"Description": "<span class=\"ConjDesc\">If</span>  <span class=\"LeftOpDesc\">Score</span> <span class=\"OpDesc\">Is Less Than</span> <span class=\"RightOpDesc\"> "" </span>"
			},
			"Type": "If"
		},
		"Type": "BooleanExpression"
	}
}

end_survey_display_flow_id = -600
end_survey_display = {
	"ID": "BL_{}",
	"Type": "Block",
	"FlowID": "FL_{}"
}

end_survey_flow_id = -500
end_survey = {
	"Type": "EndSurvey",
	"FlowID": "FL_{}"
}

set_score_flow_id = -300
set_score = {
	"Type": "EmbeddedData",
	"FlowID": "FL_-1",
	"EmbeddedData": [
		{
		"Description": "Score",
		"Type": "Custom",
		"Field": "Score",
		"VariableType": "String",
		"DataVisibility": [],
		"AnalyzeText": False,
		"Value": "${gr://SC_0/Score}"
		}
	]
}

set_end_id_flow_id = -400
set_end_id = {
	"Type": "EmbeddedData",
	"FlowID": "FL_{}",
	"EmbeddedData": [
		{
			"Description": "endID",
			"Type": "Custom",
			"Field": "endID",
			"VariableType": "String",
			"DataVisibility": [],
			"AnalyzeText": False,
			"Value": "$e{round(${gr://SC_0/Score}) * 100}${rand://int/100000:1000000}"
		}
	]
}

survey_info["SurveyEntry"] = {
	"SurveyID": "SV_eLnpGNWb3hM31cy",
	"SurveyName": survey_name,
	"SurveyDescription": None,
	"SurveyOwnerID": "UR_3WUHDMGK0A1YPvo",
	"SurveyBrandID": "",
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

survey_info["SurveyElements"] = [
	{
		"SurveyID": "SV_eLnpGNWb3hM31cy",
		"Element": "BL",
		"PrimaryAttribute": "Survey Blocks",
		"SecondaryAttribute": None,
		"TertiaryAttribute": None,
		"Payload": [],
	},
	{
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "FL",
      "PrimaryAttribute": "Survey Flow",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
      	"Type": "Root",
      	"FlowID": "FL_-1000000",
        "Flow": [
			{
				"Type": "EmbeddedData",
				"FlowID": "FL_-2000000",
				"EmbeddedData": [
					{
						"Description": "respondentID",
						"Type": "Custom",
						"Field": "respondentID",
						"VariableType": "String",
						"DataVisibility": [],
						"AnalyzeText": False,
						"Value": "${qo://QO_wsLz1sdn4gxRJxy/QuotaCount}"
					}
				]
          	},
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
        "ProgressBarDisplay": "None",
        "PartialData": "+1 week",
        "ValidationMessage": "",
        "PreviousButton": "",
        "NextButton": "",
        "SurveyTitle": "Qualtrics Survey | Qualtrics Experience Management",
        "SkinLibrary": "ucdavis",
        "SkinType": "templated",
        "Skin": {
          "brandingId": None,
          "templateId": "*base",
          "overrides": {
            "questionText": {
              "size": "16px"
            },
            "answerText": {
              "size": "14px"
            },
			"layout": {
				"spacing": 0
			}
          }
        },
        "NewScoring": 1
	  }
	},
	{
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "SCO",
      "PrimaryAttribute": "Scoring",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
        "ScoringCategories": [
          {
            "ID": "SC_0",
            "Name": "Score",
            "Description": ""
          }
        ],
        "ScoringCategoryGroups": [],
        "ScoringSummaryCategory": None,
        "ScoringSummaryAfterQuestions": 0,
        "ScoringSummaryAfterSurvey": 0,
        "DefaultScoringCategory": "SC_0",
        "AutoScoringCategory": None
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "PROJ",
      "PrimaryAttribute": "CORE",
      "SecondaryAttribute": None,
      "TertiaryAttribute": "1.1.0",
      "Payload": {
        "ProjectCategory": "CORE",
        "SchemaVersion": "1.1.0"
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "STAT",
      "PrimaryAttribute": "Survey Statistics",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
        "MobileCompatible": True,
        "ID": "Survey Statistics"
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "QC",
      "PrimaryAttribute": "Survey Question Count",
      "SecondaryAttribute": "3",
      "TertiaryAttribute": None,
      "Payload": None
    },
	{
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "QO",
      "PrimaryAttribute": "QO_wsLz1sdn4gxRJxy",
      "SecondaryAttribute": "Number of respondents",
      "TertiaryAttribute": None,
      "Payload": {
        "Name": "Number of respondents",
        "Occurrences": num_students,
        "Logic": {
          "0": {
            "0": {
              "LogicType": "Quota",
              "QuotaID": "QO_wsLz1sdn4gxRJxy",
              "QuotaType": "Simple",
              "Operator": "QuotaMet",
              "LeftOperand": "qo://QO_wsLz1sdn4gxRJxy/QuotaMet",
              "QuotaName": "Number of respondents",
              "Type": "Expression",
              "Description": "<span class=\"ConjDesc\">If</span> <span class=\"QuestionDesc\">Quota</span> <span class=\"LeftOpDesc\">Number of respondents</span> <span class=\"OpDesc\">Has Been Met</span> "
            },
            "Type": "If"
          },
          "Type": "BooleanExpression"
        },
        "LogicType": "Simple",
        "QuotaAction": "ForBranching",
        "OverQuotaAction": "Record",
        "ActionInfo": {
          "0": {
            "0": {
              "ActionType": "ForBranching",
              "Type": "Expression",
              "LogicType": "QuotaAction"
            },
            "Type": "If"
          },
          "Type": "BooleanExpression"
        },
        "ID": "QO_wsLz1sdn4gxRJxy",
        "QuotaRealm": "Survey",
        "QuotaSchedule": None,
        "EndSurveyOptions": {
          "EndingType": "Default",
          "ResponseFlag": "QuotaMet",
          "SurveyTermination": "DefaultMessage"
        }
      }
    },
	{
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "QG",
      "PrimaryAttribute": "QG_M8GH3g6zuPBjQgw",
      "SecondaryAttribute": "Default Quota Group",
      "TertiaryAttribute": None,
      "Payload": {
        "ID": "QG_M8GH3g6zuPBjQgw",
        "Name": "Default Quota Group",
        "Selected": True,
        "MultipleMatch": "PlaceInAll",
        "Public": False,
        "Quotas": [
          "QO_wsLz1sdn4gxRJxy"
        ]
      }
    },
]

survey_info["SurveyElements"][0]["Payload"].append(
	{
		"Type": "Trash",
		"Description": "Trash / Unused Questions",
		"ID": "BL_3JCZSrANuFazQ7I",
	}
)

survey_elements = survey_info["SurveyElements"]
flow_elements = survey_elements[1]["Payload"]["Flow"]

prolific_qid = -10000000
flow_elements.append({
	"Type": "EmbeddedData",
	"FlowID": "FL_{}".format(prolific_qid),
	"EmbeddedData": [
		{
		"Description": "PROLIFIC_PID",
		"Type": "Recipient",
		"Field": "PROLIFIC_PID",
		"VariableType": "String",
		"DataVisibility": [],
		"AnalyzeText": False
		}
	]
})

# add directions
directions = [pg1, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9, pg10, pg11, pg12, pg13, pg14]
if follow_up_flag:
	directions[0] = pg1_alt 

d_format_elements = [
	['Title', 'Company 1', 'Company 2'],
	['Title', 'Company 2', 'Company 1', 'Company 1', 'Company 2'],
	['Title'],
	['Title'],
	['Title', 'Company 1', 'Company 1'],
	['Title', 'Company 2', 'Company 2'],
	['Title']
]

curr = 0
image_curr = -5000
image_ids = ["IM_9B5dS6U26s0YYRM", "IM_0OMSPpaZ6IPdKtg", "IM_bwqhodFXsvLLnj8", "IM_0AL9PxBO1HSum5U", "IM_0jpOZB2TB4XXIhM", "IM_bQuvbckdHqNZxie", "IM_51OYNiheRmKoVYa"]
for d in directions:
	qid1 = "QID{}".format(curr)
	qid2 = "QID{}".format(image_curr)
	# student_qid = qid
	
	if curr == 3:
		d = d % (titles_per_student, round(titles_per_student / rate * 60))
	elif 4 <= curr <= 10:
		d_elems = list(training_flow_headlines_df.iloc[curr - 4][d_format_elements[curr - 4]])
		d = d % tuple(d_elems)

	if 4 <= curr <= 10:
		d = "<b style = 'color: #6082B6;'>TRAINING IN PROGRESS</b><br><br><div style = 'font-family: Monaco;'>" + d + "</div>"
	survey_elements.append({
		"SurveyID": "SV_eLnpGNWb3hM31cy",
		"Element": "SQ",
		"PrimaryAttribute": qid1,
		"SecondaryAttribute": d,
		"TertiaryAttribute": None,
		"Payload": {
		"QuestionText": d,
		"QuestionID": qid1,
		"QuestionType": "DB",
		"Selector": "TB",
		"QuestionDescription": d,
		"Validation": {
		"Settings": {
			"Type": "None"
		}
		},
		"Language": [],
		"DataExportTag": qid1
		}
	})

	if 4 <= curr <= 10:
		survey_elements.append({
			"SurveyID": "SV_eLnpGNWb3hM31cy",
			"Element": "SQ",
			"PrimaryAttribute": qid2,
			"SecondaryAttribute": " ",
			"TertiaryAttribute": None,
			"Payload": {
			"QuestionText": "",
			"DefaultChoices": False,
			"DataExportTag": qid2,
			"QuestionType": "DB",
			"Selector": "GRB",
			"Configuration": {
				"QuestionDescriptionOption": None
			},
			"QuestionDescription": "",
			"ChoiceOrder": [],
			"Validation": {
				"Settings": {
				"Type": "None"
				}
			},
			"GradingData": [],
			"Language": [],
			"NextChoiceId": 4,
			"NextAnswerId": 1,
			"QuestionID": qid2,
			"SubSelector": "WTXB",
			"GraphicsDescription": str(curr - 4),
			"Graphics": image_ids[curr - 4]
			}
		})

	survey_info["SurveyElements"][0]["Payload"].append({
		"Type": "Standard",
		"SubType": "",
		"Description": "Block {}".format(curr),
		"ID": "BL_{}".format(curr),
		"BlockElements": [],
		"Options": {
			"BlockLocking": "false",
			"RandomizeQuestions": "false",
			"BlockVisibility": "Collapsed",
		}
	})

	block_elements = survey_info["SurveyElements"][0]["Payload"][curr + 1]["BlockElements"]

	survey_info["SurveyElements"][1]["Payload"]["Flow"].append(
		{
			"ID": "BL_{}".format(curr),
			"Type": "Block",
			"FlowID": "FL_{}".format(curr)
		}
	)

	block_elements.append({
		"Type": "Question",
		"QuestionID": qid1
		})

	# if curr == 0:
	# 	# add prolific id question
	# 	prolific_q_text = "What is your Prolific ID? Please note that this response should auto-fill with the correct ID."

	# 	prolific_q = {
	# 			"SurveyID": "SV_eLnpGNWb3hM31cy",
	# 			"Element": "SQ",
	# 			"PrimaryAttribute": "QID{}".format(prolific_qid),
	# 			"SecondaryAttribute": prolific_q_text,
	# 			"TertiaryAttribute": None,
	# 			"Payload": {
	# 				"QuestionText": prolific_q_text,
	# 				"DefaultChoices": {
	# 					"TEXT": {
	# 						"Text": "${e://Field/PROLIFIC_PID}"
	# 					}
	# 				},
	# 				"QuestionID": "QID{}".format(prolific_qid),
	# 				"QuestionType": "TE",
	# 				"Selector": "SL",
	# 				"Configuration": {
	# 					"QuestionDescriptionOption": "UseText"
	# 				},
	# 				"QuestionDescription": prolific_q_text,
	# 				"Validation": {
	# 					"Settings": {
	# 						"ForceResponse": "OFF",
	# 						"Type": "None"
	# 					}
	# 				},
	# 				"GradingData": [],
	# 				"Language": [],
	# 				"NextChoiceId": 4,
    #     			"NextAnswerId": 1,
	# 				"SearchSource": {
	# 					"AllowFreeResponse": "false"
	# 				},
	# 				"DataExportTag": "QID{}".format(prolific_qid),
	# 			}
	# 	    }

	# 	survey_elements.append(prolific_q)

	# 	block_elements.append({
	# 		"Type": "Question",
	# 		"QuestionID": "QID{}".format(prolific_qid)
	# 	})

	if 4 <= curr <= 10:
		block_elements.append({
			"Type": "Question",
			"QuestionID": qid2
			})
		
	block_elements.append({
		"Type": "Page Break",
		})

	curr += 1
	image_curr -= 1

num_subparts = 5

title_to_student = {}
attention_check_title_to_student = {}
training_title_to_student = {}

for student, title_idxs in student_assignments.items():
	for t in title_idxs:
		if t in title_to_student:
			title_to_student[t].append(student)
		else:
			title_to_student[t] = [student]

for a_chunk in attention_check_headlines:
	for a in a_chunk:
		attention_check_title_to_student[a] = list(range(num_students))

for t in training_headlines:
	training_title_to_student[t] = list(range(num_students))

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
			"LogicType": "EmbeddedField",
			"LeftOperand": "respondentID",
			"Operator": "EqualTo",
			"RightOperand": str(sid),
			"Type": "Expression",
			"Description": "<span class=\"ConjDesc\">If</span>  <span class=\"LeftOpDesc\">respondentID</span> <span class=\"OpDesc\">Is Equal to</span> <span class=\"RightOpDesc\"> {} </span>".format(sid)
		}
		if s > 0:
			q_cond_display["0"][str(s)]["Conjuction"] = "Or"
		conj = "Or"
	return q_cond_display

eos_payload_blocks = []

def create_end_of_survey_logic(fl_id, eos_block_id, segment = 0):
	curr_end_survey_display = copy.deepcopy(end_survey_display)
	curr_end_survey_display["ID"] = curr_end_survey_display["ID"].format(eos_block_id)
	curr_end_survey_display["FlowID"] = curr_end_survey_display["FlowID"].format(end_survey_display_flow_id)
	qid = "QID{}".format(eos_block_id - 1)
	eos_payload = {
		"Type": "Standard",
		"SubType": "",
		"Description": "Block {}".format(eos_block_id),
		"ID": "BL_{}".format(eos_block_id),
		"BlockElements": [
			{
				"Type": "Question",
				"QuestionID": "QID{}".format(eos_block_id - 1),
			}
		],
		"Options": {
			"BlockLocking": "false",
			"RandomizeQuestions": "false",
			"BlockVisibility": "Collapsed",
		}
	}
	eos_payload_blocks.append(eos_payload)

	# msg = "Your score {} wasn't high enough to continue with the survey."
	# if segment == 0:
	# 	msg = msg.format("on the training questions")
	# elif segment == 1:
	# 	msg = msg.format("in the current block")
	# else:
	# 	msg = "You have completed the survey."
	msg = "You have completed the survey."

	elem = {
		"SurveyID": "SV_eLnpGNWb3hM31cy",
		"Element": "SQ",
		"PrimaryAttribute": qid,
		"SecondaryAttribute": "End of survey",
		"TertiaryAttribute": None,
		"Payload": {
		"QuestionText": msg + "<br><br>In order to get paid for the work you have done on this survey, you need to enter the following code in the box at the bottom of the Mechanical Turk page where you started once you close this survey.<br><br>Please write this down so you don't forget: <br><br>${e://Field/endID}",
		"QuestionID": qid,
		"QuestionType": "DB",
		"Selector": "TB",
		"QuestionDescription": "End of survey",
		"Validation": {
			"Settings": {
			"Type": "None"
			}
		},
		"Language": [],
		"DataExportTag": qid
		}
	}

	survey_elements.append(elem)
	return curr_end_survey_display

def create_branch_logic(branch_logic_template, fl_id, eos_block_id, thresh_mc, thresh_te, total_questions_done, segment = False):
	branch_logic_template_copy = copy.deepcopy(branch_logic_template)
	branch_logic_template_copy["FlowID"] = "FL_{}".format(fl_id)
	curr_end_survey_display = create_end_of_survey_logic(fl_id, eos_block_id, segment)

	set_end_id_copy = copy.deepcopy(set_end_id)
	set_end_id_copy["EmbeddedData"][0]["Value"] = "$e{" + str(total_questions_done) + " * 100}${rand://int/100000:1000000}"
	end_survey_copy = copy.deepcopy(end_survey)
	set_end_id_copy["FlowID"] = "FL_{}".format(set_end_id_flow_id)
	end_survey_copy["FlowID"] = "FL_{}".format(end_survey_flow_id)
	branch_logic_template_copy["Flow"] = [set_end_id_copy, curr_end_survey_display, end_survey_copy]
	branch_logic_template_copy["BranchLogic"]["0"]["0"]["RightOperand"] = str(thresh_mc + thresh_te)
	branch_logic_template_copy["BranchLogic"]["0"]["0"]["Description"] = "<span class=\"ConjDesc\">If</span>  <span class=\"LeftOpDesc\">Score</span> <span class=\"OpDesc\">Is Less Than</span> <span class=\"RightOpDesc\"> {} </span>".format(thresh_mc + thresh_te)
	return branch_logic_template_copy

def add_score(elem, weight = 1, q_type = "MC", train_ans = -1, merger = False):
	if train_ans != -1:
		if q_type == "MC":
			elem["Payload"]["GradingData"] = [
				{
					"ChoiceID": "1",
					"Grades": {
						"SC_0": 0
					},
					"index": 0
				},
				{
					"ChoiceID": "2",
					"Grades": {
						"SC_0": 0
					},
					"index": 1
				},
				{
					"ChoiceID": "3",
					"Grades": {
						"SC_0": 0
					},
					"index": 2
				},
				{
					"ChoiceID": "4",
					"Grades": {
						"SC_0": 0
					},
					"index": 3
				}
			]
			elem["Payload"]["GradingData"][train_ans]["Grades"]["SC_0"] = weight
		elif q_type == "TE":
			if merger:
				elem["Payload"]["GradingData"] = [{
					"TextEntry": t,
					"Grades": {
						"SC_0": "{}".format(weight)
					}
				} for t in train_ans]
			else:
				elem["Payload"]["GradingData"] = [{
					"TextEntry": train_ans,
					"Grades": {
						"SC_0": "{}".format(weight)
					}
				}]

def create_question(curr_title, curr, disp_settings = [], train_ans_lst = [], training = False):
	qid = "QID{}".format(curr)

	if len(train_ans_lst):
		train_ans, train_ans_acquirer, train_ans_acquired = train_ans_lst
		mc_weight, te_weight = training_mc_weight, training_te_weight
	else:
		train_ans, train_ans_acquirer, train_ans_acquired = -1, -1, -1
		mc_weight, te_weight = attention_mc_weight, attention_te_weight

	survey_info["SurveyElements"][0]["Payload"].append({
		"Type": "Standard",
		"SubType": "",
		"Description": "Block {}".format(curr),
		"ID": "BL_{}".format(curr),
		"BlockElements": [],
		"Options": {
			"BlockLocking": "false",
			"RandomizeQuestions": "false",
			"BlockVisibility": "Collapsed",
		}
	})
	block_elements = survey_info["SurveyElements"][0]["Payload"][curr + 1]["BlockElements"]
	
	# append to flow payload
	survey_info["SurveyElements"][1]["Payload"]["Flow"].append(
		{
			"ID": "BL_{}".format(curr),
			"Type": "Block",
			"FlowID": "FL_{}".format(curr)
		}
	)

	for subpart in range(num_subparts):
		curr_sub = (curr - 1) * num_subparts + subpart + 1
		qid = "QID{}".format(curr_sub)

		block_elements.append({
			"Type": "Question",
			"QuestionID": qid,
		})

		if subpart == 0:
			displayed_headline = "Headline: <br><br>\n<b>{}</b>\n".format(curr_title)
			
			if training:
				displayed_headline = "<b>TRAINING TEST IN PROGRESS</b><br><br>Headline: <br><br>\n<b>{}</b>\n".format(curr_title)
			
			elem = {
		      "SurveyID": "SV_eLnpGNWb3hM31cy",
		      "Element": "SQ",
		      "PrimaryAttribute": qid,
		      "SecondaryAttribute": "Headline: {}".format(curr_title),
		      "TertiaryAttribute": None,
		      "Payload": {
		        "QuestionText": displayed_headline,
		        "QuestionID": qid,
		        "QuestionType": "DB",
		        "Selector": "TB",
		        "QuestionDescription": curr_title,
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
					"DataExportTag": qid,
					"QuestionType": "MC",
					"Selector": "DL",
					"Configuration": {
						"QuestionDescriptionOption": "UseText"
					},
					"QuestionDescription": "Do you think that this headline refers to an acquisition or merger?",
					"Choices": {
						"1": {
							"Display": "Acquisition"
						},
						"2": {
							"Display": "Merger"
						},
						"3": {
							"Display": "Neither / Not sure / Unclear"
						},
					},
					"ChoiceOrder": [
						"1",
						"2",
						"3",
					],
					"Validation": {
						"Settings": {
							"ForceResponse": "ON",
							"ForceResponseType": "ON",
							"Type":"None"
						}
					},
					"GradingData": [],
					"Language": [],
					"NextChoiceId": 4,
        			"NextAnswerId": 1,
					"QuestionID": qid
				},
			}

			add_score(elem, mc_weight, "MC", train_ans)
		elif subpart == 2:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "ACQUIRER (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.):",
				"TertiaryAttribute": None,
				"Payload": {
					"QuestionText": "ACQUIRER (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.):\n\n",
					"DefaultChoices": False,
					"QuestionID": qid,
					"QuestionType": "TE",
					"Selector": "SL",
					"Configuration": {
						"QuestionDescriptionOption": "UseText"
					},
					"QuestionDescription": "ACQUIRER (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.):",
					"Validation": {
						"Settings": {
							"ForceResponse": "OFF",
							"Type": "None"
						}
					},
					"GradingData": [],
					"Language": [],
					"NextChoiceId": 4,
        			"NextAnswerId": 1,
					"SearchSource": {
						"AllowFreeResponse": "false"
					},
					"DataExportTag": qid,
				}
		    }

			merger = train_ans == 1
			if merger: train_ans_arg = [train_ans_acquirer, train_ans_acquired]
			else: train_ans_arg = train_ans_acquirer
			add_score(elem, te_weight, "TE", train_ans_arg, merger = merger)
		elif subpart == 3:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "ACQUIRED (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.):",
				"TertiaryAttribute": None,
				"Payload": {
					"QuestionText": "ACQUIRED (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.):\n\n",
					"DefaultChoices": False,
					"QuestionID": qid,
					"QuestionType": "TE",
					"Selector": "SL",
					"Configuration": {
						"QuestionDescriptionOption": "UseText"
					},
					"QuestionDescription": "ACQUIRED (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.):",
					"Validation": {
						"Settings": {
							"ForceResponse": "OFF",
							"Type": "None"
						}
					},
					"GradingData": [],
					"Language": [],
					"NextChoiceId": 4,
        			"NextAnswerId": 1,
					"SearchSource": {
						"AllowFreeResponse": "false"
					},
					"DataExportTag": qid,
				}
		    }

			merger = train_ans == 1
			if merger: train_ans_arg = [train_ans_acquired, train_ans_acquirer]
			else: train_ans_arg = train_ans_acquired
			add_score(elem, te_weight, "TE", train_ans_arg, merger = merger)
		elif subpart == 4:
			elem = {
		      "SurveyID": "SV_eLnpGNWb3hM31cy",
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
		        "NextChoiceId": 4,
		        "NextAnswerId": 1,
		        "QuestionID": qid
		      }
		    }

		elem["Payload"]["DisplayLogic"] = add_cond_display("QID{}".format(0), disp_settings)
		survey_elements.append(elem)
	
	block_elements.append({
		"Type": "Page Break"
	})

# # start by asking respondent to enter MTurk worker id, add pagebreak
# mturk_worker_id = -10000
# qid = "QID{}".format(mturk_worker_id)

# survey_info["SurveyElements"][0]["Payload"].append({
# 	"Type": "Standard",
# 	"SubType": "",
# 	"Description": "Block {}".format(mturk_worker_id),
# 	"ID": "BL_{}".format(mturk_worker_id),
# 	"BlockElements": [],
# 	"Options": {
# 		"BlockLocking": "false",
# 		"RandomizeQuestions": "false",
# 		"BlockVisibility": "Collapsed",
# 	}
# })
# block_elements = survey_info["SurveyElements"][0]["Payload"][curr + 1]["BlockElements"]

# # append to flow payload
# survey_info["SurveyElements"][1]["Payload"]["Flow"].append(
# 	{
# 		"ID": "BL_{}".format(mturk_worker_id),
# 		"Type": "Block",
# 		"FlowID": "FL_{}".format(mturk_worker_id)
# 	}
# )

# block_elements.append({
# 	"Type": "Question",
# 	"QuestionID": qid,
# })

# elem = {
# 	"SurveyID": "SV_eLnpGNWb3hM31cy",
# 	"Element": "SQ",
# 	"PrimaryAttribute": qid,
# 	"SecondaryAttribute": "Enter your MTurk worker ID:",
# 	"TertiaryAttribute": None,
# 	"Payload": {
# 		"QuestionText": "Enter your MTurk worker ID:\n\n",
# 		"DefaultChoices": False,
# 		"QuestionID": qid,
# 		"QuestionType": "TE",
# 		"Selector": "SL",
# 		"Configuration": {
# 			"QuestionDescriptionOption": "UseText"
# 		},
# 		"QuestionDescription": "Enter your MTurk worker ID:",
# 		"Validation": {
# 			"Settings": {
# 				"ForceResponse": "OFF",
# 				"Type": "None"
# 			}
# 		},
# 		"GradingData": [],
# 		"Language": [],
# 		"NextChoiceId": 4,
# 		"NextAnswerId": 1,
# 		"SearchSource": {
# 			"AllowFreeResponse": "false"
# 		},
# 		"DataExportTag": qid,
# 	}
# }

# survey_elements.append(elem)
# block_elements.append({
# 	"Type": "Page Break"
# })
# curr += 1

curr_offset = curr
total_questions_done = 0
# start with all training headlines
for t in list(training_title_to_student.keys()):
	create_question(t, curr, list(range(num_students)), training_answers[curr - curr_offset], training = True)
	curr += 1
	total_questions_done += 1

# set score embedded data
set_score_id = -200
set_score_copy = copy.deepcopy(set_score)
set_score_copy["FlowID"] = "FL_{}".format(set_score_id)
flow_elements.append(set_score_copy)
set_score_id -= 1

# # add branch logic to kick respondent out of survey after training q's
eos_block_id = -1000
# training_thresh_mc_num = math.ceil(training_mc_weight * training_thresh_mc * training_length)
# training_thresh_te_num = math.ceil(training_te_weight * training_thresh_te * 2 * training_length)
# attention_thresh_mc_num = math.ceil(attention_mc_weight * attention_thresh_mc * attention_check_length)
# attention_thresh_te_num = math.ceil(attention_te_weight * attention_thresh_te * 2 * attention_check_length)
fl_id = -1
# flow_elements.append(create_branch_logic(branch_logic_template, fl_id, eos_block_id, training_thresh_mc_num, training_thresh_te_num, total_questions_done, segment = 0))
# end_survey_display_flow_id -= 1
# end_survey_flow_id -= 1
# set_end_id_flow_id -= 1
# fl_id -= curr_offset
# eos_block_id -= 1

num_blocks = len(attention_check_headlines)

for i in range(num_blocks):
	# print('block', i)
	# in every iteration
	# pick attention check number of attention check headlines
	curr_at_check = attention_check_headlines[i]

	# pick block size - attention check number of regular headlines
	regular_headline_idxes = {}
	regular_headline_to_student = {}
	curr_headlines = set(curr_at_check)
	# print('iter', student_assignments, '\n')
	for j in range(num_students):
		if len(student_assignments[j]) >= block_size - len(curr_at_check):
			regular_headline_idxes[j] = np.random.choice(student_assignments[j], size = block_size - len(curr_at_check), replace = False)
		elif len(student_assignments[j]) > 0:
			regular_headline_idxes[j] = student_assignments[j]
		else:
			continue
		
		# remove the chosen headline idxes from all student assignments
		student_assignments[j] = list(set(student_assignments[j]) - set(regular_headline_idxes[j]))
		# for sa in student_assignments.keys():
		# 	print('x', sa, student_assignments[sa], regular_headline_idxes[j])
		# 	student_assignments[sa] = list(set(student_assignments[sa]) - set(regular_headline_idxes[j]))
		regular_headlines = titles[np.array(regular_headline_idxes[j])]
		curr_headlines = curr_headlines.union(set(regular_headlines))
		for r in regular_headlines:
			if r in regular_headline_to_student:
				regular_headline_to_student[r].append(j)
			else:
				regular_headline_to_student[r] = [j]

		# print(j, 'regular headline to student', regular_headline_to_student, '\n')

		if j == 0:
			total_questions_done += block_size
	
	# shuffle attention check and regular headlines in a block
	np.random.shuffle(np.array(list(curr_headlines)))
	# print(curr_headlines)

	for c in curr_headlines:
		if c in regular_headline_to_student:
			# special display settings
			create_question(c, curr, regular_headline_to_student[c])
		else:
			create_question(c, curr, list(range(num_students)), attention_check_answers[c])
		curr += 1

	# set score embedded data
	set_score_copy = copy.deepcopy(set_score)
	set_score_copy["FlowID"] = "FL_{}".format(set_score_id)
	flow_elements.append(set_score_copy)
	set_score_id -= 1

	# curr_attention_thresh_mc_num = training_thresh_mc_num + attention_thresh_mc_num * (i + 1) #sum(calc_attention_thresh[:i + 1])
	# curr_attention_thresh_te_num = training_thresh_te_num + attention_thresh_te_num * (i + 1)
	# flow_elements.append(create_branch_logic(branch_logic_template, fl_id, eos_block_id, curr_attention_thresh_mc_num, curr_attention_thresh_te_num, total_questions_done, segment = 1))
	# end_survey_display_flow_id -= 1
	# end_survey_flow_id -= 1
	# set_end_id_flow_id -= 1
	# eos_block_id -= 1
	# fl_id -= 2

# create the rest of the questions for the remaining regular headlines
remaining_headlines = []
for student, remaining in student_assignments.items():
	remaining_headlines.extend(remaining)
remaining_headlines = list(set(remaining_headlines))
	
for r in remaining_headlines:
	# special display settings
	create_question(titles[r], curr, title_to_student[r])
	total_questions_done += 1
	curr += 1

set_end_id_copy = copy.deepcopy(set_end_id)
set_end_id_copy["EmbeddedData"][0]["Value"] = "$e{" + str(total_questions_done) + " * 100}${rand://int/100000:1000000}"
set_end_id_copy["FlowID"] = "FL_{}".format(set_end_id_flow_id)
flow_elements.append(set_end_id_copy)
set_end_id_flow_id -= 1

curr_end_survey_display = create_end_of_survey_logic(fl_id, eos_block_id, segment = 2)
end_survey_display_flow_id -= 1
end_survey_flow_id -= 1
flow_elements.append(curr_end_survey_display)

flow_elements.append({
	"Type": "EndSurvey",
	"FlowID": "FL_{}".format(end_survey_flow_id),
	"EndingType": "Advanced",
	"Options": {
		"Advanced": "true",
		"SurveyTermination": "Redirect",
		"EOSRedirectURL": "{}".format(eos_redirect_url)
	}
})

for eos_block in eos_payload_blocks:
	survey_info["SurveyElements"][0]["Payload"].append(eos_block)

with open(qsf_name, 'w') as f:
	json.dump(survey_info, f, ensure_ascii = False, indent = 2)

# test that all headlines in the MTurk dump are displayed to at least one user
curr_idx = 0
mturk_survey_q_dump = survey_elements[9:]
headlines_displayed = {}
count = 0
while curr_idx < len(mturk_survey_q_dump):
	curr_headline = mturk_survey_q_dump[curr_idx]["Payload"]["QuestionDescription"]
	if not sum([i in curr_headline for i in ["End of survey", "Timing", "Do you think", "(leave blank if not indicated or unclear)"]]):
		if curr_headline in headlines_displayed:
			count += 1
			headlines_displayed[curr_headline] += 1
		else:
			headlines_displayed[curr_headline] = 1
	curr_idx += 1

displayed = set(headlines_displayed.keys())
att_flat = set(np.array(attention_check_headlines).flatten())
assert(len(displayed.intersection(set(training_headlines))) == len(training_headlines))
assert(len(displayed.intersection(att_flat)) == num_blocks * attention_check_length)
assert(len(displayed.intersection(set(titles_to_classify))) == num_headlines)
