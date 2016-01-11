#!/usr/bin/env python
import webapp2
import logging
from google.appengine.api import app_identity
from google.appengine.api import mail
from conference import ConferenceApi


class SetAnnouncementHandler(webapp2.RequestHandler):

    def get(self):
        """Set Announcement in Memcache."""
        # TODO 1
        # use _cacheAnnouncement() to set announcement in Memcache
        ConferenceApi._cacheAnnouncement()

app = webapp2.WSGIApplication([
    ('/crons/set_announcement', SetAnnouncementHandler),
], debug=True)


class SendConfirmationEmailHandler(webapp2.RequestHandler):

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


class SendSessionEmailHandler(webapp2.RequestHandler):
    """ Sends a mail to the creator of the session """

    def post(self):
        session = self.request.get('sessioninfo')
        messageTxt = """Hi There! \nYou created the following Session:{}""".format(
            session)
        logging.info(messageTxt)
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created / updated a Session!',            # subj
            messageTxt
        )


class SendSpeakerEmailHandler(webapp2.RequestHandler):
    """ Sends a mail to the speaker of the session """

    def post(self):
        session = self.request.get('sessioninfo')
        messageTxt = """Hi There! \nYou are required to speak at the following Session:{}""".format(
            session)
        logging.info(messageTxt)
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You Are Invited To Speak At A Session!',            # subj
            messageTxt
        )

app = webapp2.WSGIApplication([
    ('/crons/set_announcement', SetAnnouncementHandler),
    ('/tasks/sendemail/createconference', SendConfirmationEmailHandler),
    ('/tasks/sendemail/createsession', SendSessionEmailHandler),
    ('/tasks/sendemail/speakersessioncreated', SendSpeakerEmailHandler)
], debug=True)
