# Personal run configuration

Copy `cfd-history.example.json` to `local/cfd-history.json` and enter your case directories, mesh cell counts and labels. `host: null` reads local files. For SSH, enter your own alias and remote absolute `directory`, `scripts_directory` and `policy_path`. The remote host needs Python, `check_cfd_pair_v4.py` and the matching acceptance JSON.

```sh
python3 08_Scripts/collect_cfd_numerical_history_v5.py \
  --config local/cfd-history.json --output local/cfd-checks.json
```

This reads existing logs and heat records without advancing the solver. Keep personal configuration and outputs in ignored `local/`. Select and review result files explicitly before publishing them.

Query hosts supplied by the person running the job:

```sh
python3 08_Scripts/inspect_compute_hosts.py --hosts my-cpu-host my-gpu-host \
  --output local/compute-hosts.json
```

Mesh, solver and fixed-field heat-budget runners require explicit directories, image, process count and CPU set. Check `--help` and follow the host's scheduling rules. Example cell counts come from the existing light trial; replace them with the actual mesh counts for your case.
