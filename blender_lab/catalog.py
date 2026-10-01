"""Read the shipped capability atlas without importing optional adapters."""
import json
from pathlib import Path


def load():
    folder = Path(__file__).resolve().parent
    source = folder / 'catalog.json'
    if not source.is_file():
        source = folder.parent / 'catalog.json'
    document = json.loads(source.read_text(encoding='utf-8'))
    entries = document['experiments']
    ids = [entry['id'] for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError('Capability catalog contains duplicate IDs')
    return entries


ENTRIES = load()
BY_ID = {entry['id']: entry for entry in ENTRIES}
CATEGORIES = sorted({entry.get('category', 'Foundation') for entry in ENTRIES})


def filtered(search='', category='ALL', available=None):
    query = search.strip().casefold()
    return [entry for entry in ENTRIES
            if (category == 'ALL' or entry.get('category', 'Foundation') == category)
            and (not query or query in ' '.join(str(entry.get(key, '')) for key in
                 ('id', 'title', 'category', 'mechanism', 'moment')).casefold())
            and (available is None or entry['id'] in available)]
