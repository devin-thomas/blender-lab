"""Pure typed control admission shared by native, CLI and recipe surfaces."""
import math
from . import catalog


def validate(lab, supplied=None, base=None):
    schema = catalog.BY_ID[lab]['controls']
    fields = {item['name']: item for item in schema}
    if supplied is not None and not isinstance(supplied, dict):
        raise ValueError('Controls must be a JSON object keyed by declared control name')
    supplied = {} if supplied is None else supplied
    if any(not isinstance(key, str) for key in supplied):
        raise ValueError('Control names must be strings')
    if base is not None and not isinstance(base, dict):
        raise ValueError('Stored controls must be a JSON object')
    unknown = set(supplied) - set(fields)
    if unknown:
        raise ValueError(f'Unknown controls for {lab}: {sorted(unknown)}')
    result = {name: (base[name] if base and name in base else item['default'])
              for name, item in fields.items()}
    result.update(supplied)
    for name, item in fields.items():
        value, kind = result[name], item['type']
        if kind in ('number', 'integer'):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f'{name} must be a finite {kind}')
            if kind == 'integer' and not isinstance(value, int):
                raise ValueError(f'{name} must be an integer')
            if 'minimum' in item and value < item['minimum'] or 'maximum' in item and value > item['maximum']:
                raise ValueError(f'{name} is outside {item["range"]}')
            if kind == 'number':
                result[name] = float(value)
        elif kind in ('string', 'enum'):
            if not isinstance(value, str) or not value or len(value) > 256:
                raise ValueError(f'{name} must be a nonempty bounded string')
            if kind == 'enum' and value not in item['options']:
                raise ValueError(f'{name} must be one of {item["options"]}')
        elif kind == 'boolean':
            if not isinstance(value, bool):
                raise ValueError(f'{name} must be boolean')
        else:
            raise ValueError(f'Unsupported control contract type {kind}')
    return result


def scalar_parameters(lab, value):
    """Keep existing bounded Cappy recipes useful; typed controls are authoritative."""
    result = validate(lab)
    schema = catalog.BY_ID[lab]['controls']
    numeric = next((item for item in schema if item['type'] in ('number', 'integer')), None)
    if numeric:
        default = numeric['default']
        candidate = default * value if default else max(0, value - 1)
        candidate = max(numeric.get('minimum', candidate), min(numeric.get('maximum', candidate), candidate))
        result[numeric['name']] = round(candidate) if numeric['type'] == 'integer' else candidate
    else:
        enum = next((item for item in schema if item['type'] == 'enum'), None)
        if enum:
            options = enum['options']
            result[enum['name']] = enum['default'] if value == 1 else options[min(len(options) - 1, int(value / 2 * len(options)))]
    return validate(lab, result)


def property_name(name):
    return 'blender_lab_control_' + ''.join(character.lower() if character.isalnum() else '_' for character in name)


def expose(scene, lab, params):
    """Populate native ID-property widgets without saving preferences or handlers."""
    for item in catalog.BY_ID[lab]['controls']:
        key = property_name(item['name'])
        scene[key] = params[item['name']]
        metadata = {'description': item['purpose']}
        if item['type'] in ('number', 'integer'):
            cast = int if item['type'] == 'integer' else float
            metadata.update({key: cast(item[key]) for key in ('minimum', 'maximum') if key in item})
            metadata = {({'minimum': 'min', 'maximum': 'max'}.get(key, key)): value for key, value in metadata.items()}
        scene.id_properties_ui(key).update(**metadata)


def pending(scene, lab):
    return validate(lab, {item['name']: scene[property_name(item['name'])]
                          for item in catalog.BY_ID[lab]['controls']})
