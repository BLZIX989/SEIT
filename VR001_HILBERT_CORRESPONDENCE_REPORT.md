# VR001_HILBERT_CORRESPONDENCE_REPORT.md

VR-001 methodology test on a KNOWN manifold (S^1) where the correct answer is analytically known -- NOT a claim about real DESI data (see KC-003a/d above for why that specific case remains open)

## Uniform sampling (converges to the known true eigenspace)

- N=100: cos-projection=1.0000, sin-projection=1.0000, converged=True
- N=300: cos-projection=0.9997, sin-projection=0.9998, converged=True
- N=800: cos-projection=1.0000, sin-projection=1.0000, converged=True

## Nonuniform (density-clustered) sampling -- same unnormalized construction

- N=100: cos-projection=0.0188, sin-projection=0.1832, converged=False
- N=300: cos-projection=0.4546, sin-projection=0.1569, converged=False
- N=800: cos-projection=0.0710, sin-projection=0.2547, converged=False

## Interpretation

Under uniform sampling, the computed low eigenspace should increasingly align with the true span{cos(theta),sin(theta)} as N grows (projection norms -> 1). Under nonuniform (clustered) sampling with the SAME unnormalized graph Laplacian, density bias is expected to degrade this convergence -- exactly the known diffusion-map-theory distinction the corpus's own FC-005 investigation already turns on (density-normalized vs raw constructions).

## What this does NOT establish about real DESI data

This validates the TEST METHODOLOGY on a case with a known analytic answer (the circle). The real DESI data's own convergence status is separately, already assessed in CONVERGENCE_AUDIT.md (CONV-001) -- not re-litigated here.
