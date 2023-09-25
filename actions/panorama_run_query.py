# File: panorama_run_query.py
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
import time

import phantom.app as phantom
from phantom.action_result import ActionResult

import panorama_consts as consts
from actions import BaseAction


class RunQuery(BaseAction):

    def execute(self, connector):

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        query = self._param[consts.PAN_JSON_QUERY]
        log_type = self._param.get(consts.PAN_JSON_LOG_TYPE, "traffic")

        if log_type not in consts.LOG_TYPE_VALUE_LIST:
            return action_result.set_status(
                phantom.APP_ERROR, consts.VALUE_LIST_VALIDATION_MESSAGE.format(consts.LOG_TYPE_VALUE_LIST, "log_type")
            )

        offset_range = self._param.get("range", "1-{0}".format(consts.MAX_QUERY_COUNT))

        spl_range = offset_range.split("-")

        try:
            min_offset = int(spl_range[0].strip())
            max_offset = int(spl_range[1].strip())
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Given range has a bad format: {0}".format(connector.util._get_error_message_from_exception(e))
            )
        offset_diff = max_offset - min_offset + 1

        if max_offset < min_offset:
            return action_result.set_status(
                phantom.APP_ERROR, "The given range appears to have a larger number listed first."
            )

        if min_offset <= 0:
            return action_result.set_status(
                phantom.APP_ERROR, "The lower end of the range must be greater than zero (indexing starts at 1)"
            )

        if offset_diff > consts.MAX_QUERY_COUNT:
            return action_result.set_status(
                phantom.APP_ERROR, "The given range is too large. Maximum range is {0}.".format(consts.MAX_QUERY_COUNT)
            )

        direction = self._param.get("direction", "backward")
        if direction not in consts.DIRECTION_VALUE_LIST:
            return action_result.set_status(
                phantom.APP_ERROR, consts.VALUE_LIST_VALIDATION_MESSAGE.format(consts.DIRECTION_VALUE_LIST, "direction")
            )

        data = {
            "type": "log",
            "log-type": log_type,
            "key": connector.util._key,
            "query": query,
            "skip": min_offset - 1,
            "nlogs": offset_diff,
            "dir": direction
        }

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.update_summary({"run_query": response})

        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("running query", action_result.get_message()))

        # Get the job id of the query call from the result_data, also pop it since we don't need it
        # to be in the action result
        result_data = action_result.get_data()

        if len(result_data) == 0:
            return action_result.set_status(phantom.APP_ERROR, "Error occurred while processing response. Details: {}".format(
                action_result.get_message()))

        result_data = result_data.pop(0)
        job_id = result_data.get("job")

        if not job_id:
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_NO_JOB_ID)

        connector.debug_print("query job ID: ", job_id)

        data = {
            "type": "op",
            "key": connector.util._key,
            "cmd": "<show><query><result><id>{job}</id></result></query></show>".format(job=job_id)
        }

        while True:

            status_action_result = ActionResult()

            status, _ = connector.util._make_rest_call(data, status_action_result)

            if phantom.is_fail(status):
                action_result.set_status(phantom.APP_ERROR, "Error occurred while processing response. Details: {}".format(
                    status_action_result.get_message()))
                return action_result.get_status()

            connector.debug_print("status", status_action_result)

            # get the result_data and the job status
            result_data = status_action_result.get_data()[0]
            job = result_data.get("job")
            if not job_id:
                continue

            if job.get("status", "") == "FIN":
                if isinstance(result_data.get("log").get("logs").get("entry"), dict):
                    result_data["log"]["logs"]["entry"] = [result_data["log"]["logs"]["entry"]]
                action_result.add_data(result_data)
                action_result.update_summary({'finished_job': job})
                break

            # send the % progress
            connector.send_progress(consts.PAN_PROG_COMMIT_PROGRESS, progress=job.get('progress'))

            time.sleep(2)

        try:
            action_result.update_summary({'num_logs': int(result_data['log']['logs']['@count'])})
        except:
            pass

        return phantom.APP_SUCCESS
