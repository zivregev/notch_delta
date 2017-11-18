import math
import random
import os
from matplotlib import pyplot as plt

COLORS = {"w": 0, "b": 1}
NEIGHBOURS_OFFSET = [(i, j) for i in [-1, 0, 1] for j in [-1, 0, 1]  if not (i == 0 and j == 0)]

output_directory = "figs"
zero_width = 4


def get_nonzero_random():
    num = random.random()
    while num == 0.0:
        num = random.random()
    return num


class Cell:
    def __init__(self, alpha, beta, tau, notch_threshold):
        self._alpha = alpha
        self._beta = beta
        self._color = COLORS["w"]
        self._is_active = True
        self._notch_level = 0.0
        self._tau = tau
        self._notch_threshold = notch_threshold
        self._time_to_deactivate = float("inf")

    def _update_notch_level(self):
        self._notch_level = (self._beta / self._alpha) + (self._notch_level - (self._beta / self._alpha)) * math.exp((-1) * self._alpha)

    def _switch_to_black(self):
        self._color = COLORS["b"]

    def _signal_delta(self):
        self._time_to_deactivate = self._tau

    def _deactivate(self):
        self._is_active = False

    def is_active(self):
        return self._is_active

    def color(self):
        return self._color

    def apply_time_tick(self, delta_signal):
        if self._is_active:
            if self._time_to_deactivate == float("inf") and delta_signal:
                self._signal_delta()
            if not self._time_to_deactivate == float("inf"):
                if self._time_to_deactivate > 0:
                    self._time_to_deactivate = self._time_to_deactivate - 1
                else:
                    self._deactivate()
                    return
            self._update_notch_level()
            if self._notch_level >= self._notch_threshold:
                self._switch_to_black()
                self._deactivate()


class Colony:
    def __init__(self, rows, columns, tau, notch_threshold):
        self.cells = [[Cell(alpha= get_nonzero_random(), beta= get_nonzero_random(), tau= tau, notch_threshold= notch_threshold) for j in range(columns)] for i in range(rows)]
        self._rows = rows
        self._columns = columns

    def _apply_time_tick(self):
        for i in range(self._rows):
            for j in range(self._columns):
                cell = self.cells[i][j]
                if cell.is_active():
                    delta_signal_from_neighbours = False
                    for i_shift, j_shift in NEIGHBOURS_OFFSET:
                        neighbour_i, neighbour_j = self._index_to_cell_index(i + i_shift, j + j_shift)
                        if self.cells[neighbour_i][neighbour_j].color() == COLORS["b"]:
                            delta_signal_from_neighbours = True
                            break
                    cell.apply_time_tick(delta_signal_from_neighbours)

    def _index_to_cell_index(self, i, j):
        return (i % self._rows, j % self._columns)

    def run(self,rounds):
        for i in range(rounds):
            self._apply_time_tick()

    def as_color_array(self):
        return [[cell.color() for cell in row] for row in self.cells]


def generate_fig_name(tau):
    tau_as_str = str(tau).split(".")[0].zfill(zero_width)
    if tau == float("inf"):
        tau_as_str = "9" * zero_width
    return output_directory + "/" + "colony_" + tau_as_str

if not os.path.exists(output_directory):
    os.makedirs(output_directory)
rows = 100
columns = 100
generations = 1000
notch_threshold = 0.5
taus = [float(tau) for tau in range(0, 20)] + [float("inf")]
for tau in taus:
    print("tau: " + str(tau))
    colony = Colony(rows=rows, columns=columns, tau=tau, notch_threshold=notch_threshold)
    colony.run(generations)
    result = colony.as_color_array()
    plt.imshow(result,interpolation="nearest", cmap="Greys")
    plt.title(r'$\tau$' + "=" + str(tau))
    plt.savefig(generate_fig_name(tau))
    plt.close()

