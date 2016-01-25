#!/usr/bin/env python
import webapp2
import logging
from google.appengine.api import app_identity
from google.appengine.api import mail
from conference import ConferenceApi


class SetAnnouncementHandler(webapp2.RequestHandler):
    """ Handles the anouncement get request that come through the CRON"""

    def get(self):
        """Set Announcement in Memcache."""
        ConferenceApi._cache_announcement()


class SetStartingSoon(webapp2.RequestHandler):
    """ Handles the starting soon get request that come through the CRON"""

    def get(self):
        """Set starting soon in session."""
        ConferenceApi._cache_starting_soon()


class SetNewSpeakerSpecial(webapp2.RequestHandler):
    """ Handles the task for setting the featured speaker """

    def post(self):
        """Set featured Speaker in the Memcache."""
        logging.info("inside the featured speaker job")
        ConferenceApi._cache_featured_speaker(self.request)


class SendConfirmationEmailHandler(webapp2.RequestHandler):
    """ Handles the post request for sending emails for
    the conference creattion """

    def post(self):
        """Send email confirming Conference creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Conference!',            # subj
            'Hi, you have created a following '         # body
            'conference:\r\n\r\n%s' % self.request.get(
                'conferenceInfo')
        )


class SendSpeakerCreated(webapp2.RequestHandler):
    """ Handles the post request for sending emails when a speaker registers"""

    def post(self):
        """Send email confirming Conference creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You Registered as a Speaker!',            # subj
            """'Hi,  Welcome ! your registration as speaker was successful.
            We will assign you some sessions soon"""
        )


class SendSessionEmailHandler(webapp2.RequestHandler):
    """Handles the post request for sending emails for the session creattion"""

    def post(self):
        """ Sends emails for the session creattion """
        session = self.request.get('sessioninfo')
        message_text = """Hi There! \nYou created the
         following Session:{}""".format(
            session)
        logging.info(message_text)
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),
            self.request.get('email'),
            'You created / updated a Session!',
            message_text
        )


class SendSpeakerEmailHandler(webapp2.RequestHandler):
    """ Handles the post request for sending emails for the session creattion
     to the speaker"""

    def post(self):
        """ Sends the emails for the session creattion to the speaker"""
        session = self.request.get('sessioninfo')
        message_text = """Hi There! \nYou are required to speak at the following
         Session:{}""".format(
            session)
        logging.info(message_text)
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You Are Invited To Speak At A Session!',            # subj
            message_text
        )

app = webapp2.WSGIApplication([
    ('/tasks/setfeaturedspeaker', SetNewSpeakerSpecial),
    ('/crons/set_announcement', SetAnnouncementHandler),
    ('/crons/set_starting_soon', SetStartingSoon),
    ('/tasks/sendemail/createconference', SendConfirmationEmailHandler),
    ('/tasks/sendemail/createsession', SendSessionEmailHandler),
    ('/tasks/sendemail/speakersessioncreated', SendSpeakerEmailHandler),
    ('/tasks/sendemail/speakercreated', SendSpeakerCreated)
], debug=True)
