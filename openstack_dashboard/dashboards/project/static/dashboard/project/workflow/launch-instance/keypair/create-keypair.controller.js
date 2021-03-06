/*
 *    (c) Copyright 2015 Hewlett-Packard Development Company, L.P.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
  'use strict';

  angular
    .module('horizon.dashboard.project.workflow.launch-instance')
    .controller('LaunchInstanceCreateKeyPairController', LaunchInstanceCreateKeyPairController);

  LaunchInstanceCreateKeyPairController.$inject = [
    '$modalInstance',
    'horizon.app.core.openstack-service-api.nova',
    'horizon.framework.widgets.toast.service'
  ];

  /**
   * @ngdoc controller
   * @name horizon.dashboard.project.workflow.launch-instance.LaunchInstanceCreateKeyPairController
   * @description
   * Provide a dialog for creation of a new key pair.
   */
  function LaunchInstanceCreateKeyPairController($modalInstance, novaAPI, toastService) {
    var ctrl = this;

    ctrl.submit = submit;
    ctrl.cancel = cancel;

    ctrl.labels = {
      wizardTitle: gettext('Launch Instance'),
      title: gettext('Create Key Pair'),
      /*eslint-disable max-len */
      help: gettext('Key Pairs are how you login to your instance after it is launched. Choose a key pair name you will recognize.'),
      /*eslint-enable max-len */
      keyPairName: gettext('Key Pair Name'),
      cancel: gettext('Cancel'),
      ok: gettext('Create Key Pair'),
      required: gettext('Required')
    };

    ctrl.model = { name: '' };

    //////////

    function submit() {
      novaAPI.createKeypair(ctrl.model).success(successCallback);
    }

    function successCallback(data) {
      $modalInstance.close(data);

      var successMsg = gettext('Successfully created key pair %(name)s.');
      toastService.add('success', interpolate(successMsg, { name: data.name }, true));
    }

    function cancel() {
      $modalInstance.dismiss();
    }
  }

})();
