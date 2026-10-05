# ------------------------------------------------------------
# Cell 2 of 2: install what is missing, build the CRM, check keys.
# ------------------------------------------------------------
from revenue_copilot import config

PROVIDER = config.prepare(with_local_model=False)

from revenue_copilot import crm, evaluation, data as rc_data   # noqa: E402
from revenue_copilot.hf_adapter import ChatHFInference          # noqa: E402
import json                                                    # noqa: E402
import pandas as pd                                            # noqa: E402

pd.set_option("display.max_colwidth", 70)
pd.set_option("display.width", 180)

print(f"\n>>> Active provider: {PROVIDER}")
print("Session 2 uses a hosted model when a key is present, otherwise MockSalesLLM.")
