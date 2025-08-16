import datetime
import logging
from dataclasses import dataclass, field


@dataclass
class Schedule:
    start_date: datetime.date | None = field(default=None)
    end_date: datetime.date | None = field(default=None)


@dataclass
class User:
    pk: int
    schedulers: list[Schedule]
    status: bool


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
queue = []


def worker_generate_schedule(count_users: int = 3):
    for pk in range(1, count_users + 1):
        queue.append(User(pk=pk, schedulers=[Schedule(), Schedule()], status=False))


def worker_change_schedule():
    for user in queue:
        if user.status is False:
            user.schedulers[0].start_date = datetime.datetime(
                day=1, month=7, year=2025
            ).date()
            user.schedulers[0].end_date = datetime.datetime(
                day=14, month=7, year=2025
            ).date()

            user.schedulers[1].start_date = datetime.datetime(
                day=1, month=9, year=2025
            ).date()
            user.schedulers[1].end_date = datetime.datetime(
                day=14, month=9, year=2025
            ).date()

            user.status = True
            logger.info("Автоматическое проставление графика")


def worker_employees_notice():
    for user in queue:
        logger.info("Пользователь ID=%s уведомлен", user.pk)


class Scheduler:

    def __init__(self, date: datetime.datetime):
        self.validate_date = date.date()

    def run(self, worker_, *args, **kwargs):
        while True:
            current_date = datetime.datetime.now(datetime.timezone.utc).date()
            if current_date == self.validate_date:
                try:
                    worker_(*args, **kwargs)
                except Exception as e:
                    logger.error(e)
                else:
                    break


if __name__ == "__main__":
    logger.info(queue)
    Scheduler(date=datetime.datetime(day=16, month=8, year=2025)).run(
        worker_generate_schedule, 2
    )
    logger.info(queue)
    Scheduler(date=datetime.datetime(day=23, month=8, year=2025)).run(
        worker_employees_notice
    )
    Scheduler(date=datetime.datetime(day=30, month=8, year=2025)).run(
        worker_change_schedule
    )
    logger.info(queue)
