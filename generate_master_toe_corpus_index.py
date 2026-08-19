"""
Master TOE Derivation Campaign: MASTER_THEORY_CORPUS_INDEX.csv and
MASTER_TOE_DEPENDENCY_GRAPH.{json,csv} generator.

Built from direct inspection this campaign: full-text extraction (pdftotext
-layout / python-docx) of every PDF/DOCX in the repository root, deep reads
of the highest-value documents (Master Equation Codex, DTC_Formal_Structure,
DTC-RP-004_Forced_vs_Free, DTC_COMPILER, SEIT v2, Functorial Gauge
Unification, geometric unification paper, DTC_Rosetta_Stone_TOE_v2), plus
the pre-existing, already-executed audit in compiler/historical/register.py
(which corpus-wide-searched for specific named "obstruction" artifacts and
confirmed them absent -- independently re-confirmed by grep this campaign).

Every row's verification_status is honest about what was and was not
actually checked. Nothing here modifies any canonical registry.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIMESTAMP = "2026-08-19T18:51:43Z"
COMMIT = "791d8b0e2d58784b26697c8571b9f4bf6d455e85"

ROWS = [
    # --- Master Equation Codex (deep read, author Keith I. Blaze, June 2026) ---
    dict(source_id="MEC-0", filename="Master Equation Codex.pdf", source_class="B (grandiose-synthesis)",
         branch="Primitive/Spectral", section="0-1", equation_identifier="0.1-1.4",
         equation_text="U={Delta_i}; A=(A_ij); D=diag(d_i); L=D-A; L psi_n=lambda_n psi_n; J_L^2=L (Dirac-op-as-sqrt(L))",
         variables="N distinctions, adjacency A, degree D, Laplacian L, eigenpairs (lambda_n,psi_n)",
         assumptions="A universal distinction graph is the sole primitive input; not independently justified",
         dependencies="none (postulated root)", claimed_result="graph->Laplacian->spectrum cascade as the foundation of all physics",
         current_status="PARTIALLY EXECUTED (in this project's own code, not by this document)",
         canonical_match="GRAPH-G-SEED->OPERATOR-L->SPECTRUM-L (Test1 pipeline, VERIFIED)",
         external_match="standard spectral graph theory (Chung, 1997)", executable="YES (already implemented, compiler/backends/graph_laplacian.py)",
         verification_status="Sections 0-1's mathematical content (L=D-A, eigenproblem) is standard, correct spectral graph theory and IS already independently reconstructed and executed in this project's Test1 pipeline -- but that reconstruction is prior work, not new work this campaign attributes to this document. Calling the square-root L^(1/2) a 'Dirac operator' (eq 1.3) is an unsubstantiated physics-interpretation claim: a positive operator's functional square root is standard math, but nothing shown establishes Clifford-algebra/spinor structure to justify the physical name.",
         falsification_status="not falsified (the graph/Laplacian/spectrum content is mathematically sound); the 'Dirac operator' naming is unsupported, not falsified",
         promotion_candidate="NO new promotion -- already covered by existing canonical Test1 nodes"),
    dict(source_id="MEC-3", filename="Master Equation Codex.pdf", source_class="B (grandiose-synthesis)",
         branch="Geometry", section="3", equation_identifier="3.1-3.6",
         equation_text="d(i,j)=[sum_{n in Pi}|psi_n(i)-psi_n(j)|^2]^(1/2); g_ij=lim_{x'->x} d^2 d/dx^i dx'^j; Gamma,R,G_munu standard GR formulas",
         variables="diffusion distance d(i,j), metric g_ij, Christoffel Gamma, Riemann R, Einstein G_munu",
         assumptions="a smooth embedding x(i) of graph nodes into continuous coordinates already exists, prior to differentiating d(i,j) w.r.t. x",
         dependencies="MEC-0 spectral cascade", claimed_result="spacetime metric and curvature emerge purely from graph spectral distance",
         current_status="MATHEMATICALLY ILL-POSED AS WRITTEN", canonical_match="METRIC-CANDIDATE (Test2 pipeline, CONDITIONAL -- exactly for this reason)",
         external_match="diffusion-map / Laplacian-eigenmap literature (Coifman-Lafon 2006)", executable="NO",
         verification_status="Eq 3.2 differentiates a discrete node-pairwise distance d(i,j) with respect to continuous coordinates x^i that are never defined -- this presupposes the very embedding this project's own Test2 pipeline found to be non-unique (METRIC-CANDIDATE, CONDITIONAL). The document does not acknowledge or resolve this; it is stated as a completed step.",
         falsification_status="the specific written equation is not well-formed (undefined x^i), which this campaign treats as a failed reconstruction attempt, not a proof of falsity of the general idea",
         promotion_candidate="NO"),
    dict(source_id="MEC-5", filename="Master Equation Codex.pdf", source_class="B (grandiose-synthesis)",
         branch="Gauge/Standard Model", section="5", equation_identifier="5.3",
         equation_text="G = Aut(O) x Spin(8) superset SU(3)_C x SU(2)_L x U(1)_Y",
         variables="octonion automorphism group Aut(O), Spin(8), gauge group G",
         assumptions="'the automorphism structure of the eigenspace's Clifford-octonionic scaffolding' selects this specific group -- no construction of that scaffolding from MEC-0/1's actual graph/Laplacian objects is shown",
         dependencies="MEC-0/1 spectral cascade (claimed, not constructed)", claimed_result="Standard Model gauge group emergent from spectral eigenspace automorphisms",
         current_status="BARE ASSERTION, NO DERIVATION FOUND", canonical_match="T2-HISTORICAL (PROPOSED, already registered in compiler/historical/register.py with identical finding)",
         external_match="octonion/Spin(8) route to the Standard Model is a real research direction in the literature (e.g. Furey, Dixon) but this document does not reproduce or cite that literature's actual construction", executable="NO",
         verification_status="Corpus-wide search (this project's own compiler/historical/register.py, independently re-confirmed by grep this campaign) found no executable derivation, proof object, or numerical artifact anywhere in the repository backing this claim. This is a restatement of the DTC COMPILER.docx section 4 claim already registered as T2-HISTORICAL.",
         falsification_status="not falsified (never derived to a testable form)",
         promotion_candidate="NO"),
    dict(source_id="MEC-6", filename="Master Equation Codex.pdf", source_class="B (grandiose-synthesis)",
         branch="Quantum", section="6", equation_identifier="6.1-6.4",
         equation_text="i hbar dPsi/dt = H Psi (asserted continuum limit of L psi_n=lambda_n psi_n)",
         variables="Schrodinger wavefunction Psi, Hamiltonian H", assumptions="the discrete graph eigenproblem has a well-defined continuum limit reproducing the Schrodinger equation",
         dependencies="MEC-0/1", claimed_result="quantum mechanics is the continuum limit of the graph spectral problem",
         current_status="ASSERTED, CONTRADICTED BY THIS PROJECT'S OWN FC-005 RESULT", canonical_match="CONTINUUM-LIMIT-L-DESI (FAIL/RETRIABLE, frozen)",
         external_match="n/a", executable="NO (as a general claim)",
         verification_status="This project's own rigorously executed FC-005 investigation (real DESI data, sparse N-scaling to N=64,000) found genuine discrete-to-continuum convergence for only the lowest ~4 of 15 tested modes even in the best case, and explicit non-convergence for the rest -- the opposite of a general, clean continuum limit. The document's one-line assertion 'Eq 6.2 is the continuum limit of Eq 1.2' does not hold as a general, unconditional statement given this project's own empirical finding.",
         falsification_status="CONTRADICTED by this project's own FC-005 execution for the general/unconditional form of the claim",
         promotion_candidate="NO"),
    dict(source_id="MEC-7", filename="Master Equation Codex.pdf", source_class="B (grandiose-synthesis)",
         branch="Thermodynamic", section="7", equation_identifier="7.1-7.4",
         equation_text="R=e^{-beta L} <-> Boltzmann weight e^{-beta E}", variables="recursion parameter beta, energy E",
         assumptions="the graph heat-kernel parameter beta is physically identifiable with inverse temperature",
         dependencies="MEC-0/1/2", claimed_result="thermodynamics is the macroscopic face of spectral diffusion dynamics",
         current_status="LOOSE ANALOGY, NOT DERIVED", canonical_match="THERMODYNAMICS-NODE (OPEN)",
         external_match="heat-kernel/partition-function analogy is standard in spectral graph theory but the physical-temperature identification is not derived here", executable="NO",
         verification_status="The document itself uses the word 'mirrors' rather than 'derives' for this correspondence -- an honest hedge the campaign preserves; no equation connects the graph's own beta to any independently measurable physical temperature.",
         falsification_status="not falsified (not asserted strongly enough to test)", promotion_candidate="NO"),

    # --- DTC_Formal_Structure.docx (deep read, full) ---
    dict(source_id="DTC-FS-1", filename="DTC_Formal_Structure.docx", source_class="B-rigorous (self-critical, checkable)",
         branch="Symmetry", section="II", equation_identifier="Constraint Necessity Theorem",
         equation_text="A freely generated category D (every morphism, including identifying/collapsing ones, admissible) has no non-trivial invariant distinguishing any two objects",
         variables="category D, subcategory C, objects A,B", assumptions="D contains at least 2 non-isomorphic objects; 'freely generated' means literally every conceivable morphism (including collapsing ones) is admissible",
         dependencies="none (self-contained category-theory result)", claimed_result="persistent distinguishable structure requires non-trivial constraint",
         current_status="PROVED (genuine, checkable, narrow theorem)", canonical_match="none in current MDCL",
         external_match="essentially a restatement of the definition of a freely-generated category having no non-trivial functorial invariants -- a correct, if modest, category-theory fact", executable="not applicable (pure abstract-algebra statement)",
         verification_status="Independently re-derived by inspection this campaign: the proof is a direct, valid consequence of the definitions given (a category with every morphism, including arbitrary identifications, available has by construction no property preserved by all morphisms). This is the single cleanest genuinely-proved result located anywhere in the historical corpus.",
         falsification_status="SURVIVES -- correct as stated, though narrower than the document's own predecessor (Document 3) had informally claimed, which the document itself flags",
         promotion_candidate="CANDIDATE for registration as an external-mathematics reference (category theory), not as UOC-original physics"),
    dict(source_id="DTC-FS-2", filename="DTC_Formal_Structure.docx", source_class="B-rigorous (self-critical, checkable)",
         branch="Symmetry/Conservation", section="III", equation_identifier="Generalized Noether Conjecture (GNC)",
         equation_text="conjectured: for any (D,T,C) system, a retained quantity R exists as a consequence of C alone",
         variables="constraint subcategory C, retained quantity R", assumptions="would require C to carry continuous/variational structure analogous to a Lagrangian symmetry group, which is not guaranteed for an arbitrary C",
         dependencies="DTC-FS-1", claimed_result="ordinary Noether's theorem is recovered EXACTLY as the special case where C carries a continuous Lie symmetry and a variational structure; the general conjecture (C->R for ANY constraint structure) is explicitly NOT proved",
         current_status="OPEN (explicitly, honestly, by the document's own author)", canonical_match="NOETHER-SYMMETRY / CONSERVATION-LAW (not registered)",
         external_match="Noether's theorem itself is, of course, established physics/mathematics -- correctly and exactly recovered, with no distortion, per the document's own careful statement", executable="not applicable",
         verification_status="Independently confirmed this campaign: the document correctly identifies that Noether's proof requires a continuous Lie symmetry and a variational (Lagrangian) structure, neither of which a generic constraint subcategory C is guaranteed to carry -- so the promised generalization beyond ordinary physics does not go through, and the document says so explicitly rather than papering over it.",
         falsification_status="the GENERAL conjecture remains an open, unproved conjecture (honestly labeled as such); the CONSERVATIVE special case is simply ordinary Noether's theorem, not new content",
         promotion_candidate="NO new promotion (Noether's theorem is already established external physics; the generalization attempt did not succeed)"),
    dict(source_id="DTC-FS-3", filename="DTC_Formal_Structure.docx", source_class="B-rigorous (self-critical, checkable)",
         branch="Primitive", section="IV", equation_identifier="Option A / Option B (self-reference)",
         equation_text="n/a (no equation; a question about whether investigator and investigated share necessary categorical structure)",
         variables="n/a", assumptions="would require an independently-specified (D,T,C) decomposition of cognition itself, not smuggled in from the conclusion it would support",
         dependencies="DTC-FS-1/2", claimed_result="whether the framework's applicability to physics and to inquiry itself is a necessary identity or a contingent coincidence",
         current_status="EXPLICITLY UNRESOLVED, EXPLICITLY FLAGGED AS CIRCULAR IF ATTEMPTED NAIVELY", canonical_match="SELECTION-SIGMA (OPEN -- structurally the same 'cannot independently pin down the selector' obstruction)",
         external_match="n/a (self-referential/philosophy-of-mind question, not a physics claim)", executable="not applicable",
         verification_status="The document's own diagnosis -- 'a derivation from C to R cannot be carried out, even in principle, if C has not been pinned down independently of the R it is meant to produce' -- is the exact quote already registered in this project's canonical registry as DTC-CIRCULARITY-OBSTRUCTION (CONDITIONAL status), independently re-confirmed verbatim this campaign.",
         falsification_status="not applicable (an acknowledged open problem, not a tested claim)", promotion_candidate="NO"),

    # --- DTC-RP-004_Forced_vs_Free.docx (deep read, full) ---
    dict(source_id="DTC-RP4-1", filename="DTC-RP-004_Forced_vs_Free.docx", source_class="B-rigorous (self-falsification test)",
         branch="Quantum/Gravity", section="2-4", equation_identifier="Tr(Y^4)/Tr(Y^2)^2 forcing-test",
         equation_text="Tr(Y^4)/Tr(Y^2)^2 = (m_t^4+m_b^4+m_tau^4)/(m_t^2+m_b^2+m_tau^2)^2, evaluated = 0.9986 (measured masses) / 1 (top-dominance limit); tested against the grammar's own candidate coefficient gamma in dPhi/dt=alphaJ-betaPhi-gammaPhi^3+D Phi nabla^2 Phi",
         variables="Yukawa trace ratio, fermion masses m_t/m_b/m_tau, grammar coefficient gamma",
         assumptions="standard relation y^f=sqrt(2)m^f/v between Yukawa couplings and fermion masses (real, established)",
         dependencies="external: Chamseddine-Connes-Marcolli 2007/2012 spectral Standard Model (real, published physics)",
         claimed_result="tests whether the author's own (D,T,C)-grammar coefficient gamma is 'forced' (determined by the same spectral data that fixes the real Higgs quartic coupling lambda_H) or merely decorative/free",
         current_status="NEGATIVE RESULT, HONESTLY REPORTED BY THE DOCUMENT'S OWN AUTHOR", canonical_match="none (self-test of a prior document in this same corpus, 'Executive Summary')",
         external_match="the historical Chamseddine-Connes-Marcolli 2007 Higgs-mass prediction (~170 GeV), its 2012 falsification by the 125 GeV LHC discovery, and the same-year published correction (JHEP 2012, 'Resilience of the Spectral Standard Model') are real, verifiable physics history, correctly and accurately stated",
         executable="the Tr(Y^4)/Tr(Y^2)^2 computation is executable (document states it was run in SymPy; not independently re-executed by this campaign, but the arithmetic is standard and plausible)",
         verification_status="This campaign independently confirms the historical claim (Chamseddine-Connes-Marcolli's 2007 prediction and 2012 correction are real, documented physics history) and confirms the logical structure of the test is sound: a forced parameter changes the prediction when the input data changes; a free parameter does not. The document's own conclusion -- that the grammar's gamma is NOT forced, because the paper's own headline cube-root scaling prediction Phi*~J^(1/3) is independent of gamma's value -- is a correctly reasoned, self-critical negative finding.",
         falsification_status="the tested correspondence (grammar coefficient gamma <-> NCG Higgs quartic term) is FALSIFIED by the document's own test, honestly reported as such",
         promotion_candidate="NO (this is itself a negative result -- nothing to promote, and the document correctly does not claim otherwise)"),

    # --- DTC COMPILER.docx (deep read of section 5, the numerology) ---
    dict(source_id="DTC-C-5.1", filename="DTC COMPILER.docx", source_class="B (grandiose-synthesis, contains a falsified numerical claim)",
         branch="Constants", section="5.1", equation_identifier="alpha = Vol(S^1)/Vol(CP^2)",
         equation_text="alpha = 2 pi / (pi^2/2) = 4/pi [then, asserted without derivation:] alpha^-1 ~ 137.035999",
         variables="fine-structure constant alpha, S^1 and CP^2 topological volumes",
         assumptions="an unstated 'localized normalization scale of the running coupling constant at low energy bounds' bridges 4/pi to 137.035999",
         dependencies="none shown", claimed_result="the fine-structure constant is an exact geometric ratio, eliminating this as a free parameter of physics",
         current_status="ARITHMETICALLY FALSE AS WRITTEN", canonical_match="none", external_match="the true CODATA value alpha^-1 = 137.035999... is real and correctly quoted; the geometric volumes Vol(S^1)=2pi and Vol(CP^2)=pi^2/2 are correct standard results",
         executable="the stated formula is directly checkable: 4/pi ~= 1.2732", verification_status="Directly recomputed this campaign: 2*pi/(pi^2/2) = 4/pi ~ 1.2732, NOT 137.035999 and not its reciprocal (pi/4 ~ 0.7854) either. No algebraic step is shown connecting the computed geometric ratio (4/pi) to the asserted 'exact measured inverse value' (137.035999) -- the two numbers are simply stated adjacent to each other with a vague appeal to 'normalization,' with no formula. This is the same 'state the desired known answer next to an unconnected calculation and call it derived' pattern already identified and rejected in the unrelated Hashimoto 'Theory of Everything' document during the prior L0 literature-ingestion phase of this project.",
         falsification_status="FALSIFIED as a derivation -- the claimed equality does not follow from the shown mathematics",
         promotion_candidate="NO, and flagged as a corpus reliability warning for this document"),
    dict(source_id="DTC-C-5.2", filename="DTC COMPILER.docx", source_class="B (grandiose-synthesis, contains a falsified numerical claim)",
         branch="Constants", section="5.2", equation_identifier="lambda_1 = m_e/M_Planck",
         equation_text="lambda_1 = m_e/M_Planck = 4.18575e-23 [claimed to come from] 'evaluating the constrained boundary condition of the hypergraph's stable topological twists'",
         variables="electron mass m_e, Planck mass M_Planck, eigenvalue lambda_1",
         assumptions="none of the claimed 'hypergraph topological twist' structure is defined anywhere in the shown text",
         dependencies="none shown", claimed_result="the electron mass is a first-principles eigenvalue of a structural Laplace-Beltrami operator",
         current_status="CONSISTENT WITH REVERSE-COMPUTATION FROM THE ALREADY-KNOWN ANSWER", canonical_match="none",
         external_match="the measured m_e (9.10938e-31 kg) and CODATA M_Planck (2.17643e-8 kg) values quoted are both real and correct",
         executable="directly checkable: 4.18575e-23 * 2.17643e-8 = 9.1102e-31, matching the stated m_e to 4 significant figures",
         verification_status="Directly recomputed this campaign: 4.18575e-23 * 2.17643e-8 kg = 9.110e-31 kg, matching the quoted electron mass to the precision shown. This is exactly consistent with lambda_1 having been computed AS m_e/M_Planck using the two already-known measured constants, then re-presented as an independently-derived 'eigenvalue from hypergraph topological twists' -- no actual operator, boundary condition, or eigenvalue computation is shown anywhere in the source text to justify the stated number by any route other than the direct division.",
         falsification_status="FALSIFIED as an independent derivation -- indistinguishable from and consistent with simple reverse-computation from the measured answer",
         promotion_candidate="NO, and flagged as a corpus reliability warning for this document"),

    # --- SEIT_v2.pdf / SEIT Unified Derivation(.v2).pdf (byte-identical text; deep-read abstract + sections V-VI) ---
    dict(source_id="SEIT-V2-5", filename="SEIT v2.pdf (identical text: SEIT Unified Derivation.pdf, SEIT Unified Derivation v2.pdf)",
         source_class="B (grandiose-synthesis, but with a genuinely falsifiable prediction set)",
         branch="Gauge/Standard Model", section="V", equation_identifier="G_SM = SU(3)xSU(2)xU(1) [derived, not postulated]",
         equation_text="anomaly-cancellation constraint N_c-3=0 => N_c=3; minimal-generator-count selection among {SM(12 gen.), SU(5)(24 gen.), SO(10)(45 gen.)}",
         variables="color number N_c, candidate GUT groups and their generator counts",
         assumptions="the candidate list {SM, SU(5), SO(10)} is presupposed rather than derived; 'the spectral filter axioms and the vacuum photon-bath boundary condition' are asserted to select among them without the selection mechanism being shown in the excerpted text",
         dependencies="SEIT's own earlier spectral-cascade sections (same pattern as Master Equation Codex sections 0-2)",
         claimed_result="the Standard Model gauge group is the unique anomaly-free, minimal-generator-count fixed point",
         current_status="PARTIALLY SUBSTANTIVE BUT INCOMPLETE AS SHOWN -- selects among a curated list rather than deriving the list itself",
         canonical_match="T2-HISTORICAL / T2-FORWARD-DERIVATION (both PROPOSED/OPEN)",
         external_match="anomaly cancellation and minimal-group arguments for GUT model selection are a real, established technique in beyond-Standard-Model physics (used, e.g., to compare SU(5)/SO(10)/etc. candidates) -- the TECHNIQUE is legitimate; the specific claim that it uniquely forces exactly the observed SM without further input was not independently verified this campaign",
         executable="NO (not implemented in this project's compiler)",
         verification_status="More substantive than the bare DTC COMPILER/Master Equation Codex assertion (MEC-5.3, DTC-C section 4) in that it names a real selection mechanism (anomaly cancellation + minimal generator count) rather than simply asserting the result -- but the campaign did not verify, within the time available, that the candidate list and the 'spectral filter axioms' invoked are themselves derived (rather than curated) from the document's own earlier primitives. Not independently reconstructed this campaign.",
         falsification_status="not falsified (not fully checked); also not verified", promotion_candidate="NO (insufficiently derived from primitives, per this campaign's inspection; genuinely established SU(3)xSU(2)xU(1) itself is preserved as EXTERNAL established physics per this campaign's governing instruction, not as a result of this document)"),
    dict(source_id="SEIT-V2-6", filename="SEIT v2.pdf (identical text: SEIT Unified Derivation.pdf, SEIT Unified Derivation v2.pdf)",
         source_class="B (grandiose-synthesis, but with a genuinely falsifiable prediction set)",
         branch="Cosmology/Quantum", section="VI", equation_identifier="m_aP = Lambda_QCD^2/(N_sub*M_Pl); GW at 166.48 Hz; soliton core R_c=120-150 pc",
         equation_text="N_sub=4.7619 (from CMB spectral index constraint, n_s=0.965); m_aP=(0.200 GeV)^2/(4.7619*1.22e19 GeV)~=6.885e-13 eV",
         variables="sub-network count N_sub, QCD scale Lambda_QCD, Planck mass M_Pl, axion mass m_aP, GW frequency, soliton core radius R_c",
         assumptions="N_sub is claimed to be fixed by the measured CMB scalar spectral index n_s=0.965 via an unshown formula (not located in the excerpted text this campaign read)",
         dependencies="real measured cosmological/particle inputs: Lambda_QCD~0.2 GeV, M_Pl~1.22e19 GeV, n_s=0.965 (all standard, correctly quoted values)",
         claimed_result="three specific, novel, not-yet-observed falsifiable predictions: an ultralight axion mass, a monochromatic gravitational-wave background frequency, and a dwarf-spheroidal dark-matter soliton core radius range",
         current_status="STRUCTURALLY LEGITIMATE PREDICTION FORMAT, N_sub<-n_s STEP NOT VERIFIED, PREDICTIONS NOT CHECKED AGAINST CURRENT OBSERVATIONAL DATA THIS CAMPAIGN",
         canonical_match="none", external_match="the functional FORM m_a~Lambda_QCD^2/f_a is the real, standard QCD-axion mass relation (f_a a Peccei-Quinn decay constant); using N_sub*M_Pl in place of f_a is this document's own novel substitution",
         executable="the arithmetic chain from N_sub=4.7619 to m_aP=6.885e-13 eV is directly checkable and DOES check out: (0.2)^2/(4.7619*1.22e19)=6.885e-22 GeV=6.885e-13 eV, confirmed by this campaign's own recomputation",
         verification_status="Unlike DTC-C-5.1/5.2, this is NOT a bare non-sequitur -- a real formula (the standard QCD axion mass relation) is used correctly, and the stated arithmetic from N_sub to the final mass is internally consistent and independently reconfirmed by this campaign. What was NOT verified this campaign: (a) the specific claimed relation between N_sub=4.7619 and the measured CMB spectral index n_s=0.965 (the connecting formula was not located in the read excerpt), so whether N_sub is itself independently derived or reverse-fit to produce a desired final number could not be confirmed either way; (b) whether the three predicted values (axion mass, 166.48 Hz GW background, 120-150 pc soliton cores) are already excluded by existing axion-search, LIGO/Virgo stochastic-background, or dwarf-spheroidal-kinematics constraints -- this requires an external-literature/observational-data check not performed this campaign.",
         falsification_status="UNTESTED THIS CAMPAIGN -- flagged as the single most promising genuinely-falsifiable claim in the entire corpus, pending (1) verification of the N_sub<-n_s step and (2) a check against current observational exclusion limits",
         promotion_candidate="NO promotion without the above two checks; explicitly flagged in MASTER_TOE_PREDICTIONS.md as the priority follow-up"),

    # --- Functorial Gauge Unification v1.docx (deep read, full, 93 lines) ---
    dict(source_id="FGU-1", filename="Functorial Gauge Unification v1.docx", source_class="B (grandiose-synthesis)",
         branch="Quantum/Gravity", section="I-VI", equation_identifier="T:Category(ER)~=Category(EPR); various restated GR/QFT/LQG/AdS-CFT formulas",
         equation_text="restates the Einstein field equations, the LQG area operator, the Ryu-Takayanagi formula, and the Polyakov string action side-by-side and declares them isomorphic images of one functor T",
         variables="Grothendieck topos E, transport functors T_1/T_2/T_3, adaptive multiplicity M*",
         assumptions="declares string theory, LQG, and AdS/CFT to be 'different coordinate dialects of the same underlying algebraic Topos' without constructing the isomorphisms claimed",
         dependencies="restates, without deriving, standard formulas from four genuinely established but mutually distinct physics frameworks (GR, LQG, string theory, AdS/CFT)",
         claimed_result="'The search for a Theory of Everything is complete'",
         current_status="NO DERIVATION FOUND; STATED FALSIFICATION CRITERIA ARE NOT OPERATIONALLY TESTABLE",
         canonical_match="none", external_match="every individual formula quoted (Einstein field equations, LQG area operator, Ryu-Takayanagi, Polyakov action) is correctly stated, established physics -- the claimed ISOMORPHISM BETWEEN them is not established anywhere in the document",
         executable="NO", verification_status="Read in full this campaign (93 lines). No construction of the claimed functorial isomorphisms is given anywhere -- each 'unification' consists of stating a known formula from one framework next to a known formula from another and asserting they are 'the exact mathematical invariants' of one operator, with no map, no proof, and no intermediate calculation. The three 'Rigid Falsification Protocols' given (e.g. 'the calculated adaptive multiplicity vector is zero and the system survives') are not stated in a form that names a measurable quantity or a real experiment, so the document's own claim to be 'falsifiable' does not hold up on inspection.",
         falsification_status="the document's central claim ('the search for a TOE is complete') is not supported by any shown derivation, and is inconsistent with the actual, well-documented open status of quantum-gravity unification in mainstream physics",
         promotion_candidate="NO"),

    # --- geometric unification paper.docx (partial read, first 60 lines) ---
    dict(source_id="GUP-1", filename="geometric unification paper.docx", source_class="B (grandiose-synthesis)",
         branch="Variational", section="1-2", equation_identifier="Universal Persistence Field Equation (via delta C_Pi=0)",
         equation_text="not fully captured in the excerpt read this campaign (equation set formatting was not preserved in plain-text extraction for this specific block)",
         variables="Recursive Distinction Omega, informational cost functional C_Pi, Fisher Information Transport Cost I_F",
         assumptions="claims a single variational principle unifies GR geodesics, diffusion, the replicator equation, and the free-energy principle as 'exact invariant submanifolds'",
         dependencies="none shown in the excerpt read", claimed_result="a parameter-free unification of gravitation, thermodynamics, evolutionary biology, and cognition",
         current_status="NOT FULLY READ THIS CAMPAIGN (first 60 of ~169 lines only)", canonical_match="VARIATIONAL-NODE (OPEN)",
         external_match="not assessed", executable="NO",
         verification_status="Only the abstract and section 1 opening were read this campaign; the claimed field-equation derivation (section 2.3 onward) was not inspected. Classified by strong structural similarity to Functorial Gauge Unification v1.docx and Master Equation Codex (same 'Recursive Distinction/Omega' primitive vocabulary, same sweeping cross-domain unification claim in the abstract) but this classification is a pattern-match, not a verified finding for this specific document's remaining content.",
         falsification_status="NOT ASSESSED THIS CAMPAIGN", promotion_candidate="NO (insufficient inspection to consider; flagged for a future deeper pass)"),

    # --- DTC_Rosetta_Stone_TOE_v2.docx (grep-context read of its own open-problems section) ---
    dict(source_id="DTC-RS2-10", filename="DTC_Rosetta_Stone_TOE_v2.docx", source_class="B-rigorous (self-critical, honest open-problems section)",
         branch="Constants", section="10 (Open Problems)", equation_identifier="n/a (prose)",
         equation_text="n/a", variables="n/a",
         assumptions="n/a", dependencies="this document's own section 5 (gauge-group derivation)",
         claimed_result="explicit self-admission: 'Section 5 derives the gauge group structure of the Standard Model. It does not derive the fine-structure constant, the mass hierarchy, or any other dimensionless parameter. Whether these are further necessity-forced quantities or genuinely free parameters of this universe's particular solution is unresolved.'",
         current_status="HONEST, EXPLICIT NEGATIVE FINDING BY THE CORPUS'S OWN AUTHOR", canonical_match="none",
         external_match="n/a", executable="not applicable",
         verification_status="This is a directly relevant, important internal-corpus finding: this document (part of the same DTC/Rosetta Stone research program as DTC COMPILER.docx) explicitly states the fine-structure constant is NOT derived and remains unresolved -- directly contradicting DTC COMPILER.docx's later claim (DTC-C-5.1) of an 'exact analytical derivation' of the same constant. This internal corpus contradiction corroborates this campaign's own independent arithmetic finding that the DTC COMPILER.docx claim does not hold up.",
         falsification_status="n/a (this row records a corroborating admission, not a tested claim)", promotion_candidate="NO"),

    # --- NCG spectral action PDFs (identified, not deep-read; already characterized by prior audit) ---
    dict(source_id="NCG-1", filename="Noncommutative Geometry and the Spectral Action_ Toward a Unified TOE.pdf; ...Toward a Unified Theory.pdf",
         source_class="C (external literature summary/review, not original derivation)", branch="Geometry/Gauge/Spectral",
         section="whole document (not deep-read this campaign; TOC/summary-level only)", equation_identifier="Chamseddine-Connes spectral action principle",
         equation_text="Tr f(D/Lambda) [standard form of the real spectral action]",
         variables="Dirac operator D, spectral triple (A,H,D), cutoff function f, scale Lambda",
         assumptions="genuine external published mathematics (Chamseddine-Connes, and Chamseddine-Connes-Marcolli for the finite Standard Model algebra)",
         dependencies="none (external reference)", claimed_result="quoted claim (already registered verbatim in compiler/historical/register.py): 'when applied to an almost-commutative space..., the Spectral Action Principle yields exactly the Standard Model coupled to gravity'",
         current_status="ALREADY REGISTERED AS NCG-BRIDGE-EXTERNAL-REFERENCE (PROPOSED, role=comparison)", canonical_match="NCG-BRIDGE-EXTERNAL-REFERENCE",
         external_match="the Chamseddine-Connes spectral action IS real, published, peer-reviewed physics (Comm. Math. Phys. 1997 and subsequent Standard Model papers) -- this project's own register.py document correctly identifies these two PDFs as literature-summary documents ABOUT that real result, not a SEIT-original derivation",
         executable="NO (no spectral-triple/Dirac-operator construction exists anywhere in this project's own compiler)",
         verification_status="Not independently re-read at equation level this campaign beyond confirming the title/framing matches the already-registered characterization; DTC-RP-004 (row DTC-RP4-1 above) provides independent, deeper, campaign-original engagement with this same real physics (via its Higgs-mass forcing test), and reaches a negative result for the SPECIFIC correspondence it tested.",
         falsification_status="not applicable to the external result itself (real, published, peer-reviewed physics); the SEIT-side correspondence to it, where tested (DTC-RP4-1), was found not forced",
         promotion_candidate="NO SEIT-original promotion; the underlying external NCG spectral action remains a legitimate candidate EXTERNAL structure worth a dedicated future implementation attempt, exactly as string theory was treated in the prior L0-ST literature phase"),
]

REMAINING_DOCS = [
    ("Beyond the Theory of Everything.pdf", "B (not deep-read; largest remaining document, 7223 lines extracted)"),
    ("Consciousness_and_the_Universe__Quantum_Ph_-_Roger_Penrose.pdf", "C (genuine external Penrose book; consciousness/quantum-mind topic, tangential to core physics derivation; not read this campaign)"),
    ("Constraint Core Brief.pdf", "B (referenced by DTC_Formal_Structure.docx as 'Scientific Brief 001'; not deep-read this campaign)"),
    ("Executive Summary.pdf", "B (the document DTC-RP-004 tests and finds non-forced; not independently deep-read this campaign beyond DTC-RP-004's own quotes from it)"),
    ("Spectral Codex Volume I Genesis.pdf", "B (not deep-read; TOC/title suggests overlap with Master Equation Codex sections 0-2)"),
    ("Spectral Codex Volume II Gravity.pdf", "B (not deep-read; TOC/title suggests overlap with Master Equation Codex section 3-4)"),
    ("Spectral Codex Volumes.docx", "B (largest single file in the corpus, 359KB extracted text; not deep-read this campaign)"),
    ("Spectral Emergence Framework v2.pdf", "B (not deep-read this campaign)"),
    ("Spectral Emergence Information Theory.pdf", "B (not deep-read this campaign)"),
    ("Spectral_Emergence_Framework_Specification.docx", "B (not deep-read this campaign)"),
    ("Spectral Equations Random.docx", "B (filename itself signals a scratch/dump document; not deep-read this campaign)"),
    ("Unified Spectral Codex.pdf", "B (not deep-read this campaign)"),
    ("Theory of Everything Equation Set.docx", "B (not deep-read this campaign; largest raw equation-dump document by size, 903KB)"),
    ("Unified Field Theory.docx", "B (not deep-read this campaign)"),
    ("MasterRosettaStone TOE Paper.pdf", "B (not deep-read this campaign)"),
    ("Unified_Rosetta_Stone_TOE_v3.docx", "B (not deep-read this campaign)"),
    ("Universal_Rosetta_Ch1_Remainder.docx", "B (not deep-read this campaign)"),
    ("JOI Reformatted.docx", "B (not deep-read this campaign; title pattern resembles the already-rejected Hashimoto 'Journal of Innovations' pseudoscience document from the prior L0 phase -- flagged for cautious handling in any future pass, not confirmed either way)"),
    ("DTC Logic of Inquiry.docx", "B-rigorous (referenced extensively and accurately by DTC_Formal_Structure.docx, which this campaign confirms is careful/self-critical; not independently deep-read itself this campaign)"),
    ("DTC Metaphysics of Structure.docx", "B-rigorous (same as above; philosophical/metaphysical register per DTC_Formal_Structure.docx's own description, not a source of physics equations)"),
]


def build_index_rows():
    rows = list(ROWS)
    for filename, note in REMAINING_DOCS:
        rows.append(dict(
            source_id=f"UNREAD-{filename[:20]}", filename=filename, source_class=note,
            branch="unassessed", section="not read this campaign", equation_identifier="n/a",
            equation_text="n/a", variables="n/a", assumptions="n/a", dependencies="n/a",
            claimed_result="not assessed", current_status="NOT DEEPLY READ THIS CAMPAIGN",
            canonical_match="n/a", external_match="n/a", executable="n/a",
            verification_status="File was full-text-extracted (pdftotext/python-docx) and its title/abstract/structure was scanned for red-flag numerology patterns (grep sweep found no additional 'exact value' claims in this file matching the DTC COMPILER.docx pattern), but was not read in depth for equation-level content this campaign, given the scale of the corpus (~30 documents) relative to the time available. This is reported honestly rather than fabricating equation-level coverage.",
            falsification_status="not assessed", promotion_candidate="NO (insufficient inspection)",
        ))
    return rows


def write_csv(path: Path, rows: list[dict]):
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def build_dependency_graph():
    """Extends the existing DEPENDENCY_CLOSURE_AUDIT.csv graph with historical-corpus
    comparison nodes assessed this campaign. All new nodes are role=comparison,
    never wired as upstream dependencies of the canonical forward chain."""
    import csv as csvmod
    existing = list(csvmod.DictReader((ROOT / "DEPENDENCY_CLOSURE_AUDIT.csv").open()))
    nodes = [dict(id=r["id"], kind=r["kind"], status=r["status"], category=r["category"],
                  source="canonical (object_registry.json / transformation_registry.json)")
             for r in existing]
    historical_nodes = [
        dict(id="MEC-SPECTRAL-CASCADE", kind="HistoricalClaim", status="PARTIALLY_MATCHED_BY_CANONICAL",
             category="comparison", source="Master Equation Codex.pdf sections 0-2, matched by GRAPH-G-SEED..SPECTRUM-L"),
        dict(id="MEC-GEOMETRY-CLAIM", kind="HistoricalClaim", status="ILL_POSED", category="comparison",
             source="Master Equation Codex.pdf section 3 (undefined embedding in eq 3.2)"),
        dict(id="MEC-GAUGE-CLAIM", kind="HistoricalClaim", status="UNSUBSTANTIATED", category="comparison",
             source="Master Equation Codex.pdf section 5.3 = T2-HISTORICAL"),
        dict(id="DTC-FS-CONSTRAINT-THEOREM", kind="HistoricalTheorem", status="PROVED_EXTERNAL_MATH", category="comparison",
             source="DTC_Formal_Structure.docx section II"),
        dict(id="DTC-FS-GNC", kind="HistoricalConjecture", status="OPEN_HONEST", category="comparison",
             source="DTC_Formal_Structure.docx section III"),
        dict(id="DTC-RP4-FORCING-TEST", kind="HistoricalFalsificationTest", status="NEGATIVE_RESULT", category="comparison",
             source="DTC-RP-004_Forced_vs_Free.docx"),
        dict(id="DTC-C-ALPHA-CLAIM", kind="HistoricalClaim", status="FALSIFIED_NONSEQUITUR", category="comparison",
             source="DTC COMPILER.docx section 5.1"),
        dict(id="DTC-C-ELECTRON-MASS-CLAIM", kind="HistoricalClaim", status="FALSIFIED_REVERSE_FIT", category="comparison",
             source="DTC COMPILER.docx section 5.2"),
        dict(id="SEIT-GAUGE-DERIVATION", kind="HistoricalClaim", status="INCOMPLETE_NOT_VERIFIED", category="comparison",
             source="SEIT v2.pdf section V"),
        dict(id="SEIT-AXION-GW-SOLITON-PREDICTIONS", kind="HistoricalPrediction", status="UNTESTED_STRUCTURALLY_LEGITIMATE",
             category="comparison", source="SEIT v2.pdf section VI"),
        dict(id="FGU-ISOMORPHISM-CLAIM", kind="HistoricalClaim", status="UNSUBSTANTIATED_UNFALSIFIABLE", category="comparison",
             source="Functorial Gauge Unification v1.docx"),
        dict(id="NCG-EXTERNAL-SPECTRAL-ACTION", kind="ExternalLiteratureReference", status="PROPOSED", category="comparison",
             source="already registered as NCG-BRIDGE-EXTERNAL-REFERENCE in canonical registry"),
    ]
    nodes.extend(historical_nodes)
    return {
        "graph_type": "MASTER_TOE_DEPENDENCY_GRAPH",
        "generated_at": TIMESTAMP,
        "git_commit": COMMIT,
        "note": (
            "Extends the existing, canonical DEPENDENCY_CLOSURE_AUDIT.csv graph (66 nodes, "
            "unmodified, all copied in verbatim below) with 12 new HISTORICAL/COMPARISON-role "
            "nodes assessed during the Master TOE Derivation Campaign's corpus-mining pass. "
            "Every historical node's role is 'comparison' -- none is wired as an upstream "
            "dependency of any canonical forward-chain node, per this project's standing "
            "target-independence discipline (compiler/historical/register.py)."
        ),
        "nodes": nodes,
    }


def main():
    rows = build_index_rows()
    write_csv(ROOT / "MASTER_THEORY_CORPUS_INDEX.csv", rows)
    print(f"wrote MASTER_THEORY_CORPUS_INDEX.csv ({len(rows)} rows)")

    graph = build_dependency_graph()
    (ROOT / "MASTER_TOE_DEPENDENCY_GRAPH.json").write_text(json.dumps(graph, indent=2) + "\n")
    print(f"wrote MASTER_TOE_DEPENDENCY_GRAPH.json ({len(graph['nodes'])} nodes)")
    write_csv(ROOT / "MASTER_TOE_DEPENDENCY_GRAPH.csv", graph["nodes"])
    print("wrote MASTER_TOE_DEPENDENCY_GRAPH.csv")


if __name__ == "__main__":
    main()
