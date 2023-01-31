from typing import Optional

from hikaru.model import Job

from robusta.core.playbooks.base_trigger import TriggerEvent
from robusta.integrations.kubernetes.autogenerated.triggers import JobChangeEvent, JobUpdateTrigger
from robusta.integrations.kubernetes.base_triggers import K8sTriggerEvent


class JobFailedTrigger(JobUpdateTrigger):
    """
    Will fire when the job becomes failed.
    """

    def __init__(
        self,
        name_prefix: Optional[str] = None,
        namespace_prefix: Optional[str] = None,
        labels_selector: Optional[str] = None,
    ):
        super().__init__(
            name_prefix=name_prefix,  # type: ignore
            namespace_prefix=namespace_prefix,  # type: ignore
            labels_selector=labels_selector,  # type: ignore
        )

    def should_fire(self, event: TriggerEvent, playbook_id: str):
        should_fire = super().should_fire(event, playbook_id)
        if not should_fire:
            return should_fire

        if not isinstance(event, K8sTriggerEvent):
            return False

        exec_event = self.build_execution_event(event, {})

        if not isinstance(exec_event, JobChangeEvent):
            return False

        # fire if the job is firing now, but wasn't firing before (in case the job is updated after it failed)
        currently_failed = JobFailedTrigger.__is_job_failed(exec_event.obj)
        return currently_failed and not JobFailedTrigger.__is_job_failed(exec_event.old_obj)

    @staticmethod
    def __is_job_failed(job: Job) -> bool:
        if not job.status:
            return False

        failed_conditions = [condition for condition in job.status.conditions if condition.type == "Failed"]
        return len(failed_conditions) > 0
