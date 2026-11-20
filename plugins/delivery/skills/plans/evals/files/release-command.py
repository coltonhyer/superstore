def release_command(record):
    return f"publish {record['name']}@{record['version']}"
