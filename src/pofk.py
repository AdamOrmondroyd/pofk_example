"""
# Recreating the P(k) example from Cobaya paper https://arxiv.org/pdf/2005.05290.pdf

Here we define a Theory class that computes P(k), which only needs two methods:
1. Returning what the class can compute starting with get_, in this case get_primordial_pk()
2. calculate() taking the parameters defining the power spectrum and computing it.

The class attribute params defines what parameters are the ones which need to be passed
to this class, and which are made available by this likelihood.
The remaining class attributes defind (n_samples_wavelength and k_pivot) define parameters
that can be set in the declaration of the class in the .yaml/their default values if omitted.


"""

import numpy as np
from cobaya.theory import Theory


def feature_envelope(k, c, w):
    """
    Returns the value of the envelope at k. The envelope functional form is

        env(k) = exp(-0.5 (log10(k/c)/w)**2) * sin(2πk/l)

    """
    return np.exp(-((np.log10(k / c) / w) ** 2) / 2)  ## um where's sine gone?


def feature_power_spectrum(
    As, ns, A, l, c, w, kmin=1e-6, kmax=10, k_pivot=0.05, n_samples_wavelength=20
):
    """
    Creates the primordial scalar power spectrum as a power law plus an oscillatory
    feature of given amplitude A and wavelength l, cantered at c with a lognormal envelope
    of log10-width w, as

        ΔP/P = A * exp(-0.5 (log10(k/c)/w)**2) * sin(2πk/l)

    Ther characteristic Δk is determined by the number of samples per oscillation
    n_samples_wavelength (default: 20).

    Returns a sample of k, P(k)
    """
    # Ensure thin enough sampling at low-k
    Δk = min(0.0005, 1 / n_samples_wavelength)
    ks = np.arange(kmin, kmax, Δk)
    power_law = lambda k: As * (k / k_pivot) ** (ns - 1)
    ΔPoverP = lambda k: (A * feature_envelope(k, c, w) * np.sin(2 * np.pi * k / l))
    Pks = power_law(ks) * (1 + ΔPoverP(ks))
    return ks, Pks


class FeaturePrimordialPk(Theory):
    """
    Theory class producing a slow-roll-like power spectrum with an enveloped,
    lineary-oscillatory feature on top.
    """

    params = {
        "As": None,
        "ns": None,
        "amplitude": None,
        "wavelength": None,
        "centre": None,
        "logwidth": None,
    }

    n_samples_wavelength = 20
    k_pivot = 0.05

    def calculate(self, state, want_derived=True, **params_values_dict):
        print("here0")
        As, ns, amplitude, wavelength, centre, logwidth = [
            params_values_dict[p] for p in self.params.keys()
        ]
        ks, Pks = feature_power_spectrum(
            As,
            ns,
            amplitude,
            wavelength,
            centre,
            logwidth,
            kmin=1e-6,
            kmax=10,
            k_pivot=self.k_pivot,
            n_samples_wavelength=self.n_samples_wavelength,
        )
        state["primordial_scalar_pk"] = {"k": ks, "Pk": Pks, "log_regular": False}
        print(ks)
        print(Pks)

    def get_primordial_scalar_pk(self):
        return self.current_state["primordial_scalar_pk"]


def logprior_high_k(A, c, w, k_high=0.25, A_min=5e-3):
    """
    Returns -inf whenever the feaure acts at too high ks only, i.e. s.t. the
    product of amplitude and envelope at "k_high" is smaller than "A_min", given that the
    envelope is centred at "k > k_high.
    """
    if c < k_high:
        return 0
    return 0 if A * feature_envelope(k_high, c, w) > A_min else -np.inf
