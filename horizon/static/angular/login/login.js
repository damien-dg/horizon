/**
 * Copyright 2015 IBM Corp.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */
(function() {
  'use strict';

  angular.module('hz')

    /**
     * @ngdoc hzLoginCtrl
     * @description
     * controller for determining which
     * authentication method user picked.
     */
    .controller('hzLoginCtrl', function($scope, modals) {
      $scope.auth_type = 'credentials';
      $scope.ueseless_variable = 'test';
      $scope.alertNothing = function(){
        //window.alert('thuy anh wuz here');
        // The .open() method returns a promise that will be either
        // resolved or rejected when the modal window is closed.
                    var promise = modals.open(
                        "alert",
                        {
                            message: "I think you are kind of beautiful!"
                        }
                    );
                    promise.then(
                        function handleResolve( response ) {
                            console.log( "Alert resolved." );
                        },
                        function handleReject( error ) {
                            console.warn( "Alert rejected!" );
                        }
                    );
                };
              }
              );
    angular.module('hz').controller('AlertModalController', function($scope, modals){
       $scope.message = ( modals.params().message || "Whoa!" );
                // ---
                // PUBLIC METHODS.
                // ---
                // Wire the modal buttons into modal resolution actions.
                $scope.close = modals.resolve;

    });

    angular.module('hz').service('modals', modals);
    modals.$inject=['$rootScope', '$q'];
    
            function modals( $rootScope, $q ) {
                // I represent the currently active modal window instance.
                var modal = {
                    deferred: null,
                    params: null
                };
                // Return the public API.
                return({
                    open: open,
                    params: params,
                    proceedTo: proceedTo,
                    reject: reject,
                    resolve: resolve
                });

                  function open( type, params, pipeResponse ) {
                    var previousDeferred = modal.deferred;
                    // Setup the new modal instance properties.
                    modal.deferred = $q.defer();
                    modal.params = params;
                    // We're going to pipe the new window response into the previous
                    // window's deferred value.
                    if ( previousDeferred && pipeResponse ) {
                        modal.deferred.promise
                            .then( previousDeferred.resolve, previousDeferred.reject )
                        ;
                    // We're not going to pipe, so immediately reject the current window.
                    } else if ( previousDeferred ) {
                        previousDeferred.reject();
                    }
                    // Since the service object doesn't (and shouldn't) have any direct
                    // reference to the DOM, we are going to use events to communicate
                    // with a directive that will help manage the DOM elements that
                    // render the modal windows.
                    // --
                    // NOTE: We could have accomplished this with a $watch() binding in
                    // the directive; but, that would have been a poor choice since it
                    // would require a chronic watching of acute application events.
                    $rootScope.$emit( "modals.open", type );
                    return( modal.deferred.promise );
                };

    /**
     * @ngdoc hzLoginFinder
     * @description
     * A directive to show or hide inputs and help text
     * based on which authentication method the user selected.
     * Since HTML is generated server-side via Django form,
     * this directive is the hook to make it more dynamic.
     * Only visible if websso is enabled.
     */
    angular.module('hz').directive('hzLoginFinder', function($timeout) {
      return {
        restrict: 'A',
        link: function(scope, element) {

          // test code does not have access to document
          // so we are restricted to search through the element
          var authType = element.find('#id_auth_type');
          var userInput = element.find("#id_username").parents('.form-group');
          var passwordInput = element.find("#id_password").parents('.form-group');
          var domainInput = element.find('#id_domain').parents('form-group');
          var regionInput = element.find('#id_region').parents('form-group');

          // helptext exists outside of element
          // we have to traverse one node up
          var helpText = element.parent().find('#help_text');
          helpText.hide();

          // update the visuals
          // when user selects item from dropdown
          function onChange(e) {
            $timeout(function() {

              // if type is credential
              // show the username and password fields
              // and domain and region if applicable
              scope.auth_type = authType.val();
              switch(scope.auth_type) {
                case 'credentials':
                  userInput.show();
                  passwordInput.show();
                  domainInput.show();
                  regionInput.show();
                  break;
                default:
                  userInput.hide();
                  passwordInput.hide();
                  domainInput.hide();
                  regionInput.hide();
              }

            }); // end of timeout
          } // end of onChange

          // if authType field exists
          // then websso was enabled
          if (authType.length > 0) {

            // programmatically insert help text after dropdown
            // this is the only way to do it since template is
            // generated server side via form_fields
            authType.after(helpText);
            helpText.show();

            // trigger the onChange on first load
            // so that initial choice is auto-selected
            onChange();
            authType.change(onChange);
          }

        } // end of link
      }; // end of return
    }); // end of directive

angular.module('hz').directive('bnModals', function($rootScope, modals){
  return( link );
                // I bind the JavaScript events to the scope.
                function link( scope, element, attributes ) {
                    // I define which modal window is being rendered. By convention,
                    // the subview will be the same as the type emitted by the modals
                    // service object.
                    scope.subview = null;
                    // If the user clicks directly on the backdrop (ie, the modals
                    // container), consider that an escape out of the modal, and reject
                    // it implicitly.
                    element.on(
                        "click",
                        function handleClickEvent( event ) {
                            if ( element[ 0 ] !== event.target ) {
                                return;
                            }
                            scope.$apply( modals.reject );
                        }
                    );
                    // Listen for "open" events emitted by the modals service object.
                    $rootScope.$on(
                        "modals.open",
                        function handleModalOpenEvent( event, modalType ) {
                            scope.subview = modalType;
                        }
                    );
                    // Listen for "close" events emitted by the modals service object.
                    $rootScope.$on(
                        "modals.close",
                        function handleModalCloseEvent( event ) {
                            scope.subview = null;
                        }
                    );
                }
}

);
});