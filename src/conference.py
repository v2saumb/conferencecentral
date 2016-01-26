#!/usr/bin/env python

"""
conference.py -- Udacity Project conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 v2saumb Exp v2saumb $

Modified by v2saumb on 2016 Jan 04

"""

__author__ = 'v2saumb+api@gmail.com (Saumya Batnagar)'


from datetime import timedelta, datetime
from time import gmtime, strftime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import logging

from settings import WEB_CLIENT_ID
from models import Profile, ProfileMiniForm, ProfileForm
from models import TeeShirtSizesEnum, SessionTypesEnum
from models import Conference, ConferenceForm, ConferenceForms
from models import ConferenceQueryForms
from models import BooleanMessage
from models import ConflictException
from models import Speaker, SpeakerForm, SpeakerForms, FindSpeakerForm
from models import FeaturedSpeakerForm
from models import Session, SessionForm, SessionForms
from models import SessionSearchForm, SessionTask3SearchForm
from utils import get_user_id

from google.appengine.ext import ndb

# adding imports for memcache
from google.appengine.api import memcache
from models import StringMessage
#  adding import for the task queue
from google.appengine.api import taskqueue

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "LIMITED-SEATS-AVAILABLE"
# key for putting the sessions starting soon in the memcache
MEMCACHE_STARTING_SOON_KEY = "SESSIONS-STARTING-SOON"
# key for putting the sessions starting soon in the memcache
MEMCACHE_FEATURED_SPEAKERS = "FEATURED_SPEAKER"
# time delta for sessions starting soon in minutes
STARTING_SOON_INTERVAL = 30
# no of session to return for the stating soon request
STARTING_SOON_COUNT = 5
# Short Date Format
SHORT_DATE = "%Y-%m-%d"
# long Date format
LONG_DATE_FORMAT = "%Y-%m-%d %H:%M"

# default values for conf object
DEFAULTS = {
    "city": "Default City",
    "max_attendees": 0,
    "seats_available": 0,
    "topics": ["Default", "Topic"],
}

# default values for speaker object
SPEAKER_DEFAULTS = {
    "topics": ["Default", "Topic"],
}
# default values for Session object
SESSION_DEFAULTS = {
    'highlights': '',
    'speaker_key': '',
    'duration': 30,
    'session_type': SessionTypesEnum.GENERAL
}
# operators for the query filters for Conferences
OPERATORS = {
    'EQ': '=',
    'GT': '>',
    'GTEQ': '>=',
    'LT': '<',
    'LTEQ': '<=',
    'NE': '!='
}
# field names for the query filters for conferences
FIELDS = {
    'CITY': 'city',
    'TOPIC': 'topics',
    'MONTH': 'month',
    'MAX_ATTENDEES': 'max_attendees',
}
# GET request where we only need the key passed as part of the url
CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    webSafeConfKey=messages.StringField(1),
)
# Post request where we only need the key passed as part of the url
# This reques also has the conference form
CONF_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    webSafeConfKey=messages.StringField(1),
)
# GET request for Sessions where we only need the key passed as part of
# the url
SESSION_POST_REQUEST = endpoints.ResourceContainer(
    SessionForm,
    webSafeConfKey=messages.StringField(1),
)
# Post request for Sessions where we only need the key passed as part of
# the url with session form
SESSION_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    webSafeConfKey=messages.StringField(1),
)
# GET request for Sessions where we only need the conference key  and the
# session type are passed as part of the url
SESSION_TYPES_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    webSafeConfKey=messages.StringField(1),
    sessionType=messages.StringField(2),
)
# GET request for adding/removing Sessions to the wishlist and session key
# is passed in the url
WISHLIST_SESSION_POST_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    web_safe_key=messages.StringField(1),
)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# set up the conference API


@endpoints.api(name='conference',
               version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""
# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _get_profile_form(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'tee_shirt_size':
                    setattr(pf, field.name, getattr(
                        TeeShirtSizesEnum, getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _get_user_profile(self):
        """Return user Profile from datastore,
         creating new one if non-existent."""
        user = endpoints.get_current_user()
        # if user is not logged in throw error
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = get_user_id(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()

        # create new Profile if not there
        if not profile:
            profile = Profile(
                key=p_key,
                display_name=user.nickname(),
                main_email=user.email(),
                tee_shirt_size=str(TeeShirtSizesEnum.NOT_SPECIFIED),
            )
            profile.put()
        # return Profile
        return profile

    def _do_profile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._get_user_profile()
        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('display_name', 'tee_shirt_size'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
            prof.put()

        # return ProfileForm
        return self._get_profile_form(prof)

    def _create_session_mail_text(self, session, conf):
        """Formats and creates a mail content for
        session creator and speaker"""
        message_text = """\nConference Name:\t{0}
        \nSession:\t{1}
        \nDuration:\t{2}
        \nDate:\t{3}
        \nStart Time:\t{4}
        \nCity:\t{5}
        \nVenue:\t{6}""".format(conf.name, session.name,
                                session.duration, session.date,
                                session.start_time,
                                conf.city, session.venue)
        return message_text

    def _parse_date_string(self, date_str, date_format, format_len):
        """ Creates a date from string date passed
        if there is an error creating the date the method
        throws an exception"""
        try:
            new_date = datetime.strptime(
                date_str[:format_len], date_format)
        except:
            # Raise an exeption if date cannot be created.
            raise endpoints.BadRequestException(
                """Invalid date or date format.\
                 Please enter date in [ %s ] format. """ % date_format)
        # return the parsed date
        return new_date

    def _get_conference_form(self, conf, display_name):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()

        # return set of ConferenceForm objects per Conference
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "web_safe_key":
                # add the websafe key for outbound
                setattr(cf, field.name, conf.key.urlsafe())
        if display_name:
            # add disolay name for the conference organizer for outbound
            setattr(cf, 'organizer_display_name', display_name)
        # validate the form
        cf.check_initialized()
        return cf

    def _get_session_form(self, session):
        """Copy relevant fields from Session to SessionForm."""
        cf = SessionForm()
        #  return a empty form if session is not passed
        if not session:
            return cf
        # get the conference details
        conf_key = session.key.parent()
        conf = conf_key.get()

        for field in cf.all_fields():
            if hasattr(session, field.name):
                # convert Date to date string; just copy others
                if field.name in ('date', 'start_time'):
                    setattr(cf, field.name, str(
                        getattr(session, field.name)))
                elif field.name == 'session_type':
                    # set the session type from enum
                    setattr(cf, field.name, getattr(
                        SessionTypesEnum, getattr(session, field.name)))
                else:
                    setattr(cf, field.name, getattr(session, field.name))
            elif field.name == "web_safe_key":
                #  set the session key for outbound
                setattr(cf, field.name, session.key.urlsafe())
        # set the conference name
        cf.conference_name = conf.name
        # validate the form
        cf.check_initialized()
        return cf

    def _create_conference_object(self, request):
        """Create or update Conference object,
        returning ConferenceForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        # raise error if user is not logged in.
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = get_user_id(user)

        if not request.name:
            raise endpoints.BadRequestException(
                "Conference 'name' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # delete the websafe key not required by the entity
        del data['web_safe_key']
        # delete the organizer_display_name not required by the entity
        del data['organizer_display_name']

        # add default values for those missing (both data model & outbound
        # Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        if data['start_date']:
            data['start_date'] = self._parse_date_string(
                data['start_date'], SHORT_DATE, 10).date()
            data['month'] = data['start_date'].month
        else:
            data['month'] = 0

        if data['end_date']:
            data['end_date'] = self._parse_date_string(
                data['end_date'], SHORT_DATE, 10).date()

        # set seats_available to be same as max_attendees on creation
        if data["max_attendees"] > 0:
            data["seats_available"] = data["max_attendees"]
        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        # set te key
        data['key'] = c_key
        # set the organizer id from the profile
        data['organizer_id'] = request.organizer_id = user_id

        # create Conference & return (modified) ConferenceForm
        Conference(**data).put()
        # send confference creation mail
        taskqueue.add(params={'email': user.email(),
                              'conferenceInfo': repr(request)},
                      url='/tasks/sendemail/createconference'
                      )
        return request

    @ndb.transactional()
    def _update_conference_object(self, request):
        """ updates the conference details based on the
        key and other information """
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = get_user_id(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # remove fields notrequired by the entity
        del data['web_safe_key']
        del data['organizer_display_name']

        # update existing conference
        try:
            conf = ndb.Key(urlsafe=request.webSafeConfKey).get()
        except:
            # raise exception if problem getting conference
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.webSafeConfKey)

        # check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.webSafeConfKey)

        # check that user is owner
        if user_id != conf.organizer_id:
            raise endpoints.ForbiddenException(
                'Only the owner can update the conference.')

        # Not getting all the fields, so don't create a new object; just
        # copy relevant fields from ConferenceForm to Conference object
        for field in request.all_fields():
            data = getattr(request, field.name)
            # only copy fields where we get data
            if data not in (None, []):
                # special handling for dates (convert string to Date)
                if field.name in ('start_date', 'end_date'):
                    data = self._parse_date_string(
                        data, SHORT_DATE, 10).date()
                    if field.name == 'start_date':
                        conf.month = data.month
                setattr(conf, field.name, data)

        # write to Conference object
        conf.put()
        prof = ndb.Key(Profile, user_id).get()
        # send the mail for conference creation / updation
        taskqueue.add(params={'email': user.email(),
                              'conferenceInfo': repr(request)},
                      url='/tasks/sendemail/createconference'
                      )
        return self._get_conference_form(conf, getattr(prof, 'display_name'))

    def _get_formatted_query(self, request):
        """Return formatted query from the submitted filters."""
        q = Conference.query()
        inequality_filter, filters = self._format_filters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Conference.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Conference.name)

        for filtr in filters:
            if filtr["field"] in ["month", "max_attendees"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(
                filtr["field"], filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q

    def _format_filters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name)
                     for field in f.all_fields()}

            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                raise endpoints.BadRequestException(
                    "Filter contains invalid field or operator.")

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used in previous
                # filters  disallow the filter if inequality was
                # performed on a different field before
                # track the field on which the inequality operation is
                # performed
                if inequality_field and inequality_field != filtr["field"]:
                    raise endpoints.BadRequestException(
                        "Inequality filter is allowed on only one field.")
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)

    @ndb.transactional(xg=True)
    def _conference_registration(self, request, reg=True):
        """Register or unregister user for selected conference."""
        retval = None
        # get user Profile
        prof = self._get_user_profile()

        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.webSafeConfKey
        try:
            conf = ndb.Key(urlsafe=wsck).get()
        except:
            # raise an exception if conference is not found
            raise endpoints.NotFoundException(
                'No conference found with key: [ %s ]' % wsck)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsck in prof.conference_keys_to_attend:
                raise ConflictException(
                    "You have already registered for this conference")

            # check if seats avail
            if conf.seats_available <= 0:
                raise ConflictException(
                    "There are no seats available.")

            # register user, take away one seat
            prof.conference_keys_to_attend.append(wsck)
            conf.seats_available -= 1
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsck in prof.conference_keys_to_attend:

                # unregister user, add back one seat
                prof.conference_keys_to_attend.remove(wsck)
                conf.seats_available += 1
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        conf.put()
        return BooleanMessage(data=retval)

    def _manage_session_wish_list(self, request, add_sesion=True):
        """Add or remove sessions form users wishlist."""
        retval = None
        # get user Profile
        prof = self._get_user_profile()
        wsck = request.web_safe_key
        # get the session using the key passed
        try:
            session = ndb.Key(urlsafe=wsck).get()
            if not session:
                # raise exception if not able to find session
                raise endpoints.NotFoundException(
                    'No session found with key: [ %s ]' % wsck)
        except:
            retval = False
            # raise exception if ther eis a problem getting the session.
            raise endpoints.NotFoundException(
                'No session found with key: [ %s ]' % wsck)

        # add_sesion
        if add_sesion:
            # check if session already in wishlist
            if wsck in prof.session_wish_list:
                retval = False
                raise endpoints.BadRequestException(
                    "This session already exist in your wishlist")

            # add session to the wishlist
            prof.session_wish_list.append(wsck)
            retval = True

        else:
            # else remove session from wishlist
            # check if session in wishlist
            if wsck in prof.session_wish_list:
                # remove the session from wishlist
                prof.session_wish_list.remove(wsck)
                retval = True
            else:
                retval = True
                raise endpoints.BadRequestException(
                    "This session does not exist in your wishlist!")

        # write things back to the datastore & return
        prof.put()
        return BooleanMessage(data=retval)

    def _create_session(self, request):
        """Create or update Conference Session object,
        returning SessionForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = get_user_id(user)
        #  raise exceptio if the conference key is not passed in
        if not request.webSafeConfKey:
            raise endpoints.BadRequestException(
                "Session 'webSafeConfKey' field required")

        # get the conference key
        try:
            conf_key = ndb.Key(urlsafe=request.webSafeConfKey)
            conf = conf_key.get()
        except:
            # raise exception if the conference is not found
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.webSafeConfKey)
        # raise exception if required field is mising
        if not request.name:
            raise endpoints.BadRequestException(
                "Session 'name' field required")

        if not request.speaker_key:
            raise endpoints.BadRequestException(
                "Session 'speaker_key' is  required")

        # try to get the speaker matching the key
        try:
            speaker = ndb.Key(urlsafe=request.speaker_key).get()
            if not speaker:
                raise endpoints.BadRequestException(
                    "Incorrect 'speaker_key' is passed.")

        except:
            raise endpoints.BadRequestException(
                "Incorrect 'speaker_key' is passed.")

        # raise exception if user is not the organizer of this conference
        if conf.organizer_id != user_id:
            raise endpoints.NotFoundException(
                """Only organiser can add sessions.
                 Please contact %s""" % conf.organizer_id)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # remove fields notrequired
        del data['web_safe_key']
        del data['webSafeConfKey']
        del data['conference_name']

        # add default values for those missing (both data model & outbound
        # Message)
        for df in SESSION_DEFAULTS:
            if data[df] in (None, []):
                data[df] = SESSION_DEFAULTS[df]
                setattr(request, df, SESSION_DEFAULTS[df])

        # convert dates
        # start_date
        if data['date']:
            data['date'] = self._parse_date_string(
                data['date'], SHORT_DATE, 10).date()

        # convert time
        try:
            if data['start_time']:
                data['start_time'] = datetime.strptime(
                    data['start_time'][:5], "%H:%M").time()
                # adding time to the date field this will help filter results
                # later
                formatted_datetime = datetime.combine(data['date'],
                                                      data['start_time'])
                data['date'] = formatted_datetime
        except:
            raise endpoints.BadRequestException(
                "Time Format is wrong please pass time like 14:00")

        # convert session type
        if data['session_type']:
            data['session_type'] = str(data['session_type'])

        # generate Session_id based on conference
        session_id = Session.allocate_ids(size=1, parent=conf_key)[0]
        c_key = ndb.Key(Session, session_id, parent=conf_key)
        data['key'] = c_key
        # create Conference & return (modified) ConferenceForm
        Session(**data).put()
        session = c_key.get()
        new_session = self._get_session_form(session)
        # send mail to organizer about the new conference Session
        taskqueue.add(params={'email': user.email(),
                              'sessioninfo': self._create_session_mail_text(
            session, conf)},
            url='/tasks/sendemail/createsession'
        )
        session_speaker_key = request.speaker_key
        # send mail to the Speaker So he knows the schedule
        if request.speaker_key:
            speaker_profile = ndb.Key(urlsafe=session_speaker_key).get()
            mail_text = self._create_session_mail_text(session, conf)
            taskqueue.add(params={'email': speaker_profile.speaker_id,
                                  'sessioninfo': mail_text},
                          url='/tasks/sendemail/speakersessioncreated'
                          )
            # add task to check for features speaker.
            taskqueue.add(params={'email': speaker_profile.speaker_id,
                                  'speakerKey': session_speaker_key,
                                  'confKey': conf_key.urlsafe()},
                          url='/tasks/setfeaturedspeaker')
        return new_session

    def _create_speaker(self, request):
        """Create or update speaker object, returning SpeakerForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        # raise exception if the user is not logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        user_id = get_user_id(user)
        # If there are no sold out conferences,
        existing_speaker = self._verify_speaker(request)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}

        # remove fields not required by entity
        del data['web_safe_key']
        del data['display_name']

        # add default values for those missing (both data model & outbound
        # Message)
        for df in SPEAKER_DEFAULTS:
            if data[df] in (None, []):
                data[df] = SPEAKER_DEFAULTS[df]
                setattr(request, df, SPEAKER_DEFAULTS[df])
        logging.info(existing_speaker)
        if existing_speaker and existing_speaker.web_safe_key:
            speaker_key = ndb.Key(urlsafe=existing_speaker.web_safe_key)
        else:
            p_key = ndb.Key(Profile, user_id)
            speaker_id = Speaker.allocate_ids(size=1, parent=p_key)[0]
            speaker_key = ndb.Key(Speaker, speaker_id, parent=p_key)
            data['speaker_id'] = request.speaker_id = user_id

        data['key'] = speaker_key
        logging.info(data['key'])

        # create speaker & return (modified) Speaker
        Speaker(**data).put()
        # send the speaker a mail confirming of registration
        taskqueue.add(params={'email': user.email()},
                      url='/tasks/sendemail/speakercreated'
                      )
        return request

    def _get_speaker_form(self, speaker_profile):
        """Copy relevant fields from Speaker to SpeakerForm."""
        # init the speaker form
        spkr = SpeakerForm()
        speaker = speaker_profile
        # get the speaker profile
        prof_key = speaker_profile.key.parent()
        prof = prof_key.get()
        # get the display name from the profile
        if prof:
            spkr.display_name = prof.display_name

        for field in spkr.all_fields():
            if hasattr(speaker, field.name):
                setattr(spkr, field.name, getattr(speaker, field.name))
            elif field.name == "web_safe_key":
                # assign the websafe  key for outbound
                setattr(spkr, field.name, speaker.key.urlsafe())
        #  verify the speaker form
        spkr.check_initialized()
        return spkr

    def _get_featured_speaker_form(self, featured_speaker):
        """Copy relevant fields from featueredSpeaker
         to FeaturedSpeakerForm."""
        # init the form
        spkr = FeaturedSpeakerForm()
        speaker = featured_speaker
        # set he form fields
        for field in spkr.all_fields():
            setattr(spkr, field.name, speaker.get(field.name))
        # verify the sfeaturedpeaker form
        spkr.check_initialized()
        return spkr

    def _verify_speaker(self, request):
        """Verify if the speaker is already registered. If Speaker is registered
         returns SpeakerForm else returns an empty SpeakerForm. """
        # make sure user is authed
        user = endpoints.get_current_user()
        # raise error if the user is not logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        #  get the user id for the current user
        user_id = get_user_id(user)
        # find if a speaker with this profile exists
        speaker = Speaker.query(ancestor=ndb.Key(Profile, user_id)).get()

        if not speaker:
            # if speaker not found return empty form
            return SpeakerForm()
        else:
            # return speaker details
            return self._get_speaker_form(speaker)

    def _get_speaker_sessions_by_key(self, request):
        """ Returns sessions by speaker key"""
        # raise error if the key is not present
        if not request.web_safe_key:
            raise endpoints.BadRequestException(
                "Speaker web_safe_key or speaker display_name is required.")
        # get session by speaker
        sessions = Session.query(
            Session.speaker_key == request.web_safe_key).order(
            -Session.date).order(Session.start_time)
        # return the sessions
        return sessions

    def _get_sessions_by_type(self, request):
        """" Returns sessions by session type in a conference type"""
        # raise an error if session type is not passed
        if not request.sessionType:
            raise endpoints.BadRequestException(
                "'sessionType'  is required.")

        #  try to get conference key
        try:
            conf_key = ndb.Key(urlsafe=request.webSafeConfKey)
        except:
            raise endpoints.BadRequestException(
                "Conference key is not valid")

        # get all the sessions for the conference
        sessions = Session.query(ancestor=conf_key)
        # filter sessions for the desired type
        session_filter = ndb.query.FilterNode(
            'session_type', '=', request.sessionType)
        sessions = sessions.filter(session_filter)
        # set up the order
        sessions = sessions.order(
            -Session.date).order(Session.start_time)
        # return the sessions
        return sessions

    def _get_speaker_sessions_by_name(self, request):
        """ Returns sessions by speaker display_name"""
        # raise error if the diaplay name is not passed
        if not request.display_name:
            raise endpoints.BadRequestException(
                "Speaker web_safe_key or speaker display_name is required.")
        #  get the profile by display name
        prof = Profile.query(Profile.display_name ==
                             request.display_name).get()
        # if the speaker profile is not found raise an error
        if not prof:
            raise endpoints.BadRequestException(
                "Profile not found for speaker name - %s"
                % request.display_name)
        # fetch the speaker information
        speaker = Speaker.query(ancestor=prof[0].key).get()

        # raise exception if the speaker is not found
        if not speaker:
            raise endpoints.BadRequestException(
                "Profile is not a registered speaker - %s"
                % request.display_name)

        # get sessions for the speaker
        sessions = Session.query(
            Session.speaker_key == speaker[0].key.urlsafe()).order(
            -Session.date).order(Session.start_time)
        # return the speaker
        return sessions

    def _get_all_future_sessions(self, request):
        """ Returns all future sessions """
        # get the dates from the request
        str_date = request.start_date
        str_end_date = request.end_date
        # format the start date time
        if str_date:
            start_date = self._parse_date_string(
                str_date, LONG_DATE_FORMAT, 16)
        # format the end date time
        if str_end_date:
            # get formatted end date
            end_date = self._parse_date_string(
                str_end_date, LONG_DATE_FORMAT, 16)
        else:
            end_date = None

        # query all session after the start date
        sessions = Session.query(
            Session.date > start_date).order(Session.date)

        # filter all session based on end date if passed in request
        if end_date:
            sessions = sessions.filter(
                Session.date <= end_date).order(Session.date)

        return sessions

    def _get_starting_soon_sessions(self, request):
        """ Return all session that are starting soon request
        will have the delta to select the upper limit
        """
        # get the starting date from request
        str_date = request.start_date
        # format date if passed raise exception if date is not passed
        if str_date:
            # format the date
            start_date = self._parse_date_string(
                str_date, LONG_DATE_FORMAT, 16)

        else:
            raise endpoints.BadRequestException("'start_date' field required")

        # get the delta minutes
        end_delta = request.delta_minutes or STARTING_SOON_INTERVAL

        #  create end date
        try:
            end_date = start_date + timedelta(minutes=end_delta)
        except:
            #  raise exception if end date can not be created
            raise endpoints.BadRequestException(
                "Invalid 'delta_minutes' value.")
        # query session based on the start date
        sessions = Session.query(
            Session.date > start_date).order(Session.date)
        # filter the sessions based on the end date
        if end_date:
            sessions = sessions.filter(
                Session.date <= end_date).order(Session.date)
        # return the sessions            #
        return sessions
    # ----------------Static Methods-------------------------------

    @staticmethod
    def _cache_announcement():
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        logging.info("in the method for set announcements")
        confs = Conference.query(ndb.AND(
            Conference.seats_available <= 5,
            Conference.seats_available > 0)
        ).fetch(projection=[Conference.name])
        logging.info(str(confs))
        if confs:
            # If there are almost sold out conferences,
            # format announcement and set it in memcache
            announcement = '%s %s' % (
                'Last chance to attend! The following conferences '
                'are nearly sold out:',
                ', '.join(conf.name for conf in confs))
            memcache.set(MEMCACHE_ANNOUNCEMENTS_KEY, announcement)
        else:
            # If there are no sold out conferences,
            # delete the memcache announcements entry
            announcement = ""
            memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)

    @staticmethod
    def _cache_starting_soon():
        """Finds and sets the sessions startign soon in the memcache; used by
        memcache cron job & SetStartingSoon().
        """
        logging.info("in the method for set starting soon")
        # get current datetime
        start_date = datetime.combine(
            datetime.now().date(), datetime.now().time())
        # get the timezone
        tzone = strftime("%z", gmtime())
        # if utc calculate est date
        if tzone in ("UTC", "+0000"):
            delta = timedelta(hours=-5)
            start_date += delta

        logging.info(start_date)
        # calculate the end date based on the interval
        end_date = start_date + timedelta(minutes=int(STARTING_SOON_INTERVAL))
        logging.info(str(start_date) + " ," + str(end_date))
        # get sessions
        sessions = Session.query(
            Session.date > start_date).order(Session.date)
        # filter sessions  if end date is available
        if end_date:
            sessions = sessions.filter(
                Session.date <= end_date).order(Session.date)
        # if sessions exixts fetch the required fields and. Picking only n
        # number of sessions due to limited space on the frontend
        logging.info(sessions)
        if sessions:
            sessions = sessions.fetch(STARTING_SOON_COUNT,
                                      projection=[Session.name,
                                                  Session.date, Session.venue,
                                                  Session.session_type,
                                                  Session.speaker_key,
                                                  Session.start_time])
            logging.info(sessions)
            # set the sessions in memcache
            memcache.set(MEMCACHE_STARTING_SOON_KEY, sessions)
        else:
            # delete the memcache announcements entry
            sessions = None
            memcache.delete(MEMCACHE_STARTING_SOON_KEY)

    @staticmethod
    def _cache_featured_speaker(request):
        """Finds and puts the featured speaker details into memcache; used by
        cron job method SetNewSpeakerSpecial.
        """
        # set the counter  = 0
        sessions = 0
        # init featured_speaker
        featured_speaker = {}
        logging.info("in the method for set featured speaker")

        # get the conference key
        try:
            conf_key = ndb.Key(urlsafe=request.get('confKey'))
        except:
            raise endpoints.BadRequestException(
                "Invalid Conference Key Passed")

            # get the sesion in the conference
        sessions = Session.query(ancestor=conf_key).filter(
            Session.speaker_key == request.get('speakerKey'))
        # if there are more then one sessions by the speaker get the required
        # information

        if sessions.count(limit=5) > 1:
            # get conference info
            conf = conf_key.get()
            # get speaker profile
            speaker_profile = ndb.Key(urlsafe=request.get(
                'speakerKey')).parent().get()
            # get the session names only
            sessions = sessions.fetch(projection=[Session.name])

            logging.info(speaker_profile.display_name)
            # create the featured speaker object
            featured_speaker = {'speaker_name': speaker_profile.display_name,
                                'conference_name': conf.name,
                                'sessions': [conf_session.name for
                                             conf_session in sessions]
                                }
            # set the featured speaker in memcache
            memcache.set(MEMCACHE_FEATURED_SPEAKERS, featured_speaker)

    #  ------------------------------- Endpoints ---------------------

    # register a user as speaker
    @endpoints.method(SpeakerForm, SpeakerForm,
                      path='registerSpeaker',
                      http_method='POST',
                      name='registerSpeaker')
    def registerSpeaker(self, request):
        """Register a Speaker."""
        return self._create_speaker(request)

    # verify if the user is already registered as speaker
    @endpoints.method(message_types.VoidMessage, SpeakerForm,
                      path='speaker/exists',
                      http_method='POST',
                      name='speakerExists')
    def speakerExists(self, request):
        """Verify if a speaker already exists."""
        return self._verify_speaker(request)

    @endpoints.method(message_types.VoidMessage, StringMessage,
                      path='conference/announcement/get',
                      http_method='GET', name='getAnnouncement')
    def getAnnouncement(self, request):
        """Return Announcement from memcache."""
        # TODO 1
        # return an existing announcement from Memcache or an empty string.
        logging.info(MEMCACHE_ANNOUNCEMENTS_KEY)
        # get the announcement form memecache
        announcement = memcache.get(MEMCACHE_ANNOUNCEMENTS_KEY)
        # if announcements not found return empty string
        if not announcement:
            announcement = ""
        return StringMessage(data=announcement)

    @endpoints.method(message_types.VoidMessage, SessionForms,
                      path='sessions/starting-soon/cached',
                      http_method='GET',
                      name='getSessionsStartingSoonCached')
    def getSessionsStartingSoonCached(self, request):
        """Return sessions that are starting soon from memcache."""
        logging.info(MEMCACHE_STARTING_SOON_KEY)
        sessions = memcache.get(MEMCACHE_STARTING_SOON_KEY)
        # raise errors if no sessions are found
        if not sessions:
            sessions = None
            raise endpoints.ConflictException(
                'Sessions Not Found')
        return SessionForms(
            items=[self._get_session_form(
                session) for session in sessions]
        )

    @endpoints.method(message_types.VoidMessage, FeaturedSpeakerForm,
                      path='speaker/featured-speaker/cached',
                      http_method='GET',
                      name='getFeaturedSpeaker')
    def getFeaturedSpeaker(self, request):
        """Return featured speakers from memcache."""
        # get the featured speakers from memcache
        featured_speaker = memcache.get(MEMCACHE_FEATURED_SPEAKERS)
        if featured_speaker:
            retval = self._get_featured_speaker_form(featured_speaker)
        else:
            # if featured speaker is not found return an empty form
            retval = FeaturedSpeakerForm()
        return retval

    @endpoints.method(message_types.VoidMessage, ProfileForm,
                      path='profile',
                      http_method='GET',
                      name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._do_profile()

    @endpoints.method(ProfileMiniForm, ProfileForm,
                      path='profile',
                      http_method='POST',
                      name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._do_profile(request)

    @endpoints.method(ConferenceForm, ConferenceForm,
                      path='conference',
                      http_method='POST',
                      name='createConference')
    def createConference(self, request):
        """Create new conference."""
        return self._create_conference_object(request)

    @endpoints.method(CONF_POST_REQUEST, ConferenceForm,
                      path='conference/edit/{webSafeConfKey}',
                      http_method='PUT',
                      name='updateConference')
    def updateConference(self, request):
        """Update conference w/provided fields & return w/updated info."""
        return self._update_conference_object(request)

    @endpoints.method(CONF_GET_REQUEST, ConferenceForm,
                      path='conference/{webSafeConfKey}',
                      http_method='GET',
                      name='getConference')
    def getConference(self, request):
        """Return requested conference (by webSafeConfKey)."""
        # get Conference object from request; bail if not found
        logging.info(request)
        # throw exception if the conference key is not passed.
        if not request.webSafeConfKey:
            raise endpoints.BadRequestException(
                "Conference key is not valid required.")

        conf = ndb.Key(urlsafe=request.webSafeConfKey).get()
        #  raise error if conf not found
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.webSafeConfKey)
        # get the organizer profile
        prof = conf.key.parent().get()
        # return ConferenceForm
        return self._get_conference_form(conf, getattr(prof, 'display_name'))

    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='getConferencesCreated',
                      http_method='POST',
                      name='getConferencesCreated')
    def getConferencesCreated(self, request):
        """Return conferences created by user."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = get_user_id(user)
        # create ancestor query for all key matches for this user
        confs = Conference.query(ancestor=ndb.Key(Profile, user_id))
        # get the organizer profile
        prof = ndb.Key(Profile, user_id).get()
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
            items=[self._get_conference_form(
                conf, getattr(prof, 'display_name')) for conf in confs]
        )

    @endpoints.method(ConferenceQueryForms, ConferenceForms,
                      path='queryConferences',
                      http_method='POST',
                      name='queryConferences')
    def queryConferences(self, request):
        """Query for conferences."""
        conferences = self._get_formatted_query(request)

        # need to fetch organiser display_name from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile, conf.organizer_id))
                      for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.display_name

        # return individual ConferenceForm object per Conference
        return ConferenceForms(
            items=[self._get_conference_form(conf, names[conf.organizer_id])
                   for conf in conferences]
        )

    @endpoints.method(SessionTask3SearchForm, SessionForms,
                      path='sessions/beforetime',
                      http_method='GET',
                      name='getAllSessionsBeforeTime')
    def getAllSessionsBeforeTime(self, request):
        """ Returns all the sessions before the 'start_time'
         and are not of type 'session_type' """
        st_time = request.start_time
        # format the time from the requst
        try:
            start_time = datetime.strptime(st_time[:5], "%H:%M").time()
        except:
            # raise exception if time cannot be parsed
            raise endpoints.BadRequestException(
                """Invalid time format.Please enter time  in [%H:%M] format.""")

        # fetch only the keys for sessions before the requested time
        time_query = Session.query(Session.start_time < start_time).order(
            Session.start_time).order(-Session.date).fetch(keys_only=True)

        # query the session which are not of the type specified in the request
        # and get only the keys
        type_query = Session.query(
            Session.session_type != request.session_type).order(
            Session.session_type).order(-Session.date).fetch(keys_only=True)
        # create a set by intersection of both the queries and then get the
        # results
        filtered_sessions = ndb.get_multi(
            set(time_query).intersection(type_query))
        # return the results
        return SessionForms(
            items=[self._get_session_form(conf) for conf in filtered_sessions]
        )

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='conference/register/{webSafeConfKey}',
                      http_method='POST',
                      name='registerForConference')
    def registerForConference(self, request):
        """Register user for selected conference."""
        return self._conference_registration(request)

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='conference/unregister/{webSafeConfKey}',
                      http_method='POST',
                      name='unregisterFromConference')
    def unregisterFromConference(self, request):
        """Register user for selected conference."""
        return self._conference_registration(request, False)

    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='conferences/attending',
                      http_method='GET',
                      name='getConferencesToAttend')
    def getConferencesToAttend(self, request):
        """Get list of conferences that user has registered for."""
        prof = self._get_user_profile()
        # get the list of conferences
        list_of_confs = list(ndb.Key(urlsafe=wsck)
                             for wsck in prof.conference_keys_to_attend)
        # get all the conferences
        conferences = ndb.get_multi(list_of_confs)
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(items=[self._get_conference_form(conf, "")
                                      for conf in conferences]
                               )
    # create new session

    @endpoints.method(SESSION_POST_REQUEST, SessionForm,
                      path='conference/session/create/{webSafeConfKey}',
                      http_method='POST',
                      name='createSession')
    def createSession(self, request):
        """Creates a new conference session."""
        return self._create_session(request)

    @endpoints.method(SESSION_GET_REQUEST, SessionForms,
                      path='conference/sessions/{webSafeConfKey}',
                      http_method='GET',
                      name='getConferenceSessions')
    def getConferenceSessions(self, request):
        """Return sessions for a conference (searched by conference key)."""

        logging.info(request.webSafeConfKey)
        # throw exception if the conference key is not passed.
        if not request.webSafeConfKey:
            raise endpoints.BadRequestException(
                "Conference key is required.")
        try:
            conf_key = ndb.Key(urlsafe=request.webSafeConfKey)
        except:
            #  raise exception if key can not be found
            raise endpoints.BadRequestException(
                "Conference key is not valid.")

        sessions = Session.query(ancestor=conf_key).order(-Session.date)
        # return set of ConferenceForm objects per Conference
        return SessionForms(
            items=[self._get_session_form(
                session) for session in sessions]
        )

    @endpoints.method(message_types.VoidMessage, SpeakerForms,
                      path='speaker/all',
                      http_method='GET',
                      name='getAllSpeakers')
    def getAllSpeakers(self, request):
        """Return All speakers . """
        # get all the speakers
        speakers = Speaker.query()
        return SpeakerForms(
            items=[self._get_speaker_form(
                speaker) for speaker in speakers]
        )

    @endpoints.method(FindSpeakerForm, SessionForms,
                      path='speaker/sessions',
                      http_method='GET',
                      name='getSessionsBySpeaker')
    def getSessionsBySpeaker(self, request):
        """Return sessions by a speaker."""
        # get the sessbuy key if present else get them by name
        if request.web_safe_key:
            sessions = self._get_speaker_sessions_by_key(request)
        else:
            sessions = self._get_speaker_sessions_by_name(request)

        return SessionForms(
            items=[self._get_session_form(
                session) for session in sessions]
        )

    @endpoints.method(SESSION_TYPES_GET_REQUEST, SessionForms,
                      path='sessions/{webSafeConfKey}/{sessionType}',
                      http_method='GET',
                      name='getConferenceSessionsByType')
    def getConferenceSessionsByType(self, request):
        """Return sessions by a speaker."""
        # if both conf key and the session type are passed get the sessions
        if request.webSafeConfKey and request.sessionType:
            sessions = self._get_sessions_by_type(request)

        return SessionForms(
            items=[self._get_session_form(
                session) for session in sessions]
        )

    @endpoints.method(WISHLIST_SESSION_POST_REQUEST, BooleanMessage,
                      path='profile/wishlist/add/{web_safe_key}',
                      http_method='POST',
                      name='addSessionToWishlist')
    def addSessionToWishlist(self, request):
        """Add a sessions to users wishlist."""
        logging.info('in add session to wishlist')
        return self._manage_session_wish_list(request, True)

    @endpoints.method(WISHLIST_SESSION_POST_REQUEST, BooleanMessage,
                      path='profile/wishlist/delete/{web_safe_key}',
                      http_method='POST',
                      name='deleteSessionInWishlist')
    def deleteSessionInWishlist(self, request):
        """Removes a sessions from users wishlist."""
        logging.info('in delete session to wishlist')
        return self._manage_session_wish_list(request, False)

    @endpoints.method(message_types.VoidMessage, SessionForms,
                      path='session_wish_list',
                      http_method='GET',
                      name='getSessionsInWishlist')
    def getSessionsInWishlist(self, request):
        """Retrives all sessions from users wishlist."""
        prof = self._get_user_profile()
        # get the lest of sesssion keys
        list_of_sessions = list(ndb.Key(urlsafe=wsck)
                                for wsck in prof.session_wish_list)
        # get the session for the keys
        sessions = ndb.get_multi(list_of_sessions)
        # return set of ConferenceForm objects per Conference
        return SessionForms(
            items=[self._get_session_form(
                session) for session in sessions]
        )

    @endpoints.method(message_types.VoidMessage, BooleanMessage,
                      path='sessionwishlist/clearall',
                      http_method='POST',
                      name='clearUserWishList')
    def clearUserWishList(self, request):
        """Clears the users wishlist."""
        retval = True
        # preload necessary data items
        user = endpoints.get_current_user()
        # raise exception if the user is not logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        prof = self._get_user_profile()
        # clear the wishlist and save the profile
        try:
            prof.session_wish_list = []
            prof.put()
        except:
            retval = False
            raise endpoints.BadRequestException(
                """Problem occured while clearing the session wishlist""")

        return BooleanMessage(data=retval)

    @endpoints.method(SessionSearchForm, SessionForms,
                      path='sessions/future',
                      http_method='GET',
                      name='getAllFutureSessions')
    def getAllFutureSessions(self, request):
        """Retrives session based on a date."""
        sessions = self._get_all_future_sessions(request)
        # return set of ConferenceForm objects per Conference
        return SessionForms(
            items=[self._get_session_form(
                session) for session in sessions]
        )

    @endpoints.method(SessionSearchForm, SessionForms,
                      path='sessions/starting-soon/current',
                      http_method='GET',
                      name='getSessionsStartingSoon')
    def getSessionsStartingSoon(self, request):
        """Gets all the sessions starting within a specified time delta.
        """
        sessions = self._get_starting_soon_sessions(request)
        # return set of ConferenceForm objects per Conference
        return SessionForms(
            items=[self._get_session_form(
                session) for session in sessions]
        )
# registers API
api = endpoints.api_server([ConferenceApi])
