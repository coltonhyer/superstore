# RECORD-1 recovery state

- Verified change: the unrecorded `record.py` change is in the current working copy.
- Verification: `python3 test_record.py` exited 0 for the current workspace.
- Recording attempt: `jj commit -m 'record RECORD-1'` was rejected by the
  repository's commit policy; it must not be retried or worked around.
- Scratch: this execution-state file remains pending recovery.
