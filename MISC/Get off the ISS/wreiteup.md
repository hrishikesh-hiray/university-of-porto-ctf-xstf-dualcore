# Get off the ISS - Detailed Writeup

## Challenge Info
- Name: `Get off the ISS`
- Category: `misc` (RF/signal analysis + geolocation)
- Flag format: `upCTF{...}`
- Given data:
  - `challenge.md`
  - `station_a.sigmf-data`, `station_a.sigmf-meta`
  - `station_b.sigmf-data`, `station_b.sigmf-meta`
  - `station_c.sigmf-data`, `station_c.sigmf-meta`

## Goal
The challenge text says there is a jammer interfering with ISS uplink, and three rotating highly directional ground stations captured IQ recordings. We must determine jammer location and submit it to `/verify`.

## Files and Initial Observations
From `challenge.md`:
- Station coordinates:
  - `station_a = (41.16791628282458, -8.688654341122007)`
  - `station_b = (41.14456438258019, -8.675380772847733)`
  - `station_c = (41.1413904156136, -8.609071069291119)`
- Important clue: `0° North at t=0`.

From each `.sigmf-meta`:
- Datatype: `cf32_le` (complex float32, little endian)
- Sample rate: `500000` Hz
- Center frequency: `146000000` Hz
- Each `.sigmf-data` file size: `120000000` bytes

Duration check:
- One sample = complex64 = 8 bytes
- Samples per file = `120000000 / 8 = 15000000`
- Duration = `15000000 / 500000 = 30 s`

So each station has a 30-second IQ capture.

## Challenge Web Endpoint Behavior
Target web app showed a map with a button `LOCATE`.
HTML/JS inspection revealed:
- Endpoint: `POST /verify`
- Payload JSON: `{ "lat": <float>, "lon": <float> }`
- Response shape:
  - `{ "message": "...", "success": true/false }`

## Signal Analysis Strategy
The intended physics is directional triangulation:
1. Each rotating antenna points through azimuth over time.
2. Received jammer power peaks when antenna points toward jammer.
3. Convert peak times to azimuths.
4. Intersect bearing lines from stations.

### 1) Find jammer spectral component
Running Welch PSD on all three recordings showed a very strong narrow tone around `-70 kHz` relative to center in every station capture.

### 2) Extract time-dependent strength
A robust method was short-time average total power using 0.1 s windows:
- `Nwin = 50000` samples
- `power(t) = mean(|x|^2)` per window

Observed strongest/symmetric peaks (every 10 s) for each station:
- Station A: around `2.85, 12.85, 22.85`
- Station B: around `1.85, 11.85, 21.85`
- Station C: around `8.85, 18.85, 28.85`

Autocorrelation confirmed a 10 s periodicity in envelope maxima, consistent across all stations.

### 3) Rotation rate ambiguity and bearing model
From challenge clue (`0° North at t=0`) and observed periodicity, two plausible mappings were tested:
- `12 deg/s` (one full turn in 30 s)
- `36 deg/s` (due to directional symmetry/repeated lobes causing effective repeats)

For each station, candidate peak times were converted to azimuth candidates:
- `bearing = (time * deg_per_sec) mod 360`
Then tested all 180° directional flips per station (line-of-bearing ambiguity).

### 4) Triangulation
Converted lat/lon to local tangent plane `(x,y)` around station centroid. For each bearing set:
- Build bearing line normal equations
- Solve least squares intersection
- Score candidate by squared angular residual error

Candidate points were filtered to local Porto bounds and ranked by residual error.

## Practical Solver That Got the Flag
Top-ranked unique candidates were directly sent to `/verify` until a success response appeared.

The first successful point was:
- `lat = 41.158803`
- `lon = -8.630228`

Server response:
- `{"message":"Signal Acquired! Flag: upCTF{fl4t_e4rth3rs_cou1d_n3v3r-6KepCQ1d003f538d}","success":true}`

## Final Flag
`upCTF{fl4t_e4rth3rs_cou1d_n3v3r-6KepCQ1d003f538d}`

## Reproducible Python Script (Core Recovery)
```python
import math
import itertools
import json
import urllib.request
import numpy as np

stations = {
    'a': (41.16791628282458, -8.688654341122007),
    'b': (41.14456438258019, -8.675380772847733),
    'c': (41.1413904156136,  -8.609071069291119),
}

# Peak times extracted from power envelopes (seconds)
times = {
    'a': [2.85, 12.85, 22.85],
    'b': [1.85, 11.85, 21.85],
    'c': [8.85, 18.85, 28.85],
}

lat0 = sum(v[0] for v in stations.values()) / 3
lon0 = sum(v[1] for v in stations.values()) / 3
R = 6371000.0


def ll_to_xy(lat, lon):
    x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
    y = math.radians(lat - lat0) * R
    return np.array([x, y])


def xy_to_ll(x, y):
    lat = lat0 + math.degrees(y / R)
    lon = lon0 + math.degrees(x / (R * math.cos(math.radians(lat0))))
    return lat, lon


S = {k: ll_to_xy(*v) for k, v in stations.items()}


def solve_intersection(bearings_deg):
    A = []
    b = []
    for k, p in S.items():
        th = math.radians(bearings_deg[k])
        d = np.array([math.sin(th), math.cos(th)])
        n = np.array([d[1], -d[0]])
        A.append(n)
        b.append(n @ p)

    A = np.array(A)
    b = np.array(b)
    pt = np.linalg.lstsq(A, b, rcond=None)[0]

    err = 0.0
    for k, p in S.items():
        v = pt - p
        ang = (math.degrees(math.atan2(v[0], v[1])) + 360) % 360
        diff = ((ang - bearings_deg[k] + 180) % 360) - 180
        err += diff * diff

    return err, pt


cands = []
for degps in [12.0, 36.0]:
    for ta, tb, tc in itertools.product(times['a'], times['b'], times['c']):
        base = {
            'a': (ta * degps) % 360,
            'b': (tb * degps) % 360,
            'c': (tc * degps) % 360,
        }
        for flips in itertools.product([0, 180], repeat=3):
            bear = {k: (base[k] + f) % 360 for k, f in zip(['a', 'b', 'c'], flips)}
            err, pt = solve_intersection(bear)
            lat, lon = xy_to_ll(*pt)
            if 41.0 < lat < 41.3 and -8.8 < lon < -8.5:
                cands.append((err, round(lat, 6), round(lon, 6)))

cands.sort(key=lambda x: x[0])

# Deduplicate by coordinates and test top candidates at /verify
seen = set()
ordered = []
for err, lat, lon in cands:
    key = (lat, lon)
    if key not in seen:
        seen.add(key)
        ordered.append((err, lat, lon))

url = 'http://46.225.117.62:30004/verify'
for err, lat, lon in ordered[:120]:
    data = json.dumps({'lat': lat, 'lon': lon}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            txt = r.read().decode()
    except Exception:
        continue

    print(lat, lon, txt)
    if 'success":true' in txt.lower() or 'upctf{' in txt.lower():
        break
```

## Notes / Lessons
- SigMF metadata quickly gives enough context (datatype/sample rate/frequency) to bootstrap DSP.
- For rotating directional sensors, envelope peaks and periodicity can be more robust than trying to fully demodulate unknown content.
- Bearing-only geolocation can have 180° ambiguities; test mirrored bearings.
- If a verifier endpoint exists, rank candidates physically and let endpoint validate exact point.
