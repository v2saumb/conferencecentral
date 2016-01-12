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
conferenceApp.directives = angular.module('conferenceDirectives', ['ui.bootstrap']);

conferenceApp.directives.directive('conferenceSessions', confSessionDir);
confSessionCtrl.$inject = ['$rootScope', '$scope']

conferenceApp.directives.directive('collapsibleItemDetails', collapsibleItemDetails);
collapsibleItemDetails.$inject = ['$timeout'];
collapsableCtrl.$inject = ['$scope']

function confSessionDir() {
    var dir = {
        restrict: 'E',
        scope: {
            sessions: '=',
            showConfName: '@',
            showAddRemove: '@'
        },
        replace: true,
        templateUrl: "/partials/directives/conf-sessions.html",
        link: confSessionLink,
        controller: confSessionCtrl,
        controllerAs: 'csCtrl'

    };
    return dir;

    function confSessionLink(scope, iElement, iAttrs) {}
}

function confSessionCtrl($rootScope, $scope) {
    $scope.filterText = "";
    var vm = this;
    vm.addSessionToWishlist = function(wssk) {
        vm.loading = true;
        gapi.client.conference.addSessionToWishlist({
            websafeKey: wssk
        }).
        execute(function(resp) {
            $scope.$apply(function() {
                vm.loading = false;
                if (resp.error) {
                    if (resp.code && resp.code == 409) {
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Error:' + errorMessage;
                        $scope.alertStatus = 'warning';
                    }
                } else {
                    /*if (resp.result.items && resp.result.items.length > 0) {
                        $scope.submitted = false;
                        vm.speakerExists = true;
                        vm.sessions = resp.result.items;
                    } else {
                        $scope.messages = 'No Records Found!';
                        $scope.alertStatus = 'warning';
                        
                    }*/
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