#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import project_settings


class DefaultConfig(object):
    """ Bot Configuration """

    PORT = project_settings.MS_BOT_PORT
    APP_ID = project_settings.MicrosoftAppId
    APP_PASSWORD = project_settings.MicrosoftAppPassword
    CONNECTION_NAME = project_settings.ConnectionName
    BLOB_CONNECTION_STRING = project_settings.AZURE_STORAGE_CONNECTION_STRING
    BLOB_CONTAINER_NAME = project_settings.AZURE_BLOB_CONTAINER_NAME
