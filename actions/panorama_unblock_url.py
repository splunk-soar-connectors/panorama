# File: panorama_.py
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

from panorama_consts import PAN_ERROR_MESSAGE, DEL_URL_CATEGORY_XPATH, URL_CATEGORY_XPATH, MAX_NODE_NAME_LEN, PAN_JSON_DEVICE_GRP, BLOCK_URL_PROF_NAME, PAN_JSON_URL, DEL_URL_XPATH, URL_PROF_XPATH
from actions import BaseAction


class UnblockUrl(BaseAction):

    def _unblock_url_8_and_below(self):

        # Add the block url, will create the url profile if not present
        block_url = self._param[PAN_JSON_URL]
        url_prof_name = BLOCK_URL_PROF_NAME.format(device_group=self._param[PAN_JSON_DEVICE_GRP])
        url_prof_name = url_prof_name[:MAX_NODE_NAME_LEN].strip()

        # Remove the given url from UrlFiltering > Profile > BlockList
        xpath = "{0}{1}".format(
            URL_PROF_XPATH.format(config_xpath=self._connector.util._get_config_xpath(self._param), url_profile_name=url_prof_name),
            DEL_URL_XPATH.format(url=block_url))
        
        data = {'type': 'config',
                'action': 'delete',
                'key': self._connector.util._key,
                'xpath': xpath}

        status, response = self._connector.util._make_rest_call(data, self._action_result)
        self._action_result.update_summary({'delete_url_from_block_list': response})
        if phantom.is_fail(status):
            return self._action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("unblocking url", self._action_result.get_message()))

        url_category_del_message = self._action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = self._connector.util._commit_and_commit_all(self._param, self._action_result)
            if phantom.is_fail(status):
                return self._action_result.get_status()

        return self._action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(url_category_del_message))

    def _unblock_url_9_and_above(self):

        # Add the block url, will create the url profile if not present
        block_url = self._param[PAN_JSON_URL]
        url_prof_name = BLOCK_URL_PROF_NAME.format(
            device_group=self._param[PAN_JSON_DEVICE_GRP])
        url_prof_name = url_prof_name[:MAX_NODE_NAME_LEN].strip()

        # Remove url from Objects -> Custom Objects -> URL Category
        xpath = "{0}{1}".format(
            URL_CATEGORY_XPATH.format(config_xpath=self._connector.util._get_config_xpath(self._param), url_profile_name=url_prof_name),
            DEL_URL_CATEGORY_XPATH.format(url=block_url))
        data = {'type': 'config',
                'action': 'delete',
                'key': self._connector.util._key,
                'xpath': xpath}

        status, response = self._connector.util._make_rest_call(data, self._action_result)
        self._action_result.update_summary({'delete_url_from_url_category': response})
        if phantom.is_fail(status):
            return self._action_result.set_status(
                phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("unblocking url", self._action_result.get_message()))

        block_list_del_message = self._action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = self._connector.util._commit_and_commit_all(self._param, self._action_result)
            if phantom.is_fail(status):
                return self._action_result.get_status()

        return self._action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(block_list_del_message))

    def execute(self):

        self._connector.debug_print("Removing the Blocked URL")

        status = self._connector.util._load_pan_version(self._action_result)
        if phantom.is_fail(status):
            return self._action_result.set_status(
                phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("blocking url", self._action_result.get_message()))

        major_version = self._connector.util._get_pan_major_version()
        if major_version < 9:
            return self._unblock_url_8_and_below()

        return self._unblock_url_9_and_above()