from __future__ import annotations
import json, random, struct, zipfile, hashlib, shutil
from pathlib import Path

OUT = Path("Neon_Forms_40_AETHER_IMPOSSIBLE_Serum2.zip")
TMP = Path("aether40_build")
shutil.rmtree(TMP, ignore_errors=True)
TMP.mkdir(parents=True)

W = [
    "Analog/Basic Shapes.wav","Analog/Basic Mg.wav","Analog/Basic Mini.wav","Analog/SawRounded.wav",
    "Analog/SawRoundedToSquare.wav","Analog/PWM Juno.wav","Analog/PWM Mini.wav","Analog/PWM Inception.wav",
    "Analog/Jno.wav","Analog/MsAw.wav","Analog/4088.wav","Analog/BSOD_Square.wav","Analog/MATRIXY C64.wav",
    "Digital/Kream.wav","Digital/bipole_harmonic.wav","Digital/Reese.wav","Digital/Evol Longreece.wav"
]
FILTERS = ["L12","L18","L24","MgL18","MgL24","LadderMg","LadderEMS","B12","B24","LN12","LNH12","LNH24",
            "Combs","PZ_SVF","Phase48P","Diffuser","FormantONE","FormantTWO","Wsp","RM"]
NAMES = ["Aether","Silkglass","Halo","Morrow","Lumen","Velour","Nacre","Lucent","Echowisp","Frostline",
         "Softwire","Mooncell","Paleform","Glassvine","Cloudmetal","Stillwater","Prismveil","Velvetair",
         "Daydream","Starloom","Mercury","Pearlcode","Bloomglass","Quietform","Opaline","Softsignal",
         "Rainmemory","Citrine","Airframe","Petalshift","Silvermilk","Bluehour","Lucidfall","Featherphase",
         "Mirage Bloom","Warm Halo","Ghost Silk","Vaporbell","Satin Orbit","White Ember"]
CONCEPTS = ["TIDE","VEIL","ORBIT","DRIFT","BLOOM","THREAD","MIRROR","PULSE","MIST","GLOW",
            "FLUX","SHEEN","SUSPEND","FOLD","RIPPLE","HALO","BREATH","GLASS","FLOAT","ECHO"]

def cu(n, m):
    if n < 24: return bytes([(m << 5) | n])
    if n < 256: return bytes([(m << 5) | 24, n])
    if n < 65536: return bytes([(m << 5) | 25, (n >> 8) & 255, n & 255])
    if n < 2**32: return bytes([(m << 5) | 26, (n >> 24) & 255, (n >> 16) & 255, (n >> 8) & 255, n & 255])
    return bytes([(m << 5) | 27]) + struct.pack(">Q", n)

def cb(x):
    if x is None: return b"\xf6"
    if x is False: return b"\xf4"
    if x is True: return b"\xf5"
    if isinstance(x, int): return cu(x, 0) if x >= 0 else cu(-1-x, 1)
    if isinstance(x, float): return b"\xfb" + struct.pack(">d", x)
    if isinstance(x, str):
        b = x.encode("utf-8"); return cu(len(b), 3) + b
    if isinstance(x, list): return cu(len(x), 4) + b"".join(cb(v) for v in x)
    if isinstance(x, dict): return cu(len(x), 5) + b"".join(cb(k) + cb(v) for k, v in x.items())
    raise TypeError(type(x))

def zraw(payload):
    n = len(payload)
    bh = (1 << 0) | (n << 3)
    return b"\x28\xb5\x2f\xfd\xa0" + struct.pack("<I", n) + struct.pack("<I", bh)[:3] + payload

def osc(wt, vol, pan, uni, fine, semi, octave, warp, wd, wd2):
    return {
        "plainParams": {
            "kParamEnable": 1.0, "kParamVolume": vol, "kParamPan": pan, "kParamUnison": float(uni),
            "kParamFine": fine, "kParamSemitone": float(semi), "kParamOctave": float(octave), "kParamLevel": 1.0
        },
        "WTOsc0": {
            "plainParams": {"kParamWarp": wd, "kParamWarp2": wd2, "kParamWarpMenu": warp},
            "relativePathToWT": wt
        }
    }

def build(i, r):
    family = i % 8
    a = W[(i * 3) % len(W)]
    b = W[(i * 7 + 5) % len(W)]
    if family == 0:
        o0 = osc(a,.72,.50,r.choice([1,2,3]),r.uniform(49,51),0,0,r.choice(["kBendPos","kPWM","kPD_OSC"]),r.uniform(.05,.28),r.uniform(.05,.22))
        o1 = osc(b,.30,r.uniform(.43,.57),r.choice([1,2]),r.uniform(48,52),12,0,"kFM_OSC",r.uniform(.03,.16),r.uniform(0,.12))
        env = {"kParamAttack":r.uniform(.001,.012),"kParamDecay":r.uniform(.35,.9),"kParamSustain":r.uniform(.12,.48),"kParamRelease":r.uniform(.35,1.2)}
        filt = "Combs"
    elif family == 1:
        o0 = osc(a,.68,.48,r.choice([1,2,3]),r.uniform(49,51),0,0,"kPWM",r.uniform(0,.10),r.uniform(.05,.16))
        o1 = osc(b,.34,.52,r.choice([1,2]),r.uniform(48,52),7,0,"kBendNeg",r.uniform(.02,.18),r.uniform(.02,.12))
        env = {"kParamAttack":r.uniform(.03,.12),"kParamDecay":r.uniform(.4,1.1),"kParamSustain":r.uniform(.62,.92),"kParamRelease":r.uniform(.5,1.5)}
        filt = r.choice(["L12","L18","MgL18","FormantONE"])
    elif family == 2:
        o0 = osc(a,.74,.50,r.choice([2,3,4]),r.uniform(47,53),0,0,"kFM_OSC2",r.uniform(.02,.20),r.uniform(.04,.24))
        o1 = osc(b,.28,.50,1,r.uniform(47,53),19,0,"kBendPosNeg",r.uniform(.04,.30),r.uniform(.02,.18))
        env = {"kParamAttack":r.uniform(.008,.04),"kParamDecay":r.uniform(.6,1.5),"kParamSustain":r.uniform(.35,.72),"kParamRelease":r.uniform(.4,1.3)}
        filt = r.choice(["L18","L24","PZ_SVF","Phase48P"])
    elif family == 3:
        o0 = osc(a,.70,.50,r.choice([1,2]),r.uniform(48,52),0,1,r.choice(["kPD_OSC","kBendPos"]),r.uniform(.08,.22),r.uniform(.04,.16))
        o1 = osc(b,.22,.50,1,r.uniform(47,53),12,-1,"kRM_OSC",r.uniform(.02,.12),r.uniform(.02,.10))
        env = {"kParamAttack":r.uniform(.002,.02),"kParamDecay":r.uniform(.25,.8),"kParamSustain":r.uniform(.15,.5),"kParamRelease":r.uniform(.3,.9)}
        filt = r.choice(["Combs","FormantONE","FormantTWO","Wsp"])
    elif family == 4:
        o0 = osc(a,.82,.50,r.choice([1,2,3]),r.uniform(48,52),0,-1,"kFilterLPF",r.uniform(.02,.12),r.uniform(.02,.10))
        o1 = osc(b,.16,.50,1,r.uniform(48,52),12,0,"kPWM",r.uniform(.02,.10),r.uniform(.02,.08))
        env = {"kParamAttack":r.uniform(.001,.02),"kParamDecay":r.uniform(.25,.75),"kParamSustain":r.uniform(.52,.82),"kParamRelease":r.uniform(.12,.55)}
        filt = r.choice(["L12","L18","MgL18","LN12"])
    elif family == 5:
        o0 = osc(a,.60,.42,r.choice([2,3,4,5]),r.uniform(46,54),0,0,"kBendPosNeg",r.uniform(.02,.16),r.uniform(.02,.14))
        o1 = osc(b,.42,.58,r.choice([2,3]),r.uniform(46,54),12,0,"kPWM",r.uniform(.04,.20),r.uniform(.02,.16))
        env = {"kParamAttack":r.uniform(.08,.3),"kParamDecay":r.uniform(.7,1.8),"kParamSustain":r.uniform(.68,.94),"kParamRelease":r.uniform(.9,2.2)}
        filt = r.choice(["L12","L18","B12","B24","Diffuser"])
    elif family == 6:
        o0 = osc(a,.78,.50,r.choice([1,2,3]),r.uniform(48,52),0,0,r.choice(["kBendPos","kBendNeg","kSync"]),r.uniform(0,.16),r.uniform(0,.14))
        o1 = osc(b,.12,.50,1,r.uniform(48,52),19,0,"kFM_OSC",r.uniform(.01,.10),r.uniform(0,.08))
        env = {"kParamAttack":r.uniform(.0005,.006),"kParamDecay":r.uniform(.18,.5),"kParamSustain":r.uniform(.02,.28),"kParamRelease":r.uniform(.35,1.0)}
        filt = r.choice(["Combs","PZ_SVF","L24","Phase48P"])
    else:
        o0 = osc(a,.70,.50,r.choice([1,2,3]),r.uniform(47,53),0,0,r.choice(["kPWM","kBendPos","kBendNeg"]),r.uniform(.03,.20),r.uniform(.02,.16))
        o1 = osc(b,.24,.50,r.choice([1,2]),r.uniform(47,53),7,0,"kFM_OSC2",r.uniform(.01,.10),r.uniform(.01,.08))
        env = {"kParamAttack":r.uniform(.01,.07),"kParamDecay":r.uniform(.3,.9),"kParamSustain":r.uniform(.45,.8),"kParamRelease":r.uniform(.25,.9)}
        filt = r.choice(["FormantONE","FormantTWO","L18","LNH12","Wsp"])

    p = {
      "Oscillator0": o0, "Oscillator1": o1,
      "Oscillator2": {"plainParams":"default"}, "Oscillator3": {"plainParams":"default"}, "Oscillator4": {"plainParams":"default"},
      "VoiceFilter0": {"plainParams":{"kParamEnable":1.0,"kParamType":filt,"kParamFreq":r.uniform(.12,.78),"kParamReso":r.uniform(4,48),"kParamDrive":r.uniform(0,10),"kParamVar":r.uniform(0,100)}},
      "VoiceFilter1": {"plainParams":"default"},
      "Global0": {"plainParams":{"kParamMasterVolume":r.uniform(.48,.74),"kParamPortamentoTime":r.uniform(.01,.12),"kParamPolyphony":float(r.choice([6,8,10,12,16]))}},
      "Env0": {"plainParams":env},
      "Env1": {"plainParams":{"kParamAttack":r.uniform(.01,.25),"kParamDecay":r.uniform(.2,.9),"kParamSustain":r.uniform(0,.65),"kParamRelease":r.uniform(.2,1.2)}},
      "Env2": {"plainParams":"default"}, "Env3": {"plainParams":"default"},
      "LFO0": {"plainParams":{"kParamRate":r.choice([.0625,.125,.1666667,.25,.3333333,.5,1,1.5,2]),"kParamMode":r.choice(["Free","Trigger","Envelope"]),"kParamType":r.choice(["Path","Lorenz","Rossler"]),"kParamSmooth":r.uniform(.35,.9),"kParamDelay":r.uniform(0,.16)},"pathData":{"curveVals":[r.uniform(-.1,.1),r.uniform(.1,.9),r.uniform(.8,1.1)],"isOpen":True,"numPoints":3,"xVals":[0,.5,1],"yVals":[r.uniform(.15,.45),r.uniform(.3,.7),r.uniform(.55,.95)]}},
      "LFO1": {"plainParams":{"kParamRate":r.choice([.125,.25,.5,1,2,3,4]),"kParamMode":r.choice(["Free","Trigger"]),"kParamType":"Path","kParamSmooth":r.uniform(.25,.85),"kParamDelay":0}},
      "LFO2": {"plainParams":{"kParamRate":r.choice([.125,.25,.5,1,2]),"kParamMode":"Free","kParamType":"RandomSH","kParamSmooth":r.uniform(.65,.95),"kParamDelay":0}},
      "Macro0":{"name":"SHAPE","plainParams":{"kParamValue":r.uniform(45,85)}},
      "Macro1":{"name":"BLOOM","plainParams":{"kParamValue":r.uniform(35,90)}},
      "Macro2":{"name":"TIDE","plainParams":{"kParamValue":r.uniform(25,90)}},
      "Macro3":{"name":"AIR","plainParams":{"kParamValue":r.uniform(30,95)}},
      "ModSlot0":{"destModuleID":0,"destModuleParamID":3,"destModuleParamName":"kParamFreq","destModuleTypeString":"VoiceFilter","plainParams":{"kParamAmount":r.uniform(8,38)},"source":[6,0]},
      "ModSlot1":{"destModuleID":0,"destModuleParamID":0,"destModuleParamName":"kParamWarp","destModuleTypeString":"WTOsc","plainParams":{"kParamAmount":r.uniform(6,30),"kParamBipolar":1.0},"source":[1,0]},
      "ModSlot2":{"destModuleID":1,"destModuleParamID":0,"destModuleParamName":"kParamWarp","destModuleTypeString":"WTOsc","plainParams":{"kParamAmount":r.uniform(4,22),"kParamBipolar":1.0},"source":[7,0]},
      "ModSlot3":{"destModuleID":0,"destModuleParamID":1,"destModuleParamName":"kParamWarp2","destModuleTypeString":"WTOsc","plainParams":{"kParamAmount":r.uniform(-18,18),"kParamBipolar":1.0},"source":[18,0]},
    }

    fx = []
    if i % 6 in (0,2,5):
        fx.append({"FXChorus":{"plainParams":{"kParamRate":r.uniform(.05,.8),"kParamDepth":r.uniform(18,68),"kParamMix":r.uniform(8,30)}},"kUIParamMixOrGain":0.0,"type":4})
    if i % 6 in (1,2,4):
        fx.append({"FXPhaser":{"plainParams":{"kParamRate":r.uniform(.03,.7),"kParamDepth":r.uniform(15,60),"kParamMix":r.uniform(6,25)}},"kUIParamMixOrGain":0.0,"type":7})
    if i % 3 != 1:
        fx.append({"FXDelay":{"plainParams":{"kParamWet":r.uniform(5,22),"kParamFeedback":r.uniform(10,48),"kParamTime":r.uniform(.08,.55)}},"kUIParamMixOrGain":0.0,"type":2})
    fx.append({"FXReverb":{"plainParams":{"kParamSize":r.uniform(35,100),"kParamWet":r.uniform(8,28)}},"kUIParamMixOrGain":0.0,"type":3})
    p["FXRack0"] = {"FX":fx}
    p["Arp0"] = {"plainParams":{"kParamEnabled":0.0,"kParamActiveClipID":0.0}}
    for j in range(3,10): p.setdefault(f"LFO{j}",{"plainParams":"default"})
    for j in range(4,8): p.setdefault(f"Macro{j}",{"name":"","plainParams":{"kParamValue":0.0}})
    for j in range(4,64): p.setdefault(f"ModSlot{j}",{"plainParams":"default"})
    p.update({"lockOversampling":False,"lockTuning":False,"mpeConfig":0,"mpeEnabled":False,"mpePitchBendRange":48})
    return p

records = []
pack = TMP / "Presets" / "Neon Forms 40 AETHER IMPOSSIBLE"
pack.mkdir(parents=True, exist_ok=True)
for i in range(40):
    r = random.Random(0xAE7E12 + i*7919)
    name = f"{NAMES[i]} {CONCEPTS[i % len(CONCEPTS)]} {i+1:03d}"
    payload = cb(build(i,r))
    comp = zraw(payload)
    header = {
      "fileType":"SerumPreset","presetName":name,"presetAuthor":"sjoesnds",
      "presetDescription":"Aether Series — clean impossible instruments built from motion, resonance, formant color, and spatial depth; no distortion FX.",
      "product":"Serum2","productVersion":"2.1.4",
      "tags":["Serum 2","Aether","Clean","Motion","Resonance","Experimental"],
      "url":"https://xferrecords.com/","vendor":"Xfer Records","version":7.0,"hash":hashlib.md5(comp).hexdigest()
    }
    hb = json.dumps(header,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    blob = b"XferJson\x00" + struct.pack("<Q",len(hb)) + hb + struct.pack("<II",len(payload),2) + comp
    fp = pack / f"{i+1:03d} - {name}.SerumPreset"
    fp.write_bytes(blob)
    records.append({"index":i+1,"name":name,"path":f"Presets/Neon Forms 40 AETHER IMPOSSIBLE/{fp.name}","bytes":len(blob),"family":CONCEPTS[i % len(CONCEPTS)]})

manifest = {
  "collection":"Neon Forms 40 AETHER IMPOSSIBLE","count":40,"format":"Serum 2 .SerumPreset","target_version":"2.1.4",
  "archive":OUT.name,
  "design_note":"A clean experimental companion pack focused on impossible-instrument character: resonance, formant color, stereo motion, liquid modulation, glassy plucks, soft harmonic layers, and spatial depth. No distortion FX.",
  "presets":records
}
(TMP/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")

with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,9) as z:
    for f in sorted(TMP.rglob("*")):
        if f.is_file(): z.write(f,f.relative_to(TMP).as_posix())
print(f"{OUT} {OUT.stat().st_size} bytes; {len(records)} presets")
