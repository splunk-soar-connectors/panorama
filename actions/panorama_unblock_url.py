# File: panorama_unblock_url.py
#
# Copyright (c) 2016-2025 Splunk Inc.
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

from actions import BaseAction
from panorama_consts import (
    BLOCK_URL_PROF_NAME,
    DEL_URL_CATEGORY_XPATH,
    DEL_URL_XPATH,
    MAX_NODE_NAME_LEN,
    PAN_ERROR_MESSAGE,
    PAN_JSON_DEVICE_GRP,
    PAN_JSON_URL,
    URL_CATEGORY_XPATH,
    URL_PROF_XPATH,
)


class UnblockUrl(BaseAction):
    def _unblock_url_8_and_below(self, connector, action_result):
        # Add the block url, will create the url profile if not present
        block_url = self._param[PAN_JSON_URL]
        url_prof_name = BLOCK_URL_PROF_NAME.format(device_group=self._param[PAN_JSON_DEVICE_GRP])
        url_prof_name = url_prof_name[:MAX_NODE_NAME_LEN].strip()

        # Remove the given url from UrlFiltering > Profile > BlockList
        xpath = f"{URL_PROF_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), url_profile_name=url_prof_name)}{DEL_URL_XPATH.format(url=block_url)}"

        data = {"type": "config", "action": "delete", "key": connector.util._key, "xpath": xpath}

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.update_summary({"delete_url_from_block_list": response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("unblocking url", action_result.get_message()))

        url_category_del_message = action_result.get_message()

        if self._param.get("should_commit_changes", False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Response Received: {url_category_del_message}")

    def _unblock_url_9_and_above(self, connector, action_result):
        # Add the block url, will create the url profile if not present
        block_url = self._param[PAN_JSON_URL]
        url_prof_name = BLOCK_URL_PROF_NAME.format(device_group=self._param[PAN_JSON_DEVICE_GRP])
        url_prof_name = url_prof_name[:MAX_NODE_NAME_LEN].strip()

        # Remove url from Objects -> Custom Objects -> URL Category
        xpath = f"{URL_CATEGORY_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), url_profile_name=url_prof_name)}{DEL_URL_CATEGORY_XPATH.format(url=block_url)}"
        data = {"type": "config", "action": "delete", "key": connector.util._key, "xpath": xpath}

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.update_summary({"delete_url_from_url_category": response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("unblocking url", action_result.get_message()))

        block_list_del_message = action_result.get_message()

        if self._param.get("should_commit_changes", False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Response Received: {block_list_del_message}")

    def execute(self, connector):
        connector.debug_print("Removing the Blocked URL")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        status = connector.util._load_pan_version(action_result)
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message()))

        connector.debug_print("Getting major version of panorama")
        major_version = connector.util._get_pan_major_version()
        if major_version < 9:
            return self._unblock_url_8_and_below(connector, action_result)

        return self._unblock_url_9_and_above(connector, action_result)
