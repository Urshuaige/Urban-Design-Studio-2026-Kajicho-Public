#!/usr/bin/env python3
"""Read existing CFD histories with a caller-provided local or SSH configuration.

Exports diagnostic curves, never city fields or accepted design effects.
"""
import argparse
import inspect
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def collect_runs(config):
    from check_cfd_pair_v4 import inspect_pair, numeric_rows
    policy = json.loads(Path(config['policy_path']).read_text())
    result = []
    for item in config['runs']:
        base = Path(item['directory'])
        checks = inspect_pair(base, policy)
        heat = {}
        for name in ('baseline', 'retrofit'):
            case = checks['cases'][name]
            if 'last_completed_iteration' not in case:
                raise ValueError(str(base) + ': completed solver log required for ' + name)
            last = case['last_completed_iteration']
            rows = numeric_rows(base / 'cases' / name / 'postProcessing/roofHeatBalance.csv', 6)
            heat[name] = [[i, abs(row[3]) / row[1] * 100]
                          for i, row in sorted(rows.items()) if i <= last and row[1] > 0]
            checks['cases'][name] = {k: case[k] for k in [
                'accepted', 'last_completed_iteration', 'normal_end',
                'SIMPLE_residual_control_reached', 'latest_initial_residuals',
                'solver_controls', 'heat', 'street_probe_stability']}
        checks.pop('case_directory', None)
        checks.pop('next_action', None)
        result.append({'key': item['key'], 'label': item['label'], 'cells': item['cells'],
                       'checks': checks, 'heat': heat})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if not config.get('runs'):
        raise ValueError('Configuration requires at least one run')
    host = config.get('host')
    config.setdefault('scripts_directory', '08_Scripts')
    config.setdefault('policy_path', '03_Theme_B/Simulation_V3/CFD_Acceptance_v4.json')
    if not host:
        for key in ('scripts_directory', 'policy_path'):
            config[key] = str((ROOT / config[key]).resolve())
        for run in config['runs']:
            run['directory'] = str((ROOT / run['directory']).resolve())
        runs = collect_runs(config)
    else:
        code = ('import json,sys\nfrom pathlib import Path\n'
                + 'config=' + repr(config) + '\n'
                + "sys.path.insert(0,config['scripts_directory'])\n"
                + inspect.getsource(collect_runs)
                + '\nprint(json.dumps(collect_runs(config),allow_nan=False))\n')
        remote = subprocess.run(['ssh', '-o', 'BatchMode=yes', '--', host, 'python3 -'],
                                input=code, capture_output=True, text=True, check=True, timeout=60)
        runs = json.loads(remote.stdout)
    result = {'schema_version': 1, 'snapshot_utc': datetime.now(timezone.utc).isoformat(),
              'default_run': runs[0]['key'],
              'scope': 'Diagnostic histories only; do not treat unaccepted fields as design effects',
              'source': 'OpenFOAM stage logs, native roofHeatBalance.csv and the supplied acceptance policy',
              'reproduction': ['03_Theme_B/Simulation_V3/Protocol.md', 'docs/CFD_STATUS.md'],
              'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n')
    print(json.dumps({'output': str(args.output), 'runs': [r['key'] for r in runs]}))


if __name__ == '__main__':
    main()
