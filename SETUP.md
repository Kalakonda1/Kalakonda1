# 🚀 GitHub Profile Enhancer — Setup Guide

A self-running repository that keeps your GitHub profile README fresh and
prominent automatically, every 6 hours, 24/7.

---

## What it does

| Feature | How |
|---|---|
| Live GitHub stats | GitHub Readme Stats (vercel-hosted) |
| Contribution streak | DemoLab streak-stats widget |
| Activity graph | github-readme-activity-graph |
| Recent public activity | GitHub Events API |
| Language breakdown | Aggregated from your repos |
| Coding-time stats | WakaTime API (optional) |
| Trophy showcase | github-profile-trophy |
| Auto-commit | Keeps your contribution graph active |

---

## Setup (5 minutes)

### 1 — Create your special profile repo

GitHub renders `README.md` from a repo named **exactly** your username.

```
https://github.com/new  →  Repository name: YOUR_USERNAME
```

Make it **Public** and check **Add a README file**.

### 2 — Copy these files into that repo

```
.github/workflows/update-readme.yml   ← the automation engine
scripts/update_readme.py               ← data fetcher + renderer
README.template.md                     ← your profile template
```

### 3 — Allow Actions to write to the repo

Go to **Settings → Actions → General → Workflow permissions**
and select **Read and write permissions**.

### 4 — (Optional) Add WakaTime coding-time stats

1. Sign up at https://wakatime.com and install the editor plugin.
2. Copy your API key from https://wakatime.com/settings/api-key.
3. In your repo: **Settings → Secrets → Actions → New repository secret**
   - Name: `WAKATIME_API_KEY`
   - Value: your key

### 5 — Run it for the first time

Go to **Actions → Update Profile README → Run workflow**.

Your `README.md` will be generated and committed. Done!

---

## Customising the template

Edit `README.template.md`. Available placeholders:

| Placeholder | Value |
|---|---|
| `{{NAME}}` | Your GitHub display name |
| `{{USERNAME}}` | Your GitHub username |
| `{{BIO}}` | Your GitHub bio |
| `{{LOCATION}}` | Location from your profile |
| `{{FOLLOWERS}}` | Follower count |
| `{{FOLLOWING}}` | Following count |
| `{{PUBLIC_REPOS}}` | Public repo count |
| `{{YEARS_ON_GITHUB}}` | Account age |
| `{{STATS_CARD}}` | Stats image card |
| `{{STREAK_BADGE}}` | Contribution streak widget |
| `{{TOP_LANGS_CARD}}` | Top languages card |
| `{{TROPHY_ROW}}` | Achievement trophies |
| `{{ACTIVITY_GRAPH}}` | Contribution heat-map graph |
| `{{RECENT_ACTIVITY}}` | Last 5 public events |
| `{{LANGUAGE_TABLE}}` | Language % breakdown table |
| `{{WAKATIME_STATS}}` | Coding time (if key provided) |
| `{{TOP_REPOS}}` | Top 6 repos by stars |
| `{{UPDATED_AT}}` | Timestamp of last run |

---

## Changing the refresh frequency

Edit `.github/workflows/update-readme.yml` — the `cron` line:

```yaml
- cron: "0 */6 * * *"   # every 6 hours  (default)
- cron: "0 */1 * * *"   # every hour
- cron: "0 8 * * *"     # once daily at 08:00 UTC
```

---

## Troubleshooting

**README not updating?**
- Check Actions tab for error logs.
- Confirm workflow write permissions are enabled (Step 3 above).

**Stats card shows 0 / wrong data?**
- Private repo stats need `count_private=true` in the API URL — already included.
- It can take up to 24h for fresh accounts to populate.

**WakaTime section shows placeholder?**
- Verify the `WAKATIME_API_KEY` secret is set correctly.
- Your WakaTime account must be public or have a valid API key.
