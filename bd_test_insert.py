from setup.db import get_db_cursor
from lib.logger import CustomLogger

logger = CustomLogger.get_logger('bot')


def select_one(employeeId: str):
    sql_select = """SELECT aoe.employeeId AS employeeId,
                    aoe.member_id AS member_id,
                    aoe.displayName AS displayName, 
                    aoe.userPrincipalName AS userPrincipalName, 
                    aoe.mobilePhone AS mobilePhone,
                    aoe.city AS city,
                    aoe.is_current_state_reply_received AS is_current_state_reply_received            
             FROM customers aoe
             WHERE aoe.employeeId = ?"""
    if not employeeId:
        print('Exit without searching')
        return

    employeeId = str(employeeId)

    with get_db_cursor() as cur:
        try:
            cur.execute(sql_select, employeeId)
            db_result = cur.fetchall()
        except Exception:
            logger.exception('DB ERROR')

    print(db_result)


if __name__ == '__main__':
    x = input('employeeId for SEARCH: ')
    select_one(x)


