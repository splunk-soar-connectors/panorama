# File: panorama_move_policy.py
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

from actions import BaseAction
from panorama_consts import (PAN_ERROR_MESSAGE, PAN_JSON_DEVICE_GRP, PAN_JSON_DST, PAN_JSON_POLICY_NAME, PAN_JSON_POLICY_TYPE, PAN_JSON_WHERE,
                             POLICY_TYPE_VALUE_LIST, VALUE_LIST_VALIDATION_MESSAGE)


class MovePolicy(BaseAction):

    def execute(self, connector):

        connector.debug_print("Inside Move policy action")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        policy_name = self._param[PAN_JSON_POLICY_NAME]
        policy_list = policy_name.split(",")
        policy_list = [value.strip() for value in policy_list if value.strip(" ,")]
        dst_device_group = self._param.get("dst_device_group", None)
        curr_device_group = self._param[PAN_JSON_DEVICE_GRP]
        curr_pre_post = self._param[PAN_JSON_POLICY_TYPE]
        dst_pre_post = self._param.get("dst_policy_type", None)
        where = self._param.get(PAN_JSON_WHERE, None)
        dst = self._param.get(PAN_JSON_DST, None)

        # validate policy type
        if curr_pre_post not in POLICY_TYPE_VALUE_LIST:
            return action_result.set_status(
                phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(POLICY_TYPE_VALUE_LIST, PAN_JSON_POLICY_TYPE)
            )

        if dst_pre_post and dst_pre_post not in POLICY_TYPE_VALUE_LIST:
            return action_result.set_status(
                phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(POLICY_TYPE_VALUE_LIST, "dst_pre_post")
            )

        if dst_pre_post and not dst_device_group:
            dst_device_group = curr_device_group
        elif not dst_pre_post and dst_device_group:
            dst_pre_post = curr_pre_post

        if not where and not dst_pre_post and not dst_device_group:
            return action_result.set_status(phantom.APP_ERROR, "either 'where' or 'dst_device group' or 'dst_pre_post' is required.")

        if where in ["before", "after"] and not dst:
            return action_result.set_status(phantom.APP_ERROR, "dst is a required parameter for the entered value of \"where\"")

        status, policies = connector.util._element_prep(param_name="policy_name", param_val=policy_name, member=True)
        connector.debug_print(f"policies {policies}")

        data = {
            'type': 'config',
            'key': connector.util._key,
        }

        if dst_device_group or dst_pre_post:
            param = {
                PAN_JSON_DEVICE_GRP: dst_device_group
            }
            config_path = connector.util._get_config_xpath(param, 'localhost.localdomain')
            xpath = f"{config_path}/{dst_pre_post}/security/rules"
            param[f"{PAN_JSON_DEVICE_GRP}"] = curr_device_group
            config_path = connector.util._get_config_xpath(param, 'localhost.localdomain')
            element = f'<selected-list><source xpath="{config_path}/{curr_pre_post}/security/rules">\
                {policies}</source></selected-list><all-errors>no</all-errors>'
            data.update(
                {
                    'action': 'multi-move',
                    'xpath': xpath,
                    'element': element
                }
            )
        else:
            if len(policy_list) > 1:
                return action_result.set_status(phantom.APP_ERROR, "Moving multiple policies at a time is only possible if they have \
                                                to be moved to a different device group or rule base")
            param = {
                PAN_JSON_DEVICE_GRP: curr_device_group,
                PAN_JSON_POLICY_NAME: policy_name,
                PAN_JSON_POLICY_TYPE: curr_pre_post
            }
            xpath = f"{connector.util._get_security_policy_xpath(param,action_result)[1]}"

            data.update(
                {
                    'action': 'move',
                    'where': where,
                    'dst': dst,
                    'xpath': xpath
                }
            )
        status, response = connector.util._make_rest_call(data, action_result)
        action_result.add_data(response)
        message = action_result.get_message()
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred: ", {message}))
        if self._param.get('should_commit_changes', False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Successfully moved policy")
