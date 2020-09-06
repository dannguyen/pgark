from pgark import current_time
from pgark import mylogger

from datetime import datetime
import json as jsonlib
from typing import NoReturn, Union as tyUnion


class TaskMeta(object):
    def __init__(self, target_url: str, service: str, subcommand: str, **kwargs):
        self.service = service
        self.subcommand = subcommand
        # self.was_new_snapshot_created = False
        self.snapshot_url = None
        self.created_at = current_time()
        self.request_meta = {
            "target_url": target_url,
            "created_at": str(self.created_at),
            "user_agent": kwargs.get("user_agent"),
        }
        # self.job = {'id': None, 'url': None}
        self.server_payload = {}
        self.issues = {}

        # place holder to indicate that the original task was supplanted by a
        # different one, e.g. when snapshot gets a "too many today" response, and
        # then reverts to returning snapshot_url from check subcommand
        self.redirected_task = None

    def to_dict(self) -> dict:
        df = {"was_new_snapshot_created": self.was_new_snapshot_created()}

        for key in (
            "service",
            "subcommand",
            "snapshot_url",
            "issues",
            "request_meta",
            "server_payload",
        ):
            df[key] = getattr(self, key)

        return df

    def __repr__(self):
        return jsonlib.dumps(self.to_dict(), indent=2)

    def is_success(self) -> bool:
        # TODO: wayback machine specific stuff, will subclass later
        return self.snapshot_url is not None

    def was_new_snapshot_created(self) -> bool:
        # TODO: we should obviously subclass TaskMeta into SnapshotTask and CheckTask; refactor
        # this branching crap later
        if self.subcommand == "check":
            return False
        elif self.subcommand == "snapshot":
            if self.redirected_task:
                return False
            else:
                ## TODO: refactor this later, when there are more issues
                return not any(
                    i for i in [self.too_many_during_period(), self.too_soon()]
                )
        else:
            raise TodoError(
                f"TaskMeta.was_new_snapshot_created() can't handle the subcommand of {self.subcommand}!"
            )

    # TODO: kill these
    # def add_issue(self, name:str, msg:str) -> NoReturn:
    #     self.issues[name] = msg

    def set_issues(self, issues: dict) -> NoReturn:
        self.issues = issues

    def set_payload(self, payload: dict) -> NoReturn:
        self.server_payload = payload

    ## issue stuff
    def too_many_during_period(self) -> tyUnion[str, None]:
        msg = self.issues.get("too_many_during_period")
        return msg

    def too_soon(self) -> tyUnion[str, None]:
        msg = self.issues.get("too_soon")
        return msg

    # just wtf is this doing here? TODO: worry about it later
    def created_within(self, x: int, dt: datetime, unit: str = "hours") -> bool:
        delta_seconds = (self.created_at - dt).seconds
        delta_hours = delta_seconds / (60 * 60)
        mylogger.debug(
            f"{dt} is_within {delta_seconds} seconds (i.e. {delta_hours} hours) of {self.created_at}"
        )
        delta = delta_hours if unit == "hours" else delta_seconds

        return delta <= x
        # mylogger.debug(f"Most recent snapshot available: {recent_url}")
