import asyncio
import logging
import sys
import typing

__all__ = ['StartupTasks', 'BackgroundTasks', 'ExecutionLoop']

from functools import wraps

from .. import utils
from ..exceptions import ClosingError

logger = logging.getLogger(__name__)


class StartupTasks:
    """ Class intended to inherit all StartupTasks """
    pass


class BackgroundTasks:
    """ Class intended to inherit all BackgroundTasks """
    pass


class ExecutionLoop:
    """
    Loop that executes tasks in the background.

    Not intended for usage for users yet
    """

    def __init__(self, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        """
        :param loop: Event loop that will be used to execute all async functions.
        """
        self.loop = loop
        self.background_tasks = []
        self.background_tasks_handler = BackgroundTasks()
        self.startup_tasks = []
        self.startup_tasks_handler = StartupTasks()
        self._finished_tasks = []
        self._active = False
        self._startup_finished = False

        # Variable that stores the current running_loop => Will be None when the loop is not running
        self.running_loop = None

    @property
    def active(self):
        """
        Represents the current status of the loop. If True that means the loop is still running
        """
        return self._active

    @property
    def startup_finished(self):
        """
        Represents the status of the Startup Tasks. If True that means it was successfully executed
        and the execution loop is now running!
        """
        return self._startup_finished

    async def start(self) -> None:
        """
        Starts the current execution_loop!

        ---

        Does not return until the loop has finished!
        """
        async def _loop(startup_tasks, tasks):
            """
            Loop coroutine that runs the tasks
            :param startup_tasks: Tasks that will be executed once at the beginning of the bot
            :param tasks: Tasks that will run infinitely in the background
            """
            # Startup Tasks
            self._active = True

            # Startup tasks that only get executed once
            async def startup():
                """
                Tasks that are scheduled to run at the start one time before then running the
                general execution_loop
                """
                try:
                    if not startup_tasks == []:
                        _tasks = []
                        for task_name in startup_tasks:
                            # Fetching the startup_task from the object that stores them
                            async_task = getattr(self.startup_tasks_handler, task_name)
                            _tasks.append(asyncio.create_task(async_task(), name=task_name))

                        # Passing all tasks as args to the event loop
                        await asyncio.gather(*_tasks)

                except asyncio.CancelledError:
                    logger.debug(f"[EXEC-LOOP] Startup tasks were cancelled and stopped unexpectedly!")

                except Exception as e:
                    utils.log_traceback(
                        msg="[EXEC-LOOP] Traceback:",
                        suffix=f"Error in startup tasks in the execution loop: \n{sys.exc_info()[0].__name__}: {e}"
                    )

                finally:
                    self._startup_finished = True
                    return

            async def background_loop():
                """
                Background Loop for all tasks that will be run in the background infinitely
                """
                if not tasks == []:
                    # Checks whether the loop is supposed to be running
                    while self._active:
                        _tasks = []
                        for task_name in tasks:
                            # Fetching the startup_task from the object that stores them
                            async_task = getattr(self.background_tasks_handler, task_name)
                            _tasks.append(asyncio.create_task(async_task(), name=task_name))

                        # Passing all tasks as args to the event loop
                        await asyncio.gather(*_tasks)
                return

            try:
                await asyncio.gather(startup(), background_loop(), return_exceptions=True)
            except asyncio.CancelledError:
                logger.debug(f"[EXEC-LOOP] Async gather of tasks was cancelled and stopped unexpectedly!")

        self.running_loop = asyncio.create_task(_loop(self.startup_tasks, self.background_tasks))
        try:
            await self.running_loop
        except asyncio.CancelledError:
            logger.debug("[EXEC-LOOP] Async task was cancelled and stopped unexpectedly! "
                         "No more tasks will be executed!")
        except Exception as e:
            utils.log_traceback(
                msg="[EXEC-LOOP] Traceback:",
                suffix=f"Failed to start or keep alive execution_loop: \n{sys.exc_info()[0].__name__}: {e}"
            )
        finally:
            self._active = False
            return

    async def stop(self) -> None:
        """ Forces the current execution_loop to stop! """
        try:
            if not self.running_loop.cancelled():
                self.running_loop.cancel()

            # Ensuring the tasks stops as soon as possible
            self._active = False
            logger.debug("[EXEC-LOOP] The execution loop was cancelled and stopped")

            # Setting the running_loop to None again!
            self.running_loop = None

        except Exception as e:
            utils.log_traceback(
                msg="[EXEC-LOOP] Traceback:",
                suffix=f"Failed to stop or keep alive execution_loop: \n{sys.exc_info()[0].__name__}: {e}"
            )
            raise ClosingError("Failed to stop or keep alive execution_loop!"
                               f"> {sys.exc_info()[0].__name__}: {e}")
        finally:
            return

    def add_to_loop(self, coro: typing.Awaitable = None):
        """
        Decorator used for registering Tasks for the execution_loop

        ---

        Tasks will run in a loop until the close() function was called

        :param coro: Function that should be wrapped and then executed in the Execution Loop
        """
        def decorator(coro: typing.Union[typing.Callable, typing.Awaitable]):
            @wraps(coro)
            async def wrapper():
                # Sleeping to avoid too many executions at once
                await asyncio.sleep(0.05)
                return await coro

            if getattr(self.background_tasks_handler, 'func_.__name__', None) is None:
                setattr(self.background_tasks_handler, coro.__name__, wrapper)
            self.background_tasks.append(coro.__name__)

            logger.debug(f"[EXEC-LOOP] >> Task {coro.__name__} added to loop")

            return coro  # returning func so it still can be used outside the class

        if coro is None:
            return decorator
        else:
            return decorator(coro)

    def add_to_startup(self, coro: typing.Awaitable = None):
        """
        Decorator used for registering Startup Tasks for the execution_loop

        ---

        Startup Tasks only will be executed one time at startup

        :param coro: Function that should be wrapped and then executed at startup in the Execution Loop
        """
        def decorator(coro: typing.Union[typing.Callable, typing.Awaitable]):
            @wraps(coro)
            async def wrapper():
                return await coro

            if getattr(self.startup_tasks_handler, 'func_.__name__', None) is None:
                setattr(self.startup_tasks_handler, coro.__name__, wrapper)
            self.startup_tasks.append(coro.__name__)

            logger.debug(f"[EXEC-LOOP] >> Startup Task {coro.__name__} added to loop")

            return coro  # returning func so it still can be used outside the class

        if coro is None:
            return decorator
        else:
            return decorator(coro)
