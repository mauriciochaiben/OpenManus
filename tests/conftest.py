import asyncio
import inspect


def pytest_pyfunc_call(pyfuncitem):
    testfunc = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunc):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(testfunc(**pyfuncitem.funcargs))
        loop.close()
        return True
    return None
