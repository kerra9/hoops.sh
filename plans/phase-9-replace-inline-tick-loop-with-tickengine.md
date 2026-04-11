
# Phase 9: Replace Inline Tick Loop with TickEngine

## Problem Statement

The simulator's `_simulate_possession()` method contains an inline tick loop (lines 465-500) that manually:
1. Advances the game clock via `_advance_clock(TICK_DURATION)`
2. Checks quarter end via `_check_quarter_end()`
3. Checks shot clock via `gs.clock.shot_clock <= 0.0`
4. Ticks all player FSMs via `_tick_all_players()`
5. Runs ball handler AI decisions
6. Drains energy

Meanwhile, [`TickEngine`](src/hoops_sim/engine/tick.py:58) exists as a standalone class that was designed to be "the heart of the simulation" but is never imported by anything. It handles steps 1-3 (clock, shot clock, quarter end) in a clean `process_tick()` method.

## Gap Analysis: Why TickEngine Can't Be Dropped In Today

The TickEngine's `process_tick()` does:
```python
def process_tick(self) -> TickResult:
    gs.clock.tick(self.dt)         # 1. Advance clock
    gs.possession.tick()           # 2. Advance possession counter
    # 3. Check shot clock violation
    # 4. Check quarter end
    return TickResult(events=...)
```

The simulator's inline loop does:
```python
while not possession_resolved:
    self._advance_clock(TICK_DURATION)   # 1. Advance clock
    if self._check_quarter_end(): ...    # 2. Check quarter end (with complex handling)
    if gs.clock.shot_clock <= 0.0: ...   # 3. Check shot clock
    self._tick_all_players(...)          # 4. Player FSMs + contact detection
    if handler.fsm.can_interrupt: ...    # 5. AI decision
    self._drain_energy_for_ticks(1)      # 6. Energy
```

**Key mismatches:**

| Feature | TickEngine | Simulator Inline |
|---------|-----------|-----------------|
| Clock advance | `gs.clock.tick(dt)` | `gs.clock.tick(seconds)` via `_advance_clock` |
| Shot clock check | `gs.clock.is_shot_clock_violation()` | `gs.clock.shot_clock <= 0.0` |
| Quarter end handling | Sets `PossessionState.END_OF_QUARTER` | Calls `_check_quarter_end()` which does quarter transition, halftime swap, overtime logic, broadcast events, and game-over detection |
| Possession tick | `gs.possession.tick()` | Not called (possession ticks tracked separately) |
| Player FSMs | Not handled | `_tick_all_players()` with 10 FSMs + contact detection |
| AI decisions | Not handled | `_process_ball_handler_tick()` |
| Energy | Not handled | `_drain_energy_for_ticks(1)` |
| Variable dt | Fixed `TICK_DURATION` | Variable -- `_advance_clock` is called with different dt values for bring-up, drives, screens, etc. |

The biggest blocker is that the simulator uses `_advance_clock()` with **variable time steps** (e.g. `bring_up_ticks * TICK_DURATION`, `uniform(1.5, 3.0)` for drives, `uniform(0.5, 1.5)` for shots). The TickEngine only supports fixed `TICK_DURATION` steps.

## Implementation Plan

### Step 1: Extend TickEngine to Support the Simulator's Needs

Modify [`engine/tick.py`](src/hoops_sim/engine/tick.py:58) to:

**1a. Add hooks for external systems:**
```python
class TickEngine:
    def __init__(self, game_state: GameState) -> None:
        self.game_state = game_state
        self.tick_number = 0
        self.dt = TICK_DURATION
        # NEW: Callback hooks for subsystems
        self._on_tick_callbacks: list[Callable[[float], None]] = []
        self._on_shot_clock_violation: Callable[[], None] | None = None
        self._on_quarter_end: Callable[[], None] | None = None

    def register_on_tick(self, callback: Callable[[float], None]) -> None:
        """Register a callback that runs every tick (for FSMs, energy, etc.)."""
        self._on_tick_callbacks.append(callback)
```

**1b. Support variable-dt advance:**
```python
    def advance(self, seconds: float) -> list[TickEvent]:
        """Advance by an arbitrary number of seconds (for drives, screens, etc.).
        
        Internally runs ceil(seconds / dt) ticks, so all hooks fire correctly.
        """
        events = []
        remaining = seconds
        while remaining > 0:
            step = min(self.dt, remaining)
            result = self.process_tick(dt_override=step)
            events.extend(result.events)
            remaining -= step
        return events
```

**1c. Add `process_tick` dt_override parameter:**
```python
    def process_tick(self, dt_override: float | None = None) -> TickResult:
        dt = dt_override or self.dt
        self.tick_number += 1
        events = []
        gs = self.game_state
        
        if gs.possession.is_live():
            gs.clock.tick(dt)
        gs.possession.tick()
        
        # Run registered callbacks
        for callback in self._on_tick_callbacks:
            callback(dt)
        
        # Check shot clock
        if gs.clock.is_shot_clock_violation() and gs.possession.is_live():
            events.append(TickEvent(...))
            if self._on_shot_clock_violation:
                self._on_shot_clock_violation()
        
        # Check quarter end
        if gs.clock.is_quarter_over() and gs.possession.is_live():
            events.append(TickEvent(...))
            if self._on_quarter_end:
                self._on_quarter_end()
        
        return TickResult(tick_number=self.tick_number, dt=dt, events=events)
```

### Step 2: Wire TickEngine into Simulator.__init__

```python
# In GameSimulator.__init__:
from hoops_sim.engine.tick import TickEngine

self.tick_engine = TickEngine(self.game_state)
```

### Step 3: Replace `_advance_clock` with TickEngine

Replace:
```python
def _advance_clock(self, seconds: float) -> None:
    gs = self.game_state
    gs.clock.tick(seconds)
```

With:
```python
def _advance_clock(self, seconds: float) -> None:
    self.tick_engine.advance(seconds)
```

### Step 4: Replace Shot Clock Check in Tick Loop

Replace:
```python
if gs.clock.shot_clock <= 0.0:
    self._shot_clock_violation(home_on_offense)
    self._end_possession_and_flip()
    return
```

With:
```python
# TickEngine handles shot clock detection via registered callback
# The callback sets a flag that the loop checks
if self._shot_clock_violated:
    self._shot_clock_violation(home_on_offense)
    self._end_possession_and_flip()
    return
```

### Step 5: Replace `_check_quarter_end` with TickEngine Callback

Register the quarter-end handler as a TickEngine callback:
```python
self.tick_engine._on_quarter_end = self._handle_quarter_end
```

Where `_handle_quarter_end()` contains the current body of `_check_quarter_end()`.

### Step 6: Register FSM/Energy/Contact as Tick Callbacks

```python
self.tick_engine.register_on_tick(self._on_tick_fsm_and_energy)
```

Where `_on_tick_fsm_and_energy(dt)` encapsulates the current inline logic:
```python
def _on_tick_fsm_and_energy(self, dt: float) -> None:
    self._tick_all_players(self._current_home_on_offense)
    self._drain_energy_for_ticks(1)
```

### Step 7: Rewrite the Main Tick Loop

The possession loop becomes:
```python
while not possession_resolved and ticks_elapsed < MAX_TICKS_PER_POSSESSION:
    ticks_elapsed += 1
    
    # TickEngine handles clock, shot clock, quarter end, FSMs, energy
    result = self.tick_engine.process_tick()
    
    # Check for terminating events
    for event in result.events:
        if event.event_type == TickEventType.SHOT_CLOCK_VIOLATION:
            self._shot_clock_violation(home_on_offense)
            self._end_possession_and_flip()
            return
        if event.event_type == TickEventType.QUARTER_END:
            self._handle_quarter_end_from_tick()
            self._flush_broadcast_lines()
            return
    
    # Ball handler AI decision
    handler = self._get_ball_handler(home_on_offense)
    if handler is None:
        break
    if handler.fsm.can_interrupt:
        possession_resolved = self._process_ball_handler_tick(
            handler, home_on_offense, ticks_elapsed, sit_mods,
        )
```

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Variable-dt advance breaks timing | High | The `advance()` method decomposes into fixed-dt sub-ticks |
| Quarter-end logic is complex (halftime swap, overtime, broadcast events) | High | Move the full body of `_check_quarter_end` into a callback, test extensively |
| FSM callbacks fire at wrong time relative to AI decisions | Medium | AI decisions must run AFTER tick callbacks, not during them |
| `_advance_clock` is called 8+ places with different semantics | Medium | Map each callsite; some (bring-up, drive) need full tick hooks, others (consume screen time) just need clock advance |
| Energy drain runs per-tick but also in `_drain_energy_for_ticks(bring_up_ticks)` bulk calls | Medium | Bulk calls become `tick_engine.advance(bring_up_ticks * TICK_DURATION)` which fires hooks correctly |

## Testing Plan

1. **Unit test TickEngine.advance()**: Verify that `advance(3.0)` fires exactly 30 ticks with dt=0.1
2. **Unit test callbacks**: Register a counter callback, verify it fires on every tick
3. **Unit test shot clock detection**: Set shot clock to 0.5, advance 1.0s, verify SHOT_CLOCK_VIOLATION event
4. **Unit test quarter end**: Set game clock to 0.5, advance 1.0s, verify QUARTER_END event
5. **Integration test**: Run a full game through the new TickEngine path, verify same stat distributions (within RNG tolerance) as the old inline path
6. **Regression test**: Verify that existing `test_engine/test_simulator.py` still passes

## Execution Order

1. Extend TickEngine with callbacks and variable-dt advance (tick.py only)
2. Add unit tests for the new TickEngine features
3. Wire TickEngine into simulator `__init__`
4. Replace `_advance_clock` to delegate to TickEngine
5. Replace shot clock check to use TickEngine events
6. Replace quarter-end check to use TickEngine callback
7. Register FSM/energy as tick callbacks
8. Rewrite the main possession loop
9. Run full test suite, verify no regressions
10. Profile performance (TickEngine adds function call overhead per tick)

## Estimated Effort

- TickEngine extension: ~80 lines of new code in tick.py
- Simulator refactor: ~60 lines changed, ~30 lines removed
- Tests: ~100 lines of new test code
- Total: ~2-3 hours of focused work

## Why This is Worth Doing

After this phase:
- The tick loop is a proper engine with clear extension points (register callbacks)
- Adding new per-tick systems (e.g., injury risk per tick, crowd energy per tick) requires zero changes to the simulator -- just register a callback
- The TickEngine becomes testable in isolation (currently it's dead code with its own tests that pass vacuously)
- Variable-dt advance eliminates the current pattern of manually managing clock + shot clock + quarter end checks at every `_advance_clock` callsite
