# RECORD-1 recovery state

- Verified change: the unrecorded `record.py` change is in the current working copy.
- Verification: `python3 test_record.py` exited 0 for the current workspace.
- Recording attempt: `jj commit -m 'record RECORD-1'` was rejected by the
  repository recorder because storage is temporarily unavailable.
- Scratch: this execution-state file remains pending recovery.
