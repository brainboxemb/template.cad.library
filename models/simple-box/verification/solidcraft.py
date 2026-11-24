"""Native SolidCraft contract for the standard simple-box implementation."""
from cad_verification import (
    BodyEnvelope,
    SolidCraftModelExpectation,
    SolidCraftTimelineExpectation,
    SolidCraftVerification,
)


VERIFICATION = SolidCraftVerification(
    verification_id="simple-box-native",
    baseline=SolidCraftModelExpectation(
        body_count=1,
        body_envelopes=(
            BodyEnvelope(
                (-20.0, -15.0, 0.0),
                (20.0, 15.0, 10.0),
            ),
        ),
        bounds_tolerance=0.000001,
        timeline=(
            SolidCraftTimelineExpectation(
                feature_type="BoxFeature",
            ),
        ),
    ),
)
