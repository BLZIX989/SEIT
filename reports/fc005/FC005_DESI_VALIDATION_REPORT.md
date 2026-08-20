# FC-005 DESI Validation Report

File: `LRG_SGC_clustering.dat.fits`
Rows: 662492
Redshift range observed: [0.4000, 1.1000]

| check | passed | detail |
|---|---|---|
| fits_opens | PASS |  |
| expected_hdus_exist | PASS | HDUs: ['PRIMARY', 'LSS'] |
| required_columns_exist | PASS | all present: ['TARGETID', 'RA', 'DEC', 'Z', 'WEIGHT', 'WEIGHT_FKP', 'WEIGHT_SYS'] |
| column_datatypes_valid | PASS | issues: [] |
| object_count_agrees_with_metadata | PASS | file has 662492 rows, manifest recorded 662492 |
| ra_finite | PASS | n_nonfinite=0 |
| dec_finite | PASS | n_nonfinite=0 |
| z_finite | PASS | n_nonfinite=0 |
| weights_finite | PASS | {'WEIGHT': 0, 'WEIGHT_FKP': 0, 'WEIGHT_SYS': 0} |
| redshift_within_documented_tracer_range | PASS | observed [0.4000, 1.1000] vs documented (0.4, 1.1) |
| duplicate_targetids_understood | PASS | 0 duplicate TARGETID rows out of 662492 (none -- one row per unique object) |
| mask_selection_fields_present | PASS | found: ['PHOTSYS', 'NTILE', 'FRAC_TLOBS_TILES'] |
| no_silent_range_contamination | PASS | RA out of [0,360]: 0; DEC out of [-90,90]: 0 |

**Overall: PASSED**