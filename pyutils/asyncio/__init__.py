from logging import getLogger
from typing import Callable, Any, Iterable, Optional
from asyncio import Task, Semaphore, Event, iscoroutine
from contextvars import ContextVar, Token, copy_context

LOG = getLogger(__name__)


async def limited_gather(
    iteration_coroutine: Callable[[Any], Any],
    iterable: Iterable[Any],
    result_callback: Callable[[Task, Any], Any],
    num_concurrent: int = 5
) -> None:
    """
    Run coroutines concurrently with a maximum limit.

    :param iteration_coroutine: A coroutine to call with the values in the iterable.
    :param iterable: An iterable with values to pass to the coroutine
    :param result_callback: A callback which to call with the result of a call to the coroutine.
    :param num_concurrent: The maximum number of concurrent invocations of the coroutine.
    :return: None
    """

    if not iterable:
        return

    limiting_semaphore = Semaphore(num_concurrent)
    all_finished_event = Event()

    num_started = 0
    num_finished = 0

    passed_iteration_value_context_var = ContextVar('passed_iteration_value')

    def signal_callback_finished(*_, **__):
        nonlocal num_finished
        num_finished += 1
        all_finished_event.set()

    def task_done_callback(finished_task: Task) -> None:
        limiting_semaphore.release()

        response: Optional[Any] = None

        try:
            response = result_callback(finished_task, passed_iteration_value_context_var.get())
        except:
            LOG.exception(f'Unexpected exception in result callback.')
        finally:
            if iscoroutine(response):
                Task(coro=response).add_done_callback(signal_callback_finished)
                return

            signal_callback_finished()

    for iteration_value in iterable:
        await limiting_semaphore.acquire()
        num_started += 1

        passed_iteration_value_token: Token = passed_iteration_value_context_var.set(iteration_value)

        Task(
            coro=iteration_coroutine(iteration_value)
        ).add_done_callback(
            task_done_callback,
            context=copy_context()
        )

        passed_iteration_value_context_var.reset(passed_iteration_value_token)

    while num_finished < num_started:
        await all_finished_event.wait()
        all_finished_event.clear()
