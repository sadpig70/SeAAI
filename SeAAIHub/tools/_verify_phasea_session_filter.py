import sys
sys.path.insert(0, r"D:\SeAAI\SeAAIHub\tools")
from phasea_guardrails import attach_session_meta, build_session_token, message_in_active_session
session_start = 200.0
session_token = build_session_token("Synerion", session_start)
old_msg = {"id": "old-1", "from": "MockHub", "body": "legacy backlog", "ts": 100.0}
new_msg = {"id": "new-1", "from": "Aion", "body": attach_session_meta("hello", session_token, session_start), "ts": 205.0}
wrong_msg = {"id": "new-2", "from": "Aion", "body": attach_session_meta("hello", "Other_200_deadbe", session_start), "ts": 206.0}
assert message_in_active_session(old_msg, session_start, session_token) is False
assert message_in_active_session(new_msg, session_start, session_token) is True
assert message_in_active_session(wrong_msg, session_start, session_token) is False
print("Session filter verification passed.")