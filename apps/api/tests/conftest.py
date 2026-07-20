import os


# Tests must never call a paid external model. Local development keeps the
# provider enabled in apps/api/.env; the test process explicitly disables it.
os.environ["AI_ENABLED"] = "false"
