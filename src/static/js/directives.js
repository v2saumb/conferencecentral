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
conferenceApp.directives = angular.module('conferenceDirectives', ['ui.bootstrap', 'toastr']);

conferenceApp.directives.directive('conferenceSessions', SessionDir);
SessionCtrl.$inject = ['$scope', 'toastr']

conferenceApp.directives.directive('collapsibleItemDetails', collapsibleItemDetails);
collapsibleItemDetails.$inject = ['$timeout'];
collapsableCtrl.$inject = ['$scope']

conferenceApp.directives.directive('userNameDisplay', userNameDisplayDir);


function SessionDir() {
    var dir = {
        restrict: 'E',
        scope: {
            sessions: '=',
            showconference_name: '@',
            showAddRemove: '@',
            showFilter: '@',
            showDetails: '@',
            autoArchive: "="

        },
        replace: true,
        templateUrl: "/partials/directives/conf-sessions.html",
        link: SessionLink,
        controller: SessionCtrl,
        controllerAs: 'csCtrl'

    };
    return dir;

    function SessionLink(scope, iElement, iAttrs) {
        if (!iAttrs.showFilter) {
            scope.showFilter = "true"
        }
        if (!iAttrs.showAddRemove) {
            scope.showAddRemove = "true"
        }
        if (!iAttrs.showDetails) {
            scope.showDetails = "true"
        }
    }
}

function SessionCtrl($scope, toastr) {

    $scope.filterText = "";
    var vm = this;
    vm.addSessionToWishlist = function(session) {
        vm.loading = true;
        gapi.client.conference.addSessionToWishlist({
            web_safe_key: session.web_safe_key
        }).
        execute(function(resp) {
            $scope.$apply(function() {
                vm.loading = false;
                if (resp.error) {
                    var errorMessage = resp.error.message || '';
                    toastr.error('Error:' + errorMessage);

                } else {
                    toastr.success("Session [ " + session.name + " ] added to your wishlist")
                }
            });
        });
    }

    vm.deleteSessionInWishlist = function(session) {
        vm.loading = true;
        gapi.client.conference.deleteSessionInWishlist({
            web_safe_key: session.web_safe_key
        }).
        execute(function(resp) {
            $scope.$apply(function() {
                vm.loading = false;
                if (resp.error) {
                    var errorMessage = resp.error.message || '';
                    toastr.warning('Error:' + errorMessage);

                } else {
                    if ($scope.autoArchive) {
                        toastr.success("Session [ " + session.name + " ] removed to your wishlist")
                        $scope.sessions.pop(session);
                    }

                }
            });
        });
    }

}



function collapsibleItemDetails($timeout) {
    var directive = {
        restrict: 'E',
        scope: {
            item: "=item",
            type: "=itemType",
        },
        templateUrl: getTemplate,
        controller: collapsableCtrl,
        controllerAs: "pcidCtrl",
        link: cidLink
    };
    return directive;

    function cidLink(scope, iElement, iAttrs, ctrl) {
        ctrl.init("<i class=\"fa fa-caret-down\"></i> " + (iAttrs.displayText || "See Details"), "<i class=\"fa fa-caret-up\"></i> " + (iAttrs.displayText || "Hide Details"))
        ctrl.toggleLink = iElement[0].querySelector(".toggle-link");
        if (iAttrs.itemType) {
            ctrl.itemType = iAttrs.itemType;
        }
        if (iAttrs.displayText) {
            scope.displayText = iAttrs.displayText;
        }
        scope.showType = "ALL";
        ctrl.linkVisibility();
    }

    function getTemplate(iElement, iAttrs) {
        if (iAttrs.itemType && iAttrs.itemType === "SESSION") {
            return "/partials/directives/session_collapsable.html";
        } else if (iAttrs.itemType && iAttrs.itemType === "CONFERENCE") {
            return "/partials/directives/conference_collapsable.html";
        } else {
            throw new Error('Error: Template not Defined for item type [' + iAttrs.itemType + "]");
        }
    }
};

function collapsableCtrl($scope) {
    var ctrl = this;
    ctrl.toggleLink = null
    ctrl.showDetails = false;
    ctrl.timeOut = null;
    ctrl.init = initFn;
    ctrl.toggleDetails = toggleDetails;
    ctrl.linkTextToggle = linkTextToggle;
    ctrl.showLink = showLink;
    ctrl.linkVisibility = linkVisibility;
    ctrl.displayTextShow = "<i class=\"fa fa-caret-down\"></i> Show Details";
    ctrl.displayTextHide = "<i class=\"fa fa-caret-up\"></i> Hide Details";

    function initFn(dispTextShow, dispTextHide) {
        ctrl.displayTextShow = dispTextShow;
        ctrl.displayTextHide = dispTextHide;
    };

    function toggleDetails() {
        ctrl.showDetails = !ctrl.showDetails;
        ctrl.linkTextToggle();
    };

    function linkTextToggle() {
        if (ctrl.showDetails) {
            ctrl.toggleLink.innerHTML = ctrl.displayTextHide;
        } else {
            ctrl.toggleLink.innerHTML = ctrl.displayTextShow;
        }
    };

    function showLink() {
        var result = false;
        if ($scope.showType === "ALL") {
            result = true;
        }
        return result;
    };

    function linkVisibility() {
        ctrl.showDetails = false;
        ctrl.linkTextToggle()

    };
};


function userNameDisplayDir() {
    var directive = {
        ristrict: "E",
        scope: {
            displayName: "="
        },
        replase: true,
        link: undLink,
        template: "<div class='user-name-display'><span class='user-name-circle' ng-bind='firstChar'></span><span class='user-name' ng-bind='displayName'></span></div>"


    };
    return directive;

    function undLink(scope, iElement, iAttrs, ctrl) {
        scope.getFirstChar = function() {
            if (scope.displayName) {
                scope.firstChar = scope.displayName.substr(0, 1).toUpperCase();
            }
        }
        scope.$watch('displayName', function(newVal, oldVal) {
            if (newVal !== oldVal) {
                scope.getFirstChar();
            }
        });
    }
}