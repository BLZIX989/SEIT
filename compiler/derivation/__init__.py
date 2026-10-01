"""Universal Mathematical Derivation Environment (see reports/derivation_environment/DERIVATION_ENGINE_SPEC.md).

This package sits BENEATH the existing MDCL/chainlink architecture as an
execution layer -- it does not replace compiler.core.status.Status,
compiler.ir.registry.MDCLRegistries, or compiler.protocol.registry.ChainlinkRegistry,
all of which continue to govern canonical state exactly as before this
package existed. See reports/derivation_environment/DERIVATION_ENGINE_SPEC.md section 0 for the layering
diagram and reports/derivation_environment/DERIVATION_ENGINE_IMPLEMENTATION_PLAN.md for build order.
"""
