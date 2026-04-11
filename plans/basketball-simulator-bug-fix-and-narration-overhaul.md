
# Basketball Simulator Bug Fix and Narration Overhaul

## Summary

The simulator has a solid architecture -- tick-level FSMs, 18-factor shot probability, dribble combos, PnR mechanics, a layered narration pipeline -- but is broken by a handful of bugs and over-aggressive verbosity suppression. This plan fixes the critical bugs first, then cranks up narration to "radio broadcast" level for the text-only experience.

## Phase 1: Critical Game Engine Bugs

### 1.1 Fix Possession Flip After Made Baskets
**File:** `src/hoops_sim/engine/simulator.py` lines 1395-1573

**Problem:** `_execute_shot()` returns `True` for both made baskets and offensive rebounds. The caller in `_process_ball_handler_tick()` treats both as "possession continues" and never calls `_end_possession_and_flip()`.

**Fix:** Change `_execute_shot()` to return a named result instead of a bool. Use a dataclass or enum: `ShotOutcome.MADE_BASKET`, `ShotOutcome.OFFENSIVE_REBOUND`, `ShotOutcome.DEFENSIVE_REBOUND`. The caller flips possession on `MADE_BASKET` and `DEFENSIVE_REBOUND`, continues on `OFFENSIVE_REBOUND`.

### 1.2 Fix _execute_drive Made/Missed Distinction
**File:** `src/hoops_sim/engine/simulator.py` lines 1575-1700+

**Problem:** Same conflation issue in drive finishing -- made basket should flip possession.

**Fix:** Apply the same `ShotOutcome` pattern to the drive finishing path.

### 1.3 Fix Ball Handler Dominance
**Root cause:** Cascading effect of 1.1. Once possession flips correctly, different teams and different ball handlers get the ball. The weighted selection in `_setup_possession()` already diversifies handlers by playmaking rating.

## Phase 2: Score Display Fix

### 2.1 Use SCORE_UPDATE_TEMPLATES
**File:** `src/hoops_sim/narration/play_by_play.py` line 344

**Problem:** Raw `f"{event.team_name} {event.new_score_home}-{event.new_score_away}."` is ambiguous -- reads like the named team has the first number.

**Fix:** Replace with proper template from `SCORE_UPDATE_TEMPLATES` in `shots.py`. Format as: `"Celtics 48, Knicks 45."` or `"That puts the Celtics up 3."` depending on context. Use `TIE_SCORE_TEMPLATES` when tied.

## Phase 3: Narration Verbosity Overhaul

Since this is a text-only game with no graphics, the narration must describe everything that happens. The current system actively suppresses narration at 7 different throttle points.

### 3.1 Remove Ball Advance Suppression
**File:** `src/hoops_sim/narration/possession_narrator.py` lines 252-260

**Change:** Stop filtering out ball advance events when other setup events exist. The ball advance sets the scene ("Murray brings it up, surveys the defense") and should always be narrated.

### 3.2 Lower Importance Threshold
**File:** `src/hoops_sim/narration/possession_narrator.py` line 249

**Change:** Lower threshold from 0.3 to 0.15. This ensures ball advance (0.3) and other low-importance events get through. In text-only mode, nothing should be silently dropped.

### 3.3 Soften Pacing Rhythm Suppression
**File:** `src/hoops_sim/narration/pacing.py` lines 204-206

**Change:** Remove or weaken the "forced breather" after 3 high-verbosity possessions. For a text-only game, dead-spot possessions feel like content is missing, not pacing. Change the multiplier from 0.6 to 0.85.

### 3.4 Increase Color Commentary Frequency
**File:** `src/hoops_sim/narration/color_commentary.py` lines 107-109

**Changes:**
- Lower cooldown from 3 to 1 possession
- Increase interjection probability from 0.5 to 0.7
- Add early-game triggers: general observations, matchup comments, PnR coverage analysis
- Use the existing `TENDENCY_TEMPLATES`, `PNR_COVERAGE_ANALYSIS`, `DEFENSIVE_SCHEME_TEMPLATES`, and `MISMATCH_TEMPLATES` in `color.py` -- they exist but are never referenced

### 3.5 Join Setup + Terminal Into Flowing Prose
**File:** `src/hoops_sim/narration/possession_narrator.py` lines 196-229

**Problem:** Setup prose and terminal shot narration are added as separate `pbp_lines`, producing separate broadcast lines. A real broadcast flows: "Murray hesi... crossover... pulls up from 18 -- BANG!"

**Fix:** When the chain composer produces setup text and the terminal event is a shot/finish, join them with " -- " or "... " into a single line before adding to `pbp_lines`.

### 3.6 Add Off-Ball and Defensive Action Narration
**File:** `src/hoops_sim/narration/play_by_play.py`

**Problem:** `OFF_BALL_ACTION` and `DEFENSIVE_ACTION` have no handlers in the `_HANDLERS` dispatch table. These events pass through the importance filter but produce empty output.

**Fix:** Add handlers and templates for:
- Off-ball: cuts, spot-ups, relocations, off-ball screens
- Defense: closeouts, help rotations, switches, denials
- Examples: "Johnson curls off the pin-down to the corner", "Williams rotates from the weak side"

### 3.7 Populate Spatial Context
**File:** `src/hoops_sim/engine/simulator.py` (event emission points)

**Problem:** Events have `court_location`, `drive_direction`, `distance_description` fields but they are never populated. Templates use `{zone}` and `{distance}` but get generic values.

**Fix:** When emitting events, populate spatial fields from the court zone system. Map zone enums to readable locations: "left wing", "top of the key", "right corner", "paint". Set drive direction based on the vector from handler position to basket.

### 3.8 Add Crowd/Arena Atmosphere
**File:** New templates + simulator emission

**Problem:** `CROWD_REACTION` event type exists in the enum but is never emitted or handled. Zero atmosphere.

**Fix:** Emit crowd reaction events after big plays (dunks, threes in clutch, scoring runs, blocks). Add templates: "The crowd is on their feet!", "The arena goes quiet after that three", "The bench is going wild!"

### 3.9 Vary Chain Composer Connectors
**File:** `src/hoops_sim/narration/chain_composer.py` lines 158-168

**Problem:** Clusters always join with `"... "` between different types and `", {connector} "` within types. Every multi-action possession sounds the same rhythmically.

**Fix:** Randomize between `"... "`, `" -- "`, `", "`, and `". "` based on cluster transition type and verbosity level. High-intensity moments use dashes; routine plays use commas; pauses use ellipses.

## Phase 4: Validation

### 4.1 Run Test Suite
Run `pytest` to identify any tests broken by the changes, especially in `tests/test_engine/test_simulator.py` and `tests/test_narration/`.

### 4.2 Output Quality Check
Simulate a full game and verify:
- Both teams score, possessions alternate correctly
- Score displays clearly (team name + score, not ambiguous format)
- Every possession has narration (no silent possessions)
- Ball advance, dribble moves, screens, passes, drives, shots all narrated
- Color commentary interjects regularly with tactical analysis
- Spatial context appears ("from the left wing", "drives baseline")
- Crowd/atmosphere reactions on big plays
- Varied sentence rhythm (not all ellipses)

## Execution Order

The fixes should be applied in dependency order:
1. Phase 1 first (possession flip) -- this unblocks realistic game flow
2. Phase 2 (score display) -- quick fix, no dependencies
3. Phase 3.1-3.4 (remove throttles) -- immediately increases output volume
4. Phase 3.5-3.9 (enrich narration) -- builds on unthrottled pipeline
5. Phase 4 (validate) -- confirm everything works together
