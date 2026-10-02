#!/usr/bin/env python3
"""Bygger webbplatsen till docs/, som GitHub Pages publicerar.

Innehållet ligger i content/sv och content/en; sidhuvud, sidfot och
språkväxling är gemensamma och ligger här. Kör: python3 build.py
"""
import html, pathlib, shutil

root = pathlib.Path(__file__).resolve().parent
out = root / 'docs'

SITE = 'https://focus.vestigio.se'
EMAIL = 'focus@vestigio.se'
ORG = {
    'name': 'Vestigio',
    'number': '802504-2188',
    'address': 'c/o Knackeriet, Sankt Paulsgatan 25, 118 48 Stockholm',
}

# (nyckel, svensk sökväg, engelsk sökväg)
PAGES = [
    ('home', '/', '/en/'),
    ('observers', '/observatorer/', '/en/observers/'),
    ('support', '/support/', '/en/support/'),
    ('privacy', '/integritet/', '/en/privacy/'),
]

# Adresser som bytts ut: gammal → ny.
REDIRECTS = {
    '/kommuner/': '/observatorer/',
    '/en/municipalities/': '/en/observers/',
}

TEXT = {
    'sv': {
        'lang_name': 'English', 'other': 'en',
        'nav': {'observers': 'För observatörer', 'support': 'Support',
                'privacy': 'Integritet'},
        'titles': {
            'home': 'FOCUS – app för klassrumsobservationer',
            'observers': 'Dela data med andra observatörer – FOCUS',
            'support': 'Support – FOCUS',
            'privacy': 'Integritetspolicy – FOCUS',
        },
        'description': 'FOCUS är en app för systematiska '
                       'klassrumsobservationer: tidtagning, kodning, '
                       'sammanfattning, sambedömning och gemensamt '
                       'kalkylark.',
        'footer_by': 'FOCUS utvecklas av',
        'org_number': 'Org.nr',
        'contact': 'Kontakt',
        'skip': 'Till innehållet',
    },
    'en': {
        'lang_name': 'Svenska', 'other': 'sv',
        'nav': {'observers': 'For observers', 'support': 'Support',
                'privacy': 'Privacy'},
        'titles': {
            'home': 'FOCUS – classroom observation app',
            'observers': 'Share data with other observers – FOCUS',
            'support': 'Support – FOCUS',
            'privacy': 'Privacy Policy – FOCUS',
        },
        'description': 'FOCUS is an app for systematic classroom '
                       'observations: timing, coding, summaries, '
                       'co-observation and a shared spreadsheet.',
        'footer_by': 'FOCUS is developed by',
        'org_number': 'Reg. no.',
        'contact': 'Contact',
        'skip': 'Skip to content',
    },
}

LAYOUT = '''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{site}{path}">
<link rel="alternate" hreflang="sv" href="{site}{sv_path}">
<link rel="alternate" hreflang="en" href="{site}{en_path}">
<link rel="icon" href="/assets/img/icon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/icon-180.png">
<meta name="theme-color" content="#395801">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{home}">FOCUS</a>
    <nav class="nav" aria-label="{nav_label}">
{nav}
      <a class="lang" href="{other_path}" hreflang="{other}" lang="{other}">{lang_name}</a>
    </nav>
  </div>
</header>
{body}
<footer>
  <div class="wrap">
    <div>
      <p>{footer_by} <strong>{org_name}</strong></p>
      <p>{org_number} {org_nr} · {org_address}</p>
    </div>
    <div>
      <p>{contact}: <a href="mailto:{email}">{email}</a></p>
      <p><a href="{privacy}">{privacy_label}</a></p>
    </div>
  </div>
</footer>
</body>
</html>
'''


def page_path(key, lang):
    for k, sv, en in PAGES:
        if k == key:
            return sv if lang == 'sv' else en
    raise KeyError(key)


def build():
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(root / 'assets', out / 'assets')
    shutil.copytree(root / 'files', out / 'files')

    for lang, text in TEXT.items():
        for key, sv_path, en_path in PAGES:
            path = sv_path if lang == 'sv' else en_path
            other_path = en_path if lang == 'sv' else sv_path
            body = (root / 'content' / lang / f'{key}.html').read_text()
            body = (body.replace('{{email}}', EMAIL)
                        .replace('{{org_name}}', ORG['name'])
                        .replace('{{org_number}}', ORG['number'])
                        .replace('{{org_address}}', ORG['address']))
            for k, _, _ in PAGES:
                body = body.replace('{{link:%s}}' % k, page_path(k, lang))
            nav = '\n'.join(
                '      <a href="%s"%s>%s</a>' % (
                    page_path(k, lang),
                    ' aria-current="page"' if k == key else '',
                    label)
                for k, label in text['nav'].items())
            html_text = LAYOUT.format(
                lang=lang, title=html.escape(text['titles'][key]),
                description=html.escape(text['description']),
                site=SITE, path=path, sv_path=sv_path, en_path=en_path,
                home=page_path('home', lang), nav=nav,
                nav_label='Meny' if lang == 'sv' else 'Menu',
                other_path=other_path, other=text['other'],
                lang_name=text['lang_name'], body=body,
                footer_by=text['footer_by'], org_name=ORG['name'],
                org_number=text['org_number'], org_nr=ORG['number'],
                org_address=ORG['address'], contact=text['contact'],
                email=EMAIL, privacy=page_path('privacy', lang),
                privacy_label=text['nav']['privacy'],
            )
            target = out / path.strip('/') / 'index.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html_text)

    # Sidan som visas för adresser som inte finns, på båda språken.
    not_found = LAYOUT.format(
        lang='sv', title='Sidan finns inte – FOCUS',
        description=html.escape(TEXT['sv']['description']),
        site=SITE, path='/', sv_path='/', en_path='/en/', home='/',
        nav='', nav_label='Meny', other_path='/en/', other='en', lang_name='English',
        body='''<main><div class="wrap narrow">
<h2>Sidan finns inte</h2>
<p>Adressen leder ingenstans. Gå till <a href="/">startsidan</a>.</p>
<p lang="en">This page does not exist. Go to the <a href="/en/">home page</a>.</p>
</div></main>''',
        footer_by=TEXT['sv']['footer_by'], org_name=ORG['name'],
        org_number=TEXT['sv']['org_number'], org_nr=ORG['number'],
        org_address=ORG['address'], contact=TEXT['sv']['contact'],
        email=EMAIL, privacy='/integritet/', privacy_label='Integritet')
    (out / '404.html').write_text(not_found)

    # Gamla adresser skickas vidare, så att länkar som spridits fungerar.
    for old, new in REDIRECTS.items():
        target = out / old.strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            '<!doctype html><meta charset="utf-8">'
            f'<title>FOCUS</title><link rel="canonical" href="{SITE}{new}">'
            f'<meta http-equiv="refresh" content="0; url={new}">'
            f'<a href="{new}">{SITE}{new}</a>\n')
    (out / 'CNAME').write_text('focus.vestigio.se\n')
    (out / '.nojekyll').write_text('')
    print('Byggt:', sum(1 for _ in out.rglob('index.html')), 'sidor')


if __name__ == '__main__':
    build()
