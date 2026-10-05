# ------------------------------------------------------------
# Cell 2 of 2: install what is missing, build the CRM, check keys.
# ------------------------------------------------------------
from revenue_copilot import config

# Set to True if you want to download and run a model on this machine
# (~1 GB, section 3). Leave False to skip straight to the hosted model.
USE_LOCAL_MODEL = True

PROVIDER = config.prepare(with_local_model=USE_LOCAL_MODEL)

from revenue_copilot import crm, evaluation          # noqa: E402
import pandas as pd                                  # noqa: E402

pd.set_option("display.max_colwidth", 60)
pd.set_option("display.width", 180)

print(f"\n>>> Active provider: {PROVIDER}")
