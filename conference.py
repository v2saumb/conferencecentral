#!/usr/bin/env python

"""
conference.py -- Udacity Project conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 v2saumb Exp v2saumb $

Modified by v2saumb on 2016 Jan 04

"""

__author__ = 'v2saumb+api@gmail.com (Saumya Batnagar)'


from datetime import datetime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import logging
from google.appengine.ext import ndb

from models import Profile
from models import ProfileMiniForm
from models import ProfileForm
from models import TeeShirtSize, SESSION_TYPE


from utils import getUserId

from settings import WEB_CLIENT_ID
from models import Conference
from models import ConferenceForm
from models import ConferenceForms
from models import ConferenceQueryForm
from models import ConferenceQueryForms
from models import BooleanMessage
from models import ConflictException
from models import Speaker, SpeakerForm, SpeakerForms, FindSpeakerForm
from models import ConfSession, ConfSessionForm, ConfSessionForms
from google.appengine.api.logservice import logservice

# adding imports for memcache
from google.appengine.api import memcache
from models import StringMessage
#  adding import for the task queue
from google.appengine.api import taskqueue

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "LIMITED-SEATS-AVAILABLE"

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
    'type_of_session': "NOT_SPECIFIED"
}

OPERATORS = {
    'EQ':   '=',
    'GT':   '>',
    'GTEQ': '>=',
    'LT':   '<',
    'LTEQ': '<=',
    'NE':   '!='
}

FIELDS = {
    'CITY': 'city',
    'TOPIC': 'topics',
    'MONTH': 'month',
    'MAX_ATTENDEES': 'maxAttendees',
}

CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)

CONF_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    websafeConferenceKey=messages.StringField(1),
)

CONFSESSION_POST_REQUEST = endpoints.ResourceContainer(
    ConfSessionForm,
    websafeConferenceKey=messages.StringField(1),
)
CONFSESSION_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)
CONFSESSIONTYPES_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
    sessionType=messages.StringField(2),
)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


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
                # elif field.name == 'conferenceKeysToAttend':
                #     conf_keys = list(wsck for wsck in getattr(prof, field.name))
                #     setattr(pf, field.name, conf_keys)
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        user = endpoints.get_current_user()
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

        return profile      # return Profile

    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()
        logging.info(str(prof))

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
        logging.info(messageTxt)
        return messageTxt


# - - - Conference objects - - - - - - - - - - - - - - - - - - -

    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        logging.info(str(conf))
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
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            setattr(cf, 'organizerDisplayName', displayName)
        cf.check_initialized()
        return cf

    def _copyConfSessionToForm(self, confsession):
        """Copy relevant fields from Conference to ConferenceForm."""
        logging.info(str(confsession))
        conf_key = confsession.key.parent()
        conf = conf_key.get()
        cf = ConfSessionForm()
        for field in cf.all_fields():
            if hasattr(confsession, field.name):
                # convert Date to date string; just copy others
                if field.name in ('date', 'start_time'):
                    setattr(cf, field.name, str(
                        getattr(confsession, field.name)))
                elif field.name == 'type_of_session':
                    logging.info("the field ame ")
                    logging.info(
                        str(getattr(SESSION_TYPE, getattr(confsession, field.name))))
                    setattr(cf, field.name, getattr(
                        SESSION_TYPE, getattr(confsession, field.name)))
                else:
                    setattr(cf, field.name, getattr(confsession, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, confsession.key.urlsafe())
        cf.confName = conf.name
        cf.check_initialized()
        return cf

    def _createConferenceObject(self, request):
        """Create or update Conference object, returning ConferenceForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        if not request.name:
            raise endpoints.BadRequestException(
                "Conference 'name' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        del data['websafeKey']
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
        data['key'] = c_key
        data['organizerUserId'] = request.organizerUserId = user_id

        # create Conference & return (modified) ConferenceForm
        Conference(**data).put()
        taskqueue.add(params={'email': user.email(),
                              'conferenceInfo': repr(request)},
                      url='/tasks/sendemail/createconference'
                      )
        return request

    @ndb.transactional()
    def _updateConferenceObject(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}

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
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                    if field.name == 'startDate':
                        conf.month = data.month
                # write to Conference object
                setattr(conf, field.name, data)
        conf.put()
        prof = ndb.Key(Profile, user_id).get()
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
                logging.debug("Helooe")
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

    def _createConfSession(self, request):
        """Create or update Conference Session object, returning ConfSessionForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        if not request.websafeConferenceKey:
            raise endpoints.BadRequestException(
                "Conference 'websafeConferenceKey' field required")

        if not request.session_name:
            raise endpoints.BadRequestException(
                "Conference 'session_name' field required")
        # get the conference key
        conf_key = ndb.Key(urlsafe=request.websafeConferenceKey)
        conf = conf_key.get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)

        if conf.organizerUserId != user_id:
            logging.info(conf.organizerUserId + " != " + user_id)
            raise endpoints.NotFoundException(
                'Only organiser can add sessions. Please contact %s' % conf.organizerUserId)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
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

        # send mail to the Speaker So he knows the schedule
        if request.speaker:
            speakerProf = ndb.Key(urlsafe=request.speaker).get()
            taskqueue.add(params={'email': speakerProf.speakerUserId,
                                  'sessioninfo': self._createSessionMailContent(confSession, conf)},
                          url='/tasks/sendemail/speakersessioncreated'
                          )
        return returnObj

# - - - Announcements - - - - - - - - - - - - - - - - - - - -

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

    def _createSpeaker(self, request):
        """Create or update speaker object, returning SpeakerForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        exSpeaker = self._verifySpeaker(request, True)

        if not request.topics:
            raise endpoints.BadRequestException(
                "Speaker 'topics' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
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

        # create Conference & return (modified) ConferenceForm
        Speaker(**data).put()
        # taskqueue.add(params={'email': user.email(),
        #     'conferenceInfo': repr(request)},
        #     url='//tasks/sendemail/createconference'
        # )
        return request

    def _copySpeakerToForm(self, speakerProfile):
        """Copy relevant fields from Speaker to SpeakerForm."""
        spkr = SpeakerForm()
        speaker = speakerProfile
        prof_key = speakerProfile.key.parent()
        prof = prof_key.get()
        if prof:
            spkr.displayName = prof.displayName

        for field in spkr.all_fields():
            if hasattr(speaker, field.name):
                setattr(spkr, field.name, getattr(speaker, field.name))
            elif field.name == "websafeKey":
                setattr(spkr, field.name, speaker.key.urlsafe())
        spkr.check_initialized()
        logging.info(str(spkr))
        return spkr

    def _verifySpeaker(self, request, suppressEx=False):
        """Verifys if the speaker is registered SpeakerForm/request."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # create ancestor query for all key matches for this user
        speaker = Speaker.query(ancestor=ndb.Key(Profile, user_id)).fetch()
        logging.info(str(speaker))
        prof = ndb.Key(Profile, user_id).get()

        # raise error if speaker not found
        if not suppressEx:
            if not speaker:
                raise endpoints.ConflictException(
                    'Speaker Not Found')
        logging.info(str(speaker))
        if not speaker:
            logging.info('retruning ss')
            return None
        else:
            return self._copySpeakerToForm(speaker[0])

    def _getSpeakerSessionsByKey(self, request):
        """ Returns sessions by speaker key"""
        logging.info(str(request))
        if not request.websafeKey:
            raise endpoints.BadRequestException(
                "Speaker websafeKey or speaker displayName is required.")
        sessions = ConfSession.query(ConfSession.speaker == request.websafeKey).order(
            -ConfSession.date).order(ConfSession.start_time)
        return sessions

    def _getSessionsByType(self, request):
        """" Returns sessions by type"""
        if not request.sessionType:
            raise endpoints.BadRequestException(
                "'sessionType'  is required.")
        confSessions = ConfSession.query(
            ancestor=ndb.Key(urlsafe=request.websafeConferenceKey))

        sessionFilter = ndb.query.FilterNode(
            'type_of_session', '=', request.sessionType)
        confSessions = confSessions.filter(sessionFilter)
        confSessions = confSessions.order(
            -ConfSession.date).order(ConfSession.start_time)
        return confSessions

    def _getSpeakerSessionsByName(self, request):
        """ Returns sessions by speaker displayname"""
        if not request.displayName:
            raise endpoints.BadRequestException(
                "Speaker websafeKey or speaker displayName is required.")
        prof = Profile.query(Profile.displayName ==
                             request.displayName).fetch()
        logging.info(str(prof))
        if len(prof) == 0:
            raise endpoints.BadRequestException(
                "Profile not found for speaker name - %s" % request.displayName)
        speaker = Speaker.query(ancestor=prof[0].key).fetch()
        if len(speaker) == 0:
            raise endpoints.BadRequestException(
                "Profile is not a registered speaker - %s" % request.displayName)
        sessions = ConfSession.query(ConfSession.speaker == speaker[0].key.urlsafe()).order(
            -ConfSession.date).order(ConfSession.start_time)
        return sessions
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
        announcement = memcache.get(MEMCACHE_ANNOUNCEMENTS_KEY)
        if not announcement:
            announcement = ""
        logging.info(announcement)
        return StringMessage(data=announcement)

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
                      path='conference/{websafeConferenceKey}',
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
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)
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

    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='filterPlayground',
                      http_method='GET', name='filterPlayground')
    def filterPlayground(self, request):
        q = Conference.query()
        # simple filter usage:
        # q = q.filter(Conference.city == "Paris")

        # advanced filter building and usage
        field = "city"
        operator = "="
        value = "London"
        f = ndb.query.FilterNode(field, operator, value)
        q = q.filter(f)
        field2 = "topics"
        operator2 = "="
        value2 = "Medical Innovations"
        f2 = ndb.query.FilterNode(field2, operator2, value2)
        q = q.filter(f2)
        field3 = "maxAttendees"
        operator3 = ">"
        value3 = "6"
        f3 = ndb.query.FilterNode(field3, operator3, value3)
        q = q.filter(f3)

        # TODO
        # add 2 filters:
        # 1: city equals to London
        # 2: topic equals "Medical Innovations"

        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, "") for conf in q]
        )

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='conference/{websafeConferenceKey}',
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
        list_of_confs = list(ndb.Key(urlsafe=wsck)
                             for wsck in prof.conferenceKeysToAttend)
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
            ancestor=ndb.Key(urlsafe=request.websafeConferenceKey))
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
        # make sure user is authed
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

        if request.websafeConferenceKey and request.sessionType:
            sessions = self._getSessionsByType(request)

        return ConfSessionForms(
            items=[self._copyConfSessionToForm(
                session) for session in sessions]
        )
# registers API
api = endpoints.api_server([ConferenceApi])
