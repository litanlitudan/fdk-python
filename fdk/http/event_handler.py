# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import h11

from fdk import context
from fdk import constants
from fdk import log
from fdk import response
from fdk import runner

from fdk.http import routine


def event_handle(handle_code):
    async def pure_handler(request_reader, response_writer):
        log.log("in pure_handler")
        connection = h11.Connection(h11.SERVER)
        try:
            request, body = await routine.read_request(
                connection, request_reader)
            headers = dict(request.headers)

            func_response = await runner.handle_request(
                handle_code, constants.HTTPSTREAM,
                headers=headers, data=body)
            log.log("request execution completed")

            await routine.write_response(
                connection, func_response, response_writer)
        except Exception as ex:
            ctx, _ = context.context_from_format(
                constants.HTTPSTREAM, headers={}, data=None)
            await routine.write_response(connection, response.Response(
                ctx,
                response_data=str(ex),
                headers={
                    constants.CONTENT_TYPE: "text/plain",
                    constants.CONTENT_LENGTH: len(str(ex))
                },
                status_code=502
            ), response_writer)

    return pure_handler
