"""
GitHub Profile README Auto-Updater
Fetches live data from GitHub API and regenerates README.md
"""

import os
import re
import json
import requests
from datetime import datetime, timezone
from dateutil import parser as dateparser

# ── Config ────────────────────────────────────────────────────────────────────
USERNAME     = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
GH_TOKEN     = os.environ.get("GITHUB_TOKEN", "")
WAKA_KEY     = os.environ.get("WAKATIME_API_KEY", "")
TEMPLATE_PATH = "README.template.md"
OUTPUT_PATH   = "README.md"

HEADERS = {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}

# ── GitHub API helpers ────────────────────────────────────────────────────────

def gh_get(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def get_user_stats():
    data = gh_get(f"https://api.github.com/users/{USERNAME}")
    return {
        "name":        data.get("name") or USERNAME,
        "bio":         data.get("bio") or "",
        "followers":   data.get("followers", 0),
        "following":   data.get("following", 0),
        "public_repos":data.get("public_repos", 0),
        "location":    data.get("location") or "",
        "blog":        data.get("blog") or "",
        "avatar_url":  data.get("avatar_url", ""),
        "created_at":  data.get("created_at", ""),
    }

def get_top_repos(limit=6):
    repos = gh_get(
        f"https://api.github.com/users/{USERNAME}/repos",
        params={"sort": "stars", "per_page": 100, "type": "owner"}
    )
    # Filter forks, sort by stars
    owned = [r for r in repos if not r.get("fork")]
    owned.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
    return owned[:limit]

def get_recent_activity(limit=5):
    events = gh_get(
        f"https://api.github.com/users/{USERNAME}/events/public",
        params={"per_page": 30}
    )
    lines = []
    seen  = set()
    type_map = {
        "PushEvent":             "🚀 Pushed to",
        "CreateEvent":           "✨ Created",
        "PullRequestEvent":      "🔀 PR in",
        "IssuesEvent":           "💬 Opened issue in",
        "WatchEvent":            "⭐ Starred",
        "ForkEvent":             "🍴 Forked",
        "IssueCommentEvent":     "💬 Commented in",
        "ReleaseEvent":          "🏷️ Released in",
        "PullRequestReviewEvent":"👀 Reviewed PR in",
    }
    for e in events:
        if len(lines) >= limit:
            break
        etype = e.get("type", "")
        repo  = e.get("repo", {}).get("name", "")
        key   = f"{etype}:{repo}"
        if key in seen:
            continue
        seen.add(key)
        label = type_map.get(etype)
        if label:
            ts  = dateparser.parse(e["created_at"])
            ago = _time_ago(ts)
            lines.append(f"- {label} **[{repo}](https://github.com/{repo})** — {ago}")
    return "\n".join(lines)

def get_language_stats(limit=6):
    repos = gh_get(
        f"https://api.github.com/users/{USERNAME}/repos",
        params={"per_page": 100, "type": "owner"}
    )
    lang_bytes = {}
    for r in repos:
        if r.get("fork"):
            continue
        lang = r.get("language")
        if lang:
            lang_bytes[lang] = lang_bytes.get(lang, 0) + (r.get("size", 0))
    total = sum(lang_bytes.values()) or 1
    sorted_langs = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:limit]
    bars = []
    for lang, size in sorted_langs:
        pct = round(size / total * 100, 1)
        bar = _progress_bar(pct)
        bars.append(f"| {lang:<20} | `{bar}` | {pct:>5}% |")
    return "\n".join(bars)

def get_wakatime_stats():
    if not WAKA_KEY:
        return "_Connect WakaTime for coding-time stats (see Setup section)_"
    try:
        import base64
        key_b64 = base64.b64encode(WAKA_KEY.encode()).decode()
        r = requests.get(
            "https://wakatime.com/api/v1/users/current/stats/last_7_days",
            headers={"Authorization": f"Basic {key_b64}"},
            timeout=15
        )
        data = r.json().get("data", {})
        total = data.get("human_readable_total_including_other_language", "N/A")
        daily = data.get("human_readable_daily_average_including_other_language", "N/A")
        langs = data.get("languages", [])[:4]
        lang_str = ", ".join(f"{l['name']} ({l['text']})" for l in langs)
        return (
            f"⏱️ **{total}** coded this week  •  "
            f"📅 **{daily}** / day  \n"
            f"🔤 Top languages: {lang_str}"
        )
    except Exception:
        return "_WakaTime stats unavailable right now_"

def get_contribution_graph_url():
    # Uses the GitHub contribution graph SVG (dark + light versions available)
    return (
        f"[![{USERNAME}'s GitHub contribution graph]"
        f"(https://github-readme-activity-graph.vercel.app/graph"
        f"?username={USERNAME}&theme=react-dark&hide_border=true)]"
        f"(https://github.com/{USERNAME})"
    )

def get_streak_badge():
    return (
        f"[![GitHub Streak]"
        f"(https://streak-stats.demolab.com?user={USERNAME}"
        f"&theme=transparent&hide_border=true&date_format=M%20j%5B%2C%20Y%5D)]"
        f"(https://git.io/streak-stats)"
    )

def get_stats_card():
    return (
        f"![{USERNAME}'s GitHub stats]"
        f"(https://github-readme-stats.vercel.app/api"
        f"?username={USERNAME}"
        f"&show_icons=true&theme=transparent&hide_border=true"
        f"&count_private=true&include_all_commits=true)"
    )

def get_top_langs_card():
    return (
        f"![Top Langs]"
        f"(https://github-readme-stats.vercel.app/api/top-langs"
        f"?username={USERNAME}"
        f"&layout=compact&theme=transparent&hide_border=true"
        f"&langs_count=8)"
    )

def get_trophy_row():
    return (
        f"[![trophy](https://github-profile-trophy.vercel.app/"
        f"?username={USERNAME}"
        f"&theme=flat&no-frame=true&column=7&rank=SECRET,SSS,SS,S,AAA,AA,A,B,C)]"
        f"(https://github.com/ryo-ma/github-profile-trophy)"
    )

# ── Utilities ─────────────────────────────────────────────────────────────────

def _time_ago(dt: datetime) -> str:
    now   = datetime.now(timezone.utc)
    delta = now - dt.astimezone(timezone.utc)
    s     = int(delta.total_seconds())
    if s < 60:       return "just now"
    if s < 3600:     return f"{s//60}m ago"
    if s < 86400:    return f"{s//3600}h ago"
    return f"{s//86400}d ago"

def _progress_bar(pct: float, width: int = 20) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)

def _years_on_github(created_at: str) -> str:
    if not created_at:
        return ""
    since = dateparser.parse(created_at)
    years = (datetime.now(timezone.utc) - since.astimezone(timezone.utc)).days // 365
    return f"{years}+ years" if years else "< 1 year"

def build_top_repos_section(repos):
    lines = []
    for r in repos:
        stars   = r.get("stargazers_count", 0)
        forks   = r.get("forks_count", 0)
        desc    = r.get("description") or ""
        lang    = r.get("language") or ""
        url     = r.get("html_url", "")
        name    = r.get("name", "")
        stars_s = f"⭐ {stars}" if stars else ""
        forks_s = f"🍴 {forks}" if forks else ""
        meta    = "  ".join(filter(None, [lang, stars_s, forks_s]))
        lines.append(f"### [{name}]({url})")
        if desc:
            lines.append(f"{desc}")
        if meta:
            lines.append(f"\n`{meta}`\n")
    return "\n".join(lines)

# ── Template rendering ────────────────────────────────────────────────────────

def render(template: str, ctx: dict) -> str:
    for key, val in ctx.items():
        template = template.replace(f"{{{{{key}}}}}", str(val))
    return template

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Fetching data for: {USERNAME}")
    stats    = get_user_stats()
    top_repos = get_top_repos()
    ctx = {
        "USERNAME":          USERNAME,
        "NAME":              stats["name"],
        "BIO":               stats["bio"],
        "LOCATION":          stats["location"],
        "FOLLOWERS":         stats["followers"],
        "FOLLOWING":         stats["following"],
        "PUBLIC_REPOS":      stats["public_repos"],
        "YEARS_ON_GITHUB":   _years_on_github(stats["created_at"]),
        "STATS_CARD":        get_stats_card(),
        "STREAK_BADGE":      get_streak_badge(),
        "TOP_LANGS_CARD":    get_top_langs_card(),
        "TROPHY_ROW":        get_trophy_row(),
        "ACTIVITY_GRAPH":    get_contribution_graph_url(),
        "RECENT_ACTIVITY":   get_recent_activity(),
        "LANGUAGE_TABLE":    get_language_stats(),
        "WAKATIME_STATS":    get_wakatime_stats(),
        "TOP_REPOS":         build_top_repos_section(top_repos),
        "UPDATED_AT":        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    readme = render(template, ctx)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md written successfully.")

if __name__ == "__main__":
    main()
