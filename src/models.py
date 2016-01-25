#!/usr/bin/env python

"""models.py

Conference server-side Python App Engine data & ProtoRPC models

$Id: models.py,v 1.1 2016/01/23 22:01:10 v2saumb Exp $

created/forked from conferences.py by v2saumb on 2016/01/23

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb


class SessionTypesEnum(messages.Enum):
    """ENUM for Conference session type"""
    GENERAL = 0
    WORKSHOP = 1
    LECTURE = 2
    THINKTANK = 3
    SKILLBUILDER = 4
    EXPERTSPEAK = 5
    KEYNOTE = 6


class TeeShirtSizesEnum(messages.Enum):
    """tee_shirt_size - t-shirt size enumeration value"""
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


class StringMessage(messages.Message):
    """StringMessage- outbound (single) string message"""
    data = messages.StringField(1, required=True)


class Speaker(ndb.Model):
    """Speaker - Speaker object"""
    speaker_id = ndb.StringProperty(required=True)
    topics = ndb.StringProperty(repeated=True)
    about_speaker = ndb.StringProperty()


class Session(ndb.Model):
    """ Entity for the conference sessions """
    name = ndb.StringProperty(required=True)
    highlights = ndb.StringProperty()
    speaker_key = ndb.StringProperty(required=True)
    duration = ndb.IntegerProperty(default=30)
    session_type = ndb.StringProperty(default="GENERAL")
    date = ndb.DateTimeProperty(required=True)
    start_time = ndb.TimeProperty(required=True)
    venue = ndb.StringProperty()


class Conference(ndb.Model):
    """Conference - Conference object"""
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    organizer_id = ndb.StringProperty()
    topics = ndb.StringProperty(repeated=True)
    city = ndb.StringProperty()
    start_date = ndb.DateProperty()
    month = ndb.IntegerProperty()
    end_date = ndb.DateProperty()
    max_attendees = ndb.IntegerProperty()
    seats_available = ndb.IntegerProperty()


class Profile(ndb.Model):
    """Profile - User profile object"""
    display_name = ndb.StringProperty()
    main_email = ndb.StringProperty()
    tee_shirt_size = ndb.StringProperty(default='NOT_SPECIFIED')
    conference_keys_to_attend = ndb.StringProperty(repeated=True)
    session_wish_list = ndb.StringProperty(repeated=True)


class SessionForm(messages.Message):
    """Session Form for inbound and outboud conferene sessions"""
    name = messages.StringField(1, required=True)
    highlights = messages.StringField(2)
    speaker_key = messages.StringField(3, required=True)
    duration = messages.IntegerField(4)
    session_type = messages.EnumField('SessionTypesEnum', 5)
    date = messages.StringField(6, required=True)
    start_time = messages.StringField(7, required=True)
    web_safe_key = messages.StringField(8)
    venue = messages.StringField(9)
    conference_name = messages.StringField(10)


class SessionSearchForm(messages.Message):
    """ Sessions search form."""
    start_date = messages.StringField(1, required=True)
    end_date = messages.StringField(2)
    session_type = messages.StringField(3)
    delta_minutes = messages.StringField(4)


class SessionTask3SearchForm(messages.Message):
    """ Sessions search form for the problem in Task 3."""
    start_time = messages.StringField(1, required=True)
    session_type = messages.StringField(2, required=True)


class FeaturedSpeakerForm(messages.Message):
    """Form to return featured speaker"""
    conference_name = messages.StringField(1)
    speaker_name = messages.StringField(2)
    sessions = messages.StringField(3, repeated=True)


class SpeakerForm(messages.Message):
    """Speaker - Speaker object"""
    speaker_id = messages.StringField(1)
    topics = messages.StringField(2, repeated=True)
    about_speaker = messages.StringField(3)
    display_name = messages.StringField(4)
    web_safe_key = messages.StringField(5)


class FindSpeakerForm(messages.Message):
    display_name = messages.StringField(1)
    web_safe_key = messages.StringField(2)

# Allows to return multiple Speakers


class SpeakerForms(messages.Message):
    """SpeakerForm - multiple SpeakerForm outbound form message"""
    items = messages.MessageField(SpeakerForm, 1, repeated=True)

# return multiple sessions


class SessionForms(messages.Message):
    """ConfSesionForms - multiple Conference session outbound form message"""
    items = messages.MessageField(SessionForm, 1, repeated=True)


class ConferenceForm(messages.Message):
    """ConferenceForm - Conference outbound form message"""
    name = messages.StringField(1)
    description = messages.StringField(2)
    organizer_id = messages.StringField(3)
    topics = messages.StringField(4, repeated=True)
    city = messages.StringField(5)
    start_date = messages.StringField(6)  # DateTimeField()
    month = messages.IntegerField(7)
    max_attendees = messages.IntegerField(8)
    seats_available = messages.IntegerField(9)
    end_date = messages.StringField(10)  # DateTimeField()
    web_safe_key = messages.StringField(11)
    organizer_display_name = messages.StringField(12)


class ProfileMiniForm(messages.Message):
    """ProfileMiniForm - update Profile form message"""
    display_name = messages.StringField(1)
    tee_shirt_size = messages.EnumField('TeeShirtSizesEnum', 2)


class ProfileForm(messages.Message):
    """ProfileForm - Profile outbound form message"""
    display_name = messages.StringField(1)
    main_email = messages.StringField(2)
    tee_shirt_size = messages.EnumField('TeeShirtSizesEnum', 3)
    conference_keys_to_attend = messages.StringField(4, repeated=True)
    session_wish_list = messages.StringField(5, repeated=True)


class ConferenceForms(messages.Message):
    """ConferenceForms - multiple Conference outbound form message"""
    items = messages.MessageField(ConferenceForm, 1, repeated=True)


class ConferenceQueryForm(messages.Message):
    """ConferenceQueryForm - Conference query inbound form message"""
    field = messages.StringField(1)
    operator = messages.StringField(2)
    value = messages.StringField(3)

#  form for passing multiple query filters


class ConferenceQueryForms(messages.Message):
    """ConferenceQueryForms - multiple ConferenceQueryForm
     inbound form message"""
    filters = messages.MessageField(ConferenceQueryForm, 1, repeated=True)


# needed for conference registration
class BooleanMessage(messages.Message):
    """BooleanMessage - outbound Boolean value message"""
    data = messages.BooleanField(1)


class ConflictException(endpoints.ServiceException):
    """ConflictException - exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT
