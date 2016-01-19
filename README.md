## Introduction
Sams Conference App is conference organization application that exists on the web. There are two parts of the appliation 
1. The ConferenceApi
1. The Web Application
multiple enhancements have been made to the provided base application to accomodate the new features and functionality 

---

## Table of Contents

1. [Introduction ](#introduction)
    - [Program Features](#program-features)
1. [Setup ](#setup)
    - [Prerequisites ](#prerequisites)
    - [Local Application Setup ](#local-appliction-setup)   
    - [Application Details](#application-Details)   
1. [Assumptions](#assumptions)
1. [Extra Credit Features](#extra-credit-features)
1. [Code Documentation ](#code-documentation)
    - [Folder Structure ](#folder-structure)
    - [ConferenceApi](#conferenceapi)
1. [Database Structure ](#database-structure)

---

###Program Features.
	
* ** Responsive Web Interface: ** The web interface for the application is responsive and supports multiple screen sizes.

![alt text][hpage]

* ** Administration Module: ** Application supports an administration module. If your are logged in as an Administrator you can add new categories and modify items posted by any user. Admin user can enable and disable users, categories and items. 

![alt text][admmnu]

---

![alt text][loginli]

---

![alt text][adminLogin]

---

   ** Default Login Information for Administrator **

| User Name | admin@itemcatalog.com |
|:---------:|:---------------------:|
|  Password |         123456        | 

* **Sub-Categories: ** Application supports one level of sub categories Like the category Electronics and Computers  can have sub categories Headphones, Video Games , Laptops and Tablets.

![alt text][catli]

---

* **Pagination: ** Pagination of results for easy readability on most of the pages.

![alt text][itmli]

---

* **Moderation: ** Administrator can enable and disable users, categories and items. The disabled items and categories will not show up in the catalog but will still be available in the users 

![alt text][editu]

---

![alt text][edititm]

---

![alt text][catli]

---

* **Third Party Login :** The application allows you to use you google account to login.

![alt text][loginli]

---

* **CRUD :** The application allows a logged in user to perform CRUD operations on their items. An administrator can update all items.

![alt text][editu]

---

![alt text][delfonf]

---

* **Item Images :** The application allows a logged in user to specify a picture / image url for there items these images are used in the listings.

![alt text][itmviewnoli]

---

![alt text][itmvli]

* **Latest Items :** The application displays latest items in a carousel on the home page. The number of Items and the cut of date can be changed in code. The default values are 7 days and 9 Items.

![alt text][hpage]

---

* **XML Catalog :** The application has an option to get the entire catalog as an XML. You can use the following URL ** http://localhost:8000/catalog.xml ** or using the Administration menu This is assuming the server is running on port 8000 


* **JSON Catalog :** The application has an option to get the entire catalog as an XML. You can use the following URL ** http://localhost:8000/catalog.json ** or using the Administration menu This is assuming the server is running on port 8000 

* **ATOM Feed :** The application has an option to get an ATOM RSS feed for the latest items from the catalog as an XML. You can use the following URL ** http://localhost:8000/newitems.atom ** or using the Administration menu This is assuming the server is running on port 8000 

![alt text][admmnu]

* **Readable URLs : ** most of the relevant urls are readable.


---


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


the bootstrap updated
changes in the UI
added sessions 
added speakers 
view sessions by speakers
shows who is logged in 


**[Back to top](#table-of-contents)**

---

## Extra Credit Features

1. ** Sub-Categories: ** Application supports one level of sub categories Like the category Electronics and Computers  can have sub categories Headphones, Video Games , Laptops and Tablets.
1. ** Pagination: ** Pagination of results for easy readability on most of the pages.
1. ** Moderation: ** Administrator can enable and disable users, categories and items. The disabled items and categories will not show up in the catalog but will still be available in the users 
1. ** Item Images :** The application allows a logged in user to specify a picture / image url for there items these images are used in the listings.
1. ** Latest Items :** The application displays latest items in a carousel on the home page. The number of Items and the cut of date can be changed in code. The default values are 7 days and 9 Items.
1. ** XML Catalog :** The application has an option to get the entire catalog as an XML. You can use the following URL ** http://localhost:8000/catalog.xml ** this is assuming the server is running on port 8000
1. ** JSON Catalog :** The application has an option to get the entire catalog as an JSON. You can use the following URL ** http://localhost:8000/catalog.json ** this is assuming the server is running on port 8000
1. ** ATOM Feed :** The application has an option to get an ATOM RSS feed for the latest items from the catalog as an XML. You can use the following URL ** http://localhost:8000/newitems.atom ** this is assuming the server is running on port 8000
**[Back to top](#table-of-contents)**

---
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
[editus]: https://github.com/v2saumb/catalog/blob/master/docs/images/userlist.gif "Edit users"
[loginli]: https://github.com/v2saumb/catalog/blob/master/docs/images/login-options.gif "Login Options"
[itmvli]: https://github.com/v2saumb/catalog/blob/master/docs/images/viewitems-loggedin.gif "Logged in Items View"
[itmviewnoli]: https://github.com/v2saumb/catalog/blob/master/docs/images/itemview.gif "Items view"
[itmnoli]: https://github.com/v2saumb/catalog/blob/master/docs/images/items-nologin.gif "Items No Login"
[itmli]: https://github.com/v2saumb/catalog/blob/master/docs/images/items-loggedin.gif "Items Logged in"
[edititm]: https://github.com/v2saumb/catalog/blob/master/docs/images/item-edit.gif "Edit Items"
[editu]: https://github.com/v2saumb/catalog/blob/master/docs/images/edit-user.gif "Edit User"
[delfonf]: https://github.com/v2saumb/catalog/blob/master/docs/images/delete-conf.gif "Delete Confirmation"
[catnoli]: https://github.com/v2saumb/catalog/blob/master/docs/images/cats-nologin.gif "Catagory Screen Without Login"
[catli]: https://github.com/v2saumb/catalog/blob/master/docs/images/cat-loggedin.gif "Category Screen Logged In"
[catitm]: https://github.com/v2saumb/catalog/blob/master/docs/images/cat-items.gif "Category Items Screen"
[admmnu]: https://github.com/v2saumb/catalog/blob/master/docs/images/admin-menu.gif "Admin Menu"
[hpage]: https://github.com/v2saumb/catalog/blob/master/docs/images/homepage.gif "Home Page"
[fstr]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/folderstructure.jpg "Folder Structure"
[adminLogin]: https://github.com/v2saumb/catalog/blob/master/docs/images/admin-login.gif "Admin Login Screen"
[dbdesign]: https://github.com/v2saumb/conferencecentral/blob/feature/speakers/docs/imgs/databasediag.jpg "Database Design"
[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
[6]: https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool

## Products
- [App Engine][1]

## Language
- [Python][2]

## APIs
- [Google Cloud Endpoints][3]







I Created a separate entity for Speakers for capturing a more information.
Any Logged in user can register as a speaker.
Sessions can be created under a conference and must have  a speaker
There are methods in in the app to filter the sessions based on type speaker conference etc.
The UI has also been updated to accommodate the new methods and sessions and conferences


assumptions
the end date is 23:59
the bootstrap updated
changes in the UI
added sessions 
added speakers 
view sessions by speakers
shows who is logged in 
