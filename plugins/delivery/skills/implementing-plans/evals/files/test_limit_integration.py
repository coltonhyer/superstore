from pathlib import Path


assert Path("/var/run/limit-integration/ready").is_file(), (
    "required external limit integration is not provisioned"
)
