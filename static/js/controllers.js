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
conferenceDetailCtrl.$inject = ['$scope', '$log', '$routeParams', 'HTTP_ERRORS'];
/**
 * @ngdoc controller
 * @name MyProfileCtrl
 *
 * @description
 * A controller used for the My Profile page.
 */
conferenceApp.controllers.controller('MyProfileCtrl', function($scope, $log, oauth2Provider, HTTP_ERRORS) {
    $scope.submitted = false;
    $scope.loading = false;
    /**
     * The initial profile retrieved from the server to know the dirty state.
     * @type {{}}
     */
    $scope.initialProfile = {};
    /**
     * Candidates for the teeShirtSize select box.
     * @type {string[]}
     */
    $scope.teeShirtSizes = [{
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
                    $scope.messages = 'Failed to update a profile : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages + 'Profile : ' + JSON.stringify($scope.profile));
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.messages = 'The profile has been updated';
                    $scope.alertStatus = 'success';
                    $scope.submitted = false;
                    $scope.initialProfile = {
                        displayName: $scope.profile.displayName,
                        teeShirtSize: $scope.profile.teeShirtSize
                    };
                    $log.info($scope.messages + JSON.stringify(resp.result));
                }
            });
        });
    };
});
/**
 * @ngdoc controller
 * @name CreateConferenceCtrl
 *
 * @description
 * A controller used for the Create conferences page.
 */
conferenceApp.controllers.controller('CreateConferenceCtrl', function($scope, $log, oauth2Provider, HTTP_ERRORS) {
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
    $scope.isValidMaxAttendees = function() {
        if (!$scope.conference.maxAttendees || $scope.conference.maxAttendees.length == 0) {
            return true;
        }
        return /^[\d]+$/.test($scope.conference.maxAttendees) && $scope.conference.maxAttendees >= 0;
    }
    /**
     * Tests if the conference.startDate and conference.endDate are valid.
     * @returns {boolean} true if the dates are valid, false otherwise.
     */
    $scope.isValidDates = function() {
        if (!$scope.conference.startDate && !$scope.conference.endDate) {
            return true;
        }
        if ($scope.conference.startDate && !$scope.conference.endDate) {
            return true;
        }
        return $scope.conference.startDate <= $scope.conference.endDate;
    }
    /**
     * Tests if $scope.conference is valid.
     * @param conferenceForm the form object from the create_conferences.html page.
     * @returns {boolean|*} true if valid, false otherwise.
     */
    $scope.isValidConference = function(conferenceForm) {
        return !conferenceForm.$invalid && $scope.isValidMaxAttendees() && $scope.isValidDates();
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
                    $scope.messages = 'Failed to create a conference : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages + ' Conference : ' + JSON.stringify($scope.conference));
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.messages = 'The conference has been created : ' + resp.result.name;
                    $scope.alertStatus = 'success';
                    $scope.submitted = false;
                    $scope.conference = {};
                    $log.info($scope.messages + ' : ' + JSON.stringify(resp.result));
                }
            });
        });
    };
});
/**
 * @ngdoc controller
 * @name ShowConferenceCtrl
 *
 * @description
 * A controller used for the Show conferences page.
 */
conferenceApp.controllers.controller('ShowConferenceCtrl', function($scope, $log, oauth2Provider, HTTP_ERRORS) {
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
        displayName: 'City'
    }, {
        enumValue: 'TOPIC',
        displayName: 'Topic'
    }, {
        enumValue: 'MONTH',
        displayName: 'Start month'
    }, {
        enumValue: 'MAX_ATTENDEES',
        displayName: 'Max Attendees'
    }]
    /**
     * Possible operators.
     *
     * @type {{displayName: string, enumValue: string}[]}
     */
    $scope.operators = [{
        displayName: '=',
        enumValue: 'EQ'
    }, {
        displayName: '>',
        enumValue: 'GT'
    }, {
        displayName: '>=',
        enumValue: 'GTEQ'
    }, {
        displayName: '<',
        enumValue: 'LT'
    }, {
        displayName: '<=',
        enumValue: 'LTEQ'
    }, {
        displayName: '!=',
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
                    $scope.messages = 'Failed to query conferences : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages + ' filters : ' + JSON.stringify(sendFilters));
                } else {
                    // The request has succeeded.
                    $scope.submitted = false;
                    $scope.messages = 'Query succeeded : ' + JSON.stringify(sendFilters);
                    $scope.alertStatus = 'success';
                    $log.info($scope.messages);
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
                    $scope.messages = 'Failed to query the conferences created : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.submitted = false;
                    $scope.messages = 'Query succeeded : Conferences you have created';
                    $scope.alertStatus = 'success';
                    $log.info($scope.messages);
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
                    $scope.messages = 'Failed to query the conferences to attend : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.conferences = resp.result.items;
                    $scope.loading = false;
                    $scope.messages = 'Query succeeded : Conferences you will attend (or you have attended)';
                    $scope.alertStatus = 'success';
                    $log.info($scope.messages);
                }
                $scope.submitted = true;
            });
        });
    };
});
/**
 * @ngdoc controller
 * @name ConferenceDetailCtrl
 *
 * @description
 * A controller used for the conference detail page.
 */
function conferenceDetailCtrl($scope, $log, $routeParams, HTTP_ERRORS) {
    var vm = this;
    $scope.conference = {};
    $scope.confsessions = [];
    $scope.isUserAttending = false;
    /**
     * Initializes the conference detail page.
     * Invokes the conference.getConference method and sets the returned conference in the $scope.
     *
     */
    $scope.init = function() {
        $scope.loading = true;
        gapi.client.conference.getConference({
            websafeConferenceKey: $routeParams.websafeConferenceKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to get the conference : ' + $routeParams.websafeKey + ' ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                } else {
                    // The request has succeeded.
                    $scope.alertStatus = 'success';
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
                    if (profile && profile.conferenceKeysToAttend) {
                        for (var i = 0; i < profile.conferenceKeysToAttend.length; i++) {
                            if ($routeParams.websafeConferenceKey == profile.conferenceKeysToAttend[i]) {
                                // The user is attending the conference.
                                $scope.alertStatus = 'info';
                                $scope.messages = 'You are attending this conference';
                                $scope.isUserAttending = true;
                            }
                        }
                    }
                }
            });
        });
        gapi.client.conference.getConferenceSessions({
            websafeConferenceKey: $routeParams.websafeConferenceKey
        }).execute(function(resp) {
            if (!resp.error) {
                $scope.confsessions = resp.result.items;

            }

        });
    };
    /**
     * Invokes the conference.registerForConference method.
     */
    $scope.registerForConference = function() {
        $scope.loading = true;
        gapi.client.conference.registerForConference({
            websafeConferenceKey: $routeParams.websafeConferenceKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to register for the conference : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result) {
                        // Register succeeded.
                        $scope.messages = 'Registered for the conference';
                        $scope.alertStatus = 'success';
                        $scope.isUserAttending = true;
                        $scope.conference.seatsAvailable = $scope.conference.seatsAvailable - 1;
                    } else {
                        $scope.messages = 'Failed to register for the conference';
                        $scope.alertStatus = 'warning';
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
            websafeConferenceKey: $routeParams.websafeConferenceKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to unregister from the conference : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result) {
                        // Unregister succeeded.
                        $scope.messages = 'Unregistered from the conference';
                        $scope.alertStatus = 'success';
                        $scope.conference.seatsAvailable = $scope.conference.seatsAvailable + 1;
                        $scope.isUserAttending = false;
                        $log.info($scope.messages);
                    } else {
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Failed to unregister from the conference : ' + $routeParams.websafeKey + ' : ' + errorMessage;
                        $scope.messages = 'Failed to unregister from the conference';
                        $scope.alertStatus = 'warning';
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
conferenceApp.controllers.controller('RootCtrl', function($scope, $location, oauth2Provider) {
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
                $scope.$apply(function() {
                    if (resp.email) {
                        oauth2Provider.signedIn = true;
                        $scope.alertStatus = 'success';
                        $scope.rootMessages = 'Logged in with ' + resp.email;
                    }
                });
            });
        });
    };
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
    /**
     * Logs out the user.
     */
    $scope.signOut = function() {
        oauth2Provider.signOut();
        $location.path('/home');
        $scope.alertStatus = 'success';
        $scope.rootMessages = 'Logged out';
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
                    $scope.profile.displayName = resp.result.displayName;
                    $scope.profile.teeShirtSize = resp.result.teeShirtSize;
                    $scope.initialProfile = resp.result;
                }
            });
        });
    };
});
/**
 * @ngdoc controller
 * @name OAuth2LoginModalCtrl
 *
 * @description
 * The controller for the modal dialog that is shown when an user needs to login to achive some functions.
 *
 */
conferenceApp.controllers.controller('OAuth2LoginModalCtrl', function($scope, $modalInstance, $rootScope, oauth2Provider) {
    $scope.singInViaModal = function() {
        oauth2Provider.signIn(function() {
            gapi.client.oauth2.userinfo.get().execute(function(resp) {
                $scope.$root.$apply(function() {
                    oauth2Provider.signedIn = true;
                    $scope.$root.alertStatus = 'success';
                    $scope.$root.rootMessages = 'Logged in with ' + resp.email;
                });
                $modalInstance.close();
            });
        });
    };
});
/**
 * @ngdoc controller
 * @name DatepickerCtrl
 *
 * @description
 * A controller that holds properties for a datepicker.
 */
conferenceApp.controllers.controller('DatepickerCtrl', function($scope) {
    $scope.today = function() {
        $scope.dt = new Date();
    };
    $scope.today();
    $scope.clear = function() {
        $scope.dt = null;
    };
    // Disable weekend selection
    $scope.disabled = function(date, mode) {
        return (mode === 'day' && (date.getDay() === 0 || date.getDay() === 6));
    };
    $scope.toggleMin = function() {
        $scope.minDate = ($scope.minDate) ? null : new Date();
    };
    $scope.toggleMin();
    $scope.open = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };
    $scope.dateOptions = {
        'year-format': "'yy'",
        'starting-day': 1
    };
    $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'shortDate'];
    $scope.format = $scope.formats[0];
});
/**
 * @ngdoc controller
 * @name CreateConferenceCtrl
 *
 * @description
 * A controller used for the Create conferences page.
 */
conferenceApp.controllers.controller('RegisterSpeakerCtrl', registerSpeakerCtrl);
registerSpeakerCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$timeout'];

function registerSpeakerCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $timeout) {
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
        if (vm.speaker.aboutSpeaker && vm.speaker.aboutSpeaker.length >= 10) {
            result = true;
        }
        return result;
    }
    /**
     * Tests if the conference.startDate and conference.endDate are valid.
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
                    $scope.messages = 'Failed to register you as speaker : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages + ' Speaker : ' + JSON.stringify(vm.speaker));
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.messages = 'The Speaker has been registerd!';
                    $scope.alertStatus = 'success';
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
                        $scope.messages = 'Failed to verify speaker : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    }
                } else {
                    if (resp.result.speakerUserId) {
                        $scope.messages = 'You are Already Registered As A Speaker!';
                        $scope.alertStatus = 'warning';
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
conferenceApp.controllers.controller('CreateConfSessionsCtrl', createConfSessionsCtrl);
createConfSessionsCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$timeout', '$routeParams', '$filter'];

function createConfSessionsCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $timeout, $routeParams, $filter) {
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
    vm.confSession = vm.confSession || {};
    vm.confSession.start_time = new Date().setHours(0, 0, 0, 0);
    /**
     * Holds the default values for the input candidates for topics select.
     * @type {string[]}
     */
    vm.topics = ['NOT_SPECIFIED', 'WORKSHOP', 'LECTURE', 'THINKTANK', 'SKILLBUILDER', 'EXPERTSPEAK'];
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
        if (vm.speaker.aboutSpeaker && vm.speaker.aboutSpeaker.length >= 10) {
            result = true;
        }
        return result;
    }
    /**
     * Tests if the conference.startDate and conference.endDate are valid.
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
                    $scope.messages = 'Failed to register you as speaker : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages + ' Speaker : ' + JSON.stringify(vm.speaker));
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.messages = 'The Speaker has been registerd!';
                    $scope.alertStatus = 'success';
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
                    $scope.messages = 'Failed to verify speaker : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result.speakerUserId) {
                        $scope.messages = 'You are Already Registered As A Speaker!';
                        $scope.alertStatus = 'warning';
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
        if (!vm.confSession.duration || vm.confSession.duration.length == 0) {
            return true;
        }
        return /^[\d]+$/.test(vm.confSession.duration) && vm.confSession.duration >= 0;
    }
    vm.isValidDate = function() {
        var result = false;
        if (vm.confSession.date >= vm.minDate && vm.confSession.date <= vm.maxDate) {
            result = true;
        }
        return result;
    }
    vm.isValidConfSession = function(conferenceSessionForm) {
        return !conferenceSessionForm.$invalid && vm.isValidDuration() && vm.isValidDate();
    }
    vm.init = function() {
        $scope.loading = true;
        gapi.client.conference.getConference({
            websafeConferenceKey: $routeParams.websafeConferenceKey
        }).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to get the conference : ' + $routeParams.websafeKey + ' ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                } else {
                    // The request has succeeded.
                    $scope.alertStatus = 'success';
                    vm.conference = resp.result;
                    vm.createAllowed = $scope.profile.displayName === vm.conference.organizerDisplayName;
                    vm.minDate = vm.getDateFromString(vm.conference.startDate)
                    vm.maxDate = vm.getDateFromString(vm.conference.endDate)
                    if (!vm.createAllowed) {
                        $scope.messages = "";
                        $scope.messages = 'Only Conference Organizers can Create Sessions';
                        $scope.alertStatus = 'warning';
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
                    $scope.messages = 'Failed to get the conference : ' + $routeParams.websafeKey + ' ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                } else {
                    vm.speakers = resp.result.items;
                }
            });
        });
    }
    vm.formatFormObj = function(formObj) {
        formObj.speaker = formObj.speaker.websafeKey;
        formObj.start_time = $filter('date')(formObj.start_time, 'H:mm');
        return formObj;
    }
    vm.createConferenceSession = function(conferenceSessionForm) {
        if (!vm.isValidConfSession(conferenceSessionForm)) {
            return;
        }
        vm.confSession.websafeConferenceKey = $routeParams.websafeConferenceKey;
        vm.confSession = vm.formatFormObj(vm.confSession);
        gapi.client.conference.createSession(vm.confSession).execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to create Sessions : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    if (resp.result.websafeKey) {
                        $scope.messages = 'Session Creates Successfully';
                        $scope.alertStatus = 'success';
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
conferenceApp.controllers.controller('ViewSpeakerCtrl', ViewSpeakerCtrl);
ViewSpeakerCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$timeout', '$routeParams', '$filter'];

function ViewSpeakerCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $timeout, $routeParams, $filter) {
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
                    $scope.messages = 'Failed to verify speaker : ' + errorMessage;
                    $scope.alertStatus = 'warning';
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
                        $scope.messages = 'No REcords found!';
                        $scope.alertStatus = 'warning';
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
conferenceApp.controllers.controller('ViewSpeakerSessionsCtrl', viewSpeakerSessionsCtrl);
viewSpeakerSessionsCtrl.$inject = ['$scope', '$log', 'oauth2Provider', 'HTTP_ERRORS', '$timeout', '$routeParams', '$filter'];

function viewSpeakerSessionsCtrl($scope, $log, oauth2Provider, HTTP_ERRORS, $timeout, $routeParams, $filter) {
    var vm = this;
    vm.init = function() {
        vm.speakerName = $routeParams.speakername
        $scope.loading = true;
        gapi.client.conference.getSessionsBySpeaker({
            websafeKey: $routeParams.websafeKey
        }).
        execute(function(resp) {
            console.log(resp);
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'No Sessions Found ';
                    $scope.alertStatus = 'warning';
                } else {
                    if (resp.result.items && resp.result.items.length > 0) {
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.sessions = resp.result.items;
                    } else {
                        $scope.messages = 'No Records Found!';
                        $scope.alertStatus = 'warning';
                        /*the user is not registered show the form as usual*/
                    }
                }
            });
        });
    }
}