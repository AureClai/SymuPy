"""
    Visualization tools for ISTTT
    Usage:
        As module
            from visualize tool import AnimateTrajectories
            A = AnimateTrajectories(d)
        Input:
            d = Dataframe with columns ['id','t','x']
        As demo:
            python visualizetool.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import pandas as pd
import random


class AnimateTrajectories(animation.TimedAnimation):
    """
        Class specified to animate a set trajectories
    """

    def __init__(self,
                 trajectories=pd.DataFrame(
            {'id':  sorted(list(range(10)) * 100),
             't': list(np.linspace(0, 1, 100)) * 10,
             'x': [random.random() for i in range(1000)]
             })):
        """
        Initialize the data frame of traces
        Input:
            DataFrame object with 3 columns ['id','t','x']
        Output:
            AnimationTrajectories object.
        """
        
        # Rearange ids
        trajectories['id'] = trajectories['id'].replace(
                pd.Series(
                        dict(zip(list(pd.unique(trajectories.id)), list(range(len(pd.unique(trajectories.id))))))).astype(int), regex=True)
        
        self.trajectories = trajectories
        self.x = []
        self.y = []
        self.lineb = []
        self.linea = []
        self.linep = []

        TMAX = max(trajectories.t)
        XMAX = max(trajectories.x)

        # parse data for each vehicle
        self.veh_id = set(self.trajectories.id)
        self.iter = sorted(list(set(self.trajectories.t)))
        self.iterp = []
        for i in self.veh_id:
            self.x.append(
                self.trajectories[trajectories.id == i]['t'].tolist())
            self.y.append(
                self.trajectories[trajectories.id == i]['x'].tolist())
            self.iterp.append(0)

        # plot initialize
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)

        # emtpy lines
        self.lineb = [Line2D([], [], color='blue', alpha=0.2)
                      for i in self.veh_id]  # background
        self.linea = [Line2D([], [], color='blue', linewidth=2)
                      for i in self.veh_id]  # animate
        self.linep = [Line2D(
            [], [], color='green', marker='o',
            markeredgecolor='green') for i in self.veh_id]  # scatter

        # list of lines
        self._drawn_artists = [*self.lineb, *self.linea, *self.linep]
        for line in self._drawn_artists:
            ax1.add_line(line)
            ax1.set_xlim(0, TMAX)
            ax1.set_ylim(0, XMAX)
            ax1.set_xlabel('time [s]')
            ax1.set_ylabel('space [m]')

        animation.TimedAnimation.__init__(
            self, fig, interval=50, blit=True)

    def _init_draw(self):
        lines = [*self.lineb, *self.linea, *self.linep]
        for l in lines:
            l.set_data([], [])

    def new_frame_seq(self):
        """
            Update of the superclass method
            Input:
                None
            Returns:
                Iterator object to detail each frame
        """
        return iter(self.iter)

    def _find_actual_frame(self, id, frame):
        """
            Determine frame for according to the
            iterator self.iter. Assignes previous iteration
            in case no information is found. This is useful
            when having different lenghts on (x,y) data
            Input:
                id: integer
                frame: iteration
            Output
                index: actual index to be ploted x[:index]
        """
        time_id = self.x[id]
        try:
            index = time_id.index(frame)
        except Exception:
            if self.iterp[id] != 0:
                index = self.iterp[id]
            else:
                index = 1
        return index

    def _draw_frame(self, framedata):
        """
            Update extension: method to update, update objects
            in figures.
            Input:
                Framedata: iterator
            Output:
                None
        """
        for j in self.veh_id:
            i = self._find_actual_frame(j, framedata)
            head = i - 1
            self.lineb[j].set_data(self.x[j][:], self.y[j][:])
            self.linea[j].set_data(self.x[j][:i], self.y[j][:i])
            self.linep[j].set_data(self.x[j][head], self.y[j][head])
            self.iterp[j] = i

        self._drawn_artists = [*self.lineb, *self.linea, *self.linep]


def main():
    """ Main file
        Creates a simple demo data set of trajectories car following type
    """
    n = 100
    v = 25
    t = np.linspace(start=0, stop=40, num=400).tolist()
    x = [[v * i - 10 * j for i in t] for j in range(n)]
    dft = pd.DataFrame({'id': [],
                        't': [],
                        'x': []})
    for i in range(10):
        x_f = [s for s in x[i] if s >= 0]
        t_f = [t[x[i].index(s)] for s in x[i] if s >= 0]
        df = pd.DataFrame({'id': [int(i)] * len(t_f),
                           't': t_f,
                           'x': x_f})
        dft = pd.concat([dft, df])
    dft['id'] = dft['id'].apply(int)
    print('Demo Created: ')
    print(dft.head(5))
    A = AnimateTrajectories(dft)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
