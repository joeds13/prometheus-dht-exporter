prometheus-dht-exporter
================================================================================

Collects DHT/envirophat environmental sensor readings and exports them as Prometheus metrics

## Usage

```
usage: dht-exporter.py [-h] --sensor-connection [gpio|envirophat]
                       [--sensor-version [11|22|2302]] [--sensor-pin N]
                       [--room <room name>] [--listen-port N]
```

If `--sensor-connection` is `gpio`, `--sensor-version` and `--sensor-pin` are required

## To Do

- Create build script
    - Update repo
    - Install deps
    - Check systemd unit file
    - Restart
- Daemonise properly
- Dockerise?
- Setup and packaging stuff
- Publish to PyPI?
- Rewrite in Go?
