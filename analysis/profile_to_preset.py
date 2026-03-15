import json
from pathlib import Path

PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"
ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine_presets"

def convert(profile_path):

    with open(profile_path,"r") as f:
        data=json.load(f)

    ftrs=data["features"]

    brightness=min(max(ftrs["spectral_centroid_mean"]/6000,0),1)

    pitch_tightness=min(max(ftrs["pitch_std_hz"]/200,0),1)

    compression_density=min(max(ftrs["rms_std"]*10,0),1)

    preset={
        "song":profile_path.stem,
        "features":{
            "brightness":round(brightness,3),
            "pitch_tightness":round(pitch_tightness,3),
            "compression_density":round(compression_density,3)
        }
    }

    ENGINE_DIR.mkdir(exist_ok=True)

    out=ENGINE_DIR/(profile_path.stem+".json")

    with open(out,"w") as f:
        json.dump(preset,f,indent=2)

    print("Created preset:",out)

def main():

    for p in PRESETS_DIR.glob("*.json"):
        convert(p)

if __name__=="__main__":
    main()
