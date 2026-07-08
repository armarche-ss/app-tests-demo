set -e

echo "Running init-db.sh — seeding database if needed..."

# psql is available inside the postgres container.
# We connect as the POSTGRES_USER (set via docker-compose env) and
# create the database only if it doesn't exist.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    SELECT 'CREATE DATABASE devops_rating'
    WHERE NOT EXISTS (
        SELECT FROM pg_database WHERE datname = 'devops_rating'
    )\gexec

    \c devops_rating\gexec

    CREATE TABLE IF NOT EXISTS tools (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        github_stars INTEGER NOT NULL,
        github_repo TEXT,
        last_synced_at TIMESTAMPTZ
    )\gexec


    INSERT INTO tools (id, name, category, description, github_stars, github_repo) VALUES
    ('pytest',          'pytest',          'Testing',       'The most popular Python testing framework.', 12400, 'pytest-dev/pytest'),
    ('locust',          'Locust',          'Testing',       'Write load tests in plain Python. Scalable and distributed.', 24800, 'locustio/locust'),
    ('k6',              'k6',              'Testing',       'Developer-centric performance testing with a JS API.', 26000, 'grafana/k6'),
    ('testcontainers',  'Testcontainers',  'Testing',       'Spin up real Docker containers in your tests.', 8200, 'testcontainers/testcontainers-java'),
    ('httpx',           'HTTPX',           'Testing',       'Async-first HTTP client for Python.', 13200, 'encode/httpx'),
    ('docker',          'Docker',          'Containers',    'The container runtime that started it all.', 69000, 'moby/moby'),
    ('docker-compose',  'Docker Compose',  'Containers',    'Define multi-container apps in a single YAML file.', 34000, 'docker/compose'),
    ('podman',          'Podman',          'Containers',    'Daemonless, rootless Docker alternative.', 24400, 'containers/podman'),
    ('github-actions',  'GitHub Actions',  'CI/CD',         'Workflows as YAML in your repo.', 0, 'actions/runner'),
    ('argocd',          'Argo CD',         'CI/CD',         'Declarative GitOps CD for Kubernetes.', 18600, 'argoproj/argo-cd'),
    ('prometheus',      'Prometheus',      'Observability', 'Pull-based metrics collection with PromQL.', 56200, 'prometheus/prometheus'),
    ('grafana',         'Grafana',         'Observability', 'Beautiful dashboards for any data source.', 65000, 'grafana/grafana'),
    ('opentelemetry',   'OpenTelemetry',   'Observability', 'Vendor-neutral tracing, metrics, and logs.', 4800, 'open-telemetry/opentelemetry-collector'),
    ('terraform',       'Terraform',       'IaC',           'Declare infrastructure as HCL. Multi-cloud provisioning.', 43700, 'hashicorp/terraform'),
    ('ansible',         'Ansible',         'IaC',           'Agentless automation in YAML playbooks.', 63200, 'ansible/ansible')
    ON CONFLICT (id) DO NOTHING\gexec
EOSQL

echo "init-db.sh complete"
