#!/usr/bin/env python

"""models.py

Conference server-side Python App Engine data & ProtoRPC models

$Id: models.py,v 1.1 2016/01/08 22:01:10 v2saumb Exp $

created/forked from conferences.py by v2saumb on 2016/01/08

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class SESSION_TYPE(messages.Enum):
    NOT_SPECIFIED = 0
    WORKSHOP = 1
    LECTURE = 2
    THINKTANK = 3
    SKILLBUILDER = 4
    EXPERTSPEAK = 5

class TeeShirtSize(messages.Enum):
    """TeeShirtSize -- t-shirt size enumeration value"""
    NOT_SPECIFIED = 1
    XS_M = 2
    XS_W = 3
    S_M = 4
    S_W = 5
    M_M = 6
    M_W = 7
    L_M = 8
    L_W = 9
    XL_M = 10
    XL_W = 11
    XXL_M = 12
    XXL_W = 13
    XXXL_M = 14
    XXXL_W = 15

# creating entity for speaker
class Speaker(ndb.Model):
    """Speaker -- Speaker object"""
    speakerUserId = ndb.StringProperty()
    topics = ndb.StringProperty(repeated=True)
    aboutSpeaker = ndb.StringProperty()

# entity for Session
class ConfSession(ndb.Model):
    session_name = ndb.StringProperty(required=True)
    highlights = ndb.StringProperty()
    speaker =  ndb.StringProperty()
    duration = ndb.IntegerProperty(default=30)
    type_of_session = ndb.StringProperty(default="NOT_SPECIFIED")
    date = ndb.DateProperty()
    start_time = ndb.TimeProperty()
    venue = ndb.StringProperty()

# Entity for Conference
class Conference(ndb.Model):
    """Conference -- Conference object"""
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    organizerUserId = ndb.StringProperty()
    topics = ndb.StringProperty(repeated=True)
    city = ndb.StringProperty()
    startDate = ndb.DateProperty()
    month = ndb.IntegerProperty()
    endDate = ndb.DateProperty()
    maxAttendees = ndb.IntegerProperty()
    seatsAvailable = ndb.IntegerProperty()

# Entity for Profile
class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    teeShirtSize = ndb.StringProperty(default='NOT_SPECIFIED')
    conferenceKeysToAttend = ndb.StringProperty(repeated=True)
    sessionWishList = ndb.StringProperty(repeated=True)

# conference session Form
class ConfSessionForm(messages.Message):
    session_name = messages.StringField(1)
    highlights = messages.StringField(2)
    speaker =  messages.StringField(3)
    duration = messages.IntegerField(4)
    type_of_session = messages.EnumField('SESSION_TYPE',5)
    date = messages.StringField(6)
    start_time = messages.StringField(7)
    websafeKey = messages.StringField(8)
    venue = messages.StringField(9)
    confName=messages.StringField(10)
# speaker form
class SpeakerForm(messages.Message):
    """Speaker -- Speaker object"""
    speakerUserId = messages.StringField(1)
    topics = messages.StringField(2,repeated=True)
    aboutSpeaker = messages.StringField(3)
    displayName = messages.StringField(4)
    websafeKey = messages.StringField(5)



class FindSpeakerForm(messages.Message):
    displayName = messages.StringField(1)
    websafeKey = messages.StringField(2)

# Allows to return multiple Speakers
class SpeakerForms(messages.Message):
    """SpeakerForm -- multiple SpeakerForm outbound form message"""
    items = messages.MessageField(SpeakerForm, 1, repeated=True)

# return multiple sessions
class ConfSessionForms(messages.Message):
    """ConfSesionForms -- multiple Conference session outbound form message"""
    items = messages.MessageField(ConfSessionForm, 1, repeated=True)


class ConferenceForm(messages.Message):
    """ConferenceForm -- Conference outbound form message"""
    name = messages.StringField(1)
    description = messages.StringField(2)
    organizerUserId = messages.StringField(3)
    topics = messages.StringField(4, repeated=True)
    city = messages.StringField(5)
    startDate = messages.StringField(6)  # DateTimeField()
    month = messages.IntegerField(7)
    maxAttendees = messages.IntegerField(8)
    seatsAvailable = messages.IntegerField(9)
    endDate = messages.StringField(10)  # DateTimeField()
    websafeKey = messages.StringField(11)
    organizerDisplayName = messages.StringField(12)
    


class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName = messages.StringField(1)
    teeShirtSize = messages.EnumField('TeeShirtSize', 2)

class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)
    teeShirtSize = messages.EnumField('TeeShirtSize', 3)
    conferenceKeysToAttend = messages.StringField(4,repeated=True)
    sessionWishList = messages.StringField(5,repeated=True)

class ConferenceForms(messages.Message):
    """ConferenceForms -- multiple Conference outbound form message"""
    items = messages.MessageField(ConferenceForm, 1, repeated=True)


class ConferenceQueryForm(messages.Message):
    """ConferenceQueryForm -- Conference query inbound form message"""
    field = messages.StringField(1)
    operator = messages.StringField(2)
    value = messages.StringField(3)

#  form for passing multiple query filters
class ConferenceQueryForms(messages.Message):
    """ConferenceQueryForms -- multiple ConferenceQueryForm inbound form message"""
    filters = messages.MessageField(ConferenceQueryForm, 1, repeated=True)


# needed for conference registration
class BooleanMessage(messages.Message):
    """BooleanMessage-- outbound Boolean value message"""
    data = messages.BooleanField(1)

class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT
    
# adding string message for the announcements
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)