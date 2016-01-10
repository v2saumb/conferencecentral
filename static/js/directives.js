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

function confSessionDir() {
    var dir = {
        restrict: 'E',
        scope: {
            sessions: '=',
            showConfName: '@'
        },
        replace: true,
        templateUrl: "/partials/directives/conf-sessions.html",
        link: confSessionLink

    };
    return dir;

    function confSessionLink(scope, iElement, iAttrs) {
        scope.filterText = "";
    }
}