import json
from pathlib import Path

PRICES = json.loads(
    (Path(__file__).parent / "data" / "pricing-eu-west-1.json").read_text()
)

HOURS_PER_MONTH = 730
CLIENT_ASSETS_GB = 1.0
LAMBDA_MEMORY_GB = 0.5
LAMBDA_DURATION_S = 0.2
READ_SHARE = 0.8

ARCHETYPES = {
    "serverless": {
        "name": "Fully serverless",
        "services": ["API Gateway", "Lambda", "DynamoDB", "S3", "CloudFront"],
    },
    "single_server": {
        "name": "Single server",
        "services": ["EC2", "RDS", "S3"],
    },
    "classic": {
        "name": "Classic web tier",
        "services": ["EC2", "Application Load Balancer", "RDS", "NAT gateway", "S3"],
    },
    "fargate": {
        "name": "Containers on Fargate",
        "services": [
            "Fargate",
            "Application Load Balancer",
            "RDS",
            "NAT gateway",
            "S3",
        ],
    },
    "eks": {
        "name": "Containers on EKS",
        "services": [
            "EKS",
            "EC2",
            "Application Load Balancer",
            "RDS",
            "NAT gateway",
            "S3",
        ],
    },
}

EC2_SIZE = {"low": "t3.small", "moderate": "t3.medium", "high": "t3.large"}
RDS_SIZE = {"low": "db.t3.micro", "moderate": "db.t3.small", "high": "db.t3.medium"}
FARGATE_SIZE = {"low": (0.25, 0.5), "moderate": (0.5, 1.0), "high": (1.0, 2.0)}

QUESTIONS = [
    {
        "id": "stage",
        "prompt": "Do you already have the application, or are you starting fresh?",
        "options": [
            {"value": "greenfield", "label": "Starting fresh"},
            {"value": "existing", "label": "It already exists"},
        ],
    },
    {
        "id": "current_stack",
        "prompt": "If it exists, how does it run today?",
        "options": [
            {"value": "server", "label": "A traditional server process"},
            {"value": "containers", "label": "Packaged as containers"},
            {"value": "functions", "label": "Already serverless functions"},
            {"value": "none", "label": "Not applicable"},
        ],
    },
    {
        "id": "ops_capacity",
        "prompt": "How much infrastructure does the team want to manage?",
        "options": [
            {"value": "managed", "label": "As little as possible"},
            {"value": "containers", "label": "Containers, but not Kubernetes"},
            {"value": "kubernetes", "label": "Kubernetes"},
            {"value": "server", "label": "A plain server"},
        ],
    },
    {
        "id": "high_availability",
        "prompt": "Must the application survive a machine or zone failure?",
        "options": [
            {"value": "yes", "label": "Yes, high availability is required"},
            {"value": "no", "label": "A short downtime is acceptable"},
        ],
    },
    {
        "id": "traffic_pattern",
        "prompt": "How do you expect the traffic to behave?",
        "options": [
            {"value": "flat", "label": "Low and flat"},
            {"value": "steady", "label": "Steady and predictable"},
            {"value": "spiky", "label": "Variable and spiky"},
        ],
    },
    {
        "id": "traffic_volume",
        "prompt": "What volume of traffic do you expect?",
        "options": [
            {"value": "low", "label": "Very low"},
            {"value": "moderate", "label": "Moderate"},
            {"value": "high", "label": "High"},
        ],
    },
    {
        "id": "data_type",
        "prompt": "What kind of data does the application store?",
        "options": [
            {"value": "relational", "label": "Relational"},
            {"value": "key_value", "label": "Key-value or document"},
            {"value": "none", "label": "Little or none"},
        ],
    },
    {
        "id": "team_size",
        "prompt": "How large is the team that will maintain it?",
        "options": [
            {"value": "solo", "label": "One or two people"},
            {"value": "small", "label": "A small team"},
            {"value": "several", "label": "Several teams"},
        ],
    },
    {
        "id": "structure",
        "prompt": "How is the application organised?",
        "options": [
            {"value": "monolith", "label": "A single deployable unit"},
            {"value": "microservices", "label": "Independent services"},
        ],
    },
    {
        "id": "request_duration",
        "prompt": "How long do the requests or processes run?",
        "options": [
            {"value": "short", "label": "Mostly short"},
            {"value": "long", "label": "Long-running or persistent"},
        ],
    },
    {
        "id": "portability",
        "prompt": "Do you need to stay portable across providers?",
        "options": [
            {"value": "yes", "label": "Yes, avoid vendor lock-in"},
            {"value": "no", "label": "Being AWS-native is fine"},
        ],
    },
    {
        "id": "commitment",
        "prompt": "Can you commit for one to three years for a discount?",
        "options": [
            {"value": "yes", "label": "Yes, we can commit"},
            {"value": "no", "label": "We prefer flexibility"},
        ],
    },
    {
        "id": "requests_per_month",
        "prompt": "Roughly how many requests per month do you expect?",
        "type": "number",
        "unit": "requests",
    },
    {
        "id": "storage_gb",
        "prompt": "How much data will you store?",
        "type": "number",
        "unit": "GB",
    },
    {
        "id": "transfer_gb",
        "prompt": "How much data will you send to the internet each month?",
        "type": "number",
        "unit": "GB",
    },
]


def recommend(answers: dict) -> dict:
    survivors = _eliminate(answers)
    priced = [
        {"archetype": code, "monthly_cost": round(_cost(code, answers), 2)}
        for code in sorted(survivors)
    ]
    priced.sort(key=lambda option: option["monthly_cost"])
    winner = priced[0]
    code = winner["archetype"]
    return {
        "archetype": code,
        "name": ARCHETYPES[code]["name"],
        "services": ARCHETYPES[code]["services"],
        "monthly_cost": winner["monthly_cost"],
        "config": _config(code, answers),
        "candidates": priced,
    }


def _eliminate(answers: dict) -> set[str]:
    candidates = set(ARCHETYPES)
    strong = candidates - _strong_removed(answers)
    reduced = strong - _lighter_removed(answers)
    if reduced:
        return reduced
    if strong:
        return strong
    return candidates


def _strong_removed(answers: dict) -> set[str]:
    removed: set[str] = set()
    if answers.get("stage") == "existing":
        if answers.get("current_stack") == "server":
            removed.add("serverless")
        elif answers.get("current_stack") == "functions":
            removed.update({"single_server", "classic", "fargate", "eks"})
    if answers.get("high_availability") == "yes":
        removed.add("single_server")
    if answers.get("traffic_pattern") == "spiky":
        removed.add("single_server")
    if answers.get("traffic_volume") == "high":
        removed.add("single_server")
    if answers.get("ops_capacity") == "managed":
        removed.update({"single_server", "classic", "eks"})
    elif answers.get("ops_capacity") == "containers":
        removed.add("eks")
    if answers.get("request_duration") == "long":
        removed.add("serverless")
    if answers.get("portability") == "yes":
        removed.update({"serverless", "fargate"})
    return removed


def _lighter_removed(answers: dict) -> set[str]:
    removed: set[str] = set()
    if answers.get("stage") == "existing" and answers.get("current_stack") == "server":
        removed.update({"fargate", "eks"})
    if (
        answers.get("stage") == "existing"
        and answers.get("current_stack") == "containers"
    ):
        removed.update({"single_server", "classic", "serverless"})
    if answers.get("traffic_volume") == "low":
        removed.add("eks")
    if answers.get("team_size") == "solo":
        removed.add("eks")
    if answers.get("structure") == "monolith":
        removed.add("eks")
    if (
        answers.get("team_size") == "several"
        or answers.get("structure") == "microservices"
    ):
        removed.add("single_server")
    return removed


def _cost(code: str, answers: dict) -> float:
    if code == "single_server":
        return _cost_single_server(answers)
    if code == "classic":
        return _cost_classic(answers)
    if code == "fargate":
        return _cost_fargate(answers)
    if code == "eks":
        return _cost_eks(answers)
    return _cost_serverless(answers)


def _volume(answers: dict) -> str:
    return answers.get("traffic_volume", "moderate")


def _storage_gb(answers: dict) -> float:
    return float(answers.get("storage_gb", 0))


def _transfer_gb(answers: dict) -> float:
    return float(answers.get("transfer_gb", 0))


def _requests(answers: dict) -> float:
    return float(answers.get("requests_per_month", 0))


def _ec2_month(volume: str) -> float:
    return PRICES["ec2_hour"][EC2_SIZE[volume]] * HOURS_PER_MONTH


def _rds_month(volume: str, multi_az: bool) -> float:
    tier = "multi_az" if multi_az else "single_az"
    return PRICES["rds_hour"][tier][RDS_SIZE[volume]] * HOURS_PER_MONTH


def _rds_storage(gb: float, multi_az: bool) -> float:
    tier = "multi_az" if multi_az else "single_az"
    return PRICES["rds_gp3_gb_month"][tier] * gb


def _alb_month() -> float:
    return PRICES["alb"]["hour"] * HOURS_PER_MONTH


def _nat_month(transfer_gb: float) -> float:
    return (
        PRICES["nat_gateway"]["hour"] * HOURS_PER_MONTH
        + PRICES["nat_gateway"]["gb_processed"] * transfer_gb
    )


def _s3(gb: float) -> float:
    return PRICES["s3_standard"]["gb_month"] * gb


def _fargate_month(volume: str, tasks: int) -> float:
    vcpu, memory = FARGATE_SIZE[volume]
    per_task = (
        PRICES["fargate"]["vcpu_hour"] * vcpu + PRICES["fargate"]["gb_hour"] * memory
    )
    return per_task * tasks * HOURS_PER_MONTH


def _cost_single_server(answers: dict) -> float:
    volume = _volume(answers)
    return (
        _ec2_month(volume)
        + _rds_month(volume, False)
        + _rds_storage(_storage_gb(answers), False)
        + _s3(CLIENT_ASSETS_GB)
    )


def _cost_classic(answers: dict) -> float:
    volume = _volume(answers)
    return (
        2 * _ec2_month(volume)
        + _alb_month()
        + _rds_month(volume, True)
        + _rds_storage(_storage_gb(answers), True)
        + _nat_month(_transfer_gb(answers))
        + _s3(CLIENT_ASSETS_GB)
    )


def _cost_fargate(answers: dict) -> float:
    volume = _volume(answers)
    multi_az = answers.get("high_availability") == "yes"
    tasks = 2 if multi_az else 1
    return (
        _fargate_month(volume, tasks)
        + _alb_month()
        + _rds_month(volume, multi_az)
        + _rds_storage(_storage_gb(answers), multi_az)
        + _nat_month(_transfer_gb(answers))
        + _s3(CLIENT_ASSETS_GB)
    )


def _cost_eks(answers: dict) -> float:
    volume = _volume(answers)
    return (
        PRICES["eks"]["cluster_hour"] * HOURS_PER_MONTH
        + 2 * _ec2_month(volume)
        + _alb_month()
        + _rds_month(volume, True)
        + _rds_storage(_storage_gb(answers), True)
        + _nat_month(_transfer_gb(answers))
        + _s3(CLIENT_ASSETS_GB)
    )


def _cost_serverless(answers: dict) -> float:
    requests = _requests(answers)
    reads = requests * READ_SHARE
    writes = requests * (1 - READ_SHARE)
    compute_gb_seconds = requests * LAMBDA_DURATION_S * LAMBDA_MEMORY_GB
    lambda_cost = (
        requests * PRICES["lambda"]["request"]
        + compute_gb_seconds * PRICES["lambda"]["gb_second"]
    )
    api_cost = requests / 1_000_000 * PRICES["api_gateway"]["http_per_million"]
    dynamo_cost = (
        reads / 1_000_000 * PRICES["dynamodb"]["on_demand_read_per_million"]
        + writes / 1_000_000 * PRICES["dynamodb"]["on_demand_write_per_million"]
        + _storage_gb(answers) * PRICES["dynamodb"]["storage_gb_month"]
    )
    cloudfront_cost = (
        _transfer_gb(answers) * PRICES["cloudfront"]["data_out_gb"]
        + requests / 10_000 * PRICES["cloudfront"]["https_per_10000"]
    )
    return (
        lambda_cost + api_cost + dynamo_cost + cloudfront_cost + _s3(CLIENT_ASSETS_GB)
    )


def _config(code: str, answers: dict) -> dict:
    config: dict[str, str] = {}
    volume = _volume(answers)
    steady = answers.get("traffic_pattern") in ("flat", "steady")
    commit = answers.get("commitment") == "yes"
    if code in ("single_server", "classic", "eks"):
        config["instance_size"] = EC2_SIZE[volume]
    if code == "fargate":
        vcpu, memory = FARGATE_SIZE[volume]
        config["task_size"] = f"{vcpu} vCPU, {memory} GB"
    if code in ("single_server", "classic", "fargate", "eks"):
        config["database"] = RDS_SIZE[volume]
        config["rds_multi_az"] = (
            "yes"
            if code in ("classic", "eks") or answers.get("high_availability") == "yes"
            else "no"
        )
        config["pricing_model"] = "Savings Plans" if steady and commit else "On-Demand"
    if code == "serverless":
        config["dynamodb_capacity"] = (
            "provisioned" if answers.get("traffic_pattern") == "steady" else "on-demand"
        )
    return config
