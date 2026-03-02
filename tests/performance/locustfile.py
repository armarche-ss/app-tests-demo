import random
from locust import HttpUser, task, between


class ToolBrowserUser(HttpUser):
    """
    Simulates a user browsing the DevOps tools catalogue.

    wait_time = between(1, 3):
      Each virtual user pauses 1–3 seconds between tasks.
      This mimics realistic human behaviour — people read before clicking.
      Without a wait time, you simulate bots, not real users.
    """
    wait_time = between(1, 3)

    # Tool IDs that exist in the seeded database.
    # Used by tasks that fetch individual tool details.
    tool_ids = [
        "pytest", "locust", "k6", "docker", "docker-compose",
        "prometheus", "grafana", "terraform", "ansible", "argocd",
    ]

    @task(5)
    def browse_tools_list(self):
        """
        GET /tools/ — Browse the full list of tools.

        @task(5) = this task is 5× more likely than a @task(1).
        Reflects real usage: most visitors browse the list without
        clicking into individual tools.

        This endpoint runs a SELECT on the tools table. Under heavy
        concurrent load, an unindexed table will show degradation here.
        """
        with self.client.get("/tools/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code} on GET /tools/")
            elif response.elapsed.total_seconds() > 1.0:
                # A 200 that took over 1 second is still a performance failure
                response.failure(
                    f"Slow response: {response.elapsed.total_seconds():.2f}s (threshold: 1s)"
                )

    @task(3)
    def view_single_tool(self):
        """
        GET /tools/{id} — Fetch details for a specific tool.

        @task(3) = fairly common but less so than listing all tools.

        This is the query that suffers most from a missing index —
        it filters by primary key (`id`), so it should always be fast.
        """
        tool_id = random.choice(self.tool_ids)
        with self.client.get(
            f"/tools/{tool_id}",
            name="/tools/{tool_id}",   # group all tool IDs under one stat
            catch_response=True,
        ) as response:
            if response.status_code == 404:
                # Tool may not be seeded yet — not our bug
                response.success()
            elif response.status_code != 200:
                response.failure(f"Got {response.status_code} on /tools/{tool_id}")
            elif response.elapsed.total_seconds() > 0.5:
                response.failure(
                    f"Slow tool detail: {response.elapsed.total_seconds():.2f}s (threshold: 0.5s)"
                )

    @task(1)
    def health_check(self):
        """
        GET /health — Simulates a monitoring system periodically checking health.

        @task(1) = rare. Health checks are mostly done by infra, not users.
        This should always respond quickly regardless of other load.
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")
            elif response.json().get("status") != "ok":
                response.failure(f"Health status is not ok: {response.json()}")
