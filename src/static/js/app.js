'use strict';
/**
 * @ngdoc object
 * @name conferenceApp
 * @requires $routeProvider
 * @requires conferenceControllers
 * @requires ui.bootstrap
 *
 * @description
 * Root app, which routes and specifies the partial html and controller depending on the url requested.
 *
 */
var app = angular.module('conferenceApp', ['ngAnimate', 'toastr', 'conferenceControllers', 'conferenceDirectives', 'ngRoute', 'ui.bootstrap']).
config(['$routeProvider', 'toastrConfig',
    function($routeProvider, toastrConfig) {
        $routeProvider.
        when('/conference', {
            templateUrl: '/partials/show_conferences.html',
            controller: 'ShowConferenceCtrl'
        }).
        when('/conference/create', {
            templateUrl: '/partials/create_conferences.html',
            controller: 'CreateConferenceCtrl',
            controllerAs: 'vm'
        }).
        when('/conference/edit/:web_safe_key', {
            templateUrl: '/partials/create_conferences.html',
            controller: 'EditConferenceCtrl',
            controllerAs: 'vm'
        }).
        when('/conference/detail/:webSafeConfKey', {
            templateUrl: '/partials/conference_detail.html',
            controller: 'ConferenceDetailCtrl'
        }).
        when('/profile', {
            templateUrl: '/partials/profile.html',
            controller: 'MyProfileCtrl'
        }).
        when('/profile/session-wishlist', {
            templateUrl: '/partials/view_sessions.html',
            controller: 'session_wish_listCtrl',
            controllerAs: "vm"
        }).
        when('/speaker/register', {
            templateUrl: '/partials/register_speaker.html',
            controller: 'RegisterSpeakerCtrl',
            controllerAs: 'vm'
        }).
        when('/speaker/view', {
            templateUrl: '/partials/view_speakers.html',
            controller: 'ViewSpeakerCtrl',
            controllerAs: 'vm'
        }).
        when('/speaker/sessions/:web_safe_key', {
            templateUrl: '/partials/speaker_sessions.html',
            controller: 'ViewSpeakerSessionsCtrl',
            controllerAs: 'vm'
        }).
        when('/speaker/:speaker_name/:web_safe_key', {
            templateUrl: '/partials/view_sessions.html',
            controller: 'ViewSpeakerSessionsCtrl',
            controllerAs: 'vm'
        }).
        when('/sessions', {
            templateUrl: '/partials/view_all_sessions.html',
            controller: 'ViewAllSessionsCtrl',
            controllerAs: 'vm'
        }).
        when('/conference/createsession/:webSafeConfKey', {
            templateUrl: '/partials/create_session.html',
            controller: 'CreateSessionsCtrl',
            controllerAs: 'vm'
        }).
        when('/home', {
            templateUrl: '/partials/home.html'
        }).
        otherwise({
            redirectTo: '/home'
        });
        angular.extend(toastrConfig, {
            autoDismiss: true,
            timeOut: 1500,
            containerId: 'toast-container',
            maxOpened: 2,
            newestOnTop: true,
            progressBar: true,
            closeButton: true,
            positionClass: 'toast-top-full-width',
            target: 'body',
            toastClas: 'toast-position'
        });
    }
]);
/**
 * @ngdoc filter
 * @name startFrom
 *
 * @description
 * A filter that extracts an array from the specific index.
 *
 */
app.filter('startFrom', function() {
    /**
     * Extracts an array from the specific index.
     *
     * @param {Array} data
     * @param {Integer} start
     * @returns {Array|*}
     */
    var filter = function(data, start) {
        return data.slice(start);
    }
    return filter;
});
/**
 * @ngdoc constant
 * @name HTTP_ERRORS
 *
 * @description
 * Holds the constants that represent HTTP error codes.
 *
 */
app.constant('HTTP_ERRORS', {
    'UNAUTHORIZED': 401
});
/**
 * @ngdoc service
 * @name oauth2Provider
 *
 * @description
 * Service that holds the OAuth2 information shared across all the pages.
 *
 */
app.factory('oauth2Provider', function($uibModal) {
    var oauth2Provider = {
            CLIENT_ID: '453719718803-kpltcg8jlmo351vs7vmrch8gm2caf5g2.apps.googleusercontent.com',
            SCOPES: 'email profile',
            signedIn: false
        }
        /**
         * Calls the OAuth2 authentication method.
         */
    oauth2Provider.signIn = function(callback) {
        gapi.auth.signIn({
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'accesstype': 'online',
            'approveprompt': 'auto',
            'scope': oauth2Provider.SCOPES,
            'callback': callback
        });
    };
    /**
     * Logs out the user.
     */
    oauth2Provider.signOut = function() {
        gapi.auth.signOut();
        // Explicitly set the invalid access token in order to make the API calls fail.
        gapi.auth.setToken({
            access_token: ''
        })
        oauth2Provider.signedIn = false;
    };
    /**
     * Shows the modal with Google+ sign in button.
     *
     * @returns {*|Window}
     */
    oauth2Provider.showLoginModal = function() {
        var modalInstance = $uibModal.open({
            templateUrl: '/partials/login.modal.html',
            controller: 'OAuth2LoginModalCtrl'
        });
        return modalInstance;
    };
    return oauth2Provider;
});