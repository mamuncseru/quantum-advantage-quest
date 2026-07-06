"""Bernstein-Vazirani (1993) — YOUR implementation.

Recover the hidden string s from ONE application of the phase oracle for
f(x) = s.x mod 2. The circuit is identical to Deutsch-Jozsa; only the
readout differs — that identity is the point of the exercise.

Fill in bernstein_vazirani() and make `pytest predecessors/02-bernstein-vazirani`
green. Honor system: exactly one `apply` of the oracle.
"""

from qsim import H, amplitudes, apply, sample, zero_state


def bernstein_vazirani(oracle, n):
    """Return the hidden string s as a bitstring like '10110'.

    The state after the H-sandwich has ALL its amplitude on |s> — so a
    single measurement (or a peek at the amplitudes) reads out s. Build:

        |0...0>  --H on all-->  --oracle-->  --H on all-->  read s

    TODO(you): implement.
    """
    raise NotImplementedError("Session 1 homework")
