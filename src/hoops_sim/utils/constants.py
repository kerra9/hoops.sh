"""All tunable constants for the simulation in one place."""

from __future__ import annotations

# =============================================================================
# Court Dimensions (feet)
# =============================================================================
COURT_LENGTH = 94.0
COURT_WIDTH = 50.0
HALF_COURT_LENGTH = 47.0

# Basket position (center of the rim, measured from the baseline on the left end)
BASKET_X = 5.25  # 5 feet 3 inches from the baseline
BASKET_Y = 25.0  # Center of court width
BASKET_HEIGHT = 10.0  # 10 feet above the floor

# Three-point line distances
THREE_POINT_ARC_DISTANCE = 23.75  # feet from basket center (NBA)
THREE_POINT_CORNER_DISTANCE = 22.0  # feet (shorter in corners)
THREE_POINT_CORNER_CUTOFF_Y = 3.0  # feet from sideline where corner 3 ends

# Free throw line
FREE_THROW_DISTANCE = 15.0  # feet from the basket
FREE_THROW_LANE_WIDTH = 16.0  # feet (NBA)

# Paint / restricted area
PAINT_LENGTH = 19.0  # feet from the baseline
RESTRICTED_AREA_RADIUS = 4.0  # feet from the basket center

# Backboard
BACKBOARD_WIDTH = 6.0  # feet
BACKBOARD_HEIGHT = 3.5  # feet
BACKBOARD_OFFSET = 4.0  # feet from the baseline (front of backboard)

# =============================================================================
# Ball Physics
# =============================================================================
BALL_RADIUS = 0.39  # feet (9.4 inches diameter)
BALL_MASS = 1.375  # lbs
BALL_COEFFICIENT_OF_RESTITUTION = 0.56  # bounce factor off hardwood
BALL_AIR_DRAG = 0.0005  # drag coefficient
BALL_DRIBBLE_BOUNCE_COR = 0.75  # bounce factor during dribble

# Rim
RIM_RADIUS = 0.75  # feet (18 inches diameter / 2)
RIM_HEIGHT = BASKET_HEIGHT  # 10 feet
RIM_COEFFICIENT_OF_RESTITUTION = 0.45  # bounce factor off rim

# =============================================================================
# Gravity & Environment
# =============================================================================
GRAVITY = 32.174  # ft/s^2
SEA_LEVEL_AIR_DENSITY = 0.0765  # lb/ft^3 (standard air density)

# Altitude effects
ALTITUDE_STAMINA_DRAIN_PER_1000FT = 0.006  # 0.6% extra stamina drain per 1000ft
ALTITUDE_BALL_BOUNCE_FACTOR_PER_1000FT = 0.002  # slight bounce increase at altitude

# =============================================================================
# Tick Engine
# =============================================================================
TICK_DURATION = 0.1  # seconds per tick
TICKS_PER_SECOND = 10
SUB_TICK_RESOLUTION = 0.01  # seconds per sub-tick for critical moments

# Game clock
QUARTER_LENGTH_MINUTES = 12
OVERTIME_LENGTH_MINUTES = 5
SHOT_CLOCK_SECONDS = 24
SHOT_CLOCK_OFFENSIVE_REBOUND = 14  # reset to 14 on offensive rebound
HALFTIME_LENGTH_MINUTES = 15

# =============================================================================
# Player Movement (feet/second)
# =============================================================================
# Speed ranges derived from attributes (0-99 scale)
MIN_SPRINT_SPEED = 18.0  # ft/s (slowest player at speed=1)
MAX_SPRINT_SPEED = 28.0  # ft/s (fastest player at speed=99)
BACKPEDAL_SPEED_RATIO = 0.60  # backpedal is ~60% of forward speed
LATERAL_SPEED_RATIO = 0.75  # lateral movement is ~75% of forward speed

# Acceleration
MIN_ACCELERATION = 12.0  # ft/s^2 (slowest acceleration)
MAX_ACCELERATION = 22.0  # ft/s^2 (fastest acceleration)
DECELERATION_MULTIPLIER = 1.3  # deceleration is 1.3x acceleration (braking is faster)

# =============================================================================
# Energy / Fatigue
# =============================================================================
BASE_ENERGY = 100.0
ENERGY_DRAIN_SPRINT = 0.08  # per tick at full sprint
ENERGY_DRAIN_JOG = 0.02  # per tick at jog
ENERGY_DRAIN_WALK = 0.005  # per tick at walk
ENERGY_DRAIN_STAND = 0.001  # per tick standing
ENERGY_RECOVERY_BENCH = 0.15  # per tick on the bench
ENERGY_RECOVERY_TIMEOUT = 2.0  # flat recovery during timeout
ENERGY_RECOVERY_HALFTIME = 25.0  # recovery during halftime

# Fatigue thresholds (energy percentage)
FATIGUE_THRESHOLD_LIGHT = 0.80  # below 80%: slight penalties
FATIGUE_THRESHOLD_MODERATE = 0.60  # below 60%: noticeable penalties
FATIGUE_THRESHOLD_HEAVY = 0.40  # below 40%: significant penalties
FATIGUE_THRESHOLD_EXHAUSTED = 0.20  # below 20%: severe penalties
FATIGUE_THRESHOLD_GASSED = 0.05  # below 5%: extreme penalties

# =============================================================================
# Shot Model
# =============================================================================
# Optimal release angles by distance (degrees from horizontal)
OPTIMAL_RELEASE_ANGLE_AT_RIM = 52.0
OPTIMAL_RELEASE_ANGLE_MID = 48.0
OPTIMAL_RELEASE_ANGLE_THREE = 45.0

# Variance scaling (higher = more miss variance for lower-rated shooters)
SHOT_ANGLE_VARIANCE_SCALE = 0.08  # degrees per (100 - rating) point
SHOT_SPEED_VARIANCE_SCALE = 0.04  # fraction per (100 - rating) point

# Backspin
MIN_BACKSPIN_RPM = 100.0
MAX_BACKSPIN_RPM = 220.0
BACKSPIN_COR_BONUS = 0.3  # how much backspin helps with rim "touch"

# Swish / rim zones (inches from center of rim)
SWISH_THRESHOLD = 2.0  # ball center within 2 inches of rim center = swish
RIM_GRAZE_THRESHOLD = 4.3  # ball fits through with possible rim contact
RIM_HARD_HIT_THRESHOLD = 5.5  # hits front or back rim hard
RIM_MISS_THRESHOLD = 7.0  # misses rim, hits backboard only

# =============================================================================
# Contact
# =============================================================================
CONTACT_INCIDENTAL_THRESHOLD = 0.2
CONTACT_LIGHT_THRESHOLD = 0.4
CONTACT_MODERATE_THRESHOLD = 0.6
CONTACT_HARD_THRESHOLD = 0.8
# Above 0.8 = flagrant level

# =============================================================================
# Court Surface
# =============================================================================
DEFAULT_GRIP_COEFFICIENT = 0.95  # maple hardwood in good condition
WORN_SURFACE_GRIP_PENALTY = 0.05
HUMIDITY_GRIP_THRESHOLD = 60  # humidity above this reduces grip
HUMIDITY_GRIP_PENALTY = 0.05

# =============================================================================
# Rebound
# =============================================================================
OFFENSIVE_REBOUND_BASE_RATE = 0.27  # ~27% league average OREB%
CAROM_SPIN_LATERAL_FACTOR = 0.01  # sidespin lateral shift
CAROM_BACKSPIN_DAMPEN_FACTOR = 400.0  # divisor for backspin distance reduction
CAROM_DISTANCE_BASE = 0.3  # feet per unit of contact angle
CAROM_NOISE_DEGREES = 15.0  # randomness in carom angle
CAROM_NOISE_DISTANCE = 1.5  # randomness in carom distance (feet)
