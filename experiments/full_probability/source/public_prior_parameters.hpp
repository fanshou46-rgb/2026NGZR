#pragma once
namespace _home {
// Laplace-smoothed INITIAL FIELD frequencies from the already used 45-scene
// development bank. See prior-development-02.json and its per-input hashes.
// These are transferable hypotheses, never confirmed facts or action-feedback
// calibration. All alternatives retain positive mass; new holdout validation
// is required. Runtime code reads no author truth, case IDs or fitted labels.
struct DevelopmentPublicPrior {
    static double locationHint(bool small) {return small?135.0/175:355.0/356;}
    static double doorHint() {return 181.0/182;}
    static double slotHint() {return 46.0/47;}
    static double insideHint(bool present) {return present?37.0/44:971.0/1040;}
    static double absentAt(bool received_inside) {return received_inside?43.0/44:42.0/57;}
};
}
