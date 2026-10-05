## 1. Setup and the CRM

### 1.1 Getting the teaching package

Everything the scenario needs — the synthetic CRM, the 13 tools, the offline
mock model — lives in a small Python package called `revenue_copilot`. Run the
two cells below.

🔑 **If you are in Colab**, you first need the files. Set `REPO_URL` to your
class repository, or upload the `revenue_copilot` folder with the file panel on
the left (`Session → Files → Upload`). If you do neither, the notebook still
works: the setup cell falls back to generating the data itself.

⚠️ **Do not skip the first cell.** On Colab it upgrades the pre-installed
`langchain`, which is usually several major versions behind.
