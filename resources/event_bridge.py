# Doc: https://www.pulumi.com/registry/packages/aws/api-docs/scheduler/schedule
# Doc: https://docs.aws.amazon.com/scheduler/latest/UserGuide/schedule-types.html
import pulumi
import pulumi_aws as aws

def scheduler(name: str, schedule_expression, target: dict,start_date=None, group_name: str=None, flexible_time_window: dict="OFF"):
    name = name.lower().strip()
    schedule = aws.scheduler.Schedule(f"{name}",
        name=f"{name}",
        group_name=group_name,
        flexible_time_window={
            "mode": flexible_time_window,
        },
        schedule_expression=schedule_expression,
        start_date=start_date,
        target=target)