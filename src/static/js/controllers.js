'use strict';
/**
 * The root conferenceApp module.
 *
 * @type {conferenceApp|*|{}}
 */
var conferenceApp = conferenceApp || {};
/**
 * @ngdoc module
 * @name conferenceControllers
 *
 * @description
 * Angular module for controllers.
 *
 */
conferenceApp.controllers = angular.module('conferenceControllers', ['ui.bootstrap']);
/*Adding required Controllers*/
conferenceApp.controllers.controller('ConferenceDetailCtrl', conferenceDetailCtrl);
conferenceDetailCtrl.$inject = ['$scope', '$log', '$routeParams', 'HTTP_ERRORS', 'toastr'];

conferenceApp.controllers.controller('ViewSpeakerSessionsCtrl', viewSpeakerSessionsCtrl);
viewSpeakerSessionsCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$routeParams', 'toastr'];

conferenceApp.controllers.controller('session_wish_listCtrl', session_wish_listCtrl);
session_wish_listCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$routeParams', 'toastr'];

conferenceApp.controllers.controller('ViewAllSessionsCtrl', viewAllSessionsCtrl);
viewAllSessionsCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$routeParams', 'toastr', '$filter'];



conferenceApp.controllers.controller('CarouselContentsCtrl', carouselContentsCtrl);
carouselContentsCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', 'toastr', '$interval'];


conferenceApp.controllers.controller('CreateConferenceCtrl', createConferenceCtrl);
createConferenceCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', 'toastr'];

conferenceApp.controllers.controller('EditConferenceCtrl', editConferenceCtrl);
editConferenceCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', 'toastr', '$routeParams'];

conferenceApp.controllers.controller('MyProfileCtrl', myProfileCtrl)
myProfileCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', 'toastr'];

conferenceApp.controllers.controller('RegisterSpeakerCtrl', registerSpeakerCtrl);
registerSpeakerCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$timeout', 'toastr'];

conferenceApp.controllers.controller('CreateSessionsCtrl', createSessionsCtrl);
createSessionsCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$routeParams', 'toastr', '$filter'];

conferenceApp.controllers.controller('ViewSpeakerCtrl', ViewSpeakerCtrl);
ViewSpeakerCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$routeParams', 'toastr'];

conferenceApp.controllers.controller('ShowConferenceCtrl', showConferenceCtrl);
showConferenceCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', 'toastr'];

conferenceApp.controllers.controller('RootCtrl', rootCtrl);
rootCtrl.$inject = ['$scope', '$location', 'oauth2Provider', 'toastr'];

conferenceApp.controllers.controller('OAuth2LoginModalCtrl', oAuth2LoginModalCtrl);
oAuth2LoginModalCtrl.$inject = ['$scope', '$uibModalInstance', '$rootScope', 'oauth2Provider', 'toastr'];

conferenceApp.controllers.controller('DatepickerCtrl', datePkrCtrl)
datePkrCtrl.$inject = ['$scope'];

/**
 * @ngdoc controller
 * @name MyProfileCtrl
 *
 * @description
 * A controller used for the My Profile page.
 */
function myProfileCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, toastr) {
    $scope.submitted = false;
    $scope.loading = false;
    /**
     * The initial profile retrieved from the server to know the dirty state.
     * @type {{}}
     */
    $scope.initialProfile = {};
    /**
     * Candidates for the tee_shirt_size select box.
     * @type {string[]}
     */
    $scope.tee_shirt_sizes = [{
        'size': 'XS_M',
        'text': "XS - Men's"
    }, {
        'size': 'XS_W',
        'text': "XS - Women's"
    }, {
        'size': 'S_M',
        'text': "S - Men's"
    }, {
        'size': 'S_W',
        'text': "S - Women's"
    }, {
        'size': 'M_M',
        'text': "M - Men's"
    }, {
        'size': 'M_W',
        'text': "M - Women's"
    }, {
        'size': 'L_M',
        'text': "L - Men's"
    }, {
        'size': 'L_W',
        'text': "L - Women's"
    }, {
        'size': 'XL_M',
        'text': "XL - Men's"
    }, {
        'size': 'XL_W',
        'text': "XL - Women's"
    }, {
        'size': 'XXL_M',
        'text': "XXL - Men's"
    }, {
        'size': 'XXL_W',
        'text': "XXL - Women's"
    }, {
        'size': 'XXXL_M',
        'text': "XXXL - Men's"
    }, {
        'size': 'XXXL_W',
        'text': "XXXL - Women's"
    }];
    /**
     * Initializes the My profile page.
     * Update the profile if the user's profile has been stored.
     */
    $scope.init = function() {
        if (!oauth2Provider.signedIn) {
            var modalInstance = oauth2Provider.showLoginModal();
            modalInstance.result.then($scope.retrieveProfileCallback);
        } else {
            $scope.retrieveProfileCallback();
        }
    };
    /**
     * Invokes the conference.saveProfile API.
     *
     */
    $scope.saveProfile = function() {
        $scope.submitted = true;
        $scope.loading = true;
        gapi.client.conference.saveProfile($scope.profile).
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to update a profile : ' + errorMessage);
                    $log.error($scope.messages + 'Profile : ' + JSON.stringify($scope.profile));
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    toastr.success('The profile has been updated');
                    $scope.submitted = false;
                    $scope.initialProfile = {
                        display_name: $scope.profile.display_name,
                        tee_shirt_size: $scope.profile.tee_shirt_size
                    };
                    $log.info($scope.messages + JSON.stringify(resp.result));
                }
            });
        });
    };
};
/**
 * @ngdoc controller
 * @name CreateConferenceCtrl
 *
 * @description
 * A controller used for the Create conferences page.
 */

function createConferenceCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, toastr) {
    var vm = this;
    vm.goBack = function() {
        window.history.back();
    }
    $scope.isCreate = true;
    /**
     * The conference object being edited in the page.
     * @type {{}|*}
     */
    $scope.conference = $scope.conference || {};
    /**
     * Holds the default values for the input candidates for city select.
     * @type {string[]}
     */
    $scope.cities = ['Chicago', 'London', 'Paris', 'San Francisco', 'Tokyo'];
    /**
     * Holds the default values for the input candidates for topics select.
     * @type {string[]}
     */
    $scope.topics = ['Medical Innovations', 'Programming Languages', 'Web Technologies', 'Movie Making', 'Health and Nutrition'];
    /**
     * Tests if the arugment is an integer and not negative.
     * @returns {boolean} true if the argument is an integer, false otherwise.
     */
    /*min date for the calander*/
    $scope.minDate = new Date();
    $scope.isValidmax_attendees = function() {
        if (!$scope.conference.max_attendees || $scope.conference.max_attendees.length == 0) {
            return true;
        }
        return /^[\d]+$/.test($scope.conference.max_attendees) && $scope.conference.max_attendees >= 0;
    }

    $scope.isValidstart_date = function() {
        var today = new Date().setHours(0, 0, 0, 0);
        if (!$scope.conference.start_date) {
            return true;
        }
        return today <= $scope.conference.start_date.setHours(0, 0, 0, 0);
    }
    /**
     * Tests if the conference.start_date and conference.end_date are valid.
     * @returns {boolean} true if the dates are valid, false otherwise.
     */
    $scope.isValidDates = function() {
        var today = new Date();

        if (!$scope.conference.end_date) {
            return true;
        }
        if ($scope.conference.start_date && !$scope.conference.end_date) {
            return true;
        }
        return $scope.conference.start_date <= $scope.conference.end_date;
    }
    /**
     * Tests if $scope.conference is valid.
     * @param conferenceForm the form object from the create_conferences.html page.
     * @returns {boolean|*} true if valid, false otherwise.
     */
    $scope.isValidConference = function(conferenceForm) {
        return !conferenceForm.$invalid && $scope.isValidmax_attendees() && $scope.isValidDates() && $scope.isValidstart_date();
    }
    /*placeholder */
    $scope.init = function() {

    }
    /**
     * Invokes the conference.createConference API.
     *
     * @param conferenceForm the form object.
     */
    $scope.createConference = function(conferenceForm) {
        if (!$scope.isValidConference(conferenceForm)) {
            return;
        }
        $scope.loading = true;
        gapi.client.conference.createConference($scope.conference).
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to update a conference : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    toastr.success('The conference has been updated : ' + resp.result.name);
                    $scope.submitted = false;
                    $scope.conference = {};
                    $log.info($scope.messages + ' : ' + JSON.stringify(resp.result));
                }
            });
        });
    };
};


function editConferenceCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, toastr, $routeParams) {
    var vm = this;
    vm.goBack = function() {
        window.history.back();
    }
    $scope.isCreate = false;
    /**
     * The conference object being edited in the page.
     * @type {{}|*}
     */
    $scope.conference = $scope.conference || {};
    /**
     * Holds the default values for the input candidates for city select.
     * @type {string[]}
     */
    $scope.cities = ['Chicago', 'London', 'Paris', 'San Francisco', 'Tokyo'];
    /**
     * Holds the default values for the input candidates for topics select.
     * @type {string[]}
     */
    $scope.topics = ['Medical Innovations', 'Programming Languages', 'Web Technologies', 'Movie Making', 'Health and Nutrition'];
    /**
     * Tests if the arugment is an integer and not negative.
     * @returns {boolean} true if the argument is an integer, false otherwise.
     */
    /*min date for the calander*/
    $scope.minDate = new Date();
    $scope.isValidmax_attendees = function() {
        if (!$scope.conference.max_attendees || $scope.conference.max_attendees.length == 0) {
            return true;
        }
        return /^[\d]+$/.test($scope.conference.max_attendees) && $scope.conference.max_attendees >= 0;
    }

    $scope.isValidstart_date = function() {
        var today = new Date().setHours(0, 0, 0, 0);
        if (!$scope.conference.start_date) {
            return true;
        } else {
            if (angular.isDate($scope.conference.start_date)) {
                $scope.conference.start_date.setHours(0, 0, 0, 0);

            } else {
                $scope.conference.start_date = moment($scope.conference.start_date, 'YYYY-MM-DD').toDate();
                $scope.conference.start_date.setHours(0, 0, 0, 0);
            }
        }
        return today <= $scope.conference.start_date;
    }
    /**
     * Tests if the conference.start_date and conference.end_date are valid.
     * @returns {boolean} true if the dates are valid, false otherwise.
     */
    $scope.isValidDates = function() {
        var today = new Date();

        if (!$scope.conference.end_date) {
            return true;
        }
        if ($scope.conference.start_date && !$scope.conference.end_date) {
            return true;
        }

        return $scope.conference.start_date <= $scope.conference.end_date;
    }
    /**
     * Tests if $scope.conference is valid.
     * @param conferenceForm the form object from the create_conferences.html page.
     * @returns {boolean|*} true if valid, false otherwise.
     */
    $scope.isValidConference = function(conferenceForm) {
        console.log(!conferenceForm.$invalid, $scope.isValidmax_attendees(), $scope.isValidDates(), $scope.isValidstart_date())
        return !conferenceForm.$invalid && $scope.isValidmax_attendees() && $scope.isValidDates() && $scope.isValidstart_date();
    }
    $scope.init = function() {
        $scope.loading = true;
        gapi.client.conference.getConference({
            webSafeConfKey: $routeParams.web_safe_key
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to get the conference : ' + $routeParams.web_safe_key + ' ' + errorMessage);
                } else {
                    $scope.conference = resp.result;
                    $scope.conference.start_date = moment($scope.conference.start_date, 'YYYY-MM-DD').toDate();
                    $scope.conference.end_date = moment($scope.conference.end_date, 'YYYY-MM-DD').toDate();
                }
            });
        });
        $scope.loading = true;
    };
    /**
     * Invokes the conference.createConference API.
     *
     * @param conferenceForm the form object.
     */
    $scope.updateConference = function(conferenceForm) {
        if (!$scope.isValidConference(conferenceForm)) {
            return;
        }
        $scope.loading = true;
        $scope.requestParams = {};
        $scope.conference.webSafeConfKey = $routeParams.web_safe_key;
        gapi.client.conference.updateConference($scope.conference).
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to create a conference : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    toastr.success('The conference has been created : ' + resp.result.name);
                    $scope.submitted = false;
                    $scope.conference = {};
                    $log.info($scope.messages + ' : ' + JSON.stringify(resp.result));
                }
            });
        });
    };
};
/**
 * @ngdoc controller
 * @name ShowConferenceCtrl
 *
 * @description
 * A controller used for the Show conferences page.
 */


function showConferenceCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, toastr) {
    /**
     * Holds the status if the query is being executed.
     * @type {boolean}
     */
    $scope.submitted = false;
    $scope.selectedTab = 'ALL';
    /**
     * Holds the filters that will be applied when queryConferencesAll is invoked.
     * @type {Array}
     */
    $scope.filters = [];
    $scope.filtereableFields = [{
        enumValue: 'CITY',
        display_name: 'City'
    }, {
        enumValue: 'TOPIC',
        display_name: 'Topic'
    }, {
        enumValue: 'MONTH',
        display_name: 'Start month'
    }, {
        enumValue: 'MAX_ATTENDEES',
        display_name: 'Max Attendees'
    }]
    /**
     * Possible operators.
     *
     * @type {{display_name: string, enumValue: string}[]}
     */
    $scope.operators = [{
        display_name: '=',
        enumValue: 'EQ'
    }, {
        display_name: '>',
        enumValue: 'GT'
    }, {
        display_name: '>=',
        enumValue: 'GTEQ'
    }, {
        display_name: '<',
        enumValue: 'LT'
    }, {
        display_name: '<=',
        enumValue: 'LTEQ'
    }, {
        display_name: '!=',
        enumValue: 'NE'
    }];
    /**
     * Holds the conferences currently displayed in the page.
     * @type {Array}
     */
    $scope.conferences = [];
    /**
     * Holds the state if offcanvas is enabled.
     *
     * @type {boolean}
     */
    $scope.isOffcanvasEnabled = false;
    /**
     * Sets the selected tab to 'ALL'
     */
    $scope.tabAllSelected = function() {
        $scope.selectedTab = 'ALL';
        $scope.queryConferences();
    };
    /**
     * Sets the selected tab to 'YOU_HAVE_CREATED'
     */
    $scope.tabYouHaveCreatedSelected = function() {
        $scope.selectedTab = 'YOU_HAVE_CREATED';
        if (!oauth2Provider.signedIn) {
            oauth2Provider.showLoginModal();
            return;
        }
        $scope.queryConferences();
    };
    /**
     * Sets the selected tab to 'YOU_WILL_ATTEND'
     */
    $scope.tabYouWillAttendSelected = function() {
        $scope.selectedTab = 'YOU_WILL_ATTEND';
        if (!oauth2Provider.signedIn) {
            oauth2Provider.showLoginModal();
            return;
        }
        $scope.queryConferences();
    };
    /**
     * Toggles the status of the offcanvas.
     */
    $scope.toggleOffcanvas = function() {
        $scope.isOffcanvasEnabled = !$scope.isOffcanvasEnabled;
    };
    /**
     * Namespace for the pagination.
     * @type {{}|*}
     */
    $scope.pagination = $scope.pagination || {};
    $scope.pagination.currentPage = 0;
    $scope.pagination.pageSize = 20;
    /**
     * Returns the number of the pages in the pagination.
     *
     * @returns {number}
     */
    $scope.pagination.numberOfPages = function() {
        return Math.ceil($scope.conferences.length / $scope.pagination.pageSize);
    };
    /**
     * Returns an array including the numbers from 1 to the number of the pages.
     *
     * @returns {Array}
     */
    $scope.pagination.pageArray = function() {
        var pages = [];
        var numberOfPages = $scope.pagination.numberOfPages();
        for (var i = 0; i < numberOfPages; i++) {
            pages.push(i);
        }
        return pages;
    };
    /**
     * Checks if the target element that invokes the click event has the "disabled" class.
     *
     * @param event the click event
     * @returns {boolean} if the target element that has been clicked has the "disabled" class.
     */
    $scope.pagination.isDisabled = function(event) {
        return angular.element(event.target).hasClass('disabled');
    }
    /**
     * Adds a filter and set the default value.
     */
    $scope.addFilter = function() {
        $scope.filters.push({
            field: $scope.filtereableFields[0],
            operator: $scope.operators[0],
            value: ''
        })
    };
    /**
     * Clears all filters.
     */
    $scope.clearFilters = function() {
        $scope.filters = [];
    };
    /**
     * Removes the filter specified by the index from $scope.filters.
     *
     * @param index
     */
    $scope.removeFilter = function(index) {
        if ($scope.filters[index]) {
            $scope.filters.splice(index, 1);
        }
    };
    /**
     * Query the conferences depending on the tab currently selected.
     *
     */
    $scope.queryConferences = function() {
        $scope.submitted = false;
        if ($scope.selectedTab == 'ALL') {
            $scope.queryConferencesAll();
        } else if ($scope.selectedTab == 'YOU_HAVE_CREATED') {
            $scope.getConferencesCreated();
        } else if ($scope.selectedTab == 'YOU_WILL_ATTEND') {
            $scope.getConferencesAttend();
        }
    };
    /**
     * Invokes the conference.queryConferences API.
     */
    $scope.queryConferencesAll = function() {
        var sendFilters = {
            filters: []
        }
        for (var i = 0; i < $scope.filters.length; i++) {
            var filter = $scope.filters[i];
            if (filter.field && filter.operator && filter.value) {
                sendFilters.filters.push({
                    field: filter.field.enumValue,
                    operator: filter.operator.enumValue,
                    value: filter.value
                });
            }
        }
        $scope.loading = true;
        gapi.client.conference.queryConferences(sendFilters).
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to query conferences : ' + errorMessage);
                } else {
                    // The request has succeeded.
                    $scope.submitted = false;
                    toastr.success('Query succeeded : ' + JSON.stringify(sendFilters));
                    $scope.conferences = [];
                    angular.forEach(resp.items, function(conference) {
                        $scope.conferences.push(conference);
                    });
                }
                $scope.submitted = true;
            });
        });
    }
    /**
     * Invokes the conference.getConferencesCreated method.
     */
    $scope.getConferencesCreated = function() {
        $scope.loading = true;
        gapi.client.conference.getConferencesCreated().
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.error('Failed to query the conferences created : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.submitted = false;
                    toastr.success('Query succeeded : Conferences you have created');
                    $scope.conferences = [];
                    angular.forEach(resp.items, function(conference) {
                        $scope.conferences.push(conference);
                    });
                }
                $scope.submitted = true;
            });
        });
    };
    /**
     * Retrieves the conferences to attend by calling the conference.getProfile method and
     * invokes the conference.getConference method n times where n == the number of the conferences to attend.
     */
    $scope.getConferencesAttend = function() {
        $scope.loading = true;
        gapi.client.conference.getConferencesToAttend().
        execute(function(resp) {
            $scope.$apply(function() {
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to query the conferences to attend : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.conferences = resp.result.items;
                    $scope.loading = false;
                    toastr.success('Query succeeded : Conferences you will attend (or you have attended)');
                }
                $scope.submitted = true;
            });
        });
    };
};
/**
 * @ngdoc controller
 * @name ConferenceDetailCtrl
 *
 * @description
 * A controller used for the conference detail page.
 */
function conferenceDetailCtrl($scope, $log, $routeParams, HTTP_ERRORS, toastr) {
    var vm = this;
    $scope.conference = {};
    $scope.Sessions = [];
    $scope.isUserAttending = false;
    /**
     * Initializes the conference detail page.
     * Invokes the conference.getConference method and sets the returned conference in the $scope.
     *
     */
    $scope.init = function() {
        $scope.loading = true;
        gapi.client.conference.getConference({
            webSafeConfKey: $routeParams.webSafeConfKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to get the conference : ' + $routeParams.web_safe_key + ' ' + errorMessage);
                } else {
                    $scope.conference = resp.result;
                }
            });
        });
        $scope.loading = true;
        // If the user is attending the conference, updates the status message and available function.
        gapi.client.conference.getProfile().execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // Failed to get a user profile.
                } else {
                    var profile = resp.result;
                    if (profile && profile.conference_keys_to_attend) {
                        for (var i = 0; i < profile.conference_keys_to_attend.length; i++) {
                            if ($routeParams.webSafeConfKey == profile.conference_keys_to_attend[i]) {
                                // The user is attending the conference.
                                toastr.info('You are attending this conference');
                                $scope.isUserAttending = true;
                            }
                        }
                    }
                }
            });
        });
        gapi.client.conference.getConferenceSessions({
            webSafeConfKey: $routeParams.webSafeConfKey
        }).execute(function(resp) {
            if (!resp.error) {
                $scope.Sessions = resp.result.items;

            }

        });
    };
    /**
     * Invokes the conference.registerForConference method.
     */
    $scope.registerForConference = function() {
        $scope.loading = true;
        gapi.client.conference.registerForConference({
            webSafeConfKey: $routeParams.webSafeConfKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to register for the conference : ' + errorMessage);
                    $log.error($scope.messages);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result) {
                        // Register succeeded.
                        toastr.success('Registered for the conference');
                        $scope.isUserAttending = true;
                        $scope.conference.seats_available = $scope.conference.seats_available - 1;
                    } else {
                        toastr.error('Failed to register for the conference');
                    }
                }
            });
        });
    };
    /**
     * Invokes the conference.unregisterForConference method.
     */
    $scope.unregisterFromConference = function() {
        $scope.loading = true;
        gapi.client.conference.unregisterFromConference({
            webSafeConfKey: $routeParams.webSafeConfKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to unregister from the conference : ' + errorMessage);
                    $log.error($scope.messages);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result) {
                        // Unregister succeeded.
                        toastr.success('Unregistered from the conference');
                        $scope.conference.seats_available = $scope.conference.seats_available + 1;
                        $scope.isUserAttending = false;
                        $log.info($scope.messages);
                    } else {
                        var errorMessage = resp.error.message || '';
                        toastr.warning('Failed to unregister from the conference : ' + $routeParams.web_safe_key + ' : ' + errorMessage);
                        $log.error($scope.messages);
                    }
                }
            });
        });
    };
};
/**
 * @ngdoc controller
 * @name RootCtrl
 *
 * @description
 * The root controller having a scope of the body element and methods used in the application wide
 * such as user authentications.
 *
 */
function rootCtrl($scope, $location, oauth2Provider, toastr) {
    $scope.profile = {};
    /**
     * Returns if the viewLocation is the currently viewed page.
     *
     * @param viewLocation
     * @returns {boolean} true if viewLocation is the currently viewed page. Returns false otherwise.
     */
    $scope.isActive = function(viewLocation) {
        return viewLocation === $location.path();
    };
    /**
     * Returns the OAuth2 signedIn state.
     *
     * @returns {oauth2Provider.signedIn|*} true if siendIn, false otherwise.
     */
    $scope.getSignedInState = function() {
        if (oauth2Provider.signedIn) {}
        return oauth2Provider.signedIn;
    };
    /**
     * Calls the OAuth2 authentication method.
     */
    $scope.signIn = function() {
        oauth2Provider.signIn(function() {
            gapi.client.oauth2.userinfo.get().execute(function(resp) {
                if (!resp.error) {
                    toastr.success('Logged in with ' + resp.email);
                    $scope.getUserProfile();
                }

            });
        });
    };
    /*adding a watch to check and update the profile in scope based on the signed in state*/
    $scope.$watch(function() {
        return $scope.getSignedInState();
    }, function(newVal, oldVal) {
        if (newVal !== oldVal) {
            console.log('calling the get profile');
            $scope.getUserProfile();
        }
    })
    /**
     * Render the signInButton and restore the credential if it's stored in the cookie.
     * (Just calling this to restore the credential from the stored cookie. So hiding the signInButton immediately
     *  after the rendering)
     */
    $scope.initSignInButton = function() {
        gapi.signin.render('signInButton', {
            'callback': function() {
                jQuery('#signInButton button').attr('disabled', 'true').css('cursor', 'default');
                if (gapi.auth.getToken() && gapi.auth.getToken().access_token) {
                    $scope.$apply(function() {
                        oauth2Provider.signedIn = true;
                    });
                }
            },
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'scope': oauth2Provider.SCOPES
        });

    };

    $scope.getUserProfile = function() {
        gapi.client.conference.getProfile().
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // Failed to get a user profile.
                } else {
                    // Succeeded to get the user profile.
                    $scope.profile.display_name = resp.result.display_name;
                    $scope.profile.tee_shirt_size = resp.result.tee_shirt_size;
                    $scope.initialProfile = resp.result;
                }
            });
        });
    }
    /**
     * Logs out the user.
     */
    $scope.signOut = function() {
        oauth2Provider.signOut();
        $scope.profile = {};
        $scope.initialProfile = {};
        $location.path('/home');

        toastr.success('Logged out !');
    };
    /**
     * Collapses the navbar on mobile devices.
     */
    $scope.collapseNavbar = function() {
        angular.element(document.querySelector('.navbar-collapse')).removeClass('in');
    };
    $scope.retrieveProfileCallback = function() {
        $scope.profile = {};
        $scope.loading = true;
        gapi.client.conference.getProfile().
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // Failed to get a user profile.
                } else {
                    // Succeeded to get the user profile.
                    $scope.profile.display_name = resp.result.display_name;
                    $scope.profile.tee_shirt_size = resp.result.tee_shirt_size;
                    $scope.initialProfile = resp.result;
                }
            });
        });
    };
};
/**
 * @ngdoc controller
 * @name OAuth2LoginModalCtrl
 *
 * @description
 * The controller for the modal dialog that is shown when an user needs to login to achive some functions.
 *
 */

function oAuth2LoginModalCtrl($scope, $uibModalInstance, $rootScope, oauth2Provider, toastr) {
    $scope.singInViaModal = function() {
        oauth2Provider.signIn(function() {
            gapi.client.oauth2.userinfo.get().execute(function(resp) {
                $scope.$root.$apply(function() {
                    oauth2Provider.signedIn = true;
                    toastr.success('Logged in with ' + resp.email);
                });
                $uibModalInstance.close();
            });
        });
    };
};
/**
 * @ngdoc controller
 * @name DatepickerCtrl
 *
 * @description
 * A controller that holds properties for a datepicker.
 */


function datePkrCtrl($scope) {
    $scope.today = function() {
        $scope.dt = moment().format('dd-MMMM-yyyy');
    };

    $scope.clear = function() {
        $scope.dt = null;
    };
    // Disable weekend selection
    $scope.disabled = function(date, mode) {
        return (mode === 'day' && (date.getDay() === 0 || date.getDay() === 6));
    };

    // $scope.minDate = new Date();

    $scope.open = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };
    $scope.dateOptions = {
        'year-format': "'yy'",
        'starting-day': 1,
    };
    $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'shortDate'];
    $scope.format = $scope.formats[0];
};
/**
 * @ngdoc controller
 * @name CreateConferenceCtrl
 *
 * @description
 * A controller used for the Create conferences page.
 */


function registerSpeakerCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $timeout, toastr) {
    var vm = this;
    vm.speakerExists = false;
    /**
     * The speaker object being edited in the page.
     * @type {{}|*}
     */
    vm.speaker = vm.speaker || {};
    /**
     * Holds the default values for the input candidates for topics select.
     * @type {string[]}
     */
    vm.topics = ['None', 'Host', 'Medical Innovations', 'Programming Languages', 'Web Technologies', 'Movie Making', 'Health and Nutrition'];
    /**
     * Tests if the arugment is not empty and min 10 characters long.
     * @returns {boolean} true if the argument is not empty an dmore than 10 characters.
     */
    vm.isValidAbout = function() {
        var result = false;
        if (vm.speaker.about_speaker && vm.speaker.about_speaker.length >= 10) {
            result = true;
        }
        return result;
    }
    /**
     * Tests if the conference.start_date and conference.end_date are valid.
     * @returns {boolean} true if the dates are valid, false otherwise.
     */
    vm.isValidTopic = function() {
        var result = false;
        if (vm.speaker.topics && vm.speaker.topics.length >= 1) {
            result = true;
        }
        return result;
    }
    /**
     * Tests if $scope.conference is valid.
     * @param speakerForm the form object from the register_speaker.html page.
     * @returns {boolean|*} true if valid, false otherwise.
     */
    vm.isValidSpeaker = function(speakerForm) {
        return !speakerForm.$invalid && vm.isValidAbout() && vm.isValidTopic();
    }
    /**
     * Invokes the conference.createConference API.
     *
     * @param speakerForm the form object.
     */
    vm.registerSpeaker = function(speakerForm) {
        if (!vm.isValidSpeaker(speakerForm)) {
            return;
        }
        $scope.loading = true;
        gapi.client.conference.registerSpeaker(vm.speaker).
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.error('Failed to register you as speaker : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    toastr.success('The Speaker has been registerd!');
                    $scope.submitted = false;
                    vm.speaker = {};
                    $log.info($scope.messages + ' : ' + JSON.stringify(resp.result));
                }
            });
        });
    };
    /**
     * Invokes the speakerExissts.
     *
     * @param none.
     */
    vm.initSpeaker = function() {
        $scope.loading = true;
        gapi.client.conference.speakerExists().
        execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    /*The request has failed.
                    and it is not that the user is not regiseres
                    */
                    if (resp.code && resp.code != 409) {
                        var errorMessage = resp.error.message || '';
                        toastr.warning('Failed to verify speaker : ' + errorMessage);
                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    }
                } else {
                    if (resp.result.speaker_id) {
                        toastr.warning('You are Already Registered As A Speaker!');
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.speaker = resp.result;
                    } else {
                        /*the user is not registered show the form as usual*/
                    }
                }
            });
        });
    };
    $timeout(function() {
        vm.initSpeaker();
    }, 100);
}


function createSessionsCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $routeParams, toastr, $filter) {
    var vm = this;
    vm.hstep = 1;
    vm.mstep = 30;
    vm.ismeridian
    vm.speakerExists = false;
    vm.minDate = new Date();
    vm.maxDate = new Date();
    vm.open = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        vm.opened = true;
    };
    vm.dateOptions = {
        formatYear: 'yy',
        startingDay: 1
    };
    vm.formats = ['yyyy-MM-dd', 'dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
    vm.format = vm.formats[0];
    /**
     * The speaker object being edited in the page.
     * @type {{}|*}
     */
    vm.Session = vm.Session || {};
    vm.Session.start_time = new Date().setHours(0, 0, 0, 0);
    /**
     * Holds the default values for the session type selection
     * @type {string[]}
     */
    vm.sessionTypes = [{
        'value': 'GENERAL',
        'text': 'General'
    }, {
        'value': 'WORKSHOP',
        'text': 'Workshop'
    }, {
        'value': 'LECTURE',
        'text': 'Lecture'
    }, {
        'value': 'THINKTANK',
        'text': 'Think Tank'
    }, {
        'value': 'SKILLBUILDER',
        'text': 'Skill Builder'
    }, {
        'value': 'EXPERTSPEAK',
        'text': 'Expert Speak'
    }, {
        'value': 'KEYNOTE',
        'text': 'Keynote'
    }];

    vm.goBack = function() {
        window.history.back();
    }
    vm.getDateFromString = function(inputDate) {
        if (inputDate === null || inputDate === undefined) {
            return new Date();
        }
        var dateParts = inputDate.split('-');
        var retVal = new Date();
        retVal.setFullYear(parseInt(dateParts[0], 10), (parseInt(dateParts[1], 10) - 1), parseInt(dateParts[2], 10));
        retVal.setHours(0, 0, 0, 0);
        return retVal;
    };
    /**
     * Tests if the arugment is not empty and min 10 characters long.
     * @returns {boolean} true if the argument is not empty an dmore than 10 characters.
     */
    vm.isValidAbout = function() {
        var result = false;
        if (vm.speaker.about_speaker && vm.speaker.about_speaker.length >= 10) {
            result = true;
        }
        return result;
    }
    /**
     * Tests if the conference.start_date and conference.end_date are valid.
     * @returns {boolean} true if the dates are valid, false otherwise.
     */
    vm.isValidTopic = function() {
        var result = false;
        if (vm.speaker.topics && vm.speaker.topics.length >= 1) {
            result = true;
        }
        return result;
    }
    /**
     * Tests if $scope.conference is valid.
     * @param speakerForm the form object from the register_speaker.html page.
     * @returns {boolean|*} true if valid, false otherwise.
     */
    vm.isValidSpeaker = function(speakerForm) {
        return !speakerForm.$invalid && vm.isValidAbout() && vm.isValidTopic();
    }
    /**
     * Invokes the conference.createConference API.
     *
     * @param speakerForm the form object.
     */
    vm.registerSpeaker = function(speakerForm) {
        if (!vm.isValidSpeaker(speakerForm)) {
            return;
        }
        $scope.loading = true;
        gapi.client.conference.registerSpeaker(vm.speaker).
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to register you as speaker : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    toastr.success('The Speaker has been registerd!');
                    $scope.submitted = false;
                    vm.speaker = {};
                    $log.info($scope.messages + ' : ' + JSON.stringify(resp.result));
                }
            });
        });
    };
    /**
     * Invokes the speakerExissts.
     *
     * @param none.
     */
    vm.initSpeaker = function() {
        $scope.loading = true;
        gapi.client.conference.speakerExists().
        execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to verify speaker : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result.speaker_id) {
                        toastr.warning('You are Already Registered As A Speaker!');
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.speaker = resp.result;
                    } else {
                        /*the user is not registered show the form as usual*/
                    }
                }
            });
        });
    };
    vm.isValidDuration = function() {
        if (!vm.Session.duration || vm.Session.duration.length == 0) {
            return true;
        }
        return /^[\d]+$/.test(vm.Session.duration) && vm.Session.duration >= 0;
    }
    vm.isValidDate = function() {
        var result = false;
        if (vm.Session.date >= vm.minDate && vm.Session.date <= vm.maxDate) {
            result = true;
        }
        return result;
    }
    vm.isValidSession = function(conferenceSessionForm) {
        return !conferenceSessionForm.$invalid && vm.isValidDuration() && vm.isValidDate();
    }
    vm.init = function() {
        $scope.loading = true;
        gapi.client.conference.getConference({
            webSafeConfKey: $routeParams.webSafeConfKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Failed to get the conference : ' + $routeParams.web_safe_key + ' ' + errorMessage);
                    $log.error($scope.messages);
                } else {

                    vm.conference = resp.result;
                    vm.createAllowed = $scope.profile.display_name === vm.conference.organizer_display_name;
                    vm.minDate = moment(vm.conference.start_date).toDate().setHours(0, 0, 0, 0);
                    vm.maxDate = moment(vm.conference.end_date).toDate().setHours(23, 59, 0, 0);
                    if (!vm.createAllowed) {
                        toastr.warning('Only Conference Organizers can Create Sessions');
                    }
                }
            });
        });
        gapi.client.conference.getAllSpeakers().execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toaster.error('Failed to get the conference : ' + $routeParams.web_safe_key + ' ' + errorMessage);
                    $log.error($scope.messages);
                } else {
                    vm.speakers = resp.result.items;
                }
            });
        });
    }
    vm.formatFormObj = function(formObj) {
        formObj.speaker_key = formObj.speaker.web_safe_key;
        formObj.start_time = $filter('date')(formObj.start_time, 'H:mm');
        return formObj;
    }
    vm.createConferenceSession = function(conferenceSessionForm) {
        if (!vm.isValidSession(conferenceSessionForm)) {
            return;
        }
        vm.Session.webSafeConfKey = $routeParams.webSafeConfKey;
        vm.Session = vm.formatFormObj(vm.Session);
        gapi.client.conference.createSession(vm.Session).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.error('Failed to create Sessions : ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result.web_safe_key) {
                        toastr.success('Session Creates Successfully');
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.speaker = resp.result;
                    } else {
                        /*the user is not registered show the form as usual*/
                    }
                }
            });
        });
    }
}
/***
ViewSpeakerCtrl is for the view speakers functionality
***/


function ViewSpeakerCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $routeParams, toastr) {
    var vm = this;
    vm.init = function() {
        $scope.loading = true;
        gapi.client.conference.getAllSpeakers().
        execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.error('Error getting Speakers: ' + errorMessage);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result.items && resp.result.items.length > 0) {
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.speakers = resp.result.items;
                    } else {
                        toastr.warning('No Speakers found!');
                    }
                }
            });
        });
    }
}
/***
viewSpeakerSessionsCtrl is for the view speakers sessions functionality
***/


function viewSpeakerSessionsCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $routeParams, toastr) {
    var vm = this;
    vm.autoArchive = true;
    vm.init = function() {
        vm.speaker_name = $routeParams.speaker_name
        vm.headingText = "Showing Session(s) by [ " + vm.speaker_name + " ]";
        $scope.loading = true;
        gapi.client.conference.getSessionsBySpeaker({
            web_safe_key: $routeParams.web_safe_key
        }).
        execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('No Sessions Found ');
                } else {
                    if (resp.result.items && resp.result.items.length > 0) {
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.sessions = resp.result.items;
                    } else {
                        toastr.warning('No Sessions Found!');
                        /*the user is not registered show the form as usual*/
                    }
                }
            });
        });
    }
}




function session_wish_listCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $routeParams, toastr) {
    var vm = this;
    vm.headingText = "Showing Session(s) in wishlist"
    vm.sessions = [];
    vm.autoArchive = true;
    vm.init = function() {
        $scope.loading = true;
        gapi.client.conference.getSessionsInWishlist().
        execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('No Sessions Found ');
                } else {
                    if (resp.result.items && resp.result.items.length > 0) {
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.sessions = resp.result.items;
                    } else {
                        toastr.warning('No Records Found!');
                        /*the user is not registered show the form as usual*/
                    }
                }
            });
        });
    }
}

function viewAllSessionsCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $routeParams, toastr, $filter) {
    var vm = this;
    vm.headingText = "Showing All Session(s)"
    vm.sessions = [];
    vm.autoArchive = true;
    vm.end_date = null;
    vm.dateType = "TODAY"

    /*setup a watch to calculate the end date for the method. */
    $scope.$watch(function() {
        console.log('value changes ')
        return vm.dateType;
    }, function(newVal, oldVal) {
        if (newVal !== oldVal && newVal) {
            var date_d = moment();
            console.log(newVal);
            if (newVal === "WEEK") {
                date_d.add(7, 'days')
            } else if (newVal === "MONTH") {
                date_d.add(1, 'months')
            } else if (newVal === "YEAR") {
                date_d.add(1, 'years')
            } else if (newVal === "TODAY") {
                date_d = moment().format("YYYY-MM-DD");
                date_d = "" + date_d + " 23:59";
                date_d = moment(date_d, "YYYY-MM-DD HH:mm");
            }
            vm.end_date = date_d.format("YYYY-MM-DD HH:mm");
            vm.init();
        }
    });
    vm.init = function() {
        $scope.loading = true;
        if (!vm.end_date) {
            var date_d = moment();
            date_d = moment().format("YYYY-MM-DD");
            date_d = "" + date_d + " 23:59";
            date_d = moment(date_d, "YYYY-MM-DD HH:mm");
            vm.end_date = date_d.format("YYYY-MM-DD HH:mm");

        }
        vm.start_date = $filter('date')(new Date().setHours(0, 0, 0, 0), 'yyyy-MM-dd H:mm');
        var reqobj = {
            start_date: vm.start_date

        }
        if (vm.end_date) {
            reqobj.end_date = vm.end_date;

        }

        gapi.client.conference.getAllFutureSessions(reqobj).execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    toastr.warning('No Sessions Found ');
                } else {
                    if (resp.result.items && resp.result.items.length > 0) {
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.sessions = resp.result.items;
                    } else {
                        toastr.warning('No Records Found!');
                        vm.sessions = [];
                        /*the user is not registered show the form as usual*/
                    }
                }
            });
        });
    }
}

function carouselContentsCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $routeParams, toastr, $filter, $interval) {

    var vm = this;
    vm.sessions = [];
    vm.announcement = "";
    vm.featured_speaker = {};
    vm.autoArchive = false;
    vm.getCachedAnnouncements = function() {
        /*get the announcements*/
        gapi.client.conference.getAnnouncement().execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                if (!resp.error) {
                    vm.announcement = resp.data;

                }
            });
        });
    }

    vm.getCachedStartingSoon = function() {
        /*get the information for the sessions starting soon */
        gapi.client.conference.getSessionsStartingSoonCached().execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (!resp.error) {
                    if (resp.result.items && resp.result.items.length > 0) {
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.sessions = resp.result.items;
                    }
                }
            });
        });
    }

    vm.getFeaturedSpeaker = function() {
        /*get the featured speaker */
        gapi.client.conference.getFeaturedSpeaker().execute(function(resp) {
            $scope.$apply(function() {
                if (!resp.error) {
                    if (resp.result && resp.result.speaker_name) {
                        vm.featured_speaker = resp.result;
                    } else {
                        vm.featured_speaker = undefined;
                    }
                }

            });
        });

    }

    vm.init = function() {
        vm.getCachedAnnouncements();
        vm.getCachedStartingSoon();
        vm.getFeaturedSpeaker();
    }


}