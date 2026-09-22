#!/usr/bin/env python3
"""Generate 100 deterministic Serum 2 .SerumPreset patches."""

from __future__ import annotations

import hashlib
import json
import random
import shutil
import struct
import zipfile
from pathlib import Path

import cbor2
import zstandard


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "Presets" / "Neon Forms 100"
ARCHIVE = ROOT / "Neon_Forms_100_Serum2.zip"
MANIFEST = ROOT / "manifest.json"

WAVETABLES = [
    "Analog/Basic Shapes.wav",
    "Analog/Basic Mg.wav",
    "Analog/Basic Mini.wav",
    "Analog/BS2 - Acid.wav",
    "Analog/BS2 - Filthy.wav",
    "Analog/BS2 - Subby Saw.wav",
    "Analog/MB Saw.wav",
    "Analog/SawRounded.wav",
    "Analog/SawRoundedToSquare.wav",
    "Analog/PWM Juno.wav",
    "Analog/PWM Mini.wav",
    "Analog/PWM Inception.wav",
    "Analog/Jno.wav",
    "Analog/MsAw.wav",
    "Analog/MiniBass.wav",
    "Analog/Acid.wav",
    "Analog/4088.wav",
    "Analog/BSOD_Square.wav",
    "Analog/MATRIXY C64.wav",
    "Digital/Reese.wav",
    "Digital/Evol Longreece.wav",
    "Digital/Gritty.wav",
    "Digital/Kream.wav",
    "Digital/Sludgecrank.wav",
    "Digital/DirtySaw.wav",
    "Digital/CrushWub.wav",
    "Digital/SubBass_1.wav",
    "Digital/Dist Bass Dropper.wav",
    "Digital/Dist C2.wav",
    "Digital/Dist Fwapper SQ.wav",
    "Digital/Wraith.wav",
    "Digital/Razor.wav",
    "Digital/Scream.wav",
    "Digital/FM_Splat.wav",
    "Digital/FM_Freak.wav",
    "Digital/FMFM.wav",
    "Digital/bipole_harmonic.wav",
]

FILTERS = [
    "L12", "L24", "L18", "MgL18", "MgL24", "LadderMg",
    "LadderAcid", "LadderEMS", "DirtyMg", "Scream3LP",
    "B12", "B24", "LN12", "LNH12", "LNH24", "Combs",
]

WARPS = [
    "kSync", "kBendPos", "kBendNeg", "kBendPosNeg",
    "kFM_OSC", "kFM_OSC2", "kRM_OSC", "kPWM",
    "kASYMPos", "kASYMNeg", "kSelfPD",
]

DISTORTIONS = [
    "kSoftClip", "kHardClip", "kSoftSat", "kTapeSat",
    "kDiode1", "kDiode2", "kLinFold", "kSinFold",
    "kOverdrive", "kStompBox", "kAsym", "kSineShaper",
]

PREFIXES = [
    "Aether", "Afterglow", "Arc", "Bloom", "Brume", "Carbon",
    "Cipher", "Contour", "Crave", "Current", "Dawn", "Drift",
    "Echo", "Ember", "Flux", "Glass", "Halo", "Haze", "Ion",
    "Lucid", "Melt", "Mirror", "Nova", "Obsidian", "Orbit",
    "Pulse", "Quartz", "Ripple", "Satin", "Signal", "Silk",
    "Static", "Vapor", "Velvet", "Vessel", "Wisp", "Chrome",
    "Prism", "Lumen", "Sway", "Shiver", "Nightglass", "Softwire",
    "Polaris", "Tidal", "Fever", "Cinder",
]

HEADS = [
    "Bloom", "Core", "Edge", "Motion", "Veil", "Frame", "Thread",
    "Form", "Trace", "Shine", "Fold", "Shape", "Drift", "Skin",
    "Pulse", "Air", "Wire", "Tone", "Field", "Phase",
]

def f(value: float, digits: int = 4) -> float:
    return round(value, digits)

def make_params(index: int, rng: random.Random) -> dict:
    wt0 = WAVETABLES[index % len(WAVETABLES)]
    wt1 = WAVETABLES[(index * 7 + 11) % len(WAVETABLES)]

    osc1_on = index % 4 != 0

    params = {
        "Oscillator0": {
            "plainParams": {
                "kParamEnable": 1.0,
                "kParamVolume": f(rng.uniform(0.66, 0.88)),
                "kParamPan": f(rng.uniform(0.44, 0.56)),
                "kParamUnison": float(rng.choice([1, 2, 3, 4, 5, 6])),
                "kParamFine": f(rng.uniform(48.0, 52.0)),
                "kParamSemitone": float(rng.choice([-12, -7, -5, 0, 5, 7, 12])),
                "kParamOctave": float(rng.choice([-1, 0, 0, 0, 1])),
                "kParamLevel": 1.0,
            },
            "WTOsc0": {
                "plainParams": {
                    "kParamWarp": f(rng.uniform(0.08, 0.82)),
                    "kParamWarp2": f(rng.uniform(0.0, 0.45)),
                    "kParamWarpMenu": WARPS[index % len(WARPS)],
                },
                "relativePathToWT": wt0,
            },
        },
        "Oscillator1": {
            "plainParams": {
                "kParamEnable": 1.0 if osc1_on else 0.0,
                "kParamVolume": f(rng.uniform(0.20, 0.58)),
                "kParamPan": f(rng.uniform(0.42, 0.58)),
                "kParamUnison": float(rng.choice([1, 2, 3, 4])),
                "kParamFine": f(rng.uniform(48.0, 52.0)),
                "kParamSemitone": float(rng.choice([-12, -7, -3, 0, 3, 7, 12])),
                "kParamOctave": 0.0,
            },
            "WTOsc1": {
                "plainParams": {
                    "kParamWarp": f(rng.uniform(0.0, 0.65)),
                    "kParamWarp2": f(rng.uniform(0.0, 0.35)),
                    "kParamWarpMenu": WARPS[(index + 5) % len(WARPS)],
                },
                "relativePathToWT": wt1,
            },
        },
        "Oscillator2": {"plainParams": "default"},
        "Oscillator3": {"plainParams": "default"},
        "Oscillator4": {"plainParams": "default"},
        "VoiceFilter0": {
            "plainParams": {
                "kParamEnable": 1.0,
                "kParamType": FILTERS[index % len(FILTERS)],
                "kParamFreq": f(rng.uniform(0.20, 0.86)),
                "kParamReso": f(rng.uniform(8.0, 50.0), 3),
                "kParamDrive": f(rng.uniform(0.0, 24.0), 3),
                "kParamVar": f(rng.uniform(0.0, 60.0), 3),
            }
        },
        "Global0": {
            "plainParams": {
                "kParamMasterVolume": f(rng.uniform(0.46, 0.70)),
                "kParamPortamentoTime": f(rng.uniform(0.0, 0.06)),
                "kParamPolyphony": float(rng.choice([8, 10, 12, 16])),
            }
        },
        "Env0": {
            "plainParams": {
                "kParamAttack": rng.choice([0.001, 0.003, 0.005, 0.010, 0.020]),
                "kParamDecay": f(rng.uniform(0.18, 0.80)),
                "kParamSustain": f(rng.uniform(0.15, 0.92)),
                "kParamRelease": f(rng.uniform(0.08, 0.60)),
            }
        },
        "Env1": {
            "plainParams": {
                "kParamAttack": f(rng.uniform(0.002, 0.04)),
                "kParamDecay": f(rng.uniform(0.08, 0.45)),
                "kParamSustain": f(rng.uniform(0.0, 0.32)),
                "kParamRelease": f(rng.uniform(0.08, 0.40)),
            }
        },
        "LFO0": {
            "plainParams": {
                "kParamRate": rng.choice([0.125, 0.25, 0.5, 1.0, 2.0]),
                "kParamMode": rng.choice(["Free", "Envelope", "Trigger"]),
                "kParamType": rng.choice(["Path", "RandomSH", "Lorenz", "Rossler"]),
                "kParamSmooth": f(rng.uniform(0.0, 0.40)),
                "kParamDelay": 0.0,
            },
            "pathData": {
                "curveVals": [0.0, f(rng.uniform(0.2, 0.8)), 1.0],
                "isOpen": True,
                "numPoints": 3,
                "xVals": [0.0, 0.5, 1.0],
                "yVals": [f(rng.uniform(0.0, 0.25)), f(rng.uniform(0.25, 0.75)), f(rng.uniform(0.75, 1.0))],
            },
        },
        "Macro0": {
            "name": HEADS[index % len(HEADS)],
            "plainParams": {"kParamValue": f(rng.uniform(55.0, 95.0), 3)},
        },
        "Macro1": {
            "name": "MOVE",
            "plainParams": {"kParamValue": f(rng.uniform(35.0, 75.0), 3)},
        },
        "Macro2": {
            "name": "WIDTH",
            "plainParams": {"kParamValue": f(rng.uniform(25.0, 65.0), 3)},
        },
        "ModSlot0": {
            "destModuleID": 0,
            "destModuleParamID": 3,
            "destModuleParamName": "kParamFreq",
            "destModuleTypeString": "VoiceFilter",
            "plainParams": {"kParamAmount": f(rng.uniform(18.0, 52.0), 3)},
            "source": [6, 0],
        },
        "ModSlot1": {
            "destModuleID": 0,
            "destModuleParamID": 0,
            "destModuleParamName": "kParamWarp",
            "destModuleTypeString": "WTOsc",
            "plainParams": {
                "kParamAmount": f(rng.uniform(10.0, 42.0), 3),
                "kParamBipolar": 1.0,
            },
            "source": [1, 0],
        },
        "FXRack0": {
            "FX": [
                {
                    "FXDistortion": {
                        "plainParams": {
                            "kParamDrive": f(rng.uniform(7.0, 42.0), 3),
                            "kParamMode": DISTORTIONS[(index * 3) % len(DISTORTIONS)],
                            "kParamWet": f(rng.uniform(32.0, 78.0), 3),
                        }
                    },
                    "kUIParamMixOrGain": 0.0,
                    "type": 0,
                }
            ]
        },
    }

    if index % 3 == 1:
        params["FXRack0"]["FX"].append(
            {
                "FXReverb": {
                    "plainParams": {
                        "kParamSize": f(rng.uniform(12.0, 55.0), 3),
                        "kParamWet": f(rng.uniform(8.0, 26.0), 3),
                    }
                },
                "kUIParamMixOrGain": 0.0,
                "type": 3,
            }
        )

    return params

def make_preset(index: int) -> tuple[str, bytes]:
    rng = random.Random(0x5EED2000 + index * 104729)
    name = f"{PREFIXES[index % len(PREFIXES)]} {HEADS[index % len(HEADS)]} {index + 1:03d}"

    payload = cbor2.dumps(make_params(index, rng))
    compressed = zstandard.ZstdCompressor(level=3).compress(payload)

    header = {
        "fileType": "SerumPreset",
        "presetName": name,
        "presetAuthor": "sjoesnds",
        "presetDescription": "Polished Serum 2 patch — clean movement, controlled stereo, restrained effects.",
        "product": "Serum2",
        "productVersion": "2.1.4",
        "tags": ["Serum 2", "Wavetable", "Movement", "Modern", "Polished"],
        "url": "https://xferrecords.com/",
        "vendor": "Xfer Records",
        "version": 7.0,
        "hash": hashlib.md5(compressed).hexdigest(),
    }

    header_bytes = json.dumps(
        header, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")

    # Serum 2 .SerumPreset:
    # XferJson\0 + uint64 LE JSON length + JSON metadata
    # + uint32 LE CBOR size + uint32 LE format/section value + zstd CBOR.
    blob = (
        b"XferJson\x00"
        + struct.pack("<Q", len(header_bytes))
        + header_bytes
        + struct.pack("<II", len(payload), 2)
        + compressed
    )
    return name, blob

def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    entries = []

    for index in range(100):
        name, blob = make_preset(index)
        path = OUT_DIR / f"{index + 1:03d} - {name}.SerumPreset"
        path.write_bytes(blob)
        entries.append(
            {
                "name": name,
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(blob),
            }
        )

    if ARCHIVE.exists():
        ARCHIVE.unlink()

    with zipfile.ZipFile(
        ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zf:
        for item in entries:
            source = ROOT / item["path"]
            zf.write(source, item["path"])

    MANIFEST.write_text(
        json.dumps(
            {
                "collection": "Neon Forms 100",
                "count": 100,
                "format": "Serum 2 .SerumPreset",
                "target_version": "2.1.4",
                "archive": ARCHIVE.name,
                "notes": "100 original polished patches with varied wavetable movement, filters, envelopes, modulation and restrained effects.",
                "presets": entries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Generated {len(entries)} presets")
    print(f"Archive: {ARCHIVE} ({ARCHIVE.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
