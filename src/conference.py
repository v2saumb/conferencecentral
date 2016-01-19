#!/usr/bin/env python

"""
conference.py -- Udacity Project conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 v2saumb Exp v2saumb $

Modified by v2saumb on 2016 Jan 04

"""

__author__ = 'v2saumb+api@gmail.com (Saumya Batnagar)'


from datetime import tzinfo, timedelta, datetime
from time import gmtime, strftime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import logging

from settings import WEB_CLIENT_ID
from models import Profile, ProfileMiniForm, ProfileForm
from models import TeeShirtSize, SESSION_TYPE
from models import Conference, ConferenceForm, ConferenceForms
from models import ConferenceQueryForm, ConferenceQueryForms
from models import BooleanMessage
from models import ConflictException
from models import Speaker, SpeakerForm, SpeakerForms, FindSpeakerForm, FeaturedSpeakerForm
from models import ConfSession, ConfSessionForm, ConfSessionForms
from models import ConfSessionSearchForm, ConfSessionTask3SearchForm
from utils import getUserId

from google.appengine.ext import ndb
# adding the log service import
from google.appengine.api.logservice import logservice

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

# default values for conf object
DEFAULTS = {
    "city": "Default City",
    "maxAttendees": 0,
    "seatsAvailable": 0,
    "topics": ["Default", "Topic"],
}

# default values for speaker object
SPEAKER_DEFAULTS = {
    "topics": ["Default", "Topic"],
}
# default values for confSession object
SESSION_DEFAULTS = {
    'highlights': '',
    'speaker':  '',
    'duration': 30,
    'type_of_session': "General"
}
# operators for the query filters for Conferences
OPERATORS = {
    'EQ':   '=',
    'GT':   '>',
    'GTEQ': '>=',
    'LT':   '<',
    'LTEQ': '<=',
    'NE':   '!='
}
# field names for the query filters for conferences
FIELDS = {
    'CITY': 'city',
    'TOPIC': 'topics',
    'MONTH': 'month',
    'MAX_ATTENDEES': 'maxAttendees',
}
# GET request where we only need the key passed as part of the url
CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)
# Post request where we only need the key passed as part of the url
# This reques also has the conference form
CONF_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    websafeConferenceKey=messages.StringField(1),
)
# GET request for Sessions where we only need the key passed as part of the url
CONFSESSION_POST_REQUEST = endpoints.ResourceContainer(
    ConfSessionForm,
    websafeConferenceKey=messages.StringField(1),
)
# Post request for Sessions where we only need the key passed as part of
# the url with session form
CONFSESSION_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)
# GET request for Sessions where we only need the conference key  and the
# session type are passed as part of the url
CONFSESSIONTYPES_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
    sessionType=messages.StringField(2),
)
# GET request for adding/removing Sessions to the wishlist and session key
# is passed in the url
WISHLIST_SESSION_POST_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeKey=messages.StringField(1),
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

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'teeShirtSize':
                    setattr(pf, field.name, getattr(
                        TeeShirtSize, getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        user = endpoints.get_current_user()
        # if user is not logged in throw error
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()

        # create new Profile if not there
        if not profile:
            profile = Profile(
                key=p_key,
                displayName=user.nickname(),
                mainEmail=user.email(),
                teeShirtSize=str(TeeShirtSize.NOT_SPECIFIED),
            )
            profile.put()
        # return Profile
        return profile

    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()
        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName', 'teeShirtSize'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
            prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)

    def _createSessionMailContent(self, session, conf):
        """ formats and creates a mail content for session creator and speaker"""
        messageTxt = """\nConference Name:\t{0}
        \nSession:\t{1}
        \nDuration:\t{2}
        \nDate:\t{3}
        \nStart Time:\t{4}
        \nCity:\t{5}
        \nVenue:\t{6}""".format(conf.name, session.session_name,
                                session.duration, session.date, session.start_time,
                                conf.city, session.venue)
        return messageTxt


# - - - Private methods  - - - - - - - - - - - - - - - - - - -

    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()

        # return set of ConferenceForm objects per Conference
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('Date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "websafeKey":
                # add the websafe key for outbound
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            # add disolay name for the conference organizer for outbound
            setattr(cf, 'organizerDisplayName', displayName)
        # validate the form
        cf.check_initialized()
        return cf

    def _copyConfSessionToForm(self, confsession):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConfSessionForm()
        #  return a empty form if session is not passed
        if not confsession:
            return cf
        # get the conference details
        conf_key = confsession.key.parent()
        conf = conf_key.get()

        for field in cf.all_fields():
            if hasattr(confsession, field.name):
                # convert Date to date string; just copy others
                if field.name in ('date', 'start_time'):
                    setattr(cf, field.name, str(
                        getattr(confsession, field.name)))
                elif field.name == 'type_of_session':
                    # set the session type from enum
                    setattr(cf, field.name, getattr(
                        SESSION_TYPE, getattr(confsession, field.name)))
                else:
                    setattr(cf, field.name, getattr(confsession, field.name))
            elif field.name == "websafeKey":
                #  set the session key for outbound
                setattr(cf, field.name, confsession.key.urlsafe())
        # set the conference name
        cf.confName = conf.name
        # validate the form
        cf.check_initialized()
        return cf

    def _createConferenceObject(self, request):
        """Create or update Conference object, returning ConferenceForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        # raise error if user is not logged in.
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        if not request.name:
            raise endpoints.BadRequestException(
                "Conference 'name' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # delete the websafe key not required by the entity
        del data['websafeKey']
        # delete the organizerDisplayName not required by the entity
        del data['organizerDisplayName']

        # add default values for those missing (both data model & outbound
        # Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on
        # start_date
        if data['startDate']:
            data['startDate'] = datetime.strptime(
                data['startDate'][:10], "%Y-%m-%d").date()
            data['month'] = data['startDate'].month
        else:
            data['month'] = 0
        if data['endDate']:
            data['endDate'] = datetime.strptime(
                data['endDate'][:10], "%Y-%m-%d").date()

        # set seatsAvailable to be same as maxAttendees on creation
        if data["maxAttendees"] > 0:
            data["seatsAvailable"] = data["maxAttendees"]
        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        # set te key
        data['key'] = c_key
        # set the organizer id from the profile
        data['organizerUserId'] = request.organizerUserId = user_id

        # create Conference & return (modified) ConferenceForm
        Conference(**data).put()
        # send confference creation mail
        taskqueue.add(params={'email': user.email(),
                              'conferenceInfo': repr(request)},
                      url='/tasks/sendemail/createconference'
                      )
        return request

    @ndb.transactional()
    def _updateConferenceObject(self, request):
        """ updates the conference details based on the key and other information """
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # remove fields notrequired by the entity
        del data['websafeKey']
        del data['organizerDisplayName']

        # update existing conference
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        # check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)

        # check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can update the conference.')

        # Not getting all the fields, so don't create a new object; just
        # copy relevant fields from ConferenceForm to Conference object
        for field in request.all_fields():
            data = getattr(request, field.name)
            # only copy fields where we get data
            if data not in (None, []):
                # special handling for dates (convert string to Date)
                if field.name in ('startDate', 'endDate'):
                    data = datetime.strptime(data[:10], "%Y-%m-%d").date()
                    if field.name == 'startDate':
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
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))

    def _getQuery(self, request):
        """Return formatted query from the submitted filters."""
        q = Conference.query()
        inequality_filter, filters = self._formatFilters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Conference.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Conference.name)

        for filtr in filters:
            if filtr["field"] in ["month", "maxAttendees"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(
                filtr["field"], filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q

    def _formatFilters(self, filters):
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
                # check if inequality operation has been used in previous filters
                # disallow the filter if inequality was performed on a different field before
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
    def _conferenceRegistration(self, request, reg=True):
        """Register or unregister user for selected conference."""
        retval = None
        prof = self._getProfileFromUser()  # get user Profile

        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.websafeConferenceKey
        conf = ndb.Key(urlsafe=wsck).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % wsck)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsck in prof.conferenceKeysToAttend:
                raise ConflictException(
                    "You have already registered for this conference")

            # check if seats avail
            if conf.seatsAvailable <= 0:
                raise ConflictException(
                    "There are no seats available.")

            # register user, take away one seat
            prof.conferenceKeysToAttend.append(wsck)
            conf.seatsAvailable -= 1
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsck in prof.conferenceKeysToAttend:

                # unregister user, add back one seat
                prof.conferenceKeysToAttend.remove(wsck)
                conf.seatsAvailable += 1
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        conf.put()
        return BooleanMessage(data=retval)

    def _manageSessionWishList(self, request, reg=True):
        """Add or remove sessions form users wishlist."""
        retval = None
        prof = self._getProfileFromUser()  # get user Profile
        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.websafeKey
        session = ndb.Key(urlsafe=wsck).get()
        if not session:
            raise endpoints.NotFoundException(
                'No session found with key: %s' % wsck)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsck in prof.sessionWishList:
                raise ConflictException(
                    "This session already exist in your wishlist")

            # register user, take away one seat
            prof.sessionWishList.append(wsck)
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsck in prof.sessionWishList:

                # unregister user, add back one seat
                prof.sessionWishList.remove(wsck)
                retval = True
            else:
                raise ConflictException(
                    "This session does not exist in your wishlist!")
                retval = False

        # write things back to the datastore & return
        prof.put()
        return BooleanMessage(data=retval)

    def _createConfSession(self, request):
        """Create or update Conference Session object, returning ConfSessionForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        #  raise exceptio if the conference key is not passed in
        if not request.websafeConferenceKey:
            raise endpoints.BadRequestException(
                "Conference 'websafeConferenceKey' field required")
        # raise exception if required field is mising
        if not request.session_name:
            raise endpoints.BadRequestException(
                "Conference 'session_name' field required")
            
        if not request.speaker:
            raise endpoints.BadRequestException(
                "Conference 'speaker' is  required")
        # get the conference key
        conf_key = ndb.Key(urlsafe=request.websafeConferenceKey)
        conf = conf_key.get()
        # raise exception if the conference is not found
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)
        # raise exception if user is not the organizer of this conference
        if conf.organizerUserId != user_id:
            raise endpoints.NotFoundException(
                'Only organiser can add sessions. Please contact %s' % conf.organizerUserId)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # remove fields notrequired
        del data['websafeKey']
        del data['websafeConferenceKey']
        del data['confName']

        # add default values for those missing (both data model & outbound
        # Message)
        for df in SESSION_DEFAULTS:
            if data[df] in (None, []):
                data[df] = SESSION_DEFAULTS[df]
                setattr(request, df, SESSION_DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on
        # start_date
        if data['date']:
            data['date'] = datetime.strptime(
                data['date'][:10], "%Y-%m-%d").date()

        # convert time
        if data['start_time']:
            data['start_time'] = datetime.strptime(
                data['start_time'][:5], "%H:%M").time()
            # adding time to the date field the will help filter results later
            combTime = datetime.combine(data['date'], data['start_time'])
            data['date'] = combTime

        # convert session type
        if data['type_of_session']:
            data['type_of_session'] = str(data['type_of_session'])

        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        c_id = ConfSession.allocate_ids(size=1, parent=conf_key)[0]
        c_key = ndb.Key(ConfSession, c_id, parent=conf_key)
        data['key'] = c_key
        # create Conference & return (modified) ConferenceForm
        ConfSession(**data).put()
        confSession = c_key.get()
        returnObj = self._copyConfSessionToForm(confSession)
        # send mail to organizer about the new conference Session
        taskqueue.add(params={'email': user.email(),
                              'sessioninfo': self._createSessionMailContent(confSession, conf)},
                      url='/tasks/sendemail/createsession'
                      )
        speakerKey = request.speaker
        # send mail to the Speaker So he knows the schedule
        if request.speaker:
            speakerProf = ndb.Key(urlsafe=speakerKey).get()
            taskqueue.add(params={'email': speakerProf.speakerUserId,
                                  'sessioninfo': self._createSessionMailContent(confSession, conf)},
                          url='/tasks/sendemail/speakersessioncreated'
                          )
            # add task to check for features speaker.
            taskqueue.add(params={'email': speakerProf.speakerUserId,
                                  'speakerKey': speakerKey,
                                  'confKey': conf_key.urlsafe()}, url='/tasks/setfeaturedspeaker')
        return returnObj

    def _createSpeaker(self, request):
        """Create or update speaker object, returning SpeakerForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        # raise exception if the user is not logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        user_id = getUserId(user)
        # If there are no sold out conferences,
        exSpeaker = self._verifySpeaker(request, True)
        # raise exception if the user already exixts
        if not request.topics:
            raise endpoints.BadRequestException(
                "Speaker 'topics' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}

        # remove fields not required by entity
        del data['websafeKey']
        del data['displayName']

        # add default values for those missing (both data model & outbound
        # Message)
        for df in SPEAKER_DEFAULTS:
            if data[df] in (None, []):
                data[df] = SPEAKER_DEFAULTS[df]
                setattr(request, df, SPEAKER_DEFAULTS[df])

        if exSpeaker:
            speaker_key = ndb.Key(urlsafe=exSpeaker.websafeKey)
        else:
            p_key = ndb.Key(Profile, user_id)
            speaker_id = Speaker.allocate_ids(size=1, parent=p_key)[0]
            speaker_key = ndb.Key(Speaker, speaker_id, parent=p_key)
            data['speakerUserId'] = request.speakerUserId = user_id

        data['key'] = speaker_key
        logging.info(data['key'])

        # create speaker & return (modified) Speaker
        Speaker(**data).put()
        # send the speaker a mail confirming of registration
        taskqueue.add(params={'email': user.email()},
                      url='/tasks/sendemail/speakercreated'
                      )
        return request

    def _copySpeakerToForm(self, speakerProfile):
        """Copy relevant fields from Speaker to SpeakerForm."""
        # init the speaker form
        spkr = SpeakerForm()
        speaker = speakerProfile
        # get the speaker profile
        prof_key = speakerProfile.key.parent()
        prof = prof_key.get()
        # get the display name from the profile
        if prof:
            spkr.displayName = prof.displayName

        for field in spkr.all_fields():
            if hasattr(speaker, field.name):
                setattr(spkr, field.name, getattr(speaker, field.name))
            elif field.name == "websafeKey":
                # assign the websafe  key for outbound
                setattr(spkr, field.name, speaker.key.urlsafe())
        #  verify the speaker form
        spkr.check_initialized()
        return spkr

    def _copyFeaturedSpeakerToForm(self, featuredSpeaker):
        """Copy relevant fields from featuerSpeaker to FeaturedSpeakerForm."""
        # init the form
        spkr = FeaturedSpeakerForm()
        speaker = featuredSpeaker
        # set he form fields
        for field in spkr.all_fields():
            setattr(spkr, field.name, speaker.get(field.name))
        # verif the speaker form
        spkr.check_initialized()
        return spkr

    def _verifySpeaker(self, request, suppressEx=False):
        """Verifys if the speaker is registered SpeakerForm/request."""
        # make sure user is authed
        user = endpoints.get_current_user()
        # raise error if the user is not logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # create ancestor query for all key matches for this user
        speaker = Speaker.query(ancestor=ndb.Key(Profile, user_id)).fetch()
        # get the profile for the speaker
        prof = ndb.Key(Profile, user_id).get()

        # raise error if speaker not found
        if not suppressEx:
            if not speaker:
                raise endpoints.ConflictException(
                    'Speaker Not Found')
        if not speaker:
            return SpeakerForm()
        else:
            return self._copySpeakerToForm(speaker[0])

    def _getSpeakerSessionsByKey(self, request):
        """ Returns sessions by speaker key"""
        # raise error if the key is not present
        if not request.websafeKey:
            raise endpoints.BadRequestException(
                "Speaker websafeKey or speaker displayName is required.")
        # get session by speaker
        sessions = ConfSession.query(ConfSession.speaker == request.websafeKey).order(
            -ConfSession.date).order(ConfSession.start_time)
        # return the sessions
        return sessions

    def _getSessionsByType(self, request):
        """" Returns sessions by session type in a conference type"""
        # raise an error if session type is not passed
        if not request.sessionType:
            raise endpoints.BadRequestException(
                "'sessionType'  is required.")
        # get all the sessions for the conference
        confSessions = ConfSession.query(
            ancestor=ndb.Key(urlsafe=request.websafeConferenceKey))
        # filter sessions for the desired type
        sessionFilter = ndb.query.FilterNode(
            'type_of_session', '=', request.sessionType)
        confSessions = confSessions.filter(sessionFilter)
        # set up the order
        confSessions = confSessions.order(
            -ConfSession.date).order(ConfSession.start_time)
        # return the sessions
        return confSessions

    def _getSpeakerSessionsByName(self, request):
        """ Returns sessions by speaker displayname"""
        # raise error if the diaplay name is not passed
        if not request.displayName:
            raise endpoints.BadRequestException(
                "Speaker websafeKey or speaker displayName is required.")
        #  get the profile by display name
        prof = Profile.query(Profile.displayName ==
                             request.displayName).fetch()
        # if the speaker profile is not found raise an error
        if len(prof) == 0:
            raise endpoints.BadRequestException(
                "Profile not found for speaker name - %s" % request.displayName)
        # fetch the speaker information
        speaker = Speaker.query(ancestor=prof[0].key).fetch()

        # raise exception if the speaker is not found
        if len(speaker) == 0:
            raise endpoints.BadRequestException(
                "Profile is not a registered speaker - %s" % request.displayName)

        # get sessions for the speaker
        sessions = ConfSession.query(ConfSession.speaker == speaker[0].key.urlsafe()).order(
            -ConfSession.date).order(ConfSession.start_time)
        # return the speaker
        return sessions

    def _getAllFutureSessions(self, request):
        """ Returns all future sessions """
        # get the dates from the request
        strdate = request.start_date
        strEndDate = request.end_date
        # format the start date time
        if strdate:
            startDate = datetime.combine(datetime.strptime(strdate[
                :16], "%Y-%m-%d %H:%M").date(),
                datetime.strptime(strdate[:16], "%Y-%m-%d %H:%M").time())

        # format the end date time
        if strEndDate:
            endDate = datetime.combine(datetime.strptime(strEndDate[
                :16], "%Y-%m-%d %H:%M").date(),
                datetime.strptime(strEndDate[:16], "%Y-%m-%d %H:%M").time())
        else:
            endDate = None

        # query all session after the start date
        sessions = ConfSession.query(
            ConfSession.date > startDate).order(ConfSession.date)

        # filter all session based on end date if passed in request
        if endDate:
            sessions = sessions.filter(
                ConfSession.date <= endDate).order(ConfSession.date)

        return sessions

    def _getStartingSoonSessions(self, request):
        """ Return all session that are starting soon request
        will have the delta to select the upper limit
        """
        # get the starting date from request
        strdate = request.start_date
        # format date if passed raise exception if date is not passed
        if strdate:
            startDate = datetime.combine(datetime.strptime(strdate[
                :16], "%Y-%m-%d %H:%M").date(),
                datetime.strptime(strdate[:16], "%Y-%m-%d %H:%M").time())
        else:
            raise endpoints.BadRequestException("'startDate' field required")

        # get the delta minutes
        endDelta = int(request.deltaMinutes) or STARTING_SOON_INTERVAL
        #  create end date
        endDate = startDate + timedelta(minutes=endDelta)
        # query session based on the start date
        sessions = ConfSession.query(
            ConfSession.date > startDate).order(ConfSession.date)
        # filter the sessions based on the end date
        if endDate:
            sessions = sessions.filter(
                ConfSession.date <= endDate).order(ConfSession.date)
        # return the sessions            #
        return sessions
    # ----------------Static Methods-------------------------------

    @staticmethod
    def _cacheAnnouncement():
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        logging.info("in the method for set announcements")
        confs = Conference.query(ndb.AND(
            Conference.seatsAvailable <= 5,
            Conference.seatsAvailable > 0)
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

        return announcement

    @staticmethod
    def _cacheStartingSoon():
        """Finds and sets the sessions startign soon in the memcache; used by
        memcache cron job & putAnnouncement().
        """
        logging.info("in the method for set starting soon")
        # get current datetime
        startDate = datetime.combine(
            datetime.now().date(), datetime.now().time())
        # get the timezone
        tzone = strftime("%z", gmtime())
        # if utc calculate est date
        if tzone in ("UTC", "+0000"):
            delta = timedelta(hours=-5)
            startDate += delta

        logging.info(startDate)
        # calculate the end date based on the interval
        endDate = startDate + timedelta(minutes=int(STARTING_SOON_INTERVAL))
        logging.info(str(startDate) + " ," + str(endDate))
        # get sessions
        sessions = ConfSession.query(
            ConfSession.date > startDate).order(ConfSession.date)
        # filter sessions  if end date is available
        if endDate:
            sessions = sessions.filter(
                ConfSession.date <= endDate).order(ConfSession.date)
        # if sessions exixts fetch the required fields and. Picking only n
        # number of sessions due to limited space on the frontend
        if sessions:
            sessions = sessions.fetch(
                STARTING_SOON_COUNT, projection=[ConfSession.session_name,
                                                 ConfSession.date, ConfSession.venue,
                                                 ConfSession.type_of_session])
            # set the sessions in memcache
            memcache.set(MEMCACHE_STARTING_SOON_KEY, sessions)
        else:
            # delete the memcache announcements entry
            sesssions = None
            memcache.delete(MEMCACHE_STARTING_SOON_KEY)
        # return the sessions not required though
        return sessions

    @staticmethod
    def _cacheFeaturedSpeaker(request):
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        # set the counter  = 0
        sessions = 0
        # init featuredSpeaker
        featuredSpeaker = {}
        logging.info("in the method for set featured speaker")
        # get the sesion in the conference
        sessions = ConfSession.query(ancestor=ndb.Key(urlsafe=request.get(
            'confKey'))).filter(ConfSession.speaker == request.get('speakerKey'))
        # if there are more then one sessions by the speaker get the required
        # information

        if sessions.count(limit=5) > 1:
            # get conference info
            conf = ndb.Key(urlsafe=request.get('confKey')).get()
            # get speaker profile
            speakerProf = ndb.Key(urlsafe=request.get(
                'speakerKey')).parent().get()
            # get the session names only
            sessions = sessions.fetch(5, projection=[ConfSession.session_name])

            logging.info(speakerProf.displayName)
            # create the featured speaker object
            featuredSpeaker = {'speakerName': speakerProf.displayName,
                               'confName': conf.name,
                               'sessions': [conf_session.session_name for conf_session in
                                            sessions]
                               }
            # set the featured speaker in memcache
            memcache.set(MEMCACHE_FEATURED_SPEAKERS, featuredSpeaker)
        return featuredSpeaker

    #  ------------------------------- Endpoints ---------------------

    # register a user as speaker
    @endpoints.method(SpeakerForm, SpeakerForm, path='registerSpeaker',
                      http_method='POST', name='registerSpeaker')
    def registerSpeaker(self, request):
        """Register a Speaker."""
        return self._createSpeaker(request)

    # verify if the user is already registered as speaker
    @endpoints.method(message_types.VoidMessage, SpeakerForm, path='speakerExists',
                      http_method='POST', name='speakerExists')
    def speakerExists(self, request):
        """Register a Speaker."""
        return self._verifySpeaker(request)

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

    @endpoints.method(message_types.VoidMessage, ConfSessionForms,
                      path='sessions/starting-soon/cached',
                      http_method='GET', name='getSessionsStartingSoonCached')
    def getSessionsStartingSoonCached(self, request):
        """Return Announcement from memcache."""
        logging.info(MEMCACHE_STARTING_SOON_KEY)
        #
        sessions = memcache.get(MEMCACHE_STARTING_SOON_KEY)
        # raise errors if no sessions are found
        if not sessions:
            sessions = None
            raise endpoints.ConflictException(
                'Sessions Not Found')
        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                session) for session in sessions]
        )

    @endpoints.method(message_types.VoidMessage, FeaturedSpeakerForm,
                      path='speaker/featured-speaker/cached',
                      http_method='GET', name='getFeaturedSpeakerCached')
    def getFeaturedSpeakerCached(self, request):
        """Return featured speakers from memcache."""
        logging.info(MEMCACHE_FEATURED_SPEAKERS)
        # get the featured speakers from memcache
        featuredSpeaker = memcache.get(MEMCACHE_FEATURED_SPEAKERS)
        # raise error if the speaker is not found
        if not featuredSpeaker:
            featuredSpeaker = None
            raise endpoints.ConflictException(
                'Featured Speaker Not Found')
        return self._copyFeaturedSpeakerToForm(featuredSpeaker)

    @endpoints.method(message_types.VoidMessage, ProfileForm,
                      path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()

    @endpoints.method(ProfileMiniForm, ProfileForm,
                      path='profile', http_method='POST', name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)

    @endpoints.method(ConferenceForm, ConferenceForm, path='conference',
                      http_method='POST', name='createConference')
    def createConference(self, request):
        """Create new conference."""
        return self._createConferenceObject(request)

    @endpoints.method(CONF_POST_REQUEST, ConferenceForm,
                      path='conference/edit/{websafeConferenceKey}',
                      http_method='PUT', name='updateConference')
    def updateConference(self, request):
        """Update conference w/provided fields & return w/updated info."""
        return self._updateConferenceObject(request)

    @endpoints.method(CONF_GET_REQUEST, ConferenceForm,
                      path='conference/{websafeConferenceKey}',
                      http_method='GET', name='getConference')
    def getConference(self, request):
        """Return requested conference (by websafeConferenceKey)."""
        # get Conference object from request; bail if not found
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        #  raise error if conf not found
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)
        # get the organizer profile
        prof = conf.key.parent().get()
        # return ConferenceForm
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))

    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='getConferencesCreated',
                      http_method='POST', name='getConferencesCreated')
    def getConferencesCreated(self, request):
        """Return conferences created by user."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # create ancestor query for all key matches for this user
        confs = Conference.query(ancestor=ndb.Key(Profile, user_id))
        # get the organizer profile
        prof = ndb.Key(Profile, user_id).get()
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
            items=[self._copyConferenceToForm(
                conf, getattr(prof, 'displayName')) for conf in confs]
        )

    @endpoints.method(ConferenceQueryForms, ConferenceForms,
                      path='queryConferences',
                      http_method='POST',
                      name='queryConferences')
    def queryConferences(self, request):
        """Query for conferences."""
        conferences = self._getQuery(request)

        # need to fetch organiser displayName from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile, conf.organizerUserId))
                      for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return individual ConferenceForm object per Conference
        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, names[conf.organizerUserId]) for conf in
                   conferences]
        )

    @endpoints.method(ConfSessionTask3SearchForm, ConfSessionForms,
                      path='sessions/beforetime',
                      http_method='GET', name='getAllSessionsBeforeTime')
    def getAllSessionsBeforeTime(self, request):
        """ Returns all the sessions before the 'start_time' and are not of type 'session_type' """
        stTime = request.start_time
        # format the time from the requst
        startTime = datetime.strptime(stTime[:5], "%H:%M").time()
        # fetch only the keys for sessions before the requested time
        timeQry = ConfSession.query(ConfSession.start_time < startTime).order(
            ConfSession.start_time).order(-ConfSession.date).fetch(keys_only=True)

        # query the session which are not of the type specified in the request
        # and get only the keys
        typeQry = ConfSession.query(ConfSession.type_of_session != request.session_type).order(
            ConfSession.type_of_session).order(-ConfSession.date).fetch(keys_only=True)
        # create a set by intersection of both the queries and then get the
        # results
        cSessions = ndb.get_multi(set(timeQry).intersection(typeQry))
        # return the results
        return ConfSessionForms(
            items=[self._copyConfSessionToForm(conf) for conf in cSessions]
        )

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='conference/register/{websafeConferenceKey}',
                      http_method='POST', name='registerForConference')
    def registerForConference(self, request):
        """Register user for selected conference."""
        return self._conferenceRegistration(request)

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='conference/unregister/{websafeConferenceKey}',
                      http_method='POST', name='unregisterFromConference')
    def unregisterFromConference(self, request):
        """Register user for selected conference."""
        return self._conferenceRegistration(request, False)

    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='conferences/attending',
                      http_method='GET', name='getConferencesToAttend')
    def getConferencesToAttend(self, request):
        """Get list of conferences that user has registered for."""
        prof = self._getProfileFromUser()
        # get the list of conferences
        list_of_confs = list(ndb.Key(urlsafe=wsck)
                             for wsck in prof.conferenceKeysToAttend)
        # get all the conferences
        conferences = ndb.get_multi(list_of_confs)
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(items=[self._copyConferenceToForm(conf, "")
                                      for conf in conferences]
                               )
    # create new session

    @endpoints.method(CONFSESSION_POST_REQUEST, ConfSessionForm, path='confSession/create/{websafeConferenceKey}',
                      http_method='POST', name='createSession')
    def createSession(self, request):
        """Creates a new conference session."""
        return self._createConfSession(request)

    @endpoints.method(CONFSESSION_GET_REQUEST, ConfSessionForms,
                      path='conference/sessions/{websafeConferenceKey}',
                      http_method='GET', name='getConferenceSessions')
    def getConferenceSessions(self, request):
        """Return sessions for a conference."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # conf_key = ndb.Key(urlsafe=request.websafeConferenceKey)
        # conf = conf_key.get()
        # create ancestor query for all key matches for this conference
        confSessions = ConfSession.query(
            ancestor=ndb.Key(urlsafe=request.websafeConferenceKey)).order(-ConfSession.date)
        # return set of ConferenceForm objects per Conference
        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                confSession) for confSession in confSessions]
        )

    @endpoints.method(message_types.VoidMessage, SpeakerForms,
                      path='speaker/all',
                      http_method='GET', name='getAllSpeakers')
    def getAllSpeakers(self, request):
        """Return All speakers . """
        # get all the speakers
        speakers = Speaker.query()
        return SpeakerForms(
            items=[self._copySpeakerToForm(
                speaker) for speaker in speakers]
        )

    @endpoints.method(FindSpeakerForm, ConfSessionForms,
                      path='speaker/sessions',
                      http_method='GET', name='getSessionsBySpeaker')
    def getSessionsBySpeaker(self, request):
        """Return sessions by a speaker."""
        # get the sessbuy key if present else get them by name
        if request.websafeKey:
            sessions = self._getSpeakerSessionsByKey(request)
        else:
            sessions = self._getSpeakerSessionsByName(request)

        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                session) for session in sessions]
        )

    @endpoints.method(CONFSESSIONTYPES_GET_REQUEST, ConfSessionForms,
                      path='conference/sessions/{websafeConferenceKey}/{sessionType}',
                      http_method='GET', name='getConferenceSessionsByType')
    def getConferenceSessionsByType(self, request):
        """Return sessions by a speaker."""
        # if both conf key and the session type are passed get the sessions
        if request.websafeConferenceKey and request.sessionType:
            sessions = self._getSessionsByType(request)

        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                session) for session in sessions]
        )

    @endpoints.method(WISHLIST_SESSION_POST_REQUEST, BooleanMessage,
                      path='session/addtowishlist/{websafeKey}',
                      http_method='POST', name='addSessionToWishlist')
    def addSessionToWishlist(self, request):
        """Add a sessions to users wishlist."""
        logging.info('in add session to wishlist')
        return self._manageSessionWishList(request, True)

    @endpoints.method(WISHLIST_SESSION_POST_REQUEST, BooleanMessage,
                      path='session/deletefromwishlist/{websafeKey}',
                      http_method='POST', name='deleteSessionInWishlist')
    def deleteSessionInWishlist(self, request):
        """Removes a sessions from users wishlist."""
        logging.info('in add session to wishlist')
        return self._manageSessionWishList(request, False)

    @endpoints.method(message_types.VoidMessage, ConfSessionForms,
                      path='sessionwishList',
                      http_method='GET', name='getSessionsInWishlist')
    def getSessionsInWishlist(self, request):
        """Retrives all sessions from users wishlist."""
        prof = self._getProfileFromUser()
        # get the lest of sesssion keys
        list_of_sessions = list(ndb.Key(urlsafe=wsck)
                                for wsck in prof.sessionWishList)
        # get the session for the keys
        sessions = ndb.get_multi(list_of_sessions)
        # return set of ConferenceForm objects per Conference
        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                session) for session in sessions]
        )

    @endpoints.method(ConfSessionSearchForm, ConfSessionForms,
                      path='sessions/future',
                      http_method='GET', name='getAllFutureSessions')
    def getAllFutureSessions(self, request):
        """retrives session based on a date."""
        sessions = self._getAllFutureSessions(request)
        # return set of ConferenceForm objects per Conference
        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                session) for session in sessions]
        )

    @endpoints.method(ConfSessionSearchForm, ConfSessionForms,
                      path='sessions/starting-soon/current',
                      http_method='GET', name='getSessionsStartingSoon')
    def getSessionsStartingSoon(self, request):
        """Gets all the sessions starting within a specified time delta.
            RequestType: ConfSessionSearchForm 
            ResponseType: ConfSessionForms (list of sessions)
            Type: GET
            Path: sessions/starting-soon/current
        """
        sessions = self._getStartingSoonSessions(request)
        # return set of ConferenceForm objects per Conference
        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                session) for session in sessions]
        )
# registers API
api = endpoints.api_server([ConferenceApi])
