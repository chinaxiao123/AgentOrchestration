import sys
import time

from src.agent.runtime import AgentRuntime, RuntimeState


def wait_for_exit(runtime: AgentRuntime, agent_id: str) -> int:
    proc = runtime._processes[agent_id]
    return proc.wait(timeout=5)


def test_get_state_returns_stopped_for_zero_exit_process():
    runtime = AgentRuntime()
    agent_id = "agent-zero-exit"

    assert runtime.start(agent_id, [sys.executable, "-c", "raise SystemExit(0)"])
    assert wait_for_exit(runtime, agent_id) == 0

    assert runtime.get_state(agent_id) == RuntimeState.STOPPED
    assert runtime.is_running(agent_id) is False


def test_get_state_returns_crashed_for_nonzero_exit_process():
    runtime = AgentRuntime()
    agent_id = "agent-nonzero-exit"

    assert runtime.start(agent_id, [sys.executable, "-c", "raise SystemExit(7)"])
    assert wait_for_exit(runtime, agent_id) == 7

    assert runtime.get_state(agent_id) == RuntimeState.CRASHED
    assert runtime.is_running(agent_id) is False


def test_get_state_preserves_running_process_state():
    runtime = AgentRuntime()
    agent_id = "agent-running"

    assert runtime.start(
        agent_id,
        [sys.executable, "-c", "import time; time.sleep(2)"],
    )
    try:
        assert runtime.get_state(agent_id) == RuntimeState.RUNNING
        assert runtime.is_running(agent_id) is True
    finally:
        runtime.stop(agent_id)


def test_get_state_preserves_stopped_after_intentional_stop():
    runtime = AgentRuntime()
    agent_id = "agent-stopped"

    assert runtime.start(
        agent_id,
        [sys.executable, "-c", "import time; time.sleep(30)"],
    )
    time.sleep(0.05)

    assert runtime.stop(agent_id, timeout=1)
    assert runtime.get_state(agent_id) == RuntimeState.STOPPED
    assert runtime.is_running(agent_id) is False
