import subprocess
import sys
import time

from src.agent.runtime import AgentRuntime, RuntimeState


def test_get_state_returns_stopped_for_zero_exit_process():
    runtime = AgentRuntime()
    agent_id = "agent-zero-exit"

    process = subprocess.Popen(
        [sys.executable, "-c", "pass"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.wait(timeout=5)

    runtime._processes[agent_id] = process
    runtime._states[agent_id] = RuntimeState.RUNNING

    assert runtime.get_state(agent_id) == RuntimeState.STOPPED


def test_get_state_returns_crashed_for_nonzero_exit_process():
    runtime = AgentRuntime()
    agent_id = "agent-nonzero-exit"

    process = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.exit(3)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.wait(timeout=5)

    runtime._processes[agent_id] = process
    runtime._states[agent_id] = RuntimeState.RUNNING

    assert runtime.get_state(agent_id) == RuntimeState.CRASHED


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
