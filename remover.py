import asyncio
import json
import pickle
import time
from datetime import datetime
from http import HTTPStatus
from typing import List, Tuple

import requests
from aioredis import Redis
from botbuilder.core import MessageFactory
from botbuilder.schema import ErrorResponseException

import project_settings
from helpers.ping_helper import ping_file_clear_old_lines
from lib.email_helpers import send_mail
from lib.logger import CustomLogger
from helpers.hero_card_helper import create_hero_card
from lib.storage_blob_helper import rm_blobs
from setup.aioredis_client import get_redis_client
from setup.db import get_db_cursor, connection_string
from setup.standalone_bot_adapter import ADAPTER, APP_ID

LOGGING_INTERVAL = 60 * 5  # sec
logger = CustomLogger.get_logger('flask')


async def exclude_employee_if_bot_banned(member_id):
    sql_user_suspended = """UPDATE customers
                                SET member_id = NULL,
                                    conversation_reference = NULL,
                                    operator_displayName = 'user was suspended' 
                                WHERE member_id = ?"""

    sql_user_fired = """UPDATE customers
                                SET member_id = NULL,
                                    conversation_reference = NULL,
                                    operator_displayName = 'user was suspended' 
                                WHERE member_id = ?"""
    with get_db_cursor() as cur:
        try:
            cur.execute(sql_update, member_id)
        except Exception:
            logger.exception('DB ERROR WHILE EXCLUDE USER FROM BROADCAST')

        logger.debug('User: %s excluded from broadcast', member_id)


async def send_message():
    sql_select = """WITH num_row AS (SELECT row_number() OVER (ORDER BY id) AS nom, * FROM customers 
                                     WHERE id = 0)
                         SELECT aoem.member_id AS member_id,
                                aoem.conversation_reference AS conversation_reference,
                                aoem.operator_displayName AS operator_displayName
                         FROM num_row aoem
                         WHERE nom BETWEEN (? - ?) AND ?"""

    cursor = 100
    limit = 100

    while 1:
        logger.debug('Try select customers from db')
        with get_db_cursor() as cur:
            try:
                cur.execute(sql_select, cursor, limit, cursor)
                db_result = cur.fetchall()
            except Exception:
                logger.exception('DB ERROR')
                await asyncio.sleep(10)
                continue

        if not db_result:
            logger.debug('No result. Finish')
            break
        logger.debug('Try to get user status from AD')
        try:
            # success_ids = await send_message_to_tg(db_result)
            logger.debug('!!! >>> Messages was send to : %s', success_ids)

        except Exception:
            logger.exception('send_message_to_tg error')
            success_ids = None

        if not success_ids:
            logger.warning('send_message_to_tg WARNING')
            await asyncio.sleep(10)
            continue

        placeholders = ', '.join(['?'] * len(success_ids))
        sql_update = """UPDATE customers
                        SET is_current_state_message_send = 1,
                            is_current_state_reply_received = 0
                        WHERE member_id IN (""" + placeholders + ")"
        with get_db_cursor() as cur:
            try:
                cur.execute(sql_update, success_ids)
                logger.debug('Db updated for: %s', success_ids)

            except Exception:
                logger.exception('DB ERROR')
                await asyncio.sleep(5)
                continue

        cursor += limit + 1
        await asyncio.sleep(60)

async def blob_remover_worker(redis_cli: Redis):
    logger.warning('Starting blob_remover_worker')
    last_logging_time = time.time()
    last_health_time = time.time()

    while 1:
        if time.time() - last_logging_time > LOGGING_INTERVAL:
            logger.info('Blob_remover_worker waiting the trigger time')
            last_logging_time = time.time()

        if time.time() - last_health_time > 30:
            await redis_cli.set(project_settings.REDIS_DIRECT_MESSAGE_WORKER_HEALTH_CHECK_KEY, 1)
            await redis_cli.expire(project_settings.REDIS_DIRECT_MESSAGE_WORKER_HEALTH_CHECK_KEY, 60)
            last_health_time = time.time()

        time_now = datetime.utcnow().replace(microsecond=0)
        hour_now = time_now.hour
        time_trigger = 1 <= hour_now < 2
        minute_now = time_now.minute
        minute_trigger = 10 <= minute_now < 12

        if time_trigger and minute_trigger:
            logger.info('All triggers are true, removing all blobs')
            try:
                rm_blobs()
            except Exception:
                logger.exception('Error while deleting blobs')
                await asyncio.sleep(5)
                continue
        await asyncio.sleep(10)
