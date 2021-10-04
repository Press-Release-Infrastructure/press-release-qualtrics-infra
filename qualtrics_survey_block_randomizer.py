import pandas as pd 
import json
import math
import numpy as np

# replace this with LexisNexis headlines (right now this is Crunchbase)
all_titles = list(pd.read_csv("all_headlines.csv", encoding = 'utf8')["BodyHeadline"])

num_headlines = 10 #1000
subset = 5 #100
survey_name = "Acquisition Headline Survey (Randomizer, Small Example)"
titles = list(all_titles)

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
            "Type": "BlockRandomizer",
            "FlowID": "FL_4",
            "SubSet": subset,
            "EvenPresentation": True,
            "Flow": [],
          }
        ],
        "Properties": {
          "Count": 11,
          "RemovedFieldsets": []
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

survey_elements = survey_info["SurveyElements"]
i = 1
num_subparts = 5
counter = 2
block_counter = 2

for curr_title in titles[:num_headlines]:
	# add to block elements
	req_qid = "QID{}".format(i + 1)

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
	survey_info["SurveyElements"][1]["Payload"]["Flow"][0]["Flow"].append({
		"Type": "Block",
		"ID": "BL_{}".format(block_counter),
		"FlowID": "FL_{}".format(block_counter),
		"Autofill": [],
		})
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
		        "NextChoiceId": "QID{}".format(i - 2),
		        "NextAnswerId": 1,
		        "QuestionID": qid
		      }
		    }

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

with open('qualtrics_survey_block_randomizer_small.qsf', 'w') as f:
	json.dump(survey_info, f, ensure_ascii = False, indent = 2)





