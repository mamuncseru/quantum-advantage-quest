# Autopsy 04 — Shor (1994)

## 1. The problem

Factor N. Two thousand years old; the reason RSA exists is that after
centuries of Fermat, Gauss, and the number field sieve, the best classical
algorithms are still superpolynomial (NFS: exp(O((log N)^(1/3) (log log N)^(2/3)))).
**This is the first problem in our curriculum that the world cared about
before quantum computing.** That is not a coincidence; it is the whole story.

## 2. The classical wall

Structural feature blocking classical progress: the multiplicative group
mod N hides its order. Factoring reduces (classically! — Miller 1976) to
**order finding**: given a coprime to N, find the least r with a^r ≡ 1 mod N.

The reduction (draft this yourself — exercise): if r is even and
a^(r/2) ≢ −1 mod N, then a^(r/2) ± 1 are nontrivial "square roots of 1"
whose gcd with N yields factors. Random a succeeds with probability ≥ 1/2.
So the wall is: **order finding = period finding of f(j) = a^j mod N**,
a function that is efficiently computable but whose period is invisible to
any known classical sampling of its values.

## 3. The primitive

Simon's algorithm with the group Z₂ⁿ replaced by Z: phase estimation of the
unitary U: |x⟩ → |ax mod N⟩. The eigenvalues of U are e^(2πik/r) — **the
order r lives in the spectrum**, and the QFT over Z_{2^t} reads it out:

    counting register in uniform superposition
    -> controlled-U^(2^j) powers entangle counting phases with eigenphases k/r
    -> inverse QFT concentrates amplitude near c ~ k 2^t / r
    -> continued fractions recover r from c/2^t.

Same architecture as Simon: quantum Fourier sampling + classical
post-processing (continued fractions instead of Gaussian elimination).
Two details that matter and are visible in `shor.py`:

- The work register starts at |1⟩ = uniform mixture of the r eigenstates of U
  with eigenphases k/r — you never need to prepare an eigenstate.
- The circuit's true cost center is **modular exponentiation** (the
  controlled-U^(2^j) cascade), not the QFT. Folklore puts the magic in the
  QFT; the engineering lives in reversible arithmetic.

## 4. The hardness evidence

Tier 2, exactly where our program aims: no proof that factoring is
classically hard — only 50+ years of the best mathematicians failing, and a
trillion-dollar cryptographic ecosystem betting on that failure. This is
what "advantage under a well-studied hardness assumption" means in practice.
No dequantization in 30 years. Post-quantum cryptography exists *because*
nobody expects one.

## 5. The lesson

Written out because it is the course's centerpiece — argue with it, then
rewrite it in your own words:

**The quantum content of Shor's algorithm existed before Shor** (Simon's
subroutine, generalized from Z₂ⁿ to Z). What Shor added was the *problem*:
the recognition that (i) factoring reduces to order finding, (ii) order
finding is period finding, (iii) period finding is exactly what Fourier
sampling does, and (iv) the oracle can be **instantiated** — a^x mod N is
efficiently computable. Every step except (iii) is classical mathematics.
The named algorithm = old primitive + new problem + an instantiable oracle.
This is the template our 6-month hunt assumes: we are looking for the
problem, not the primitive. The problem-shape: **answer encoded as the
period/coset structure of an efficiently computable function over an abelian
group.**

## Exercises

- [ ] **Proof draft #2:** the Miller reduction (§2). Draft it, then check
      against `curriculum/solutions.md`.
- [ ] Run `python predecessors/04-shor/shor.py`. Then, in `find_order`,
      print the raw measured c values for N=21 and verify by hand that
      continued fractions on c/2^t recovers r = 6 for a = 2.
- [ ] Why does the algorithm still work when gcd(k, r) > 1 makes the
      continued-fraction denominator a proper divisor of r? (Look at the
      `mult` loop in `find_order` — justify its correctness.)
- [ ] Where exactly did the promise structure of Simon become a *theorem*
      about Z_N here, removing the need for any promise at all?
