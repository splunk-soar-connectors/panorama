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

import panorama_consts as consts
from actions import BaseAction

class BlockUrl(BaseAction):

    def _set_url_filtering(self, url_prof_name):

        xpath = consts.URL_PROF_XPATH.format(
            config_xpath = self._connector.util._get_config_xpath(self._param),
            url_profile_name = url_prof_name
        )

        # For Panorama 8 and below, we can simply add the url to the block list of the URL filtering.

        if self._connector.util._get_pan_major_version() < 9:
            block_url = self._param[consts.PAN_JSON_URL]
            element = consts.URL_PROF_ELEM.format(url=block_url)
        else:
            element = consts.URL_PROF_ELEM_9.format(url_category_name=url_prof_name)

        data = {
            'type': 'config',
            'action': 'set',
            'key': self._connector.util._key,
            'xpath': xpath,
            'element': element
        }

        status, response = self._connector.util._make_rest_call(data, self._action_result)
        
        self._action_result.update_summary({ "set_url_filtering" : response })
        
        return status

    def _block_url_8_and_below(self):
        self._connector.debug_print("Adding the Block URL")

        url_prof_name = consts.BLOCK_URL_PROF_NAME.format(
            device_group = self._param[consts.PAN_JSON_DEVICE_GRP]
        )

        url_prof_name = url_prof_name[:consts.MAX_NODE_NAME_LEN].strip()

        status = self._set_url_filtering(url_prof_name)

        if phantom.is_fail(status):
            return self._action_result.set_status(
                phantom.APP_ERROR, 
                consts.PAN_ERROR_MESSAGE.format("blocking url", self._action_result.get_message())
            )
        
        message =  self._action_result.get_message()

        if self._param.get("policy_name",""):
            status = self._connector.util._update_security_policy(
                self._param, consts.SEC_POL_URL_TYPE,
                self._action_result, url_prof_name
            )

            if phantom.is_fail(status):
                return self._action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format("blocking url", self._action_result.get_message())
                )
        
        if self._param.get("should commit change", True):
            status =  self._connector.util._commit_and_commit_all(self._param, self._action_result)
            if phantom.is_fail(status):
                return self._action_result.get_status()
        
        return self._action_result.set_status(
            phantom.APP_SUCCESS, "Response Received: {}".format(message))
        

    def _block_url_9_and_above(self):
        
        url_prof_name = consts.BLOCK_URL_PROF_NAME.format(device_group=self._param[consts.PAN_JSON_DEVICE_GRP])
        url_prof_name = url_prof_name[:consts.MAX_NODE_NAME_LEN].strip()

        status = self._connector.util._add_url_to_url_category(
            self._param, 
            self._action_result, url_prof_name
        )

        if phantom.is_fail(status):
            error_message = consts.PAN_ERROR_MESSAGE.format("blocking url", self._action_result.get_message())
            return self._action_result.set_status(phantom.APP_ERROR, error_message)

        status = self._set_url_filtering(url_prof_name)
        if phantom.is_fail(status):
            error_message = consts.PAN_ERROR_MESSAGE.format("blocking url", self._action_result.get_message())
            return self._action_result.set_status(phantom.APP_ERROR, error_message)

        # We need to capture the url filter message here before it gets updated below.
        url_filter_message = self._action_result.get_message()

        # Link the URL filtering profile to the given policy.
        if self._param.get("policy_name", ""):
            status = self._connector.util._update_security_policy(self._param, consts.SEC_POL_URL_TYPE, self._action_result, url_prof_name)
            if phantom.is_fail(status):
                error_message = consts.PAN_ERROR_MESSAGE.format("blocking url", self._action_result.get_message())
                return self._action_result.set_status(phantom.APP_ERROR, error_message)

        if self._param.get('should_commit_changes', True):
            status = self._connector.util._commit_and_commit_all(self._param, self._action_result)
            if phantom.is_fail(status):
                return self._action_result.get_status()

        return self._action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(url_filter_message))
    

    def execute(self):
    
        status = self._connector.util._load_pan_version(self._action_result)

        if phantom.is_fail(status):
            return self._action_result.set_status(
                phantom.APP_ERROR, 
                consts.PAN_ERROR_MESSAGE.format("blocking url", self._action_result.get_message()))

        major_version = self._connector.util._get_pan_major_version()

        # if major_version < 9 :
        if major_version > 9: 
            return self._block_url_8_and_below()
        else:
            return self._block_url_9_and_above()
