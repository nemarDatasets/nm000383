# Intracranial recordings in humans reveal differential contributions of medial and lateral orbitofrontal cortex to approach-avoidance decision-making

Dataset DOI: [10.5061/dryad.kh18932k7](10.5061/dryad.kh18932k7)

## **Participants**

The dataset includes recordings from six patients who underwent stereotactic placement of intracranial depth electrodes (Ad-Tech or Dixi brands, with 3-5mm spacing between contacts) as part of clinical care. Five patients were implanted at UCSF and one at Washington University in St. Louis (WUSTL). In all cases, electrode locations were determined solely by clinical monitoring needs, not by research goals. The study protocol was reviewed and approved by the institutional review boards at UCSF, UC Berkeley, and WUSTL, and every participant gave written informed consent before any testing began.

**Behavior and task**

Each patient played between 192 and 220 trials of an approach-avoidance decision game, which is publicly playable at neurogame.ucsf.edu. The game runs on the Unity engine and was built by an outside studio, Cat-astrophe Games (based in Wrocław, Poland); the full source code and a guide to adjustable settings are posted at [https://github.com/cstarkweather/Starkweather-neurogame/blob/master/README.md](https://github.com/cstarkweather/Starkweather-neurogame/blob/master/README.md).

A typical session lasted about 20 minutes. On each trial, a 600ms zoom-in animation preceded the response window; patients then had up to 6 seconds to choose approach or avoidance via button press, or else forfeited a ruby and the trial ended automatically. Trial types appeared in a randomized order, shuffled within blocks of 40 trials so that similar trial types wouldn't cluster together. Time between trials followed a Poisson distribution (median 985ms, SD 249.41ms).

For five of the six patients (all tested at UCSF), task events were logged using a Black Box ToolKit mBBTK v2 / Elite event-marking system: trial onsets were captured via photodiode, button presses via a BBTK USB response pad, and the exact timing of in-game outcomes (explosions, treasure reveals) via a paired audio signal — all fed as analog inputs to keep behavioral and neural recordings in sync. The sixth patient, tested at WUSTL, instead had button presses and trial onsets logged through BCI2000, using a laptop keyboard and photodiode respectively.

Two versions of the task were used. Four patients played a 220-trial version offering reward levels of 0, 2, 4, or 7 and punishment levels of 0, 2, or 4, covering every combination of these values. The remaining two patients played a 192-trial version with finer-grained offers — rewards from 0 through 7 and punishments from 0 through 4, at every integer step. Behavioral fitting showed no meaningful differences in loss aversion, reward sensitivity, or punishment sensitivity between the two task versions, nor between patients implanted for psychiatric versus epilepsy-related reasons.

**Manual definition of orbitofrontal sulci**

Structural MRI scans were run through FreeSurfer (v6.0.0) to generate 3D pial and inflated surface reconstructions of the cortex. Two trained neuroanatomists then manually traced orbitofrontal sulci on these reconstructions, using FreeSurfer's curvature-based tools to distinguish sulcal from gyral surface, across all 12 hemispheres (6 patients). Ten sulci were of interest: the olfactory sulcus, transverse olfactory sulcus, transverse orbital sulcus, the anterior and posterior segments of the medial orbital sulcus, the anterior and posterior segments of the lateral orbital sulcus, the intermediate orbital sulcus, the posterior orbital sulcus, and the sulcus fragmentosus. The first seven of these are known to be present in every individual and were indeed found in all patients here; the remaining three vary in number across people (anywhere from 0 to 4 segments) and their presence per patient is listed in the dataset's extended tables.

**Electrode localization**

Electrode positions were determined by aligning each patient's 1mm-resolution T1 MRI with a 1mm-resolution bone-window CT scan. Once aligned in FreeSurfer, electrode contacts were marked using the region-of-interest tool, and both electrode centroid coordinates and the manually drawn sulcal boundaries were exported into MATLAB for further processing. A shared coordinate framework was built across all patients, anchored to two sulci that are consistently present: the medial orbital sulcus (treating its anterior and posterior segments as one) and the transverse orbital sulcus.

Anterior-posterior position was defined relative to the transverse orbital sulcus: for each electrode, the anterior-posterior distance was measured to the centroid of transverse-orbital-sulcus points sharing that electrode's medial-lateral position (or, if the electrode fell outside the sulcus's medial-lateral range, to the nearest available slice). Medial-lateral position was defined analogously relative to the medial orbital sulcus, using centroid points that matched the electrode's anterior-posterior position.

These coordinates were then used to sort electrodes into anatomical zones: contacts falling medial to the olfactory sulcus (i.e., within the gyrus rectus) were dropped from anatomical analyses; the remaining contacts were labeled medial OFC if medial to the medial orbital sulcus; anterior OFC if lateral to the medial orbital sulcus, anterior to the transverse orbital sulcus, and medial to the lateral orbital sulcus; posterior OFC if lateral to the medial orbital sulcus, posterior to the transverse orbital sulcus, and medial to the lateral orbital sulcus; and lateral OFC if lateral to the lateral orbital sulcus. Contacts in the inferior frontal gyrus were excluded entirely.

**Data collection and preprocessing**

A total of 128 electrode contacts within the OFC were recorded. Signals were captured through a multichannel preamplifier and digital signal processor, sampled at 3-10kHz, using either a Tucker-Davis Technologies or Nihon Kohden acquisition system. No seizures occurred during any recording session. Every recording was manually reviewed at sub-second resolution to flag and remove epileptiform activity or artifact, resulting in 4.6% of trial data being discarded on this basis; the OFC itself was not the site of seizure onset in any patient.

Signals were bipolar-referenced against the nearest neighboring contact; any electrode lacking a usable neighbor for this purpose was excluded. After removing 14 noisy channels and a further 14 electrodes rendered redundant by bipolar referencing, 100 electrodes remained in the final dataset. (Laplacian and common-average referencing were also tried as alternatives and produced comparable results to those reported in the paper, though those alternative-reference datasets are not what's included here.)

Preprocessing was carried out in MATLAB using the FieldTrip toolbox. Raw signals were bandpass filtered from 0.5-200Hz, then notch-filtered to remove 60Hz line noise and its harmonics. High-frequency activity (HFA, 70-150Hz) was extracted by filtering the signal into ten separate 10Hz sub-bands across that range, applying the Hilbert transform to each, and computing the resulting amplitude envelope. Each sub-band's amplitude was normalized against its own average amplitude during a 10-second pre-task baseline period (correcting for the natural 1/f drop-off in signal power at higher frequencies). The ten normalized sub-band envelopes were then averaged together to produce the final HFA signal used in the dataset.

### Files and variables

#### File: subject.mat, behavior_data.mat (for behavior-relevant information only)

**Description:**

##### Variables

* subject is the "master" variable. All main data figure analyses from the manuscript can be reproduced using the "subject" variable. Below I explain the subfields. Use subject(n).subfield1 to obtain subfield1 information for subject n
* STORAGE OF TRIAL INFORMATION AND BEHAVIOR:
  * decision: the decision made on a particular trial. ordered sequentially from 1-n_trials. 1 = approach. 0 = avoidance.
  * The below variables (all subfields of "subject") are the key to understanding the task the subject played, and overall how they played it:
    * <br />

      ```
      reward_trial_type: for trial type n, reward_trial_type(n) is the reward offer for that trial type (# lit treasures)

      punishment_trial_type: for trial type n, punishment_trial_type(n) is the punishment offer for that trial type (# lit bombs)

      conflict_trial_type: for trial type n, conflict_trial_type(n) is the behavioral conflict the subject exhibited

      trial_type_trial_type: the numbered trial type.

      p_approach_trial_type: for trial type n, p_approach_trial_type(n) is the subject's overall probability of approach
      ```
  * The below variables give the trial-by-trial log of the subject's behavior. Each will be 1-ntrials long.
    * <br />

      ```
          p_approach_trial: subject's overall approach probability for the particular trial type presented in the nth trial 

      conflict_trial: subject's overall behavioral conflict for the particular trial type presented in the nth trial

      reward_trial: reward offer on a particular trial

      punish_trial: punishment offer on a particular trial

      trial_type_trial: trial type from beginning to end of session
      ```
  * trial_type_trial: index of distinct trial type spanning from 1-ntrials. each trial type corresponded to a distinct reward/punishment combo.
* STORAGE OF NEURAL DATA:
  * electrode: information about each electrode for each subject. So, subject(1).electrode(1) provides coordinates (lat_coor/med_coor/olf_coor/trans_coor) relative to lateral orbital sulcus, medial orbital sulcus, olfactory sulcus, and transverse orbital sulcus for electrode 1 in subject 1. I suggest adhering to these coordinates rather than "anatomical info" as the coordinates are most accurate and obtained using manual surface labeling by neuroanatomists (see info in Methods for the anatomical method) whereas the anatomical info was not based on these detailed reconstructions.
    * The subfield within electrode is trigger: 1 = align to trial onset. 2 = align to decision (button press).
      * The subfield within trigger is high_gamma_mat, which is the neural data (high frequency activity). So, for instance, subject(1).electrode(1).trigger(1).high_gamma_mat gives a high_gamma_mat: [220×10000 double] where each row is a trial from 1-ntrials and each column is a timepoint (in milliseconds) from that trial, aligned to the trigger of interest. So, for example, this would be high frequency activity for the electrode 1 in subject 1 spanning from 5000ms prior to trial onset to 5000ms after trial onset.

## Code/software

Matlab codes to reproduce all main figures in the paper: [https://github.com/cstarkweather/OFC_analysis_codes](https://github.com/cstarkweather/OFC_analysis_codes)

## Access information

Data was derived from the following sources:

* all collected for this manuscript as stated in Methods



## Human subjects data

There is no personal health information in the deposited data. All data was obtained in accordance with our institutional IRB, and informed consent was obtained from all participants prior to participation.