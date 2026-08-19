"""
L0-ST / L0-A: string-theory literature ingestion deliverables generator.

Produces the tabular/JSON deliverables from Parts I-XIV of the L0-ST spec plus
Part IX of L0-A, built ONLY from content actually read this phase (Tong,
"String Theory" arXiv:0908.0333v3, pp.1-29 -- title/TOC/intro + full Chapter 1
"The Relativistic String"; Kiritsis, "Introduction to Superstring Theory"
hep-th/9709062v2, pp.1-23 -- title/TOC/intro + section 3 "Classical string
theory" through 3.3 oscillator expansions). Everything beyond that page range
is recorded as TOC-level / not-extracted, never fabricated.

Purely additive artifacts. No canonical registry is touched; no proposed
recovery is promoted; FC-005 is untouched.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIMESTAMP = "2026-08-19T17:30:00Z"

TONG_ST = "LIT-TONG-ST"
KIRITSIS = "LIT-KIRITSIS-SST"

# ---------------------------------------------------------------------------
# Part I -- STRING_THEORY_CORPUS_MANIFEST.json
# ---------------------------------------------------------------------------

def build_corpus_manifest() -> dict:
    return {
        "manifest_type": "STRING_THEORY_CORPUS_MANIFEST",
        "generated_at": TIMESTAMP,
        "search_performed": (
            "Searched the supplied workspace/session for files matching 'string theory', "
            "'superstring', 'string_theory', 'string-theory', 'superstring-theory', "
            "'Introduction to String Theory', 'Introduction to Superstring Theory', and the "
            "named candidates string_theory(1).pdf / string_theory.pdf / "
            "superstring-theory.pdf. None were found attached to this session -- the prior "
            "L0-ST instruction's premise ('the supplied String Theory PDFs could not be "
            "uploaded successfully') is confirmed: no such files exist in this session's "
            "upload directory or working tree. This phase instead executed L0-A: direct "
            "authoritative download of equivalent/named sources."
        ),
        "files": [
            {
                "FILE_ID": "FT-001",
                "FILENAME": "tong_string_theory_arxiv.pdf",
                "PATH": "literature/string_theory/tong_string_theory_arxiv.pdf",
                "SIZE_BYTES": 1442465,
                "HASH": "sha256:b267b9d7bb717e8e7765b202910cd464e86de290489b5a70dc27d25e07fc848c",
                "VERSION_IF_DETERMINABLE": "arXiv:0908.0333v3 [hep-th], 23 Feb 2012",
                "SOURCE_LOCATION": "downloaded from https://arxiv.org/pdf/0908.0333 (archival mirror; Cambridge primary https://www.damtp.cam.ac.uk/user/tong/string/string.pdf failed -- see literature/manifests/LITERATURE_DOWNLOAD_MANIFEST.json)",
                "INGESTION_STATUS": "PARTIAL -- title page, book recommendations, full Table of Contents, Introduction (0. Introduction, 0.1 Quantum Gravity), and full Chapter 1 'The Relativistic String' (pp.9-27: 1.1 Relativistic Point Particle incl. 1.1.1/1.1.2, 1.2 Nambu-Goto Action incl. 1.2.1/1.2.2, 1.3 Polyakov Action incl. 1.3.1/1.3.2) were read and extracted with full equation-level provenance. Chapters 2-8 (pp.28-209: quantization, D-branes, CFT, path integral/ghosts, string interactions, low-energy effective actions, compactification/T-duality) were NOT read this phase -- indexed by Table of Contents only."
            },
            {
                "FILE_ID": "FK-001",
                "FILENAME": "kiritsis_intro_superstring_arxiv.pdf",
                "PATH": "literature/superstring_theory/kiritsis_intro_superstring_arxiv.pdf",
                "SIZE_BYTES": 1798642,
                "HASH": "sha256:7f7c2e4665c5b6148b5d3718e843aefddcbf219ce33ebba1db0264fe5dd9f4ea",
                "VERSION_IF_DETERMINABLE": "arXiv:hep-th/9709062v2, 30 Mar 1998 (CERN-TH/97-218, March 1997)",
                "SOURCE_LOCATION": "downloaded from https://arxiv.org/pdf/hep-th/9709062 (this was the primary URL supplied and it succeeded directly)",
                "INGESTION_STATUS": "PARTIAL -- title page, abstract, full Table of Contents, section 1 'Introduction', section 2 'Historical perspective', and section 3 'Classical string theory' through 3.3 'Oscillator expansions' (pp.5-22: 3.1 The point particle, 3.2 Relativistic strings, 3.3 Oscillator expansions) were read and extracted with full equation-level provenance. Sections 4-15 and Appendices A-H (pp.23-243: quantization, interactions/amplitudes, CFT, CFT on the torus, scattering amplitudes, low-energy effective actions, superstrings/supersymmetry, anomalies, compactification/SUSY breaking, loop corrections, non-perturbative dualities, outlook) were NOT read this phase -- indexed by Table of Contents only."
            }
        ],
        "duplicates_found": "NONE -- no duplicate filenames or byte-identical files were encountered, since only one copy of each of the 2 successfully acquired documents exists in this corpus.",
        "documents_not_acquired": [
            "David Tong, 'The Standard Model' (Cambridge) -- download failed, no archival URL supplied, see LITERATURE_DOWNLOAD_MANIFEST.json",
            "David Tong, 'Lectures on Gauge Theory' course page and its 5 sub-PDFs (Yang-Mills Theory, Anomalies, Lattice Gauge Theory, Chiral Symmetry Breaking, Large N) -- download failed, no archival URL supplied"
        ]
    }


# ---------------------------------------------------------------------------
# Part II -- STRING_THEORY_VERSION_MATRIX.csv
# ---------------------------------------------------------------------------

VERSION_MATRIX_ROWS = [
    dict(FILE_ID="FT-001", FILENAME="tong_string_theory_arxiv.pdf",
         COMPARED_AGAINST="Cambridge original (damtp.cam.ac.uk/user/tong/string/string.pdf)",
         BYTE_IDENTICAL="UNDETERMINED -- Cambridge original could not be downloaded to compare",
         DUPLICATE="FALSE", VERSION_RELATIONSHIP="N/A -- only one copy of this document was successfully acquired",
         DETERMINATION_METHOD="single acquisition; no second copy exists in this corpus to compare against",
         PRESERVED="TRUE -- the sole acquired copy is preserved at literature/string_theory/tong_string_theory_arxiv.pdf"),
    dict(FILE_ID="FK-001", FILENAME="kiritsis_intro_superstring_arxiv.pdf",
         COMPARED_AGAINST="N/A -- only one source URL was supplied for this document and no alternate copy exists in this corpus",
         BYTE_IDENTICAL="N/A", DUPLICATE="FALSE", VERSION_RELATIONSHIP="N/A -- single copy",
         DETERMINATION_METHOD="single acquisition",
         PRESERVED="TRUE -- preserved at literature/superstring_theory/kiritsis_intro_superstring_arxiv.pdf"),
]


# ---------------------------------------------------------------------------
# Part III/IV -- STRING_THEORY_LITERATURE_REGISTRY.json
# ---------------------------------------------------------------------------

def item(item_id, source_id, page, chapter, section, subsection, eq_no,
         source_notation, math_object, operator, assumptions, derivation_context,
         source_status):
    return {
        "STRING_ITEM_ID": item_id,
        "SOURCE_ID": source_id,
        "PAGE": page,
        "CHAPTER": chapter,
        "SECTION": section,
        "SUBSECTION": subsection,
        "EQUATION_NUMBER": eq_no,
        "SOURCE_NOTATION": source_notation,
        "MATHEMATICAL_OBJECT": math_object,
        "OPERATOR": operator,
        "ASSUMPTIONS": assumptions,
        "DERIVATION_CONTEXT": derivation_context,
        "SOURCE_STATUS": source_status,
        "EXTRACTION_TIMESTAMP": TIMESTAMP,
    }


def build_literature_registry() -> list[dict]:
    items = [
        item("ST-001", TONG_ST, "9", "1", "1.1", None, "(1.1)",
             "S = -m \\int dt \\sqrt{1 - \\dot{\\vec{x}}\\cdot\\dot{\\vec{x}}}",
             "relativistic point-particle action, fixed-frame form",
             "none (Lagrangian, not yet an operator)",
             "D-dimensional Minkowski space R^{1,D-1}, signature (-,+,...,+)",
             "written directly as the natural action reproducing p=m dx/dt(1-v^2)^{-1/2}, E=sqrt(m^2+p^2); motivates the search for a manifestly Lorentz-covariant form",
             "textbook-established (standard relativistic mechanics)"),
        item("ST-002", TONG_ST, "10", "1", "1.1", None, "(1.2)",
             "S = -m \\int d\\tau \\sqrt{-\\dot{X}^\\mu \\dot{X}^\\nu \\eta_{\\mu\\nu}}",
             "reparametrization-invariant point-particle action (worldline proper-time form)",
             "worldline parameter tau; X^mu(tau)",
             "introduces reparametrization tau -> tilde-tau(tau) as a gauge symmetry",
             "derived from (1.1) by promoting t to a dynamical coordinate X^0(tau) and requiring reparametrization invariance; explicitly verified invariant under tau-> tilde tau(tau) by direct substitution",
             "textbook-established, directly re-derived in the source"),
        item("ST-003", TONG_ST, "11", "1", "1.1", "1.1.1 Quantization", "(1.5),(1.7)",
             "p_\\mu p^\\mu + m^2 = 0; (-\\partial_{X^\\mu}\\partial_{X^\\nu}\\eta^{\\mu\\nu}+m^2)\\Psi(X)=0",
             "mass-shell constraint (classical) and its quantum operator form (Klein-Gordon equation)",
             "momentum operator p_mu = -i d/dX^mu",
             "canonical quantization of the constrained system; wavefunction Psi(X) satisfies Schrodinger eq with H=0",
             "constraint (1.5) derived directly from momenta (1.4); quantum form (1.7) obtained by the standard operator replacement, explicitly identified as coinciding with (but reinterpreted from) the classical Klein-Gordon field equation",
             "textbook-established"),
        item("ST-004", TONG_ST, "13", "1", "1.1", "1.1.2 Ein Einbein", "(1.8),(1.9),(1.10)",
             "S=\\frac{1}{2}\\int d\\tau(e^{-1}\\dot X^2 - em^2)",
             "einbein form of the point-particle action, e(tau) as worldline metric/vierbein",
             "einbein field e(tau) = sqrt(-g_{tau tau})",
             "e is fixed by its own equation of motion, dot-X^2+e^2 m^2=0, substituting which recovers (1.2); this form works for massless particles (m=0), unlike (1.1)/(1.2)",
             "explicitly re-derived and shown equivalent to (1.2) in the source; reparametrization transformation law for e given explicitly, eq (1.10)",
             "textbook-established"),
        item("ST-005", TONG_ST, "14", "1", "1.2", None, "(1.11)-(1.14)",
             "\\gamma_{\\alpha\\beta}=\\partial_\\alpha X^\\mu \\partial_\\beta X^\\nu \\eta_{\\mu\\nu}; S=-T\\int d^2\\sigma \\sqrt{-\\det\\gamma}",
             "Nambu-Goto action: worldsheet induced metric gamma_{alpha beta} (pullback of flat spacetime metric) and the action proportional to worldsheet area",
             "none (Lagrangian)",
             "closed string, sigma periodic in [0,2pi]; worldsheet parametrized by (tau,sigma); reparametrization invariance required",
             "constructed by direct analogy with the point-particle worldline-length action, generalized to worldsheet area; explicit pedagogical area-element check given via a Euclidean cross-product argument, eq (1.15)",
             "textbook-established; this is THE canonical bosonic-string action"),
        item("ST-006", TONG_ST, "16", "1", "1.2", "tension/dimension discussion", "(1.17),(1.18)",
             "T=\\frac{1}{2\\pi\\alpha'};\\quad \\alpha'=l_s^2",
             "string tension T in terms of the Regge slope alpha-prime; definition of the string length scale l_s",
             "none",
             "T interpreted physically as energy per unit length by evaluating the action on a static string configuration, eq (1.16)",
             "direct derivation shown in source (static-string potential-energy argument)",
             "textbook-established; alpha' is THE fundamental length parameter of string theory"),
        item("ST-007", TONG_ST, "17-18", "1", "1.2.2", None, "(1.21)",
             "\\partial_\\alpha(\\sqrt{-\\det\\gamma}\\,\\gamma^{\\alpha\\beta}\\partial_\\beta X^\\mu)=0",
             "Nambu-Goto equations of motion for X^mu",
             "worldsheet covariant derivative implicit in the divergence structure",
             "obtained by varying (1.13)/(1.14) w.r.t. X^mu; explicitly noted to be nonlinear and intractable in this form, motivating the Polyakov reformulation",
             "directly derived in the source via delta(sqrt(-gamma)) = (1/2)sqrt(-gamma) gamma^{alpha beta} delta gamma_{alpha beta}",
             "textbook-established"),
        item("ST-008", TONG_ST, "18", "1", "1.3", None, "(1.22)",
             "S=-\\frac{1}{4\\pi\\alpha'}\\int d^2\\sigma\\sqrt{-g}\\,g^{\\alpha\\beta}\\partial_\\alpha X^\\mu \\partial_\\beta X^\\nu \\eta_{\\mu\\nu}",
             "Polyakov action: introduces an independent dynamical worldsheet metric g_{alpha beta} to eliminate the Nambu-Goto square root",
             "worldsheet metric g_{alpha beta} (2d 'gravity' field) coupled to D free scalars X^mu",
             "classically equivalent to Nambu-Goto (shown explicitly by solving g_{alpha beta}'s own e.o.m.); quantum equivalence only established in the critical dimension (flagged explicitly, not glossed over)",
             "this IS the requested S[X] from Part VIII of the L0-ST specification, confirmed present verbatim in this source with matching functional form (up to the overall convention for the 1/4pi alpha' prefactor)",
             "textbook-established; this is THE canonical action used for path-integral quantization of the bosonic string"),
        item("ST-009", TONG_ST, "19", "1", "1.3", None, "(1.24),(1.25)",
             "g_{\\alpha\\beta}=2f(\\sigma)\\,\\partial_\\alpha X\\cdot\\partial_\\beta X",
             "worldsheet metric's own equation of motion (stress tensor T_{alpha beta}=0 solved for g)",
             "none",
             "obtained by varying the Polyakov action w.r.t. g^{alpha beta}; the conformal factor f(sigma) is shown to drop out of the X-equation of motion, establishing classical equivalence to Nambu-Goto",
             "directly derived, eq (1.24)",
             "textbook-established"),
        item("ST-010", TONG_ST, "20-21", "1", "1.3.1", None, "(1.6),(1.26)-(1.29)",
             "X^\\mu \\to \\Lambda^\\mu_{\\ \\nu}X^\\nu+c^\\mu \\ (\\text{Poincare, global}); \\ \\sigma^\\alpha\\to\\tilde\\sigma^\\alpha(\\sigma)\\ (\\text{reparam., gauge}); \\ g_{\\alpha\\beta}\\to\\Omega^2(\\sigma)g_{\\alpha\\beta}\\ (\\text{Weyl})",
             "the three symmetries of the Polyakov action: Poincare invariance (global spacetime symmetry), reparametrization invariance (worldsheet diffeomorphism, gauge), Weyl invariance (local worldsheet rescaling, gauge)",
             "covariant derivative nabla_alpha with worldsheet Levi-Civita connection Gamma^sigma_{alpha beta} explicitly given",
             "Weyl invariance is explicitly noted as special to exactly two worldsheet dimensions -- the cancellation between sqrt(-g) scaling and the inverse-metric scaling only works for d=2, which is why higher-dimensional 'membranes' cannot be treated analogously (explicitly stated in source)",
             "Weyl invariance identified as the source of the counting that lets the worldsheet metric be gauge-fixed entirely (d(d+1)/2 - d - 1 = 0 for d=2)",
             "textbook-established; the two-dimensionality-dependence of Weyl invariance is a load-bearing structural fact for the whole bosonic-string construction"),
        item("ST-011", TONG_ST, "22", "1", "1.3.2", None, "(1.27),(1.28),(1.29)",
             "g_{\\alpha\\beta}=e^{2\\phi}\\eta_{\\alpha\\beta}\\ \\to\\ g_{\\alpha\\beta}=\\eta_{\\alpha\\beta}\\ (\\text{conformal gauge}); \\ \\sqrt{g'}R'=\\sqrt{g}(R-2\\nabla^2\\phi)",
             "conformal gauge fixing (using reparametrization to reach locally-conformally-flat form, then Weyl to remove the remaining conformal factor entirely); the 2D Weyl transformation law for the Ricci scalar",
             "Laplacian nabla^2 on the worldsheet",
             "explicitly restricted to worldsheets with trivial topology (non-trivial-topology subtleties are flagged as deferred to a later chapter, not treated here)",
             "the identity (1.29) is used to show that any 2D metric can be Weyl-transformed to have vanishing Ricci scalar, and that in exactly 2 dimensions a vanishing Ricci scalar implies a flat metric (via the explicit 2D Riemann-tensor decomposition R_{alpha beta gamma delta}=(R/2)(g_{alpha gamma}g_{beta delta}-g_{alpha delta}g_{beta gamma}))",
             "textbook-established; this is a genuine, source-derived (not merely stated) mathematical fact about 2D geometry, directly reusable"),
        item("ST-012", TONG_ST, "23-25", "1", "1.4", None, "(1.4.1)",
             "T_{\\alpha\\beta}=0 \\ (\\text{Virasoro constraints}), \\quad (\\dot X\\pm X')^2=0",
             "residual equations of motion for the metric after gauge-fixing (Virasoro constraints), plus the free-field wave equation for X",
             "light-cone worldsheet derivatives partial_+ , partial_-",
             "conformal gauge already imposed; periodic (closed-string) or Neumann/Dirichlet (open-string) boundary conditions",
             "obtained by varying the gauge-fixed Polyakov action; explicitly identified as 'the analog of the Gauss law in the string case'",
             "textbook-established"),
        item("ST-013", TONG_ST, "25-27", "1", "1.4", None, "mode-expansion formulas (unnumbered, ~p.25-27)",
             "X^\\mu(\\tau,\\sigma)=X_L^\\mu(\\tau+\\sigma)+X_R^\\mu(\\tau-\\sigma), \\ \\alpha_k^\\mu, \\bar\\alpha_k^\\mu \\ \\text{Fourier modes}",
             "oscillator mode expansion of the closed-string coordinate into left- and right-moving pieces",
             "Fourier mode operators alpha_k^mu (later promoted to creation/annihilation operators in Ch.2, not read this phase)",
             "solves the free 2D wave equation partial_+ partial_- X^mu = 0 subject to closed-string periodicity",
             "directly solved in source; reality condition on the alpha's given explicitly",
             "textbook-established"),
        item("ST-014", KIRITSIS, "10", "3", "3.1", None, "(3.1.1)-(3.1.4)",
             "S=m\\int_{\\tau_0}^{\\tau_1} d\\tau\\sqrt{-\\eta_{\\mu\\nu}\\dot x^\\mu \\dot x^\\nu}; \\quad p^2+m^2=0",
             "relativistic point-particle worldline action and its mass-shell constraint",
             "canonical momentum p_mu = -delta L/delta dot-x^mu",
             "signature eta_{mu nu}=diag(-1,+1,+1,+1)",
             "independently derived via the standard Lagrange-equation route; used as the classical warm-up before the string case, directly parallel to Tong ST-001/ST-002",
             "textbook-established; independent source confirms the same standard construction as Tong ST-001/002 (cross-source structural agreement, not identical notation)"),
        item("ST-015", KIRITSIS, "10-11", "3", "3.1", None, "(3.1.9),(3.1.13)",
             "S=-\\frac{1}{2}\\int d\\tau\\,e(\\tau)\\left(e^{-2}(\\tau)(\\dot x^\\mu)^2-m^2\\right); \\quad e=\\frac{1}{m}\\sqrt{-\\ddot x^2}",
             "einbein-field point-particle action and its on-shell solution for e(tau)",
             "einbein e(tau)",
             "allows the massless limit unlike the square-root action",
             "independently re-derived; used later (3.1.16 onward, not extracted this phase beyond the equation itself) to construct the free-particle propagator via a worldline path integral, including explicit zeta-function regularization of the resulting functional determinant",
             "textbook-established; matches Tong ST-004's einbein construction structurally (cross-source agreement)"),
        item("ST-016", KIRITSIS, "13-14", "3", "3.2", None, "(3.2.1),(3.2.4)",
             "S_{NG}=-T\\int dA = -T\\int\\sqrt{-\\det G_{ij}}\\,d^2\\xi",
             "Nambu-Goto action, area-of-worldsheet form, with explicit induced-metric definition G_{ij}=G_{mu nu} partial_i X^mu partial_j X^nu",
             "none (Lagrangian)",
             "flat target spacetime G_{mu nu}=eta_{mu nu} assumed for the explicit component form (3.2.4)",
             "independently constructed by direct analogy with the point-particle length action, exactly parallel to Tong ST-005 (cross-source structural agreement on the defining action of bosonic string theory)",
             "textbook-established"),
        item("ST-017", KIRITSIS, "14", "3", "3.2", None, "(3.2.7),(3.2.8)",
             "\\text{Neumann: } \\delta L/\\delta X'^\\mu|_{\\sigma=0,\\bar\\sigma}=0; \\quad \\text{Dirichlet: } \\delta L/\\delta \\dot X^\\mu|_{\\sigma=0,\\bar\\sigma}=0",
             "open-string boundary conditions (Neumann and Dirichlet)",
             "none",
             "open string worldsheet is a strip, sigma in [0,sigma-bar]",
             "stated directly, with Neumann's physical meaning (no momentum flow off string ends) proven explicitly later (via eq after 3.2.46, Tong-side ST-013's closed-string analogue is the periodicity condition instead)",
             "textbook-established; explicitly flagged in-source as relevant to D-branes (not developed further in the pages read this phase)"),
        item("ST-018", KIRITSIS, "15", "3", "3.2", None, "(3.2.12),(3.2.13),(3.2.14)",
             "S_P=-\\frac{T}{2}\\int d^2\\xi\\sqrt{-\\det g}\\,g^{\\alpha\\beta}\\partial_\\alpha X^\\mu \\partial_\\beta X^\\nu \\eta_{\\mu\\nu}; \\quad T_{\\alpha\\beta}=-\\frac{2}{T}\\frac{1}{\\sqrt{-\\det g}}\\frac{\\delta S_P}{\\delta g^{\\alpha\\beta}}",
             "Polyakov action and the worldsheet stress tensor defined as its metric variation",
             "worldsheet metric g_{alpha beta}; stress tensor T_{alpha beta}",
             "flat target space eta_{mu nu}",
             "independently constructed and varied, exactly parallel to Tong ST-008/ST-009 (cross-source structural agreement on the Polyakov action -- this is the second independent confirmation of the exact S[X] equation named in Part VIII of the L0-ST specification)",
             "textbook-established"),
        item("ST-019", KIRITSIS, "16", "3", "3.2", None, "(3.2.16),(3.2.17)",
             "\\lambda_1\\int\\sqrt{-\\det g}\\ (\\text{cosmological term, forbidden}); \\quad \\lambda_2\\int\\sqrt{-\\det g}\\,R^{(2)}\\ (\\text{Gauss-Bonnet, topological})",
             "classification of the only two additional terms Weyl invariance permits to be added to the Polyakov action",
             "worldsheet scalar curvature R^{(2)}",
             "Weyl invariance imposed as a hard constraint on allowed terms",
             "explicitly proven that the cosmological term forces trivial dynamics (g_{alpha beta}=0) if lambda_1 != 0, and that the Gauss-Bonnet term is a pure topological invariant (Euler number) with no effect on local equations of motion",
             "textbook-established; directly relevant to any future UOC variational construction wanting to know what symmetry-compatible terms exist"),
        item("ST-020", KIRITSIS, "16-17", "3", "3.2", None, "(3.2.18)-(3.2.24)",
             "\\delta X^\\mu=\\omega^\\mu_{\\ \\nu}X^\\nu+\\alpha^\\mu\\ (\\text{Poincare}); \\ \\delta g_{\\alpha\\beta}=\\nabla_\\alpha\\xi_\\beta+\\nabla_\\beta\\xi_\\alpha\\ (\\text{reparam}); \\ \\delta g_{\\alpha\\beta}=2\\Lambda g_{\\alpha\\beta}\\ (\\text{Weyl})",
             "the same three-symmetry structure as Tong ST-010 (Poincare/reparametrization/Weyl), independently presented",
             "worldsheet covariant derivative nabla_alpha",
             "same as ST-010",
             "independently derives the tracelessness of the stress tensor from conformal invariance for a GENERAL action S(g_{alpha beta}, phi^i), then specializes to the bosonic string -- this is a more general derivation than Tong's, showing tracelessness follows for ANY conformally invariant 2D theory with d_i=0 fields (eq 3.2.21-23)",
             "textbook-established; this general conformal-invariance-implies-traceless-stress-tensor argument (eq 3.2.21-23) is a reusable, independently-derived mathematical fact not explicitly given in the Tong pages read this phase"),
        item("ST-021", KIRITSIS, "18", "3", "3.2", None, "(3.2.34)-(3.2.37)",
             "\\partial_+\\partial_- X^\\mu=0\\ (\\text{e.o.m., conformal gauge}); \\quad T_{\\alpha\\beta}=0\\ (\\text{Virasoro constraints})",
             "free wave equation and Virasoro constraints in conformal gauge -- independently matches Tong ST-012",
             "light-cone derivatives partial_pm",
             "conformal gauge already fixed",
             "independently re-derived (cross-source agreement with Tong ST-012)",
             "textbook-established"),
        item("ST-022", KIRITSIS, "18-19", "3", "3.2", None, "(3.2.41)-(3.2.46)",
             "Q_f=\\int_0^{\\bar\\sigma}d\\sigma\\,f(\\xi^+)T_{++}(\\xi^+); \\quad P_\\mu^\\alpha=-T\\sqrt{\\det g}\\,g^{\\alpha\\beta}\\partial_\\beta X_\\mu; \\quad J_{\\mu\\nu}^\\alpha=-T\\sqrt{\\det g}\\,g^{\\alpha\\beta}(X_\\mu\\partial_\\beta X_\\nu-X_\\nu\\partial_\\beta X_\\mu)",
             "Noether currents and conserved charges of the Polyakov action: an infinite family Q_f from the traceless stress tensor, plus explicit momentum P_mu and angular-momentum J_{mu nu} currents from Poincare invariance",
             "conserved charge integrals P_mu = integral P_mu^tau d sigma, etc.",
             "closed-string boundary terms vanish automatically; open strings require Neumann conditions",
             "directly, explicitly derived Noether-current construction: this is a genuine, fully worked example of 'symmetry -> Noether current -> conserved charge -> proof of conservation via the field equations,' precisely the structure the canonical MDCL's unregistered NOETHER-SYMMETRY and CONSERVATION-LAW nodes require",
             "textbook-established; HIGH VALUE for the Symmetry/Conservation recovery per Part VIII/IX of the L0-ST spec -- an explicit, source-derived worked example, not merely an assertion"),
        item("ST-023", KIRITSIS, "19-20", "3", "3.3", None, "(3.3.2)-(3.3.9)",
             "X^\\mu(\\tau,\\sigma)=X_L^\\mu(\\tau+\\sigma)+X_R^\\mu(\\tau-\\sigma); \\quad \\alpha_0^\\mu=\\bar\\alpha_0^\\mu=\\frac{1}{\\sqrt{4\\pi T}}p^\\mu",
             "closed- and open-string oscillator mode expansions -- independently matches Tong ST-013 with different normalization convention",
             "Fourier modes alpha_k^mu, bar-alpha_k^mu",
             "closed-string periodicity or open-string Neumann boundary condition (giving alpha_k=bar-alpha_k, left/right movers mixed at the boundary)",
             "independently solved (cross-source agreement with Tong ST-013); explicitly shows open-string boundary condition forces p^mu=bar-p^mu and merges the two mode towers",
             "textbook-established"),
        item("ST-024", KIRITSIS, "21", "3", "3.3", None, "(3.3.16),(3.3.17)",
             "\\{X^\\mu(\\sigma,\\tau),\\dot X^\\nu(\\sigma',\\tau)\\}_{PB}=\\frac{1}{T}\\delta(\\sigma-\\sigma')\\eta^{\\mu\\nu}; \\quad \\{\\alpha_m^\\mu,\\alpha_n^\\nu\\}=\\{\\bar\\alpha_m^\\mu,\\bar\\alpha_n^\\nu\\}=-im\\delta_{m+n,0}\\eta^{\\mu\\nu}",
             "canonical (equal-time) Poisson brackets for the classical string field and the resulting oscillator-mode brackets",
             "Poisson bracket {,}_PB",
             "classical (pre-quantization) theory only -- this is the classical algebra, not yet the quantum commutator algebra (which appears in Ch.4, not read this phase)",
             "directly derived from the fundamental field/momentum bracket via the mode expansion",
             "textbook-established; this is the classical precursor to canonical quantization, explicitly NOT yet quantization itself"),
        item("ST-025", KIRITSIS, "22", "3", "3.3", None, "(3.3.21)-(3.3.27)",
             "L_m=\\frac{1}{2}\\sum_n \\alpha_{m-n}\\alpha_n; \\quad \\{L_m,L_n\\}_{PB}=-i(m-n)L_{m+n}",
             "Virasoro generators as Fourier modes of the (traceless) stress tensor, and the classical Virasoro algebra they satisfy under Poisson bracket",
             "Virasoro generators L_m, bar-L_m (classical, not yet quantum operators)",
             "conformal gauge; closed-string case shown explicitly, open-string case (no bar-L's) noted",
             "directly derived from the mode-expanded stress tensor and the oscillator Poisson brackets (ST-024); explicitly identifies H=L_0+bar-L_0 (closed) or H=L_0 (open) as the worldsheet Hamiltonian",
             "textbook-established; this is the CLASSICAL Virasoro algebra -- the quantum Virasoro algebra (with its central-charge anomaly term) is NOT in the pages read this phase (it appears in Ch.4/Tong Ch.4, not extracted here)"),
    ]
    return items


# ---------------------------------------------------------------------------
# Part V -- 52-item structure index (extra CSV, content required by spec
# though no explicit filename was mandated for this part alone)
# ---------------------------------------------------------------------------

STRUCTURE_TOPICS = [
    ("1", "Special relativity", "PRESENT", "ST-001,ST-002,ST-014", "Tong p.9-10; Kiritsis p.10", "1.1; 3.1", "(1.1),(1.2);(3.1.1)"),
    ("2", "Relativistic particles", "PRESENT", "ST-001,ST-002,ST-003,ST-004,ST-014,ST-015", "Tong p.9-13; Kiritsis p.10-11", "1.1; 3.1", "(1.1)-(1.10);(3.1.1)-(3.1.13)"),
    ("3", "Classical strings", "PRESENT", "ST-005,ST-016", "Tong p.14; Kiritsis p.13-14", "1.2; 3.2", "(1.11)-(1.14);(3.2.1)-(3.2.4)"),
    ("4", "Nambu-Goto action", "PRESENT", "ST-005,ST-006,ST-016", "Tong p.14-17; Kiritsis p.13-14", "1.2; 3.2", "(1.13),(1.14);(3.2.1),(3.2.4)"),
    ("5", "Polyakov action", "PRESENT", "ST-008,ST-018", "Tong p.18; Kiritsis p.15", "1.3; 3.2", "(1.22);(3.2.12)"),
    ("6", "Worldsheet geometry", "PRESENT", "ST-005,ST-009,ST-016", "Tong p.14,19; Kiritsis p.13", "1.2,1.3; 3.2", "(1.12),(1.25);(3.2.2),(3.2.3)"),
    ("7", "Reparametrization invariance", "PRESENT", "ST-002,ST-004,ST-010,ST-020", "Tong p.10,13,20; Kiritsis p.16-17", "1.1,1.3.1; 3.2", "(1.10),(1.26);(3.2.19),(3.2.24)"),
    ("8", "Worldsheet conformal invariance", "PRESENT", "ST-010,ST-011,ST-020", "Tong p.20-22; Kiritsis p.16-17", "1.3.1,1.3.2; 3.2", "(1.26)-(1.29);(3.2.20)-(3.2.23)"),
    ("9", "Classical equations of motion", "PRESENT", "ST-007,ST-009,ST-012,ST-021", "Tong p.17-18,23-25; Kiritsis p.15,18", "1.2.2,1.4; 3.2", "(1.21),(1.23);(3.2.15),(3.2.34)"),
    ("10", "Constraints", "PRESENT", "ST-012,ST-021", "Tong p.23-25; Kiritsis p.18", "1.4; 3.2", "T_ab=0 both sources"),
    ("11", "Gauge fixing", "PRESENT", "ST-011,ST-020", "Tong p.22; Kiritsis p.17", "1.3.2; 3.2", "(1.27),(1.28);(3.2.24)"),
    ("12", "Quantization", "TOC-ONLY, not extracted", "none (Ch.2/Ch.4 not read)", "Tong p.28+; Kiritsis p.23+", "2; 4", "none"),
    ("13", "Canonical quantization", "TOC-ONLY, not extracted", "none", "Tong p.28+; Kiritsis p.23+", "2.1; 4.1", "none"),
    ("14", "Path-integral quantization", "TOC-ONLY, not extracted", "none", "Tong p.108+ (Ch.5); Kiritsis p.28+", "5; 4.4", "none"),
    ("15", "Oscillator modes", "PRESENT (classical only)", "ST-013,ST-023,ST-024", "Tong p.25-27; Kiritsis p.19-21", "1.4; 3.3", "unnumbered (Tong); (3.3.2)-(3.3.17)"),
    ("16", "String spectrum", "TOC-ONLY, not extracted", "none (Ch.2.3 / Kiritsis 4.3 not read)", "Tong p.40+; Kiritsis p.26+", "2.3; 4.3", "none"),
    ("17", "Virasoro generators", "PRESENT (classical only)", "ST-025", "Kiritsis p.22", "3.3", "(3.3.21)-(3.3.26)"),
    ("18", "Virasoro algebra", "PRESENT (classical only)", "ST-025", "Kiritsis p.22", "3.3", "(3.3.27)"),
    ("19", "Critical dimension", "TOC-ONLY, not extracted", "none (Tong 5.3 not read)", "Tong p.117+", "5.3", "none"),
    ("20", "Ghost structure", "TOC-ONLY, not extracted", "none (Tong 2.1.1, 5.1.3 not read)", "Tong p.30,113+", "2.1.1; 5.1.3", "none"),
    ("21", "Bosonic string", "PRESENT", "ST-005 through ST-025 (all items this phase concern the bosonic string)", "Tong p.9-27; Kiritsis p.10-22", "1; 3", "many"),
    ("22", "Superstrings", "TOC-ONLY, not extracted", "none (Tong 2.5, Ch.3-superstring nod; Kiritsis Ch.10 not read)", "Tong p.48,56; Kiritsis p.104+", "2.5; 10", "none"),
    ("23", "Supersymmetry", "TOC-ONLY, not extracted", "none", "Kiritsis p.104+", "10", "none"),
    ("24", "Ramond/Neveu-Schwarz sectors", "TOC-ONLY, not extracted", "none", "Kiritsis p.104+ (implied by Ch.10 title, not seen directly in TOC line items read)", "10", "none"),
    ("25", "GSO projection", "TOC-ONLY, not extracted", "none", "not located in either TOC's visible section titles; likely within Ch.10 (Kiritsis) or Tong Ch.2.5/superstring chapters, not confirmed since unread", "unknown", "none"),
    ("26", "D-branes", "PRESENT (TOC + boundary-condition mention only, not deeply extracted)", "ST-017 (Dirichlet boundary condition explicitly flagged as D-brane-relevant)", "Tong TOC Ch.3 p.50-59; Kiritsis p.14", "3 (Tong); 3.2 (Kiritsis)", "(3.2.8) Dirichlet condition"),
    ("27", "Open strings", "PRESENT", "ST-017,ST-023", "Tong TOC Ch.3; Kiritsis p.14,19-20", "3 (Tong, TOC only); 3.2,3.3 (Kiritsis, read)", "(3.2.7),(3.2.8);(3.3.8),(3.3.9)"),
    ("28", "Closed strings", "PRESENT", "ST-005,ST-013,ST-023", "Tong p.14,25-27; Kiritsis p.19-20", "1.2,1.4; 3.3", "(1.11);(3.3.2)-(3.3.6)"),
    ("29", "String interactions", "TOC-ONLY, not extracted", "none (Tong Ch.6, Kiritsis Ch.5 not read)", "Tong p.125+; Kiritsis p.36+", "6; 5", "none"),
    ("30", "Scattering amplitudes", "TOC-ONLY, not extracted", "none", "Tong p.125+; Kiritsis p.98+", "6; 8", "none"),
    ("31", "Conformal field theory", "TOC-ONLY, not extracted", "none (Tong Ch.4, Kiritsis Ch.6 not read; only the conformal-INVARIANCE property of the Polyakov action itself was read, item 8 above, which is distinct from full CFT machinery)", "Tong p.61+; Kiritsis p.38+", "4; 6", "none"),
    ("32", "Anomalies", "TOC-ONLY, not extracted", "none (Kiritsis Ch.11 not read)", "Kiritsis p.122+", "11", "none"),
    ("33", "Modular invariance", "TOC-ONLY, not extracted", "none (Tong 6.4.1 not read)", "Tong p.143+", "6.4.1", "none"),
    ("34", "Compactification", "TOC-ONLY, not extracted", "none (Tong Ch.8, Kiritsis Ch.12 not read)", "Tong p.197+; Kiritsis p.130+", "8; 12", "none"),
    ("35", "Kaluza-Klein reduction", "TOC-ONLY, not extracted", "none (Kiritsis Appendix C not read)", "Kiritsis p.219+", "App. C", "none"),
    ("36", "Calabi-Yau compactification", "PRESENT (single passing mention only, not a derivation)", "none", "Tong p.4 (Introduction, 'mirror symmetry ... topologically different Calabi-Yau manifolds')", "Introduction", "none (prose mention only)"),
    ("37", "Gauge symmetry emergence", "PRESENT (single passing mention only)", "none", "Tong p.1 ('General relativity, electromagnetism and Yang-Mills gauge theories all appear in a surprising fashion')", "0. Introduction", "none (prose mention only)"),
    ("38", "Supersymmetry breaking", "TOC-ONLY, not extracted", "none", "Kiritsis p.130,153+", "12.5", "none"),
    ("39", "Effective field theory", "PRESENT (single passing mention + TOC)", "none", "Tong p.5-6 (non-renormalizability discussion); TOC Ch.7", "0.1; 7", "none (Ch.7 itself not read)"),
    ("40", "Low-energy limits", "TOC-ONLY, not extracted", "none (Tong Ch.7, Kiritsis Ch.9 not read)", "Tong p.157+; Kiritsis p.102+", "7; 9", "none"),
    ("41", "General relativity limit", "PRESENT (introduction discussion only, not string-derived)", "none", "Tong p.3-8 (Einstein-Hilbert action, non-renormalizability discussion -- background material, NOT derived from string theory in the pages read)", "0.1", "S_EH=(1/16 pi G_N) int d^4x sqrt(-g) R (stated, not derived from strings)"),
    ("42", "Supergravity", "TOC-ONLY, not extracted", "none (Kiritsis Appendix D not read)", "Kiritsis p.221+", "App. D", "none"),
    ("43", "Dualities", "TOC-ONLY, not extracted", "none (Tong Ch.8.3-8.4, Kiritsis Ch.14 not read)", "Tong p.204+; Kiritsis p.179+", "8.3-8.4; 14", "none"),
    ("44", "T-duality", "TOC-ONLY, not extracted", "none (Tong Ch.8, Kiritsis 7.3 not read)", "Tong p.197+; Kiritsis p.85+", "8; 7.3", "none"),
    ("45", "S-duality", "TOC-ONLY, not extracted", "none (Kiritsis 14.6 not read)", "Kiritsis p.196+", "14.6", "none"),
    ("46", "U-duality", "NONE FOUND", "n/a", "not located in either TOC's visible section titles", "n/a", "none"),
    ("47", "Nonperturbative structure", "TOC-ONLY, not extracted", "none (Kiritsis Ch.14 not read)", "Kiritsis p.179+", "14", "none"),
    ("48", "Black holes", "PRESENT (single passing mention only)", "none", "Tong p.1,6-7 (information paradox, entropy of black holes mentioned in Introduction)", "0. Introduction", "none (prose mention only, not derived)"),
    ("49", "String thermodynamics", "NONE FOUND", "n/a", "not located in the pages read (would likely be in unread chapters)", "n/a", "none"),
    ("50", "Cosmological applications", "PRESENT (single passing mention only)", "none", "Tong p.7 (cosmological constant discussion, 'explained away as an environmental quantity as in string theory')", "0.1", "none (prose mention only)"),
    ("51", "Quantum gravity implications", "PRESENT", "none (extensive prose discussion, not equation-level)", "Tong p.1-8 (full section 0.1 'Quantum Gravity')", "0.1", "(S_EH),(various perturbative-expansion schematics)"),
    ("52", "Unresolved problems", "PRESENT", "none (prose)", "Tong p.1-8 (singularities, non-renormalizability, unknown unknowns, cosmological constant); Kiritsis p.9 (UV-divergence of quantum gravity, non-renormalizability of Einstein gravity + matter)", "0.1; 2", "(2.7) Kiritsis two-graviton UV divergence estimate"),
]


# ---------------------------------------------------------------------------
# Part VI -- STRING_THEORY_MDCL_CROSSWALK.csv
# ---------------------------------------------------------------------------

MDCL_CROSSWALK_ROWS = [
    dict(STRING_ITEM_ID="ST-008,ST-018", SOURCE_ID="LIT-TONG-ST;LIT-KIRITSIS-SST", MDCL_NODE_ID="VARIATIONAL-NODE",
         MDCL_BRANCH_ID="Variational", STRUCTURAL_CORRESPONDENCE="ANALOGOUS",
         DEPENDENCY_CORRESPONDENCE="NONE -- the Polyakov action's fields (X^mu, g_ab) are not derived from SPECTRUM-NODE or any UOC object",
         NOTATION_CORRESPONDENCE="NONE -- source notation (S, X^mu, g_ab, alpha') preserved separately, no mapping performed",
         DERIVATION_CORRESPONDENCE="PARTIAL -- both sources independently derive an action -> stationarity -> equations-of-motion chain in full, twice-confirmed cross-source, but for string-specific fields, not UOC fields",
         IMPLEMENTATION_CORRESPONDENCE="NONE -- no code exists for VARIATIONAL-NODE to compare against",
         VALIDATION_CORRESPONDENCE="NONE",
         STATUS="genuine worked implementation TEMPLATE for the missing action->EL-equations pipeline, not a proof of correspondence"),
    dict(STRING_ITEM_ID="ST-022", SOURCE_ID="LIT-KIRITSIS-SST", MDCL_NODE_ID="NOETHER-SYMMETRY (not registered)",
         MDCL_BRANCH_ID="Symmetry", STRUCTURAL_CORRESPONDENCE="ANALOGOUS",
         DEPENDENCY_CORRESPONDENCE="NONE", NOTATION_CORRESPONDENCE="NONE",
         DERIVATION_CORRESPONDENCE="PARTIAL -- a full, explicit Noether current/conserved-charge construction (symmetry -> current -> charge -> proof of conservation) is present and directly reusable as an implementation template, though for the Poincare symmetry of the string action, not a UOC-specific symmetry",
         IMPLEMENTATION_CORRESPONDENCE="NONE", VALIDATION_CORRESPONDENCE="NONE",
         STATUS="highest-value single crosswalk item in this corpus for the Symmetry branch"),
    dict(STRING_ITEM_ID="ST-022", SOURCE_ID="LIT-KIRITSIS-SST", MDCL_NODE_ID="CONSERVATION-LAW (not registered)",
         MDCL_BRANCH_ID="Conservation", STRUCTURAL_CORRESPONDENCE="ANALOGOUS",
         DEPENDENCY_CORRESPONDENCE="NONE", NOTATION_CORRESPONDENCE="NONE",
         DERIVATION_CORRESPONDENCE="PARTIAL -- explicit conservation proof (d_alpha P^alpha_mu=0) is present as a direct corollary of the Noether construction above",
         IMPLEMENTATION_CORRESPONDENCE="NONE", VALIDATION_CORRESPONDENCE="NONE",
         STATUS="direct corollary of the NOETHER-SYMMETRY crosswalk row above"),
    dict(STRING_ITEM_ID="ST-011", SOURCE_ID="LIT-TONG-ST", MDCL_NODE_ID="GEOMETRY-NODE",
         MDCL_BRANCH_ID="Geometry", STRUCTURAL_CORRESPONDENCE="NONE",
         DEPENDENCY_CORRESPONDENCE="NONE", NOTATION_CORRESPONDENCE="NONE",
         DERIVATION_CORRESPONDENCE="NONE -- this is 2D WORLDSHEET geometry (Weyl-transform-to-flat, 2D Riemann tensor decomposition), not 4D target-spacetime geometry; per Part IX's explicit instruction, worldsheet geometry != target-space geometry != spacetime geometry unless the source explicitly bridges them, and the pages read this phase do NOT perform that bridge (it would require the unread Tong Ch.7 'Low Energy Effective Actions')",
         IMPLEMENTATION_CORRESPONDENCE="NONE", VALIDATION_CORRESPONDENCE="NONE",
         STATUS="explicitly NOT collapsed into a Geometry-branch correspondence -- see STRING_GR_GEOMETRY_CROSSWALK.md"),
    dict(STRING_ITEM_ID="ST-025", SOURCE_ID="LIT-KIRITSIS-SST", MDCL_NODE_ID="SPECTRUM-L / OPERATOR-L (Test1/Spectral pipeline)",
         MDCL_BRANCH_ID="Spectral", STRUCTURAL_CORRESPONDENCE="ANALOGOUS",
         DEPENDENCY_CORRESPONDENCE="NONE", NOTATION_CORRESPONDENCE="NONE",
         DERIVATION_CORRESPONDENCE="NONE -- the classical Virasoro algebra {L_m,L_n}=-i(m-n)L_{m+n} is a fundamentally different mathematical object from the graph Laplacian's eigenvalue spectrum (an infinite-dimensional Lie algebra of worldsheet-reparametrization generators, vs. a finite symmetric matrix's eigendecomposition); the resemblance is only at the level of 'both are called a spectral/mode structure,' explicitly the kind of false-equivalence this campaign's rules prohibit",
         IMPLEMENTATION_CORRESPONDENCE="NONE", VALIDATION_CORRESPONDENCE="NONE",
         STATUS="ANALOGOUS at the vocabulary level only -- see STRING_SPECTRAL_CROSSWALK.csv for the full non-equivalence argument"),
    dict(STRING_ITEM_ID="ST-010,ST-020", SOURCE_ID="LIT-TONG-ST;LIT-KIRITSIS-SST", MDCL_NODE_ID="QUANTUM-NODE",
         MDCL_BRANCH_ID="Quantum", STRUCTURAL_CORRESPONDENCE="UNDETERMINED",
         DEPENDENCY_CORRESPONDENCE="UNDETERMINED", NOTATION_CORRESPONDENCE="UNDETERMINED",
         DERIVATION_CORRESPONDENCE="UNDETERMINED -- canonical quantization of the string (Tong Ch.2 / Kiritsis Ch.4) was NOT read this phase; only the classical Poisson-bracket algebra (ST-024, the direct classical precursor) was read",
         IMPLEMENTATION_CORRESPONDENCE="NONE", VALIDATION_CORRESPONDENCE="NONE",
         STATUS="genuinely undetermined pending further reading, not silently assumed absent or present"),
    dict(STRING_ITEM_ID="n/a", SOURCE_ID="LIT-TONG-ST;LIT-KIRITSIS-SST", MDCL_NODE_ID="GAUGE-NODE",
         MDCL_BRANCH_ID="Gauge/Standard Model", STRUCTURAL_CORRESPONDENCE="UNDETERMINED",
         DEPENDENCY_CORRESPONDENCE="UNDETERMINED", NOTATION_CORRESPONDENCE="UNDETERMINED",
         DERIVATION_CORRESPONDENCE="UNDETERMINED -- gauge-symmetry-emergence content (Tong Ch.7.7 Yang-Mills action, Ch.8 compactification-generated gauge symmetry; Kiritsis Ch.12 compactification) was NOT read this phase, only referenced by TOC and one passing Introduction sentence (Tong p.1)",
         IMPLEMENTATION_CORRESPONDENCE="NONE", VALIDATION_CORRESPONDENCE="NONE",
         STATUS="genuinely undetermined -- see STRING_SM_CROSSWALK.csv"),
]


# ---------------------------------------------------------------------------
# Part VII -- STRING_THEORY_BRANCH_RECOVERY_MATRIX.csv
# ---------------------------------------------------------------------------

BRANCH_RECOVERY_ROWS = [
    dict(BRANCH="A. Variational structure", RELEVANT_DERIVATION_PRESENT="YES -- full Polyakov/Nambu-Goto action->EOM chain, twice cross-source confirmed",
         REPRODUCES_MDCL_RESULT="NO -- VARIATIONAL-NODE has no existing result to reproduce", INDEPENDENT_DERIVATION_OF_EXISTING="NO (nothing exists yet)",
         IDENTIFIES_MISSING_DEPENDENCY="YES -- confirms the missing piece is specifically 'a field content + Lagrangian density,' not the variational machinery itself, which is standard and now has 2 worked examples",
         PROVIDES_IMPLEMENTATION_TARGET="YES -- see PROPOSED_STRING_VARIATIONAL_RECOVERY.md", PROVIDES_VALIDATION_TARGET="YES -- dimensional consistency, EOM reduction checks demonstrated in-source",
         INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="YES -- string-specific fields (X^mu embedding coordinates, alpha', worldsheet metric g_ab) are not canonical UOC objects and must not be imported"),
    dict(BRANCH="B. Euler-Lagrange equations", RELEVANT_DERIVATION_PRESENT="YES -- (1.21)/(1.23) Nambu-Goto/Polyakov EOM, (3.2.15)/(3.2.34) Kiritsis parallel",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO",
         IDENTIFIES_MISSING_DEPENDENCY="YES -- same as A, EL equations are the direct corollary once an action exists",
         PROVIDES_IMPLEMENTATION_TARGET="YES (subsumed under A)", PROVIDES_VALIDATION_TARGET="YES (subsumed under A)",
         INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="YES (same as A)"),
    dict(BRANCH="C. Symmetry", RELEVANT_DERIVATION_PRESENT="YES -- ST-010/ST-020 (Poincare/reparam/Weyl) + ST-022 (explicit Noether construction)",
         REPRODUCES_MDCL_RESULT="NO -- NOETHER-SYMMETRY has no existing result", INDEPENDENT_DERIVATION_OF_EXISTING="NO",
         IDENTIFIES_MISSING_DEPENDENCY="YES -- confirms NOETHER-SYMMETRY is blocked purely on VARIATIONAL-NODE, not on any missing mathematical machinery (the Noether procedure itself is fully demonstrated)",
         PROVIDES_IMPLEMENTATION_TARGET="YES -- ST-022's derivation is directly reusable as a template once a UOC Lagrangian exists", PROVIDES_VALIDATION_TARGET="YES -- explicit conservation-law verification method (integrate d_alpha T^alpha_beta and show boundary terms vanish) demonstrated",
         INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="YES -- Poincare symmetry specifically; a UOC symmetry group would need independent justification"),
    dict(BRANCH="D. Conservation", RELEVANT_DERIVATION_PRESENT="YES -- ST-022 (direct corollary of C)",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO",
         IDENTIFIES_MISSING_DEPENDENCY="YES -- same as C", PROVIDES_IMPLEMENTATION_TARGET="YES (subsumed under C)",
         PROVIDES_VALIDATION_TARGET="YES (subsumed under C)", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="YES (same as C)"),
    dict(BRANCH="E. General relativity", RELEVANT_DERIVATION_PRESENT="PARTIAL -- Tong's Introduction (p.3-8) states the Einstein-Hilbert action and non-renormalizability arguments, but does NOT derive General Relativity from string theory in the pages read (that would be Ch.7, not read)",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO -- the Einstein-Hilbert action is stated as known background, not derived",
         IDENTIFIES_MISSING_DEPENDENCY="PARTIAL -- confirms Geometry/GR need a genuinely different reference (differential geometry text, or the unread string-theory low-energy-effective-action chapters)",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO",
         INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A -- nothing usable extracted"),
    dict(BRANCH="F. Quantum mechanics", RELEVANT_DERIVATION_PRESENT="PARTIAL -- ST-003 (point-particle Klein-Gordon quantization) and ST-024 (classical Poisson-bracket algebra, the direct precursor to canonical quantization) present; full string canonical quantization (Tong Ch.2/Kiritsis Ch.4) NOT read",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO",
         IDENTIFIES_MISSING_DEPENDENCY="PARTIAL", PROVIDES_IMPLEMENTATION_TARGET="PARTIAL -- ST-003's simple point-particle canonical-quantization example (p_mu -> -i d/dX^mu) is a usable minimal template",
         PROVIDES_VALIDATION_TARGET="PARTIAL", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="YES"),
    dict(BRANCH="G. Quantum field theory", RELEVANT_DERIVATION_PRESENT="NO -- not read this phase (QFT machinery beyond the single Klein-Gordon example is not covered by the pages extracted)",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO", IDENTIFIES_MISSING_DEPENDENCY="UNDETERMINED",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
    dict(BRANCH="H. Gauge theory", RELEVANT_DERIVATION_PRESENT="NO -- Yang-Mills-from-strings content (Tong 7.7) not read this phase; only a single passing Introduction sentence exists in the extracted pages",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO", IDENTIFIES_MISSING_DEPENDENCY="UNDETERMINED",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
    dict(BRANCH="I. Thermodynamics", RELEVANT_DERIVATION_PRESENT="NO -- not located anywhere in the pages read or in the visible TOC section titles",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO", IDENTIFIES_MISSING_DEPENDENCY="NO -- this corpus (as read) offers nothing for Thermodynamics",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
    dict(BRANCH="J. Statistical mechanics", RELEVANT_DERIVATION_PRESENT="NO -- partition-function/statistical-ensemble content (Tong Ch.6.4, one-loop partition function) not read this phase",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO", IDENTIFIES_MISSING_DEPENDENCY="UNDETERMINED",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
    dict(BRANCH="K. Cosmology", RELEVANT_DERIVATION_PRESENT="NO -- only a single passing Introduction mention of the cosmological constant as a 'string-theory environmental quantity' (Tong p.7), no derivation",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO", IDENTIFIES_MISSING_DEPENDENCY="NO",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
    dict(BRANCH="L. Quantum gravity", RELEVANT_DERIVATION_PRESENT="PARTIAL -- Tong's full section 0.1 (p.1-8) is a substantial PROSE discussion of why quantum gravity is hard and what string theory claims to offer, but contains no equation-level bridge between quantum mechanics and gravity in the pages read",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO",
         IDENTIFIES_MISSING_DEPENDENCY="PARTIAL -- confirms this campaign's own prior assessment that the Quantum/Gravity interface is closer to an open research problem than an implementation gap, from an independent source",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
    dict(BRANCH="M. Spectral operators", RELEVANT_DERIVATION_PRESENT="YES -- ST-025 classical Virasoro algebra, ST-013/ST-023 mode expansions",
         REPRODUCES_MDCL_RESULT="NO -- structurally unrelated to the existing graph-Laplacian spectral branch (see STRING_SPECTRAL_CROSSWALK.csv)", INDEPENDENT_DERIVATION_OF_EXISTING="NO",
         IDENTIFIES_MISSING_DEPENDENCY="NO -- the existing Spectral branch is already fully closed and needs nothing from this corpus",
         PROVIDES_IMPLEMENTATION_TARGET="NO -- not applicable, different mathematical object", PROVIDES_VALIDATION_TARGET="NO",
         INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A -- no recovery attempted here"),
    dict(BRANCH="N. Geometry", RELEVANT_DERIVATION_PRESENT="PARTIAL -- ST-011 (2D worldsheet Weyl-to-flat, 2D Riemann decomposition) is a genuine, source-derived 2D differential-geometry fact, but explicitly NOT target-spacetime geometry",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO",
         IDENTIFIES_MISSING_DEPENDENCY="PARTIAL -- confirms that even where this corpus DOES contain real differential geometry, it is 2D worldsheet geometry, not the 4D spacetime geometry GEOMETRY-NODE actually needs -- a negative but useful finding, not a false positive",
         PROVIDES_IMPLEMENTATION_TARGET="NO -- wrong dimensionality/target for GEOMETRY-NODE's actual requirement", PROVIDES_VALIDATION_TARGET="NO",
         INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
    dict(BRANCH="O. Effective field theory", RELEVANT_DERIVATION_PRESENT="NO -- Tong Ch.7 'Low Energy Effective Actions' not read this phase; only referenced by TOC and by the non-string-derived background discussion in the Introduction",
         REPRODUCES_MDCL_RESULT="NO", INDEPENDENT_DERIVATION_OF_EXISTING="NO", IDENTIFIES_MISSING_DEPENDENCY="UNDETERMINED",
         PROVIDES_IMPLEMENTATION_TARGET="NO", PROVIDES_VALIDATION_TARGET="NO", INTRODUCES_ASSUMPTIONS_ABSENT_FROM_CANON="N/A"),
]


# ---------------------------------------------------------------------------
# Part XI -- STRING_SM_CROSSWALK.csv
# ---------------------------------------------------------------------------

SM_CROSSWALK_ROWS = [
    dict(TOPIC="Gauge groups", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="Tong Ch.7.7 'The Yang-Mills Action' (p.191, NOT read); Kiritsis Ch.10-12 (NOT read)",
         CORRESPONDS_TO_MDCL_NODE="GAUGE-NODE", CLASSIFICATION="UNDETERMINED"),
    dict(TOPIC="Gauge fields", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="same as above",
         CORRESPONDS_TO_MDCL_NODE="GAUGE-NODE", CLASSIFICATION="UNDETERMINED"),
    dict(TOPIC="Representations", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="not read this phase",
         CORRESPONDS_TO_MDCL_NODE="GAUGE-NODE", CLASSIFICATION="UNDETERMINED"),
    dict(TOPIC="Matter fields", PRESENT_IN_PAGES_READ="PARTIAL -- X^mu are the string's own embedding-coordinate fields, not Standard-Model matter fields",
         SOURCE_LOCATION="Tong 1.2-1.3 (ST-005,ST-008)", CORRESPONDS_TO_MDCL_NODE="MATTER-NODE",
         CLASSIFICATION="NONE -- embedding coordinates are not a matter-field representation in the Standard-Model sense"),
    dict(TOPIC="Fermions", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="requires superstring/RNS chapters, not read",
         CORRESPONDS_TO_MDCL_NODE="MATTER-NODE", CLASSIFICATION="UNDETERMINED"),
    dict(TOPIC="Chiral structure", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="not read this phase",
         CORRESPONDS_TO_MDCL_NODE="MATTER-NODE", CLASSIFICATION="UNDETERMINED"),
    dict(TOPIC="Anomaly cancellation", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="Kiritsis Ch.11 'Anomalies' (p.122, NOT read)",
         CORRESPONDS_TO_MDCL_NODE="GAUGE-NODE", CLASSIFICATION="UNDETERMINED"),
    dict(TOPIC="Compactification-generated gauge symmetry", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="Tong Ch.8.2.3 'Enhanced Gauge Symmetry' (p.203, NOT read)",
         CORRESPONDS_TO_MDCL_NODE="GAUGE-NODE", CLASSIFICATION="UNDETERMINED"),
    dict(TOPIC="Effective field theory / low-energy SM limit", PRESENT_IN_PAGES_READ="NO", SOURCE_LOCATION="Tong Ch.7 (NOT read)",
         CORRESPONDS_TO_MDCL_NODE="GAUGE-NODE, MATTER-NODE", CLASSIFICATION="UNDETERMINED"),
]


# ---------------------------------------------------------------------------
# Part XII -- STRING_SPECTRAL_CROSSWALK.csv
# ---------------------------------------------------------------------------

SPECTRAL_CROSSWALK_ROWS = [
    dict(STRING_OBJECT="Classical Virasoro generators L_m (ST-025)", EXISTING_SPECTRAL_OBJECT="graph Laplacian eigenvalues lambda_n (SPECTRUM-L)",
         MATHEMATICAL_RELATIONSHIP="NONE -- L_m are Fourier modes of a 2D worldsheet stress tensor, elements of an infinite-dimensional Lie algebra (the Virasoro algebra) under a Poisson-bracket product; lambda_n are eigenvalues of a finite symmetric real matrix (the graph Laplacian) under ordinary matrix eigendecomposition. Different mathematical category entirely (Lie-algebra generator vs. matrix eigenvalue).",
         EQUIVALENCE_OR_INDEPENDENCE="INDEPENDENT", NOTES="Vocabulary overlap ('spectral', 'mode') only -- exactly the kind of false equivalence Part XII warns against inferring"),
    dict(STRING_OBJECT="Oscillator modes alpha_k^mu (ST-013, ST-023)", EXISTING_SPECTRAL_OBJECT="graph Laplacian eigenvectors phi_n (SPECTRUM-L)",
         MATHEMATICAL_RELATIONSHIP="NONE -- alpha_k^mu are Fourier coefficients of a classical field's mode expansion in a periodic worldsheet coordinate; phi_n are eigenvectors of a specific finite matrix. No shared operator, domain, or algebra.",
         EQUIVALENCE_OR_INDEPENDENCE="INDEPENDENT", NOTES="Both are called 'modes' in their respective literatures, nothing more"),
    dict(STRING_OBJECT="Worldsheet Hamiltonian H=L_0+bar-L_0 (ST-025)", EXISTING_SPECTRAL_OBJECT="heat-flow operator R(t)=exp(-tL) (HEAT-FLOW-R)",
         MATHEMATICAL_RELATIONSHIP="NONE -- H generates worldsheet time translation for the string's classical dynamics; R(t) is a fixed one-parameter semigroup built from the SAME graph Laplacian L already in SPECTRUM-L. No shared construction.",
         EQUIVALENCE_OR_INDEPENDENCE="INDEPENDENT", NOTES="No heat-kernel or heat-trace object was found anywhere in the pages read this phase (would require Tong Ch.5/CFT chapters, not read)"),
    dict(STRING_OBJECT="Partition functions", EXISTING_SPECTRAL_OBJECT="K(t)=sum_n exp(-t lambda_n) (heat trace, Spectral branch)",
         MATHEMATICAL_RELATIONSHIP="UNDETERMINED -- Tong Ch.6.4.2 'The One-Loop Partition Function' (p.146) and its relation to heat-kernel-like objects was NOT read this phase; a genuine relationship may exist (string one-loop partition functions are known in the broader literature to involve theta-function/heat-kernel structures) but this was not verified by direct reading here",
         EQUIVALENCE_OR_INDEPENDENCE="UNDETERMINED", NOTES="Flagged as the single most promising unread topic for a future, deeper Spectral-branch crosswalk"),
]


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main():
    lit_dir = ROOT / "literature"

    (lit_dir / "manifests" / "STRING_THEORY_CORPUS_MANIFEST.json").write_text(
        json.dumps(build_corpus_manifest(), indent=2) + "\n")
    print("wrote literature/manifests/STRING_THEORY_CORPUS_MANIFEST.json")

    write_csv(lit_dir / "manifests" / "STRING_THEORY_VERSION_MATRIX.csv", VERSION_MATRIX_ROWS)
    print("wrote literature/manifests/STRING_THEORY_VERSION_MATRIX.csv")

    registry = build_literature_registry()
    (lit_dir / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json").write_text(
        json.dumps(registry, indent=2) + "\n")
    print(f"wrote literature/extraction/STRING_THEORY_LITERATURE_REGISTRY.json ({len(registry)} items)")

    structure_rows = [
        dict(ITEM_NUMBER=n, TOPIC=t, PRESENT=p, SOURCE_IDS=s, PAGE_RANGE=pg, SECTION_RANGE=sec, EQUATION_REFERENCES=eq)
        for (n, t, p, s, pg, sec, eq) in STRUCTURE_TOPICS
    ]
    write_csv(lit_dir / "extraction" / "STRING_THEORY_STRUCTURE_INDEX.csv", structure_rows)
    print(f"wrote literature/extraction/STRING_THEORY_STRUCTURE_INDEX.csv ({len(structure_rows)} rows)")

    write_csv(lit_dir / "crosswalk" / "STRING_THEORY_MDCL_CROSSWALK.csv", MDCL_CROSSWALK_ROWS)
    print("wrote literature/crosswalk/STRING_THEORY_MDCL_CROSSWALK.csv")

    write_csv(lit_dir / "crosswalk" / "STRING_THEORY_BRANCH_RECOVERY_MATRIX.csv", BRANCH_RECOVERY_ROWS)
    print("wrote literature/crosswalk/STRING_THEORY_BRANCH_RECOVERY_MATRIX.csv")

    write_csv(lit_dir / "crosswalk" / "STRING_SM_CROSSWALK.csv", SM_CROSSWALK_ROWS)
    print("wrote literature/crosswalk/STRING_SM_CROSSWALK.csv")

    write_csv(lit_dir / "crosswalk" / "STRING_SPECTRAL_CROSSWALK.csv", SPECTRAL_CROSSWALK_ROWS)
    print("wrote literature/crosswalk/STRING_SPECTRAL_CROSSWALK.csv")


if __name__ == "__main__":
    main()
