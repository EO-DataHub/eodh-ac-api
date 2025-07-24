from __future__ import annotations

import json
from pathlib import Path

template = """
[default]
aws_access_key_id={accessKeyId}
aws_secret_access_key={secretAccessKey}
aws_session_token={sessionToken}
"""

OUT_PATH = Path("~/.aws/credentials")


def main() -> None:
    cred_file = Path("tmp_s3_credentials.json")
    data = json.loads(cred_file.read_text(encoding="utf-8"))
    output_content = template.format(**data)
    OUT_PATH.write_text(output_content, encoding="utf-8")


if __name__ == "__main__":
    main()
