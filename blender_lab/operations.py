"""Shared, bounded local operations and source-linked receipts for all adapters."""
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import math
from uuid import uuid4
from . import controls


@dataclass(frozen=True)
class Request:
    operation: str
    lab: str
    value: float = 1.0
    scene_id: str = ''
    request_id: str = field(default_factory=lambda: str(uuid4()))
    controls_json: str = ''

    def validate(self, implemented, typed=None):
        if self.operation not in ('open', 'apply', 'reset'):
            raise ValueError(f'Unsupported local operation: {self.operation}')
        if self.lab not in implemented:
            raise ValueError(f'{self.lab} is specified but has no implemented scene adapter')
        if not isinstance(self.value, (int, float)) or isinstance(self.value, bool) or isinstance(self.value, float) and not math.isfinite(self.value) or not .1 <= self.value <= 2:
            raise ValueError('Experiment value must be a finite number from 0.1 to 2.0')
        if not isinstance(self.request_id, str) or not self.request_id or len(self.request_id) > 128:
            raise ValueError('A bounded request ID is required')
        if not isinstance(self.scene_id, str) or len(self.scene_id) > 128:
            raise ValueError('Scene ID must be a bounded string')
        if self.operation != 'open' and not self.scene_id:
            raise ValueError('Apply and Reset require an explicit scene instance ID')
        if not isinstance(self.controls_json, str) or len(self.controls_json) > 16384:
            raise ValueError('Controls must be a bounded immutable JSON string')
        if self.controls_json:
            if typed is not None and self.lab not in typed:
                raise ValueError('Typed controls are available only for the new authoring adapters')
            if self.operation == 'reset':
                raise ValueError('Reset restores defaults; custom controls belong in Open or Apply')
            supplied = json.loads(self.controls_json)
            if not isinstance(supplied, dict):
                raise ValueError('Controls must be a JSON object')
            controls.validate(self.lab, supplied)


@dataclass(frozen=True)
class Receipt:
    schema_version: int
    request_id: str
    operation: str
    lab: str
    scene_id: str
    value: float
    summary: str
    timestamp: str
    controls_json: str = ''


_COMPLETED = OrderedDict()


def perform(request, scene=None):
    from . import labs
    request.validate(labs.LABS, labs.ADAPTERS)
    payload = asdict(request)
    if request.controls_json:
        payload['controls_json'] = json.loads(request.controls_json)
    signature = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    if request.request_id in _COMPLETED:
        previous_signature, receipt = _COMPLETED[request.request_id]
        if signature != previous_signature:
            raise ValueError('A request ID cannot be reused with different input or scene scope')
        return receipt
    if request.operation != 'open' and (scene is None or scene.get('blender_lab_id') != request.lab
            or not scene.get('blender_lab_owned') or scene.get('blender_lab_instance_id') != request.scene_id):
        raise ValueError('Apply and Reset require the matching active lab-owned scene instance')
    supplied = json.loads(request.controls_json) if request.controls_json else None
    if supplied is not None and request.operation == 'reset':
        raise ValueError('Reset restores defaults; custom controls belong in Open or Apply')
    params = None
    if supplied is not None:
        base = json.loads(scene['blender_lab_controls']) if request.operation == 'apply' and scene.get('blender_lab_controls') else None
        params = controls.validate(request.lab, supplied, base)
    if request.operation == 'open':
        scene = labs.build(request.lab)
        if params is None:
            labs.apply_value(scene, request.value)
        else:
            labs.apply_controls(scene, params)
    elif request.operation == 'apply':
        if params is None:
            labs.apply_value(scene, request.value)
        else:
            labs.apply_controls(scene, params)
    else:
        scene = labs.reset(scene)
    receipt = Receipt(1, request.request_id, request.operation, request.lab,
                      scene['blender_lab_instance_id'], scene['blender_lab_value'],
                      f"{request.operation.title()} {request.lab}" + (" with declared controls" if scene.get('blender_lab_controls') else f" at {scene['blender_lab_value']:.2f}"),
                      datetime.now(timezone.utc).isoformat(), scene.get('blender_lab_controls', ''))
    scene['blender_lab_receipt'] = json.dumps(asdict(receipt), sort_keys=True)
    _COMPLETED[request.request_id] = (signature, receipt)
    while len(_COMPLETED) > 128:
        _COMPLETED.popitem(last=False)
    return receipt
