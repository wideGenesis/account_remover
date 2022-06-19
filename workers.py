import asyncio
import json
import pickle
import time
from datetime import datetime
from typing import List, Tuple

import requests
import uvloop
from aioredis import Redis
from botbuilder.core import MessageFactory
from botbuilder.schema import ErrorResponseException

import project_settings
from graph.graph_async_client import get_user
from helpers.ping_helper import ping_file_clear_old_lines
from lib.email_helpers import send_mail
from lib.logger import CustomLogger
from helpers.hero_card_helper import create_hero_card
from lib.storage_blob_helper import rm_blobs
from setup.aioredis_client import get_redis_client
from setup.db import get_db_cursor, connection_string
from setup.standalone_bot_adapter import ADAPTER, APP_ID

LOGGING_INTERVAL = 60 * 5  # sec
logger = CustomLogger.get_logger('flask')  #TODO ! FastApi


async def exclude_employee_if_bot_banned(member_id):
    sql_update = """UPDATE customers
                                SET member_id = NULL,
                                    conversation_reference = NULL,
                                    operator_displayName = 'bot was banned' 
                                WHERE member_id = ?"""
    with get_db_cursor() as cur:
        try:
            cur.execute(sql_update, member_id)
        except Exception:
            logger.exception('DB ERROR WHILE EXCLUDE USER FROM BROADCAST')

        logger.debug('User: %s excluded from broadcast', member_id)


async def send_message_to_tg(member_list: List[Tuple[str, bytes]]) -> List[str]:
    success_ids = []
    safety_message = MessageFactory.attachment(create_hero_card())
    for member_id, conversation_reference in member_list:
        # logger.debug('Customers for message_send: %s', member_list)

        try:
            await ADAPTER.continue_conversation(
                pickle.loads(conversation_reference),
                lambda turn_context: turn_context.send_activity(safety_message),
                APP_ID
            )
            logger.info('Message was sent to ADAPTER user %s', member_id)
            success_ids.append(member_id)
        except ErrorResponseException:
            logger.warning('ADAPTER -> Error response code. User: %s', member_id)
            await exclude_employee_if_bot_banned(member_id)
            continue
        except Exception:
            logger.exception('ADAPTER -> Send message error. User: %s', member_id)
            continue

        await asyncio.sleep(5)

    return success_ids


async def send_message():
    sql_select = """WITH num_row AS (SELECT row_number() OVER (ORDER BY id) AS nom, * FROM customers 
                                     WHERE is_current_state_message_send = 0
                                     AND member_id IS NOT NULL)
                         SELECT aoem.member_id AS member_id,
                                aoem.conversation_reference AS conversation_reference
                         FROM num_row aoem
                         WHERE nom BETWEEN (? - ?) AND ?"""

    cursor = 10
    limit = 10

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
        logger.debug('Try to send message for customers')
        try:
            success_ids = await send_message_to_tg(db_result)
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


async def send_message_reset():
    sql_update = """UPDATE customers
                    SET is_current_state_message_send = 0
                    WHERE member_id IS NOT NULL
                    AND is_current_state_message_send = 1
    """
    time_now = datetime.utcnow().replace(microsecond=0)
    hour_now = time_now.hour
    minute_now = time_now.minute
    day_trigger = datetime.today().weekday()
    # print('RESET >>>>>>', project_settings.RESET_TIME_TRIGGER)
    time_trigger = int(project_settings.RESET_TIME_TRIGGER[1]) <= hour_now < int(project_settings.RESET_TIME_TRIGGER[2])
    minute_trigger = int(project_settings.RESET_TIME_TRIGGER[3]) <= minute_now < int(
        project_settings.RESET_TIME_TRIGGER[4])
    # logger.debug('time_trigger %s, day_trigger %s, hour_now %s, minute_now %s', time_trigger, day_trigger, hour_now,
    #              minute_now)
    if day_trigger == int(project_settings.RESET_TIME_TRIGGER[0]) and time_trigger and minute_trigger:
        logger.info('All triggers are true. Try to get reset status flag for all customers')
        logger.info('connection_string %s', connection_string)
        with get_db_cursor() as cur:
            try:
                cur.execute(sql_update)
            except Exception:
                logger.exception('DB ERROR')
    return


async def proactive_message_worker(redis_cli: Redis):
    logger.warning('Starting proactive_message_worker')

    last_logging_time = time.time()
    last_health_time = time.time()

    while 1:
        if time.time() - last_logging_time > LOGGING_INTERVAL:
            logger.info('Proactive_message_worker waiting the trigger time')
            last_logging_time = time.time()

        if time.time() - last_health_time > 30:
            await redis_cli.set(project_settings.REDIS_DIRECT_MESSAGE_WORKER_HEALTH_CHECK_KEY, 1)
            await redis_cli.expire(project_settings.REDIS_DIRECT_MESSAGE_WORKER_HEALTH_CHECK_KEY, 60)
            last_health_time = time.time()

        await send_message_reset()

        time_now = datetime.utcnow().replace(microsecond=0)
        hour_now = time_now.hour
        day_trigger = datetime.today().weekday()
        # print('SEND >>>>>>', project_settings.SEND_TIME_TRIGGER)
        time_trigger = int(project_settings.SEND_TIME_TRIGGER[1]) <= hour_now < int(
            project_settings.SEND_TIME_TRIGGER[2])
        # logger.debug('time_trigger %s, day_trigger %s, hour_now %s', time_trigger, day_trigger, hour_now)

        if day_trigger == int(project_settings.SEND_TIME_TRIGGER[0]) and time_trigger:
            logger.info('All triggers are true, Sending proactive message to all relevant customers')
            try:
                await send_message()
            except Exception:
                logger.exception('Send message error')
                await asyncio.sleep(5)
                continue

        await asyncio.sleep(10)


async def admin_mail_worker(redis_cli: Redis):
    logger.warning('Starting admin mail worker')
    last_logging_time = time.time()
    last_health_time = time.time()

    while 1:
        if time.time() - last_logging_time > LOGGING_INTERVAL:
            logger.info('Try to get <ADMIN MAIL> from queue')
            last_logging_time = time.time()

        if time.time() - last_health_time > 30:
            await redis_cli.set(project_settings.REDIS_ADMIN_MAIL_WORKER_HEALTH_CHECK_KEY, 1)
            await redis_cli.expire(project_settings.REDIS_ADMIN_MAIL_WORKER_HEALTH_CHECK_KEY, 60)
            last_health_time = time.time()

        try:
            result = await redis_cli.lpop(project_settings.REDIS_ADMIN_MAIL_QUEUE_KEY)
        except Exception:
            logger.exception('Get message from redis error')
            await asyncio.sleep(5)
            continue

        if result:
            # logger.debug('admin mail message found %s', result)
            logger.debug('admin mail message FOUND!')

            try:
                message_data = json.loads(result)
                await send_mail(message_data, attach=False)
            except Exception:
                logger.exception('Message proceed error')
        await asyncio.sleep(2)


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


async def get_graph_user_data(member_list: List[Tuple[str, str]]) -> List[str]:
    success_ids = []
    for userPrincipalName, member_id in member_list:
        try:
            data = await get_user(userPrincipalName, False)
            logger.info('Get user graph data- %s', data)
            if len(data) == 0:
                success_ids.append(member_id)
            else:
                pass
        except Exception:
            logger.warning('Get user graph data error. User: %s', userPrincipalName)
            continue
        await asyncio.sleep(0.1)
    return success_ids


async def search_fired_users():
    sql_select = """WITH num_row AS (SELECT row_number() OVER (ORDER BY id) AS nom, * FROM customers 
                                     WHERE member_id IS NOT NULL)
                         SELECT aoem.userPrincipalName AS userPrincipalName,
                                aoem.member_id AS member_id
                         FROM num_row aoem
                         WHERE nom BETWEEN (? - ?) AND ?"""

    cursor = 3
    limit = 3

    while 1:
        logger.debug('Try select customers from db for fired')
        with get_db_cursor() as cur:
            try:
                cur.execute(sql_select, cursor, limit, cursor)
                db_result = cur.fetchall()
                logger.debug('db_result %s >>> ', db_result)

            except Exception:
                logger.exception('DB ERROR')
                await asyncio.sleep(1)
                continue

        if not db_result:
            logger.debug('No result. Finish')
            break

        logger.debug('Try to get user status from AD')
        try:
            success_ids = await get_graph_user_data(db_result)
            logger.debug('!!! >>> Data from AD received. Success_ids: %s', success_ids)
        except Exception:
            logger.exception('get_graph_user_data error')
            success_ids = None

        if not success_ids:
            logger.warning('get_graph_user_data WARNING')
            cursor += limit + 1
            await asyncio.sleep(1)
            continue

        placeholders = ', '.join(['?'] * len(success_ids))
        sql_update_fired_user = """UPDATE customers
                                   SET member_id = NULL,
                                       conversation_reference = NULL,
                                       operator_displayName = 'user was fired'
                                   WHERE member_id IN (""" + placeholders + ")"

        with get_db_cursor() as cur_update:
            try:
                print('>>>>>>>>> <<<<<<<<<', sql_update_fired_user)
                res = cur_update.execute(sql_update_fired_user, success_ids)
                logger.debug('Db updated for: %s, %s', success_ids, res)

            except Exception:
                logger.exception('DB ERROR')
                await asyncio.sleep(2)

        cursor += limit + 1
        await asyncio.sleep(1)


async def mark_fired_users_worker(redis_cli: Redis):
    logger.warning('Starting mark_fired_users_worker')

    last_logging_time = time.time()
    last_health_time = time.time()

    while 1:
        if time.time() - last_logging_time > LOGGING_INTERVAL:
            logger.info('Mark_fired_users_worker waiting the trigger time')
            last_logging_time = time.time()

        if time.time() - last_health_time > 30:
            await redis_cli.set(project_settings.REDIS_DIRECT_MESSAGE_WORKER_HEALTH_CHECK_KEY, 1)
            await redis_cli.expire(project_settings.REDIS_DIRECT_MESSAGE_WORKER_HEALTH_CHECK_KEY, 60)
            last_health_time = time.time()

        time_now = datetime.utcnow().replace(microsecond=0)
        hour_now = time_now.hour
        day_trigger = datetime.today().weekday()
        # print('SEND >>>>>>', project_settings.SEND_TIME_TRIGGER)
        time_trigger = int(project_settings.FIRED_TIME_TRIGGER[1]) <= hour_now < int(
            project_settings.FIRED_TIME_TRIGGER[2])
        # logger.debug('time_trigger %s, day_trigger %s, hour_now %s', time_trigger, day_trigger, hour_now)

        if day_trigger == int(project_settings.FIRED_TIME_TRIGGER[0]) and time_trigger:
            logger.info('All triggers are true, marking all relevant customers')
            try:
                await search_fired_users()
            except Exception:
                logger.exception('Error while marking fired users')
                await asyncio.sleep(5)
                continue

        await asyncio.sleep(10)


async def ping():
    logger.warning('Starting ping_worker')
    if project_settings.IS_LOCAL_ENV == 0:
        pinging_url = 'https://mih-we-cnt-nyac2-p-app-01.azurewebsites.net/api/messages'
    else:
        pinging_url = 'http://localhost:3978/api/messages'
    headers = {
        'Content-Type': 'text/plain',
        'Auth': project_settings.AUTH_TOKEN
    }
    timeout = 10
    count = 0
    while 1:
        try:
            response = requests.get(
                pinging_url,
                timeout=timeout,
                headers=headers,
            )
        except Exception:
            logger.info('503. Service Unavailable. The server cannot process the request due to a high load')
            await asyncio.sleep(60 * 5)
            continue

        if response.status_code == 415:
            logger.debug(response)
            await asyncio.sleep(60 * 5)
            continue

        if response.status_code == 202:
            response_time = response.elapsed.total_seconds() * 1000
            # logger.debug('Status code: %s, response time: %s', response.status_code, response_time)
            if count == 120:
                count = 0
                try:
                    ping_file_clear_old_lines(1000, project_settings.PING_FILE)
                    logger.debug('ping file has been cut')
                except Exception:
                    logger.exception('Cutting ping file error')
                    continue

            try:
                with open(project_settings.PING_FILE, 'a') as f:
                    f.write(str(response_time) + '\n')
                count += 1
            except Exception:
                logger.exception('Append to ping file error')
                continue

        await asyncio.sleep(60)


def run():
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    redis_client = get_redis_client()
    logger.info('REDIS CLIENT %s', redis_client)
    # logger.info('connection_string %s', connection_string)

    asyncio.ensure_future(admin_mail_worker(redis_client))
    asyncio.ensure_future(proactive_message_worker(redis_client))
    asyncio.ensure_future(blob_remover_worker(redis_client))
    asyncio.ensure_future(mark_fired_users_worker(redis_client))
    asyncio.ensure_future(ping())

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        logger.info('Exit\n')

    except Exception:
        logger.exception('Runtime error')


if __name__ == "__main__":
    run()
