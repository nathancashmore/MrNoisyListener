# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper functions for the Google Assistant API."""

import logging
import sys
import json
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'

def log_assist_request_without_audio(assist_request):
    """Log AssistRequest fields without audio data."""
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        resp_copy = embedded_assistant_pb2.AssistRequest()
        resp_copy.CopyFrom(assist_request)
        if len(resp_copy.audio_in) > 0:
            size = len(resp_copy.audio_in)
            resp_copy.ClearField('audio_in')
            logging.debug('AssistRequest: audio_in (%d bytes)',
                          size)
            return
        logging.debug('AssistRequest: %s', resp_copy)


def log_assist_response_without_audio(assist_response):
    """Log AssistResponse fields without audio data."""
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        resp_copy = embedded_assistant_pb2.AssistResponse()
        resp_copy.CopyFrom(assist_response)
        has_audio_data = (resp_copy.HasField('audio_out') and
                          len(resp_copy.audio_out.audio_data) > 0)
        if has_audio_data:
            size = len(resp_copy.audio_out.audio_data)
            resp_copy.audio_out.ClearField('audio_data')
            if resp_copy.audio_out.ListFields():
                logging.debug('AssistResponse: %s audio_data (%d bytes)',
                              resp_copy,
                              size)
            else:
                logging.debug('AssistResponse: audio_data (%d bytes)',
                              size)
            return
        logging.debug('AssistResponse: %s', resp_copy)


def open_channel(credentials):
    # Load OAuth 2.0 credentials.
    try:
        with open(credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        sys.exit(-1)

    # Create an authorized gRPC channel.
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, ASSISTANT_API_ENDPOINT)
    logging.info('Connecting to %s', ASSISTANT_API_ENDPOINT)

    return grpc_channel
