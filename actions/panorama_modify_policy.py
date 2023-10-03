# File: panorama_modify_policy.py
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

from actions import BaseAction
from actions.panorama_create_policy import CreatePolicy


class ModifyPolicy(BaseAction):

    def execute(self, connector):

        connector.debug_print("Inside Modify policy action")

        policy_rule_obj = CreatePolicy(self._param)
        response = policy_rule_obj.execute(connector)

        return response
