import asyncio
import os
import uvloop
from graph.graph_async_client import get_user
from graph.graph_client import client


# client.get_msgraph_data('andrey.benimovich@metinvestholding.com ')
# print(client.get_msgraph_data('tatyana.barabash@metinvest.digital'))
# res = client.get_msgraph_data('+380502767384')
# print(res)



async def loop_graph():
    for i in [
        'tatyana.barabash@metinvest.digital',
        'viktoriya.nartenko@metinvestholding.com',
        'konstantin.zuev@metinvestholding.com',
        'y.v.nalivayko@metinvestholding.com',
        'aleksandra.dulich@metinvestholding.com',
        'viktor.malichenko@metinvestholding.com',
        'andrey.maslov@metinvestholding.com',
        'ruslan.zhemirov@metinvestholding.com'
    ]:
        await get_user(i, False)


def run():

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    asyncio.ensure_future(loop_graph())

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        print('Exit\n')

    except Exception:
        print('Runtime error')

if __name__ == "__main__":
    print('start')
    run()