# File: panorama_block_url.py
#
# Copyright (c) 2016-2023 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
import phantom.app as phantom
from phantom.action_result import ActionResult

import panorama_consts as consts
from actions import BaseAction


class BlockUrl(BaseAction):

    def _set_url_filtering(self, connector, action_result, url_prof_name):

        xpath = consts.URL_PROF_XPATH.format(
            config_xpath=connector.util._get_config_xpath(self._param),
            url_profile_name=url_prof_name
        )

        # For Panorama 8 and below, we can simply add the url to the block list of the URL filtering.

        if connector.util._get_pan_major_version() < 9:
            block_url = self._param[consts.PAN_JSON_URL]
            element = consts.URL_PROF_ELEM.format(url=block_url)
        else:
            element = consts.URL_PROF_ELEM_9.format(url_category_name=url_prof_name)

        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': xpath,
            'element': element
        }

        status, response = connector.util._make_rest_call(data, action_result)

        action_result.update_summary({ "set_url_filtering": response })

        return status

    def _block_url_8_and_below(self, connector, action_result):
        connector.debug_print("Adding the Block URL")

        url_prof_name = consts.BLOCK_URL_PROF_NAME.format(
            device_group=self._param[consts.PAN_JSON_DEVICE_GRP]
        )

        url_prof_name = url_prof_name[:consts.MAX_NODE_NAME_LEN].strip()

        status = self._set_url_filtering(connector, action_result, url_prof_name)

        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message())
            )

        message = action_result.get_message()

        if self._param.get("policy_name", ""):
            status = connector.util._update_security_policy(
                self._param, consts.SEC_POL_URL_TYPE,
                action_result, url_prof_name
            )

            if phantom.is_fail(status):
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message())
                )

        if self._param.get("should commit change", True):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(
            phantom.APP_SUCCESS, "Response Received: {}".format(message))

    def _block_url_9_and_above(self, connector, action_result):

        url_prof_name = consts.BLOCK_URL_PROF_NAME.format(device_group=self._param[consts.PAN_JSON_DEVICE_GRP])
        url_prof_name = url_prof_name[:consts.MAX_NODE_NAME_LEN].strip()

        status = connector.util._add_url_to_url_category(
            self._param, action_result, url_prof_name
        )

        if phantom.is_fail(status):
            error_message = consts.PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message())
            return action_result.set_status(phantom.APP_ERROR, error_message)

        status = self._set_url_filtering(connector, action_result, url_prof_name)
        if phantom.is_fail(status):
            error_message = consts.PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message())
            return action_result.set_status(phantom.APP_ERROR, error_message)

        # We need to capture the url filter message here before it gets updated below.
        url_filter_message = action_result.get_message()

        # Link the URL filtering profile to the given policy.
        if self._param.get("policy_name", ""):
            status = connector.util._update_security_policy(self._param, consts.SEC_POL_URL_TYPE, action_result, url_prof_name)
            if phantom.is_fail(status):
                error_message = consts.PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message())
                return action_result.set_status(phantom.APP_ERROR, error_message)

        if self._param.get('should_commit_changes', True):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(url_filter_message))

    def execute(self, connector):

        # making action result object
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        status = connector.util._load_pan_version(action_result)

        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message()))

        major_version = connector.util._get_pan_major_version()

        # if major_version < 9 :
        if major_version > 9:
            return self._block_url_8_and_below(connector, action_result)
        else:
            return self._block_url_9_and_above(connector, action_result)
