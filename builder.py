# -*- coding: utf-8 -*-
# Caliper-python testing package (testing util functions)
#
# This file is part of the IMS Caliper Analytics(tm) and is licensed to IMS
# Global Learning Consortium, Inc. (http://www.imsglobal.org) under one or more
# contributor license agreements. See the NOTICE file distributed with this
# work for additional information.
#
# IMS Caliper is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# IMS Caliper is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.standard_library import install_aliases
install_aliases()
from future.utils import with_metaclass
from builtins import *

from base64 import b64decode, b64encode
from datetime import datetime, timedelta
import sys, os
import json

# python 3.5
from urllib.parse import quote, unquote

import caliper

### NOTE
###
### FIXTURE_DIR assumes that the caliper fixtures repo contents are symlinked
### into the caliper_tests module's directory in a 'fixtures' subdirectory so
### that the tests can find all the json fixture files in that sub-directory
###


class Section(object):
    def __init__(self, course_name, school_id, course_number, section_number, year_abbr, term_abbr):
        self.course_name = course_name
        self.school_id = school_id
        self.course_number = course_number
        self.section_number = section_number
        self.year_abbr = year_abbr # 1617
        self.term_abbr = term_abbr # FY, T1, etc.


class Assessment(object):
    def __init__(self, id, name, max_attempts, max_submits, max_score):
        self.id = id
        self.name = name
        self.max_attempts = max_attempts
        self.max_submits = max_submits
        self.max_score = max_score


class AssessmentItem(object):
    def __init__(self, id, name, max_attempts, max_submits, max_score):
        self.id = id
        self.name = name
        self.max_attempts = max_attempts
        self.max_submits = max_submits
        self.max_score = max_score


class AssessmentItemResponse(object):
    def __init__(self, id, values):
        self.id = id
        self.values = values


class AssessmentResult(object):
    def __init__(self, comment, normal_score):
        self.comment = comment
        self.normal_score = normal_score
        self.extra_credit_score = 0.0
        self.penalty_score = 0.0
        self.total_score = normal_score
        self.curve_factor = 0.0
        self.curved_total_score = normal_score


class Builder(object):
    _FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../caliper_tests/fixtures')
    _FIXTURE_OUT_DIR = os.path.join(os.path.dirname(__file__), 'fixtures_out')

    _EVENTTIME = '2015-09-15T10:15:00.000Z'
    _CREATETIME = '2015-08-01T06:00:00.000Z'
    _MODTIME = '2015-09-02T11:30:00.000Z'
    _EVENT_SEND_TIME = '2015-09-15T11:05:01.000Z'
    _STARTTIME = '2015-09-15T10:15:00.000Z'
    _ENDTIME = '2015-09-15T11:05:00.000Z'
    _PUBTIME = '2015-08-15T09:30:00.000Z'
    _ACTTIME = '2015-08-16T05:00:00.000Z'
    _SHOWTIME = _ACTTIME
    _STARTONTIME = _ACTTIME
    _SUBMITTIME = '2015-09-28T11:59:59.000Z'
    _DURATION = 'PT3000S'
    _MEDIA_CURTIME = 710
    _MEDIA_DURTIME = 1420
    _VERNUM = '1.0'
    _VERED = '2nd ed.'

    _ENTITY_ID_BASE = 'https://kentfieldschools.org'
    _SENSOR_ID_FORMAT             = '{0!s}/sensor/{1!s}'
    _FEDERATED_SESSION_ID_FORMAT  = '{0!s}/session/{1!s}'
    _STUDENT_ID_FORMAT            = '{0!s}/student/{1!s}'
    _COURSE_ID_FORMAT             = '{0!s}/year/{1!s}/school/{2!s}/course/{3!s}'

    def __init__(self, id_base=_ENTITY_ID_BASE, debug=True):
        self.id_base = id_base

    def basic_auth(self, username, password):
        unencoded_bytes = '{0!s}:{1!s}'.format(quote(username), quote(password)).encode('utf-8')
        encoded_bytes = b64encode(unencoded_bytes)
        return encoded_bytes.decode('utf-8')

    def now(self):
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def duration(self, start, end):
        tstart = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
        tend = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
        tdelta = timedelta()
        if tend > tstart:
            tdelta = tend - tstart

        # split seconds to larger units
        seconds = tdelta.total_seconds()
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        days, hours, minutes = map(int, (days, hours, minutes))
        seconds = round(seconds, 6)

        ## build date
        date = ''
        if days:
            date = '%sD' % days

        ## build time
        time = 'T'
        # hours
        bigger_exists = date or hours
        if bigger_exists:
            time += '{:02}H'.format(hours)
        # minutes
        bigger_exists = bigger_exists or minutes
        if bigger_exists:
          time += '{:02}M'.format(minutes)
        # seconds
        if seconds.is_integer():
            seconds = '{:02}'.format(int(seconds))
        else:
            # 9 chars long w/leading 0, 6 digits after decimal
            seconds = '%09.6f' % seconds
        # remove trailing zeros
        seconds = seconds.rstrip('0')
        time += '{}S'.format(seconds)
        return 'P' + date + time

    def academic_session(self, section):
        return '{0!s}-{1!s}'.format(section.year_abbr, section.term_abbr)

    def sensor_id(self, id):
        return self._SENSOR_ID_FORMAT.format(self.id_base, id)

    def federated_session_id(self, id):
        return self._FEDERATED_SESSION_ID_FORMAT.format(self.id_base, id)

    def student_id(self, id):
        return self._STUDENT_ID_FORMAT.format(self.id_base, id)

    def course_id(self, section):
        return self._COURSE_ID_FORMAT.format(self.id_base, section.year_abbr, section.school_id, section.course_number)

    def section_id(self, course_entity, section_id):
        return '{0!s}/section/{1!s}'.format(course_entity.id, section_id)

    def section_group_id(self, section_entity, group_id):
        return '{0!s}/group/{1!s}'.format(section_entity.id, group_id)

    def section_enrollment_id(self, section_entity, student_id):
        return '{0!s}/student/{1!s}'.format(section_entity.id, student_id)

    def assessment_id(self, section_entity, assessment_id):
        return '{0!s}/assessment/{1!s}'.format(section_entity.id, assessment_id)

    def assessment_attempt_id(self, assessment_entity, attempt_id):
        return '{0!s}/a/{1!s}'.format(assessment_entity.id, attempt_id)

    def assessment_item_id(self, assessment_entity, item_id):
        return '{0!s}/item/{1!s}'.format(assessment_entity.id, item_id)

    def assessment_item_attempt_id(self, assessment_item_entity, attempt_id):
        return '{0!s}/a/{1!s}'.format(assessment_item_entity.id, attempt_id)

    def assessment_item_response_id(self, item_attempt_entity, response_id):
        return '{0!s}/r/{1!s}'.format(item_attempt_entity.id, response_id)

    def assessment_result_id(self, assessment_attempt_entity):
        return '{0!s}/result'.format(assessment_attempt_entity.id)

    def get_fixture(self, fixture_name):
        loc = os.path.join(_FIXTURE_DIR, fixture_name+'.json')
        with open(loc,'r') as f:
            return json.dumps(json.load(f), sort_keys=True)

    ## without DEBUG, a no-op: useful to generate more readable/diffable
    ## side-by-side comparisons of the stock fixtures with the generated events
    def put_fixture(self, fixture_name, caliper_entity):
        if self.debug:
            loc = os.path.join(_FIXTURE_DIR, fixture_name)
            with open(loc+'_out.json', 'w') as f:
                f.write(caliper_entity.as_json()
                        .replace('{"','{\n"')
                        .replace(', "',',\n"')
                        )
            with open(loc+'.json', 'w') as f:
                f.write(get_fixture(fixture_name)
                        .replace('{"','{\n"')
                        .replace(', "',',\n"')
                        )
        else:
            pass


    ### Sensor/event payloads ###
    ## build a caliper envelope ##
    def get_caliper_envelope(self, sensor=None, caliper_entity_list=None):
        return caliper.request.Envelope(
            data = caliper_entity_list,
            send_time = self._EVENT_SEND_TIME,
            sensor_id = sensor.id
            )

    ### Shared entity resources ###
    def build_student(self, student_id, ssid):
        return caliper.entities.Person(
            entity_id = self.student_id(student_id),
            extensions = {
                "local_id": student_id,
                "ssid": ssid
            },
            dateCreated = self._CREATETIME,
            dateModified = self._MODTIME
            )

    def build_course(self, section):
        return caliper.entities.CourseOffering(
            entity_id = self.course_id(section),
            academicSession = self.academic_session(section),
            courseNumber = section.course_number,
            name = section.course_name,
            dateCreated = self._CREATETIME,
            dateModified = self._MODTIME
            )

    def build_section(self, course_entity, section_id):
        return caliper.entities.CourseSection(
            entity_id = self.section_id(course_entity, section_id),
            academicSession = course_entity.academicSession,
            courseNumber = course_entity.courseNumber,
            name = course_entity.name,
            subOrganizationOf = course_entity,
            dateCreated = self._CREATETIME,
            dateModified = self._MODTIME
            )

    def build_section_group(self, section_entity, group_id, group_name):
        return caliper.entities.Group(
            entity_id = self.section_group_id(section_entity, group_id),
            name = group_name,
            subOrganizationOf = section_entity,
            dateCreated = self._CREATETIME
            )

    def build_section_enrollment(self, section_entity, student_entity):
        student_id = student_entity.extensions["local_id"]
        return caliper.entities.Membership(
            entity_id = self.section_enrollment_id(section_entity, student_id),
            member = student_entity,
            organization = section_entity,
            description = 'Roster entry',
            name = section_entity.name,
            roles = [caliper.entities.Role.Roles['LEARNER']],
            status = caliper.entities.Status.Statuses['ACTIVE'],
            dateCreated = self._CREATETIME
            )

    def build_federated_session(self, actor, session_id):
        return caliper.entities.Session(
            entity_id = self.federated_session_id(session_id),
            actor = actor,
            dateCreated = self._CREATETIME,
            startedAtTime = self._STARTTIME
            )

    def build_learning_context(self, section_group_entity,
        section_enrollment_entity, federated_session_entity,
        tool_id, tool_name):
        return caliper.entities.LearningContext(
            edApp = caliper.entities.SoftwareApplication(
                entity_id = tool_id,
                name = tool_name,
                dateCreated = self._CREATETIME
                ),
            group = section_group_entity,
            membership = section_enrollment_entity,
            session = federated_session_entity
            )

    ## build a course landing page
    def build_course_landing_page(self, url, title):
        return caliper.entities.WebPage(
            entity_id = url,
            name = title,
            dateCreated = self._CREATETIME,
            dateModified = self._MODTIME,
            version = self._VERNUM
            )

    ## build a test EPUB volume
    def build_epub_vol43(self):
        return caliper.entities.EpubVolume(
            entity_id = 'https://example.com/viewer/book/34843#epubcfi(/4/3)',
            name = 'The Glorious Cause: The American Revolution, 1763-1789 (Oxford History of the United States)',
            dateCreated = self._CREATETIME,
            dateModified = self._MODTIME,
            version = self._VERED
            )

    def build_epub_subchap431(self):
        return caliper.entities.EpubSubChapter(
            entity_id = 'https://example.com/viewer/book/34843#epubcfi(/4/3/1)',
            name = 'Key Figures: George Washington',
            isPartOf = self.build_epub_vol43(),
            dateCreated = self._CREATETIME,
            dateModified = self._MODTIME,
            version = self._VERED
            )

    def build_assessment(self, section_entity, assessment):
        return caliper.entities.Assessment(
            entity_id = self.assessment_id(section_entity, assessment.id),
            name = assessment.name,
            datePublished = self._PUBTIME,
            dateToActivate = self._ACTTIME,
            dateToShow = self._SHOWTIME,
            dateToStartOn = self._STARTONTIME,
            dateToSubmit = self._SUBMITTIME,
            maxAttempts = assessment.max_attempts,
            maxSubmits = assessment.max_submits,
            maxScore = assessment.max_score, # WARN original value is 5.0d, says Java impl
            dateCreated = self._CREATETIME,
            dateModified = self._MODTIME,
            version = self._VERNUM
            )

    ### Assessment Profile and Outcome Profile ###
    ## build a test assessment
    def build_assessment_item(self, assessment_entity, item):
        return caliper.entities.AssessmentItem(
            entity_id = self.assessment_item_id(assessment_entity, item.id),
            name = item.name,
            isPartOf = assessment_entity,
            version = self._VERNUM,
            maxAttempts = item.max_attempts,
            maxSubmits = item.max_submits,
            maxScore = item.max_score
            )

    ## build a test assessment attempt
    def build_assessment_attempt(self, assessment_entity, actor,
        attempt_id, count):
        start = self.now()
        return caliper.entities.Attempt(
            entity_id = self.assessment_attempt_id(assessment_entity, attempt_id),
            assignable = assessment_entity,
            actor = actor,
            count = count,
            dateCreated = start,
            startedAtTime = start
            )

    ## build a test assessment item attempt
    def build_assessment_item_attempt(self, assessment_item_entity, actor,
        attempt_id, count):
        start = self.now()
        return caliper.entities.Attempt(
            entity_id = self.assessment_item_attempt_id(assessment_item_entity, attempt_id),
            assignable = assessment_item_entity.isPartOf,
            actor = actor,
            count = count,
            dateCreated = start,
            startedAtTime = start
            )

    ## build a test assessment item response
    # response.values is a list
    def build_fill_in_blank_response(self, item_attempt_entity, actor, response):
        start = self.now()
        return caliper.entities.FillinBlankResponse(
            entity_id = self.assessment_item_response_id(item_attempt_entity, response.id),
            assignable = item_attempt_entity.assignable,
            actor = actor,
            attempt = item_attempt_entity,
            dateCreated = start,
            startedAtTime = start,
            values = response.values
            )

    # response.values is a single string
    def build_multiple_choice_response(self, item_attempt_entity, actor, response):
        start = self.now()
        return caliper.entities.MultipleChoiceResponse(
            entity_id = self.assessment_item_response_id(item_attempt_entity, response.id),
            assignable = item_attempt_entity.assignable,
            actor = actor,
            attempt = item_attempt_entity,
            dateCreated = start,
            startedAtTime = start,
            values = response.values[0]
            )

    # response.values is a list of strings
    def build_multiple_response_response(self, item_attempt_entity, actor, response):
        start = self.now()
        return caliper.entities.MultipleResponseResponse(
            entity_id = self.assessment_item_response_id(item_attempt_entity, response.id),
            assignable = item_attempt_entity.assignable,
            actor = actor,
            attempt = item_attempt_entity,
            dateCreated = start,
            startedAtTime = start,
            values = response.values
            )

    # response.values is a list of strings
    def build_select_text_response(self, item_attempt_entity, actor, response):
        start = self.now()
        return caliper.entities.SelectTextResponse(
            entity_id = self.assessment_item_response_id(item_attempt_entity, response.id),
            assignable = item_attempt_entity.assignable,
            actor = actor,
            attempt = item_attempt_entity,
            dateCreated = start,
            startedAtTime = start,
            values = response.values
            )

    # response.values is a single string
    def build_true_false_response(self, item_attempt_entity, actor, response):
        start = self.now()
        return caliper.entities.TrueFalseResponse(
            entity_id = self.assessment_item_response_id(item_attempt_entity, response.id),
            assignable = item_attempt_entity.assignable,
            actor = actor,
            attempt = item_attempt_entity,
            dateCreated = start,
            startedAtTime = start,
            values = response.values[0]
            )

    ## build a test assessment result
    def build_assessment_result(self, assessment_attempt_entity,
        actor, scored_by, result):
        return caliper.entities.Result(
            entity_id = self.assessment_result_id(assessment_attempt_entity),
            actor = actor,
            assignable = assessment_attempt_entity.assignable,
            comment = result.comment,
            curvedTotalScore = result.curved_total_score,
            curveFactor = result.curve_factor,
            extraCreditScore = result.extra_credit_score,
            normalScore = result.normal_score,
            penaltyScore = result.penalty_score,
            scoredBy = scored_by,
            totalScore = result.total_score,
            dateCreated = self.now()
            )
