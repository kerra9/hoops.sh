"""Physics layer: ball physics, kinematics, contact detection, court surface."""

from hoops_sim.physics.ball import Ball, BallState
from hoops_sim.physics.contact import ContactEvent, ContactSeverity, ContactType, detect_contact
from hoops_sim.physics.court_surface import CourtSurface, SurfaceCondition
from hoops_sim.physics.kinematics import MovementType, PlayerKinematics
from hoops_sim.physics.rim_interaction import RimInteractionResult, ShotOutcome, resolve_rim_interaction
from hoops_sim.physics.shot_trajectory import ShotTrajectory, calculate_shot_trajectory
from hoops_sim.physics.vec import Vec2, Vec3, distance_2d

__all__ = [
    "Ball",
    "BallState",
    "ContactEvent",
    "ContactSeverity",
    "ContactType",
    "CourtSurface",
    "MovementType",
    "PlayerKinematics",
    "RimInteractionResult",
    "ShotOutcome",
    "ShotTrajectory",
    "SurfaceCondition",
    "Vec2",
    "Vec3",
    "calculate_shot_trajectory",
    "detect_contact",
    "distance_2d",
    "resolve_rim_interaction",
]
