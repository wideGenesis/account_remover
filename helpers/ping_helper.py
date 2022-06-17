import csv
import json
import statistics
from lib.logger import CustomLogger
from project_settings import PING_FILE

logger = CustomLogger.get_logger('flask')


def ping_statistics():
    with open(PING_FILE) as f:
        csv_reader = csv.reader(f)
        rows = []
        for row in csv_reader:
            rows.append(float(row[0]))
    now = rows[-1:]
    a10 = statistics.mean(rows[:-10]) if len(rows) >= 10 else 'Not enough data'
    a60 = statistics.mean(rows[:-60]) if len(rows) >= 60 else 'Not enough data'
    std10 = statistics.stdev(rows[:-10]) if len(rows) >= 10 else 'Not enough data'
    std60 = statistics.stdev(rows[:-60]) if len(rows) >= 60 else 'Not enough data'

    data = {
            'now': now,
            'a10': a10,
            'a60': a60,
            'std10': std10,
            'std60': std60
    }

    return json.dumps(data)


def ping_file_clear_old_lines(qty_rows_to_del: int, path: str):
    _del = False
    try:
        with open(path, "r+") as in_file:
            lines = in_file.readlines()
            rm = len(lines) - qty_rows_to_del
            if len(lines) > qty_rows_to_del:
                _del = True
    except Exception:
        logger.exception('ping file read error')
        return

    if _del:
        try:
            with open(path, "w+") as out_file:
                out_file.writelines(lines[rm:])
                logger.info('Cutting ping file has been completed %s', rm)
        except Exception:
            logger.exception('ping file write error')
            return

    return

