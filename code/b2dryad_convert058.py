"""IEEG058 (Dryad doi:10.5061/dryad.kh18932k7; Starkweather et al. 2026 Nat Neurosci) -> BIDS derivative dataset.

Release = authors' high-frequency activity (HFA 70-150 Hz, 10 sub-band Hilbert envelopes, baseline-normalised, averaged),
bipolar, epoched per trial, 1 sample/ms, 12000 samples per trial; time zero at MATLAB column 5000 (authors' code
Fig_2.m: signal_bounds-5000, xlabel 'time from decision'), i.e. -4999..+7000 ms. 5 alignments ("trigger") per electrode;
README documents trigger 1 = trial onset, 2 = decision (button press); 3-5 are undocumented and kept as released.
Representation: per subject and alignment one BrainVision IEEE_FLOAT_32 file (channels = released electrodes, trials
back-to-back), values identical to the source float32; events.tsv one row per trial with all per-trial behaviour verbatim.
Usage: python b2dryad_convert058.py <src_dir> <bids_root>
"""
import csv, hashlib, json, os, shutil, sys
import h5py, numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
f = h5py.File(os.path.join(SRC, "subject.mat"), "r")
S = f["subject"]
d = lambda r: f[r]
NT, T0 = 12000, 4999  # samples per trial; 0-based index of time zero (MATLAB column 5000)
SF = 1000.0
ACQ = {1: ("onset", "trial onset (README: trigger 1 = align to trial onset)"),
       2: ("decision", "decision / button press (README: trigger 2 = align to decision (button press); code Fig_2.m 'time from decision')"),
       3: ("trig3", "undocumented alignment 3 (release field trigger(3); not described in README)"),
       4: ("trig4", "undocumented alignment 4 (release field trigger(4); not described in README)"),
       5: ("trig5", "undocumented alignment 5 (release field trigger(5); not described in README)")}
TRIAL_FIELDS = ["decision", "rt", "outcome", "reward_trial", "punish_trial", "trial_type_trial", "p_approach_trial", "conflict_trial", "value_trial"]
TYPE_FIELDS = ["trial_type_trial_type", "reward_trial_type", "punishment_trial_type", "p_approach_trial_type", "conflict_trial_type", "value_trial_type"]


def wtsv(p, h, rows):
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(h)
        for r in rows:
            w.writerow(["n/a" if (v is None or (isinstance(v, float) and np.isnan(v))) else v for v in r])


def wjson(p, o):
    with open(p, "w") as fh:
        json.dump(o, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def vec(name, i):
    return np.asarray(d(S[name][i, 0])[()], dtype=float).ravel()


def num(v):
    return "n/a" if np.isnan(v) else (int(v) if float(v).is_integer() else float(v))


os.makedirs(OUT, exist_ok=True)
report = {"subjects": []}
for i in range(S["electrode"].shape[0]):
    sub = f"sub-{i + 1:02d}"
    od = os.path.join(OUT, sub, "ieeg")
    os.makedirs(od, exist_ok=True)
    E = d(S["electrode"][i, 0])
    ne = E["trigger"].shape[0]
    names = [f"E{j + 1:02d}" for j in range(ne)]
    arr = vec("array", i)
    anat = ["".join(chr(c) for c in d(E["anatomical_info"][j, 0])[()].ravel()) for j in range(ne)]
    coor = {k: [float(np.asarray(d(E[k][j, 0])[()]).ravel()[0]) for j in range(ne)] for k in ["lat_coor", "med_coor", "mid_coor", "olf_coor", "trans_coor"]}
    trig = d(S["triggers"][i, 0])
    trig_samples = [np.asarray(d(trig[k, 0])[()], dtype=float).ravel() for k in range(trig.shape[0])]
    tr = {k: vec(k, i) for k in TRIAL_FIELDS}
    ntr = len(tr["decision"])
    srep = {"sub": sub, "electrodes": ne, "trials": ntr, "recordings": []}
    for k in range(5):
        acq, desc = ACQ[k + 1]
        stem = f"{sub}_task-approachavoid_acq-{acq}"
        x = np.empty((ntr * NT, ne), dtype="<f4")
        good = np.zeros((ne, ntr), dtype=int)
        for j in range(ne):
            t = d(E["trigger"][j, 0])
            h = d(t["high_gamma_mat"][k, 0])[()]  # HDF5 (12000, ntrials) == MATLAB [ntrials x 12000]
            assert h.shape == (NT, ntr) and h.dtype == np.float32, (sub, j, k, h.shape)
            x[:, j] = h.T.reshape(-1)
            good[j] = np.asarray(d(t["good_trials"][k, 0])[()]).ravel()
        x.tofile(os.path.join(od, stem + "_ieeg.eeg"))
        vh = ["Brain Vision Data Exchange Header File Version 1.0", "; b2dryad_convert058.py: authors' float32 HFA, trials back-to-back, resolution 1", "",
              "[Common Infos]", "Codepage=UTF-8", f"DataFile={stem}_ieeg.eeg", f"MarkerFile={stem}_ieeg.vmrk", "DataFormat=BINARY",
              "DataOrientation=MULTIPLEXED", f"NumberOfChannels={ne}", "SamplingInterval=1000", "", "[Binary Infos]", "BinaryFormat=IEEE_FLOAT_32", "",
              "[Channel Infos]"] + [f"Ch{j + 1}={n},,1,n/a" for j, n in enumerate(names)]
        open(os.path.join(od, stem + "_ieeg.vhdr"), "w").write("\n".join(vh) + "\n")
        vm = ["Brain Vision Data Exchange Marker File, Version 1.0", "", "[Common Infos]", "Codepage=UTF-8", f"DataFile={stem}_ieeg.eeg", "",
              "[Marker Infos]", "Mk1=New Segment,,1,1,0"]
        ev = []
        for n in range(ntr):
            vm.append(f"Mk{n + 2}=Stimulus,{acq},{n * NT + T0 + 1},1,0")
            ev.append(["%.3f" % (n * NT / SF), "%.3f" % (NT / SF), acq, n * NT, n + 1, "%.3f" % ((n * NT + T0) / SF), n * NT + T0]
                      + [num(tr[c][n]) for c in TRIAL_FIELDS] + [num(ts[n]) if n < len(ts) else "n/a" for ts in trig_samples])
        open(os.path.join(od, stem + "_ieeg.vmrk"), "w").write("\n".join(vm) + "\n")
        wtsv(os.path.join(od, stem + "_events.tsv"),
             ["onset", "duration", "trial_type", "sample", "trial_index", "time_zero_onset", "time_zero_sample"] + TRIAL_FIELDS
             + [f"source_trigger{q + 1}" for q in range(len(trig_samples))], ev)
        wtsv(os.path.join(od, stem + "_goodtrials.tsv"), ["channel"] + [f"trial_{n + 1}" for n in range(ntr)],
             [[names[j]] + list(good[j]) for j in range(ne)])
        wtsv(os.path.join(od, stem + "_channels.tsv"),
             ["name", "type", "units", "low_cutoff", "high_cutoff", "sampling_frequency", "reference", "status", "anatomical_info", "array",
              "lat_coor", "med_coor", "mid_coor", "olf_coor", "trans_coor", "description"],
             [[names[j], "SEEG", "n/a", 70, 150, SF, "bipolar", "good", anat[j], num(arr[j]) if j < len(arr) else "n/a"]
              + [coor[c][j] for c in ["lat_coor", "med_coor", "mid_coor", "olf_coor", "trans_coor"]]
              + ["authors' HFA (70-150 Hz) of the bipolar derivation, electrode index %d in the release" % (j + 1)] for j in range(ne)])
        wjson(os.path.join(od, stem + "_ieeg.json"), {
            "TaskName": "approachavoid",
            "TaskDescription": "Approach-avoidance decision game (neurogame.ucsf.edu): per trial a reward offer (treasures) and a punishment offer (bombs); approach or avoid by button press within 6 s.",
            "SamplingFrequency": SF, "PowerLineFrequency": 60, "SoftwareFilters": "n/a", "HardwareFilters": "n/a",
            "iEEGReference": "bipolar (nearest neighbouring contact)", "RecordingType": "epoched", "EpochLength": NT / SF,
            "RecordingDuration": ntr * NT / SF, "SEEGChannelCount": ne,
            "DerivativeDescription": f"Authors' high-frequency activity (70-150 Hz), aligned to {desc}; time zero at sample 5000 of each 12000-sample trial (-4.999 to +7.000 s). Trials back-to-back; values unchanged."})
        srep["recordings"].append({"acq": acq, "sha256": hashlib.sha256(open(os.path.join(od, stem + "_ieeg.eeg"), "rb").read()).hexdigest(),
                                   "nan_fraction": float(np.isnan(x).mean())})
        print(sub, acq, x.shape, flush=True)
    wtsv(os.path.join(od, f"{sub}_space-Other_electrodes.tsv"), ["name", "x", "y", "z", "size"], [[n, "n/a", "n/a", "n/a", "n/a"] for n in names])
    wjson(os.path.join(od, f"{sub}_space-Other_coordsystem.json"), {"iEEGCoordinateSystem": "Other", "iEEGCoordinateUnits": "n/a",
        "iEEGCoordinateSystemDescription": "No x/y/z coordinates are released. Per-electrode distances to the lateral, medial, olfactory and transverse orbital sulci (lat/med/olf/trans_coor) and mid_coor, as released, are columns of channels.tsv."})
    tt = {k: vec(k, i) for k in TYPE_FIELDS}
    wtsv(os.path.join(OUT, sub, f"{sub}_trialtypes.tsv"), TYPE_FIELDS, [[num(tt[k][n]) for k in TYPE_FIELDS] for n in range(len(tt[TYPE_FIELDS[0]]))])
    vas = vec("VAS", i)
    wtsv(os.path.join(OUT, sub, f"{sub}_VAS.tsv"), ["index", "VAS"], [[n + 1, num(v)] for n, v in enumerate(vas)])
    report["subjects"].append(srep)
os.makedirs(os.path.join(OUT, "code"), exist_ok=True)
shutil.copy(__file__, os.path.join(OUT, "code", os.path.basename(__file__)))
json.dump(report, open(os.path.join(OUT, "code", "conversion_report.json"), "w"), indent=1)
dst = os.path.join(OUT, "sourcedata", "dryad-kh18932k7")
os.makedirs(dst, exist_ok=True)
for fn in ["subject.mat", "behavior_data.mat", "README.md"]:
    shutil.copy2(os.path.join(SRC, fn), dst)
print("DONE")
