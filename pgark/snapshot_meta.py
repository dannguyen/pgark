import json as jsonlib
from typing import NoReturn, Union as tyUnion

class SnapshotMeta(object):

    def __init__(self, target_url, service, **kwargs):
        self.service = service
        # self.was_new_snapshot_created = False
        self.snapshot_url = None
        self.request_meta = {"target_url": target_url, "user_agent": kwargs.get('user_agent'), }
        # self.job = {'id': None, 'url': None}
        self.server_payload = {}
        self.issues = {}

    def to_dict(self) -> dict:
        df = {'was_new_snapshot_created': self.was_new_snapshot_created()}

        for key in ('service', 'snapshot_url',
                'issues', 'request_meta', 'server_payload',
            ):
            df[key] = getattr(self, key)

        return df
    def __repr__(self):

        return jsonlib.dumps(self.to_dict(), indent=2)

    def is_success(self) -> bool:
        # TODO: wayback machine specific stuff, will subclass later
        return self.snapshot_url is not None

    def was_new_snapshot_created(self) -> bool:
        ## issues handling
        ## refactor this later, when there are more issues
        return not any(
            i for i in [self.too_many_during_period(), self.too_soon()]
        )


    # TODO: kill these
    def set_issues(self, issues:dict) -> NoReturn:
        self.issues = issues


    def set_payload(self, payload:dict) -> NoReturn:
        self.server_payload = payload
        # TODO: wayback machine specific stuff, will subclass later
        # if self.server_payload.get('status') == 'success':


        #     js.get("status") == "success":
        #     df["snapshot_url"] = url_for_snapshot(
        #         js["original_url"], js["timestamp"]
        #     )


    ## issue stuff
    def too_many_during_period(self) -> tyUnion[str, None]:
        msg = self.issues.get('too_many_during_period')
        return msg

    def too_soon(self) -> tyUnion[str, None]:
        msg = self.issues.get('too_soon')
        return msg
