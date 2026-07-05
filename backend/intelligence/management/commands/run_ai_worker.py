import time

from django.core.management.base import BaseCommand
from django.db import close_old_connections

from problems.models import (
    Problem,
    ProblemStatus,
)

from intelligence.services import (
    run_full_intelligence_pipeline,
)


POLL_INTERVAL_SECONDS = 60


class Command(BaseCommand):
    help = (
        "Runs the JanMitra AI intelligence "
        "pipeline worker."
    )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "JanMitra AI Worker started."
            )
        )

        self.stdout.write(
            (
                "Checking for citizen requests "
                f"every {POLL_INTERVAL_SECONDS} seconds."
            )
        )

        self.stdout.write("")

        while True:
            try:
                close_old_connections()

                pending_count = (
                    Problem.objects.filter(
                        status=(
                            ProblemStatus.READY_FOR_AI
                        )
                    ).count()
                )

                timestamp = time.strftime(
                    "%H:%M:%S"
                )

                if pending_count == 0:
                    self.stdout.write(
                        (
                            f"[{timestamp}] "
                            "No pending citizen requests."
                        )
                    )

                    time.sleep(
                        POLL_INTERVAL_SECONDS
                    )

                    continue


                self.stdout.write(
                    self.style.WARNING(
                        (
                            f"[{timestamp}] "
                            f"Found {pending_count} "
                            "citizen request(s)."
                        )
                    )
                )

                self.stdout.write(
                    "Running JanMitra intelligence pipeline..."
                )


                result = (
                    run_full_intelligence_pipeline()
                )


                created_issue_count = len(
                    result["created_issues"]
                )

                prioritized_issue_count = len(
                    result["prioritized_issues"]
                )

                created_proposal_count = len(
                    result["created_proposals"]
                )


                self.stdout.write(
                    self.style.SUCCESS(
                        (
                            "Pipeline completed successfully."
                        )
                    )
                )

                self.stdout.write(
                    (
                        "Created issues: "
                        f"{created_issue_count}"
                    )
                )

                self.stdout.write(
                    (
                        "Prioritized issues: "
                        f"{prioritized_issue_count}"
                    )
                )

                self.stdout.write(
                    (
                        "Created proposals: "
                        f"{created_proposal_count}"
                    )
                )

                self.stdout.write("")


            except KeyboardInterrupt:
                self.stdout.write("")

                self.stdout.write(
                    self.style.WARNING(
                        "JanMitra AI Worker stopped."
                    )
                )

                break


            except Exception as exc:
                timestamp = time.strftime(
                    "%H:%M:%S"
                )

                self.stderr.write(
                    self.style.ERROR(
                        (
                            f"[{timestamp}] "
                            "AI pipeline failed: "
                            f"{exc}"
                        )
                    )
                )

                self.stderr.write(
                    (
                        "Worker will retry on the "
                        "next polling cycle."
                    )
                )

                self.stderr.write("")


            finally:
                close_old_connections()


            time.sleep(
                POLL_INTERVAL_SECONDS
            )