/** Experiment 2 metadata (from crop_metadata_experiment.json) */
export const EXPERIMENT2 = {
  raw_merged_holdout: {
    RandomForest: { accuracy: 0.2493, f1_macro: 0.8059 },
    XGBoost: { accuracy: 0.2412, f1_macro: 0.8019 },
    SVM: { accuracy: 0.2417, f1_macro: 0.7866 },
    KNN: { accuracy: 0.248, f1_macro: 0.7971 },
    GradientBoosting: { accuracy: 0.2518, f1_macro: 0.8038 },
  },
  smote_balanced_holdout: {
    RandomForest: { accuracy: 0.2453, f1_macro: 0.804 },
    XGBoost: { accuracy: 0.241, f1_macro: 0.802 },
    SVM: { accuracy: 0.242, f1_macro: 0.787 },
    KNN: { accuracy: 0.248, f1_macro: 0.797 },
    GradientBoosting: { accuracy: 0.252, f1_macro: 0.804 },
  },
};
