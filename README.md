## Introduction
Sams Conference App is conference organization application that exists on the web. There are two parts of the appliation 

1. The ConferenceApi
1. The Web Application

Multiple enhancements have been made to the provided base web application and the api to accomodate the new features and functionality 

---

## Table of Contents

1. [Introduction ](#introduction)
    - [Program Features](#program-features)
1. [Setup ](#setup)
    - [Prerequisites ](#prerequisites)
    - [Local Application Setup ](#local-appliction-setup)   
    - [Application Details](#application-etails)   
1. [Assumptions](#assumptions)
1. [Extra Credit Features](#extra-credit-features)
1. [Explanations](#explanations)
	- [Speaker Implementation](#speaker-implementation)
	- [Additional Queries](#additional-queries)
	- [Query Problem](#query-problem)
1. [Code Documentation ](#code-documentation)
    - [Folder Structure ](#folder-structure)
    - [ConferenceApi](#conferenceapi)
1. [Database Structure ](#database-structure)

---

###Program Features.
	
* **Responsive Web Interface:** The web interface for the application is responsive and supports multiple screen sizes.

![alt text][homepage]

---

* **Information Carousel:**The home page has a carousel that displays useful  announcements.

![alt text][announce]

---

* **Information Carousel:** The home page has a carousel that displays sessions starting sooon.

![alt text][startson]

![alt text][strson2]

---

* **Information Carousel:** The home page has a carousel that displays featured speaker.


![alt text][fspkr1]

![alt text][fspkr2]

---

* **Register Speaker:** New Screen to register speaker

![alt text][regspkr]

---

* **Create Sessions:** New Screen to create sessions


![alt text][crtsession]

---

* **View Sessions:** New Screen to view sessions


![alt text][sessions]

---


* **View Speakers:** New Screen to view speakers


![alt text][spkr]

---


* **View Speaker Sessions:** New Screen to view speaker Sessions


![alt text][spkrses]

---



* **View Users Wishlist:** New Screen to view users wishlist


![alt text][wishlist]

---


* **Other Screen Changes:**  Other screens have been modified to accomodate the new functionality
A new notification system has been added for floating error messages.

* **Email Confirmations :** Email confirmations have been added when session , speaker, conference is created/ modified

* **Task Queues :** Featured Speaker functionalityhas been implemented using the task queues


## Setup
###Prerequisites 
Following are some of the prerequsits for the development environment

1. Google Account
1. Google App Engine SDK for python
1. Python 2.7+ 

###Local Application Setup

1. Update the value of `application` in `app.yaml` to the app ID you
   have registered in the App Engine admin console and would like to use to host
   your instance.  I have already updated this with my application id
1. Update the values at the top of `settings.py` to
   reflect the respective client IDs you have registered in the
   [Developer Console][4]. The `settins.py` has been updated with my id
1. Update the value of CLIENT_ID in `static/js/app.js` to the Web client ID
1. Run the app with the devserver using `dev_appserver.py DIR`, and ensure it's running by visiting
   your local server's address (by default [localhost:8080][5].). or the port that you configured your app to run on.

###Application Details

1. Application Name 
	`sams-conference-app`
1. WEB_CLIENT_ID 
	`453719718803-kpltcg8jlmo351vs7vmrch8gm2caf5g2.apps.googleusercontent.com`
1. URL [Sams Conference App][APPURL]  




**[Back to top](#table-of-contents)**

---

## Assumptions

1. The start date and end date validation take in to account time till 23:59
1. Only the organizers can update edit and create sessions for the conference.
1. The front end application is updated but does not use all the endpoints created through the project
1. One session can have only one session.
1. Necessary modifications can be made to the provided UI
1. UI updates are optional and not all features need to be implemented in the UI
1. Test cases need not be prepared for the Web and API.

**[Back to top](#table-of-contents)**

---

## Extra Credit Features

1. **Separate Entity for Speakers:** A separate entity has been created for the speakers
1. **Design Choice :** Design Choice included in the readme.
1. **UI Changes:** All the new features added to the api have also been added to the UI of the application.
1. **Email Confirmations:** Various confirmation mails have been added to the  application.
1. **Explaination for the Problem:** Readme includes the explanation for the problem.

**[Back to top](#table-of-contents)**

---

## Explanations

### Speaker Implementation

* **Task 1 Design Choices**

The diagram below shows the different entities and their symbolic relationship.

![alt text][dbdesign]


**Speakers**
Following are some of the reason why I created a separate Speaker entity

 * A separate entity for Speakers for capturing a more information about them.
 * Separate entity allows to show user the differnt speakers at the time of session creation.
 * Asumed that a session can have only one speaker.
 * Separate entity allows me to search the session using the speaker keys.
 * Any registered user can be registered as a speaker.
 * Keeping only the speaker specific detail in this entity other information is picked from the user profile.
 * This also helps me to send the speaker data only what is required. 
 * This approach allowed me to add a whole new section in the UI for showing / filtering session by speaker
 * There is no cleanup code for this phase of the project. meaning there is no code to cleanup the old conferences and sessions whose end date has been reached.
 * When a conference is updated the start date has to be changed to min current date.


**How Speakers Are Linked Sessions**
 * When a new session is created one of the Speaker key is sent as part of the request. 
 * The speaker key is saved in the speaker field of the entity. The indexes have been updated to allow easy query of the data.
 * The session is a child of the Conference. 
 * This makes it easy to search sesssions for a conference.

### Additional Queries

* **Task 3 Additional Queries**

* **Query 1 Sessions Starting Soon**
 A new query has been added to fetch 5 of the sessions starting at a configurable interval. The query is implemented in the API and appliction. This will allow the users to know what sessions are starting say in next 30 minutes. This query allows the user to select the sessions for date and time.
 	* To make this work I have added the start_time to the start_date befoe storing the information in the datastore


 * **API implimentaion**  a new method 'getSessionsStartingSoon' has been added to to the api where the user can pass in the start date and the time interval. The system fetches the sessions if any within the specified time interval.

 * **MEMCACHE implimentaion**  a new cron task has been added to fire the similar query to fetch sessions if any within the specified time interval that are about start soon and add them to the memcache using the method `_cacheStartingSoon`. The web application has been updated to get this information out of memcache using the `getSessionsStartingSoonCached` method and show the same in the Crrousel on the home page.

* **Query 3 Sessions Within Date Range**
 A new query has been added to fetch all the sesssion in decending order of date and time within a specified start-date and end-date. The query is implemented in the API and appliction. 
 * The UI uses this query and allows the user to easly filter the sessions for today , this week, this month, and this year.

 `getAllFutureSessions` method is flexible enough that it will work only if start date is provided. In this case it will fetch the sessions form the passed start-date

* **Query 2 Sessions by speaker name**
 A new query has been added to the API to find the sessions for a speaker by speaker name. This will be really useful to searh the session if the user only knows the speaker name. The is not emplement in the ewb application yet.

 `getSessionsBySpeaker()`  method works both for speaker keys and speaker name


### Query Problem

* **Task 3 Query Problem**

**Problem:** Let’s say that you don't like workshops and you don't like sessions after 7 pm. How would you handle a query for all non-workshop sessions before 7 pm? What is the problem for implementing this query? What ways to solve it did you think of?

**Reason of the Problem**
Acording to the ndb [doccumentation][7] the datastore enforces some restrictions on queries

"Limitations: The Datastore enforces some restrictions on queries. Violating these will cause it to raise exceptions. For example, **combining too many filters, using inequalities for multiple properties, or combining an inequality with a sort order on a different property are all currently disallowed. Also filters referencing multiple properties sometimes require secondary indexes to be configured.** "

**Proposed and Implemented Soultion:** After going through multiple documents and web forums I implemented the following solution.
	1. Query the sessions before the specified time 7PM(19:00) in this case and store it a variable timeQry. remember to fetch only the keys.

	1. Query the sessions which are not of the specified type  "WORKSHOP" in this case and store it a variable typeQry. remember to fetch only the keys.

	1. Create a set by intersection the queries `set(timeQry).intersection(typeQry)` 
	1. use `ndb.get_multi(set(timeQry).intersection(typeQry))` fetch all the intersected sessions
	
The API method `getAllSessionsBeforeTime' allows the user to pass in any datetime and type of session to apply the above logicand return relevant sessions.


I choose this approach because

* This required minimum change in the application.
* Since this is a class project I do not foresee a large increase in the data

**Disadvantages of this approach**  

* As the amount of data increases this approach might not be a good solution as we will be working on large data sets
* The performance of the app might go down in case there is a large increase in the data.



##Code Documentation

###Folder Structure

Application Folder Structure

![alt text][fstr]


**[Back to top](#table-of-contents)**
---
###ConferenceAPI

`confernece.py` contains the required endpoint menthods, static methods.

### _copyProfileToForm(self, prof):
Copy relevant fields from Profile to ProfileForm.
* Arguments:

	* prof - the profile that needs to be copied
* Returns: 

	* ProfileForm  

---

### _getProfileFromUser(self):
Return user Profile from datastore, creating new one if non-existent.
* Arguments:

	* prof - the profile that needs to be copied
* Returns: 
	* profile object

---

### _doProfile(self, save_request=None):
Get user Profile and return to user, possibly updating it first.
* Arguments:

	* save_request - ProfileMiniForm that need so be saved
* Returns: 
	*	ProfileForm

---

### _createSessionMailContent(self, session, conf):

Formats and creates a mail content for session creator and speaker
* Arguments:

	* session  - the session that needs to be copied
	* conf  - the conference object
* Returns: 
	* Formatted text messsage

---

### _copyConferenceToForm(self, conf, displayName):
Copy relevant fields from Conference to ConferenceForm.
* Arguments:

	* conf - the conferenece object that needs to be copied to the form
	* dispName - the organizer display name
* Returns: 
    * ConferenceForm

---

### _copyConfSessionToForm(self, confsession):
Copy relevant fields from Conference to ConferenceForm.
* Arguments:

	* confsession - the conferenece session object that needs to be copied to the form
* Returns: 
    * ConfSessionForm

---    

### _createConferenceObject(self, request):
Create or update Conference object, returning ConferenceForm/request.
* Arguments:
	* request - ConferenceForm The confereence form 
* Returns: 
    * ConferenceForm

---

### _updateConferenceObject(self, request):
Updates the conference details based on the key and other information.
* Arguments:

	* request - ConferenceForm  the conferenece form 

* Returns: 
    * ConferenceForm 

---

### _getQuery(self, request):
Return formatted query from the submitted filters.
* Arguments:

	* request -  the filters form  containig the different filters
* Returns: 
    * Query 
      
---

### _formatFilters(self, filters):
Parse, check validity and format user supplied filters.
* Arguments:

	* filters - the filters to be applied 
* Returns: 
    * formatted filters

---


### _conferenceRegistration(self, request, reg=True):
Register or unregister user for selected conference. This is a transactional method
* Arguments:

	* request - containing the  websafe conference key
	* reg - boolean to register or unregister
* Returns: 
    * boolean true or false depending on success or error

---

### _manageSessionWishList(self, request, reg=True):
Add or remove sessions form users wishlist.
* Arguments:

	* request - containing the  websafe session key
	* reg - boolean to add or remove the session to the wishlist
* Returns: 
    * boolean true or false depending on success or error

---

### _createConfSession(self, request):
Create or update Conference Session object, returning ConfSessionForm/request.
* Arguments:

	* request - ConSessionForm containing the information about the sesssion
* Returns: 
    * ConfSessionForm containing the new information

---
    
### _createSpeaker(self, request):
Create or update speaker object, returning SpeakerForm/request.
* Arguments:

	* request - SpeakerForm  containing the speaker information
* Returns: 
    * SpeakerForm - returns the request 

---

### _copySpeakerToForm(self, speakerProfile):
Copy relevant fields from Speaker to SpeakerForm.
* Arguments:

	* speakerProfile - Speaker object containing the speaker information
* Returns: 
    * SpeakerForm 

---

### _copyFeaturedSpeakerToForm(self, featuredSpeaker):
Copy relevant fields from featuerSpeaker to FeaturedSpeakerForm.
* Arguments:

	* featuredSpeaker - FeaturedSpeaker object containing the speaker information
* Returns: 
    * FeaturedSpeakerForm 

---

### _verifySpeaker(self, request, suppressEx=False):
Verifys if the speaker is registered SpeakerForm/request.
* Arguments:

	* request  - 
	* suppressEx - flag to show / hide the warinings
* Returns: 
    * SpeakerForm

---

### _getSpeakerSessionsByKey(self, request):
Returns sessions by speaker key
* Arguments:

	* request - FindSpeakerForm - the search parameters
* Returns: 
    * List of ConfSession 

---

### _getSessionsByType(self, request):
Returns sessions by session type in a conference type
* Arguments:

	* request - FindSpeakerForm - the search parameters
* Returns: 
    * List of ConfSession         # raise an error if session type is not passed

---

### _getSpeakerSessionsByName(self, request):
 Returns sessions by speaker displayname
 * Arguments:
	* request - FindSpeakerForm - the search parameters
* Returns: 
    * List of ConfSession         # raise an error if session type is not passed

---

### _getAllFutureSessions(self, request):
 Returns all future sessions 

 * Arguments:
	* request - ConfSessionSearchForm - the search parameters
* Returns: 
    * List of ConfSession   

---

### _getStartingSoonSessions(self, request):
 Return all session that are starting soon request will have the delta to select the upper limit

 * Arguments:
	* request - ConfSessionSearchForm - the search parameters
* Returns: 
    * List of ConfSession   

---

### _cacheAnnouncement():
Create Announcement & assign to memcache; used by memcache cron job. This is a static method

---

### _cacheStartingSoon():
Finds and sets the sessions startign soon in the memcache; used by memcache cron job .
 This is a static method

---

### _cacheFeaturedSpeaker(request):
Create Announcement & assign to memcache; used by
* Arguments:

	* request - the conference and speaker information 
	* dispName - the organizer display name

* Returns: 
    * featuredSpeaker

## ENDPOINTS


### registerSpeaker(self, request):
Handles request to Register a Speaker.

	* REQUEST - SpeakerForm - speaker information 
	* RESPONSE - SpeakerForm - with the updated information
	* PATH - 'registerSpeaker'
    * METHOD_TYPE - POST

 ---

### speakerExists(self, request):
Register a Speaker. Verify if the user is already registered as speaker

	* REQUEST - VoidMessage
	* RESPONSE - SpeakerForm - with the updated information
	* PATH - 'speakerExists'
    * METHOD_TYPE - POST

---
        
### getAnnouncement(self, request):
Return Announcement from memcache.

	* REQUEST - VoidMessage 
	* RESPONSE - String containg the announcement
	* PATH - 'conference/announcement/get'
    * METHOD_TYPE - GET

 ---

### getSessionsStartingSoonCached(self, request):
Return Announcement from memcache.

	* REQUEST - VoidMessage 
	* RESPONSE - SpeakerForm - with the updated information
	* PATH - 'sessions/starting-soon/cached'
    * METHOD_TYPE - GET

---

### getFeaturedSpeakerCached(self, request):
Return featured speakers from memcache.

	* REQUEST - VoidMessage 
	* RESPONSE - FeaturedSpeakerForm - information about the featured speaker
	* PATH - 'speaker/featured-speaker/cached'
    * METHOD_TYPE - GET

---

### getProfile(self, request):
Return user profile.

	* REQUEST - VoidMessage
	* RESPONSE - ProfileForm - with the information about the profile
	* PATH - 'profile'
    * METHOD_TYPE - GET

---    

### saveProfile(self, request):
Update & return user profile.

	* REQUEST - ProfileMiniForm - speaker information 
	* RESPONSE - ProfileForm - with the information about the profile
	* PATH - 'profile'
    * METHOD_TYPE - POST

---


### createConference(self, request):
Create new conference.

	* REQUEST - ConferenceForm - Conference  information for creating a conference
	* RESPONSE - ConferenceForm - with the information about the conference
	* PATH - 'conference'
    * METHOD_TYPE - POST

---

### updateConference(self, request):
Update conference w/provided fields & return w/updated info.

    * REQUEST - CONF_POST_REQUEST - ConferenceForm and  websafeConferenceKeyonference for updating a conference
	* RESPONSE - ConferenceForm - with the information about the conference
	* PATH - 'conference/edit/{websafeConferenceKey}'
    * METHOD_TYPE - PUT

---

### getConference(self, request):
Return requested conference (by websafeConferenceKey).

    * REQUEST - CONF_GET_REQUEST -  VoidMessage and websafeConferenceKey for getting  conference
	* RESPONSE - ConferenceForm - with the information about the conference
	* PATH - 'conference/{websafeConferenceKey}'
    * METHOD_TYPE - GET

---

### getConferencesCreated(self, request):
Return conferences created by user.

    * REQUEST -  VoidMessage 
	* RESPONSE - ConferenceForms - list of conferences
	* PATH - 'getConferencesCreated'
    * METHOD_TYPE - POST

---

### queryConferences(self, request):
Query for conferences.

    * REQUEST -  ConferenceQueryForms - search parameters to find conference 
	* RESPONSE - ConferenceForms - Lit of conferences
	* PATH - 'queryConferences'
    * METHOD_TYPE - POST

---

### getAllSessionsBeforeTime(self, request):
Returns all the sessions before the 'start_time' and are not of type 'session_type' 

    * REQUEST -  ConfSessionTask3SearchForm - search parameters to find conference as required by Task 3 of the project
	* RESPONSE - ConferenceForms - list of conferences 
	* PATH - 'sessions/beforetime'
    * METHOD_TYPE - GET

---

### registerForConference(self, request):
Register user for selected conference.

    * REQUEST - CONF_GET_REQUEST -  VoidMessage and websafeConferenceKey for getting  conference
	* RESPONSE - BooleanMessage with flag if the operation was successful or not
	* PATH - 'conference/register/{websafeConferenceKey}'
    * METHOD_TYPE - POST

---

### unregisterFromConference(self, request):
Register user for selected conference.

    * REQUEST - CONF_GET_REQUEST -  VoidMessage and websafeConferenceKey for getting  conference
	* RESPONSE - BooleanMessage with flag if the operation was successful or not
	* PATH - 'conference/unregister/{websafeConferenceKey}'
    * METHOD_TYPE - POST

---

### getConferencesToAttend(self, request):

Get list of conferences that user has registered for.
    * REQUEST -  VoidMessage 
	* RESPONSE - ConferenceForms - list of conferences 
	* PATH - 'conferences/attending'
    * METHOD_TYPE - GET

---


### createSession(self, request):
Creates a new conference session.

    * REQUEST -  CONFSESSION_POST_REQUEST - ConfSessionForm and websafeConferenceKey for creating / updating a session
	* RESPONSE - ConfSessionForm - Conference session details.
	* PATH - 'confSession/create/{websafeConferenceKey}'
    * METHOD_TYPE - POST


---

### getConferenceSessions(self, request):
Return sessions for a conference.

    * REQUEST -  CONFSESSION_GET_REQUEST - VoidMessage and websafeConferenceKey for getting sessions
	* RESPONSE - ConfSessionForms - list of Conference session details.
	* PATH - 'conference/sessions/{websafeConferenceKey}'
    * METHOD_TYPE - POST

--- 

   
### getAllSpeakers(self, request):
Return All speakers . 
    * REQUEST -  VoidMessage
	* RESPONSE - SpeakerForms - list of speakers.
	* PATH - 'speaker/all'
    * METHOD_TYPE - GET

---

### getSessionsBySpeaker(self, request):
Return sessions by a speaker.

    * REQUEST -  FindSpeakerForm  search parameters for the speakers session.
	* RESPONSE - ConfSessionForms - list of ConferenceSessions by the speaker.
	* PATH - 'speaker/sessions'
    * METHOD_TYPE - GET
---


### getConferenceSessionsByType(self, request):
Return sessions by a speaker.

    * REQUEST -  CONFSESSIONTYPES_GET_REQUEST  VoidMessage, websafeConferenceKey,sessionType to search for speakers session.
	* RESPONSE - ConfSessionForms - list of ConferenceSessions by the speaker.
	* PATH - 'conference/sessions/{websafeConferenceKey}/{sessionType}'
    * METHOD_TYPE - GET

---
   
### addSessionToWishlist(self, request):
Add a sessions to users wishlist.

    * REQUEST -  WISHLIST_SESSION_POST_REQUEST  VoidMessage, websafeKey to add session to the wishlist
	* RESPONSE - BooleanMessage - true / false if theoperation sis successful.
	* PATH - 'session/addtowishlist/{websafeKey}'
    * METHOD_TYPE - POST

---

### deleteSessionInWishlist(self, request):
Removes a sessions from users wishlist.

    * REQUEST -  WISHLIST_SESSION_POST_REQUEST  VoidMessage, websafeKey to add session to the wishlist
	* RESPONSE - BooleanMessage - true / false if theoperation sis successful.
	* PATH - 'session/deletefromwishlist/{websafeKey}'
    * METHOD_TYPE - POST

---

### getSessionsInWishlist(self, request):
Retrives all sessions from users wishlist.

    * REQUEST -  VoidMessage
	* RESPONSE - ConfSessionForms - list of ConferenceSessions by the speaker.
	* PATH - 'sessionwishList'
    * METHOD_TYPE - GET

---

### getAllFutureSessions(self, request):
Retrives session based on a date.

    * REQUEST -  ConfSessionSearchForm session search parameters
	* RESPONSE - ConfSessionForms - list of ConferenceSessions by the speaker.
	* PATH - 'sessions/future'
    * METHOD_TYPE - GET

---

### getSessionsStartingSoon(self, request):
Gets all the sessions starting within a specified time delta.

    * REQUEST -  ConfSessionSearchForm session search parameters
	* RESPONSE - ConfSessionForms - list of ConferenceSessions by the speaker.
	* PATH - 'sessions/starting-soon/current'
    * METHOD_TYPE - GET



[Back to top](#table-of-contents)
---





##Database Structure

## Entities
The diagram below shows the different entities and their symbolic relationship.


![alt text][dbdesign]

### Speaker
The entity stores the speaker information.

    * speakerUserId - user id of the speaker
    * topics - topics the speaker is interested in. Can have multiple topics. 
    * aboutSpeaker - brief summary about the speaker

**[Back to top](#table-of-contents)**
---

## ConfSession
The Entity for storing the conference sessions

    * session_name - name of the session
    * highlights - session highlights 
    * speaker - speaker key to connect it with the speakers
    * duration - duration of the session
    * type_of_session - type of session can be one of the following 
    		* GENERAL 
    		* WORKSHOP 
    		* LECTURE 
    		* THINKTANK 
    		* SKILLBUILDER 
    		* EXPERTSPEAK
    		* KEYNOTE 

    * date - session date. when saved it is saved with start time 
    * start_time - start time of the session
    * venue - venue for the session

**[Back to top](#table-of-contents)**
---

## Conference
The entity to store the Conference 

    * name - Name of the conference 
    * description - description or details of the conference
    * organizerUserId - organizer id of the conference. This is the profile mainemail
    * topics - topics of the conference
    * city - city where the conference is held
    * startDate - start date of the conference
    * month - the month when the conference is held
    * endDate - the end date of the conference
    * maxAttendees - maximum number of people that can attend the conference
    * seatsAvailable - current seats available at the conference

**[Back to top](#table-of-contents)**
---    

## Profile
The entity to store the Profile information

	* displayName - the display name for the profile
	* mainEmail - main email address ussed for communication
	* teeShirtSize - Tshirt size for the user
	* conferenceKeysToAttend - the conferences that the user has registered to attend
	* sessionWishList - the sessions that the user wants to attend

**[Back to top](#table-of-contents)**
---   


[APPURL]: https://sams-conference-app.appspot.com "Sams Conference App"
[homepage]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/homepage.jpg "Home Page"
[announce]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/announcement.jpg "Announcements"
[fspkr1]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/featuredspeaker.jpg "Features Speaker"
[fspkr2]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/featuredspeaker2.jpg "Features Speaker"
[regspkr]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/registerspeaker.jpg "Register Speaker"
[crtsession]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/sessioncreate.jpg "Create Session"
[sessions]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/sessions.jpg "Sessions"
[spkr]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/speakers.jpg "Speakers"
[spkrses]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/speakerssession.jpg "Speaker Sessions"
[startson]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/startingsoon.jpg "Starting Soon"
[strson2]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/startingsoon2.jpg "Startig soon data"
[wishlist]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/wishlist.jpg "Register Speaker"
[fstr]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/folderstructure.jpg "Folder Structure"
[dbdesign]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/databasediag.jpg "Database Design"
[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
[6]: https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool
[7]: https://cloud.google.com/appengine/docs/python/ndb/queries






