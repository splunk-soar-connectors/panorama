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


class CreatePolicyRule(BaseAction):

    def execute(self):
        
        print("hello")
