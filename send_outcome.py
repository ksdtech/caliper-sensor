#!/usr/bin/env python

import caliper
import caliper.events as events
import caliper.profiles as profiles
from builder import *

builder = Builder()
api_key = builder.basic_auth('caliper', 'couchdb')

config = caliper.HttpOptions(
    host='http://127.0.0.1:5984/caliper_events/',
    auth_scheme='Basic',
    api_key=api_key)

sensor = caliper.build_sensor_from_config(
    sensor_id=builder.sensor_id(1),
    config_options=config)

# Here, you will have caliper entity representations of the various
# learning objects and entities in your wider system, and you provide
# them into the constructor for the event that has just happened.
#
# Note that you don't have to pass an action into the constructor because
# the NavigationEvent only supports one action, part of the
# Caliper base profile: caliper.profiles.CaliperProfile.Actions['NAVIGATED_TO']
#

# Example Assessment Sequence - 5.3
#
# Actors:
#  Student
#  LMS
#  Assessment EduApp
#  Grading Engine or Teacher
#

# Course, section, assessment, assessment_item, section_group
section = Section('Math 7', '104', '7177', '4', '1617', 'FY')
course_entity = builder.build_course(section)
section_entity = builder.build_section(course_entity, section.section_number)

assessment = Assessment('44001', 'Read George Washington', 2, 2, 100.0)
assessment_entity = builder.build_assessment(section_entity, assessment)


# AsssementItem fields not used
#    description - Description of Entity
#    alignedLearningObjective - Associated Learning Objectives as context. List of Strings.
#    keywords - Associated Topics as context. List of Strings.
#    dateCreated
#    dateModified
#    datePublished
#    dateToActivate - Date that the assignable object is Active
#    dateToShow - Date that the assignable object shows to students
#    dateToStartOn - Date that the assignable object is allowed to be started by Agent
#    dateToSubmit - Date that the assignable object should be submitted
#    isTimeDependent - True if the time to answer the question is important and should be recorded
#    objectType - List of Strings. Note: This property is not currently used and may be removed in a future version

item = AssessmentItem('44001.1', 'Washington Quiz Question 1', 2, 2, 10.0)
assessment_item_entity = builder.build_assessment_item(assessment_entity, item)

# Student actor
student_id = '123456'
ssid = '10736344450'
student_actor = builder.build_student(student_id, ssid)

# Section group (for learning context)
group_id = '1'
group_name = 'All Students'
section_group_entity = builder.build_section_group(section_entity, group_id, group_name)

# Section enrollment (for learning context)
section_enrollment_entity = builder.build_section_enrollment(section_entity, student_actor)

# Event sequence:
# 1. The student navigates to an assessment that was assigned in the LMS using
#    the LMS Assessment Tool. Sensor generates an navigatedEvent with the
#    action of navigated to.

federated_session_entity = builder.build_federated_session(student_actor, '4585130')
tool_id = 'https://successnet.pearson.com'
tool_name = 'Pearson SuccessNet'

learning_context = builder.build_learning_context(section_group_entity,
    section_enrollment_entity, federated_session_entity, tool_id, tool_name)

course_page_url = 'https://www.kentfieldschools.org/kent/classes/math7/index.html'
course_page_title = 'Welcome to Math 7'
course_landing_page = builder.build_course_landing_page(course_page_url, course_page_title)

navigation_resource = builder.build_epub_vol43()
navigation_target   = builder.build_epub_subchap431()

event = events.NavigationEvent(
    edApp = learning_context.edApp,
    group = learning_context.group,
    membership = learning_context.membership,
    actor = student_actor,
    event_object = navigation_resource,
    # action is set in NavigationEvent constructor
    generated = None,
    navigatedFrom = course_landing_page,
    target = navigation_target,
    endedAtTime = builder.now(),
    eventTime = builder.now())
sensor.send(event)


# 2. The student starts the assignment in the LMS Sensor sends AssignableEvent
#    with the action of started and generates an attempt Object.
#
# Generated Attempt properties
#    count
#    startedAtTime
#    endedAtTime
#    duration

assessment_attempt_id = '1'
assessment_attempt_entity = builder.build_assessment_attempt(
    assessment_entity, student_actor, assessment_attempt_id, 1)

event = events.AssignableEvent(
    edApp = learning_context.edApp,
    group = learning_context.group,
    membership = learning_context.membership,
    actor = student_actor,
    action = profiles.AssignableProfile.Actions['STARTED'],
    event_object = assessment_entity,
    generated = assessment_attempt_entity,
    eventTime = builder.now())
sensor.send(event)


# 3. The student starts the assessment in the Assessment EduApp. Sensor sends
#    AssessmentEvent with the action of started.
event = events.AssessmentEvent(
    edApp = learning_context.edApp,
    group = learning_context.group,
    membership = learning_context.membership,
    actor = student_actor,
    action = profiles.AssessmentProfile.Actions['STARTED'],
    event_object = assessment_entity,
    generated = assessment_attempt_entity,
    eventTime = builder.now())
sensor.send(event)


# 4. The student starts question 1 in the assessment in the Assessment EduApp.
#    Sensor sends AssessmentItemEvent with the assessmentItem action of started.
item_attempt_id = '11'
item_attempt_entity = builder.build_assessment_item_attempt(
    assessment_item_entity, student_actor, item_attempt_id, 1)

event = events.AssessmentItemEvent(
    edApp = learning_context.edApp,
    group = learning_context.group,
    membership = learning_context.membership,
    actor = student_actor,
    action = profiles.AssessmentItemProfile.Actions['STARTED'],
    isTimeDependent = False,
    event_object = assessment_item_entity,
    generated = item_attempt_entity,
    eventTime = builder.now())
sensor.send(event)


# 5. The student completes question 1. Sensor sends AssessmentItemEvent with
#    the assessmentItem action of completed.
#
# Generated Response properties
#    startedAtTime
#    values
#    endedAtTime
#    duration

item_attempt_entity.endedAtTime = builder.now()
item_attempt_entity.duration = builder.duration(
    item_attempt_entity.startedAtTime,
    item_attempt_entity.endedAtTime)

response = AssessmentItemResponse('44001.1.X', ['February 22'])
response_entity = builder.build_fill_in_blank_response(
    item_attempt_entity, student_actor, response)
response_entity.endedAtTime = item_attempt_entity.startedAtTime
response_entity.duration = builder.duration(
    response_entity.startedAtTime,
    response_entity.endedAtTime)

event = events.AssessmentItemEvent(
    edApp = learning_context.edApp,
    group = learning_context.group,
    membership = learning_context.membership,
    actor = student_actor,
    action = profiles.AssessmentItemProfile.Actions['COMPLETED'],
    isTimeDependent = False,
    event_object = assessment_item_entity,
    generated = response_entity,
    eventTime = builder.now())
sensor.send(event)


# 6. Steps 4-5 repeat for each question in the assignment.
# 7. Student submits the assessment in the Assessment EduApp.
#    Sensor send an AssessmentEvent with the action of submitted.
assessment_attempt_entity.endedAtTime = builder.now()
assessment_attempt_entity.duration = builder.duration(
    assessment_attempt_entity.startedAtTime,
    assessment_attempt_entity.endedAtTime)

event = events.AssessmentEvent(
    edApp = learning_context.edApp,
    group = learning_context.group,
    membership = learning_context.membership,
    actor = student_actor,
    action = profiles.AssessmentProfile.Actions['SUBMITTED'],
    event_object = assessment_entity,
    generated = assessment_attempt_entity,
    eventTime = builder.now())
sensor.send(event)


# 8. Assessment autograded by grading engine.
#    Sensor generates an OutcomeEvent with the action of graded, ncluding the
#    attempt – result pairing.
result = AssessmentResult('Good job', 95.0)
result_entity = builder.build_assessment_result(
    assessment_attempt_entity,
    student_actor, learning_context.edApp, result)

event = events.OutcomeEvent(
    edApp = learning_context.edApp,
    group = learning_context.group,
    membership = learning_context.membership,
    actor = learning_context.edApp, # or teacher?
    action = profiles.OutcomeProfile.Actions['GRADED'],
    event_object = assessment_attempt_entity,
    generated = result_entity,
    eventTime = builder.now())
sensor.send(event)
