import boto3
import pandas as pd
import lxml.etree as etree

generate_qual_hit = True
questions_filename = 'press_release_questions.xml'
answers_filename = 'color_ans_key.xml' #'press_release_answers.xml'

q_id = 0

training_test_q_filename = '../survey_data/selected_training_test.csv'

training_test_df = pd.read_csv(training_test_q_filename)
training_test_qs = list(training_test_df['Title'])
training_test_acq = list(training_test_df['Acq_Status'])
training_test_c1 = list(training_test_df['Company 1'])
training_test_c2 = list(training_test_df['Company 2'])

print(training_test_c2)

# generate qualification test in XML format
question_format = """
<QuestionForm xmlns='http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd'>
    {}
</QuestionForm>
"""

acq_q_format = """
<Question>
    <QuestionIdentifier>q_{}</QuestionIdentifier>
    <DisplayName>Q_{}</DisplayName>
    <IsRequired>true</IsRequired>
    <QuestionContent>
    <Text> Headline: {} \n\nDo you think that this headline refers to an acquisition or merger? </Text>
    </QuestionContent>
    <AnswerSpecification>
    <SelectionAnswer>
        <StyleSuggestion>radiobutton</StyleSuggestion>
        <Selections>
        <Selection>
            <SelectionIdentifier>acquisition</SelectionIdentifier>
            <Text>Acquisition</Text>
        </Selection>
        <Selection>
            <SelectionIdentifier>merger</SelectionIdentifier>
            <Text>Merger</Text>
        </Selection>
        <Selection>
            <SelectionIdentifier>neither</SelectionIdentifier>
            <Text>Neither / Not sure / Unclear</Text>
        </Selection>
        </Selections>
    </SelectionAnswer>
    </AnswerSpecification>
</Question>
"""

c1_q_format = """
<Question>
    <QuestionIdentifier>q_{}</QuestionIdentifier>
    <DisplayName>Q_{}</DisplayName>
    <IsRequired>true</IsRequired>
    <QuestionContent>
    <Text> ACQUIRER (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.): </Text>
    </QuestionContent>
    <AnswerSpecification>
    <FreeTextAnswer>
    </FreeTextAnswer>
    </AnswerSpecification>
</Question>
"""

c2_q_format = """
<Question>
    <QuestionIdentifier>q_{}</QuestionIdentifier>
    <DisplayName>Q_{}</DisplayName>
    <IsRequired>true</IsRequired>
    <QuestionContent>
    <Text> ACQUIRED (Leave blank if not indicated or unclear. You are encouraged to copy-paste from the headline text.): </Text>
    </QuestionContent>
    <AnswerSpecification>
    <FreeTextAnswer>
    </FreeTextAnswer>
    </AnswerSpecification>
</Question>
"""

all_qs = ""
for headline in training_test_qs:
    curr_acq_q = acq_q_format.format(q_id, q_id, headline)
    q_id += 1
    curr_c1_q = c1_q_format.format(q_id, q_id)
    q_id += 1
    curr_c2_q = c2_q_format.format(q_id, q_id)
    q_id += 1
    all_qs += curr_acq_q + curr_c1_q + curr_c2_q
final_questions = question_format.format(all_qs)

with open(questions_filename, 'w') as f:
    f.write(final_questions)
    f.close()

# generate qualification answer key in XML format
answer_format = """
<AnswerKey xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/AnswerKey.xsd">
  {}
</AnswerKey>
"""

acq_ans_format = """
<Question>
    <QuestionIdentifier>{}</QuestionIdentifier>
    <AnswerOption>
        <SelectionIdentifier>acquisition</SelectionIdentifier>
        <AnswerScore>{}</AnswerScore>
    </AnswerOption>
    <AnswerOption>
        <SelectionIdentifier>merger</SelectionIdentifier>
        <AnswerScore>{}</AnswerScore>
    </AnswerOption>
    <AnswerOption>
        <SelectionIdentifier>neither</SelectionIdentifier>
        <AnswerScore>{}</AnswerScore>
    </AnswerOption>
</Question>
"""

c1_ans_format = """
<Answer>
    <QuestionIdentifier>{}</QuestionIdentifier>
    <FreeText>C3</FreeText>
</Answer>
"""

c2_ans_format = """
"""

all_ans = ""
for q in range(len(training_test_qs)):


if generate_qual_hit:
    questions = open(questions_filename, mode = 'r').read()
    answers = open(answers_filename, mode = 'r').read()

    mturk = boto3.client(
        'mturk', 
        aws_access_key_id = 'AKIA4PDKL4AVWBMFRI2Y', # iam user access key
        aws_secret_access_key = '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', # iam user secret key
        region_name = 'us-east-1', 
        endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com')
    qual_response = mturk.create_qualification_type(
        Name = 'Press Release Acquisition Classification Training Test',
        Keywords = 'test, qualification, acquisition',
        Description = 'This is a brief test.',
        QualificationTypeStatus = 'Active',
        Test = questions,
        AnswerKey = answers,
        TestDurationInSeconds = 3000,
    )

    qual_type_id = qual_response['QualificationType']['QualificationTypeId']
    print(qual_type_id)

    hit = mturk.create_hit(
        Reward = '0.01',
        LifetimeInSeconds = 36000,
        AssignmentDurationInSeconds = 6000,
        MaxAssignments = 9,
        Title = 'A HIT with a qualification test',
        Description = 'A test HIT that requires a certain score from a qualification test to accept.',
        Keywords = 'boto, qualification, test',
        Question = questions,
        AutoApprovalDelayInSeconds = 0,
        QualificationRequirements = [{
            'QualificationTypeId': qual_type_id,
            'Comparator': 'EqualTo',
            'IntegerValues':[100]}]
        )

# delete open hits / cleanup

# setup resource: https://katherinemwood.github.io/post/qualifications/

# - separate / bold headlines
# - different background for questions? 
# - respnsiveness on diff devices

# - 
