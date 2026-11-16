#!/usr/bin/env python3
"""Render the last seven days of Wakapi language statistics as an SVG."""
import base64
import html
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = 'https://wakapi.universalwill.org/api/compat/wakatime/v1/users/current/stats/last_7_days'
COLORS = ('#cba6f7', '#89b4fa', '#94e2d5', '#a6e3a1', '#f9e2af', '#fab387', '#f38ba8', '#89dceb')


def escape(value):
    return html.escape(str(value), quote=True)


def main():
    key = os.environ.get('WAKAPI_API_KEY')
    if not key:
        raise SystemExit('WAKAPI_API_KEY is missing')
    auth = base64.b64encode(key.encode()).decode()
    request = Request(URL, headers={'Authorization': f'Basic {auth}', 'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)['data']
    except (HTTPError, URLError, ValueError, KeyError) as error:
        raise SystemExit(f'Could not retrieve Wakapi statistics: {type(error).__name__}') from None
    if data.get('status') != 'ok' or not isinstance(data.get('languages'), list):
        raise SystemExit('Wakapi statistics are unavailable or incomplete')

    languages = data['languages'][:8]
    height = 80 + max(len(languages), 1) * 34
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="540" height="{height}" viewBox="0 0 540 {height}" role="img" aria-label="Weekly coding languages">',
           f'<rect width="540" height="{height}" rx="10" fill="#1e1e2e"/>',
           '<g font-family="Segoe UI, Ubuntu, sans-serif" fill="#cdd6f4">',
           '<text x="22" y="30" font-size="16" font-weight="600">Weekly coding languages</text>',
           f'<text x="22" y="52" font-size="12" fill="#a6adc8">{escape(data.get("human_readable_total", ""))} · last 7 days</text>']
    if not languages:
        svg.append('<text x="22" y="94" font-size="14" fill="#a6adc8">No coding activity recorded this week.</text>')
    for index, language in enumerate(languages):
        y = 79 + index * 34
        percent = max(0.0, min(100.0, float(language.get('percent', 0))))
        color = COLORS[index % len(COLORS)]
        svg.extend([f'<text x="22" y="{y + 11}" font-size="13">{escape(language.get("name", "Unknown"))}</text>',
                    f'<text x="518" y="{y + 11}" font-size="12" fill="#bac2de" text-anchor="end">{escape(language.get("text", ""))} · {percent:.1f}%</text>',
                    f'<rect x="22" y="{y + 17}" width="496" height="7" rx="3.5" fill="#45475a"/>',
                    f'<rect x="22" y="{y + 17}" width="{496 * percent / 100:.2f}" height="7" rx="3.5" fill="{color}"/>'])
    svg.append('</g></svg>')
    path = Path('images/wakapi_weekly.svg')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(svg) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
