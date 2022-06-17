
def ping_file_clear_old_lines():
    try:

        with open('tst.csv', "r+") as in_file:

            lines = in_file.readlines()
            rm = len(lines) - 10
            if len(lines) >= 10:
                _del = True
    except Exception:
        return

    if _del:
        try:
            with open('tst.csv', "w+") as out_file:
                out_file.writelines(lines[rm:])
        except Exception:
            return

    return


if __name__ == '__main__':
    ping_file_clear_old_lines()
