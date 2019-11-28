import argparse
import os
import pickle
import numpy
import math
import re
import copy
from neware_parser.models import *
from neware_parser.neware_processing_functions import machine_learning_post_process_cycle
from django.core.management.base import BaseCommand
import tensorflow as tf
from django.db.models import Max,Min
from tensorflow.keras.layers import (
    Dense, Flatten, Conv2D, GlobalAveragePooling1D,
    BatchNormalization, Conv1D, Layer
)
from tensorflow.keras import Model

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

'''
Shortened Variable Names:
    vol -   voltage
    cap -   capacity
    dchg -  discharge
    neigh - neighbourhood
    der -   derivative
    pred -  predicted
    meas -  measured
    eval -  evaluation
    eq -    equillibrium
'''

# === Begin: make my barcodes ==================================================

def make_my_barcodes(fit_args):
    my_barcodes = CyclingFile.objects.filter(
        database_file__deprecated=False,
        database_file__is_valid=True
    ).exclude(
        database_file__valid_metadata=None
    ).order_by(
        'database_file__valid_metadata__barcode'
    ).values_list(
        'database_file__valid_metadata__barcode',
        flat=True
    ).distinct()

    used_barcodes = []
    for b in my_barcodes:
        if CycleGroup.objects.filter(barcode=b).exists():
            used_barcodes.append(b)

    if len(fit_args['wanted_barcodes'])==0:
        return used_barcodes
    else:
        return list(
            set(used_barcodes).intersection(
                set(fit_args['wanted_barcodes'])
            )
        )



# === End: make my barcodes ====================================================

# ==== Begin: initial processing ===============================================


def clamp(a, x, b):
    x = min(x, b)
    x = max(x, a)
    return x


def make_voltage_grid(min_v, max_v, n_samples, my_barcodes):
    if n_samples < 2:
        n_samples = 2
    all_cycs = Cycle.objects.filter(group__barcode__in=my_barcodes, valid_cycle=True)
    my_max = max(all_cycs.aggregate(Max('chg_maximum_voltage'))['chg_maximum_voltage__max'],
        all_cycs.aggregate(Max('dchg_maximum_voltage'))['dchg_maximum_voltage__max'])
    my_min= min(all_cycs.aggregate(Min('chg_minimum_voltage'))['chg_minimum_voltage__min'],
        all_cycs.aggregate(Min('dchg_minimum_voltage'))['dchg_minimum_voltage__min'])

    my_max = clamp(min_v, my_max, max_v)
    my_min = clamp(min_v, my_min, max_v)

    delta = (my_max - my_min)/float(n_samples-1.)
    return numpy.array([my_min + delta*float(i) for i in range(n_samples)])


def initial_processing(my_barcodes, fit_args):
    all_data = {}
    voltage_grid = make_voltage_grid(fit_args['voltage_grid_min_v'], fit_args['voltage_grid_max_v'], fit_args['voltage_grid_n_samples'], my_barcodes)

    '''
    - cycles are grouped by their charge rates and discharge rates.
    - a cycle group contains many cycles
    - things are split up this way to sample each group equally
    - each barcode corresponds to a single cell
    '''
    for barcode in my_barcodes:
        '''
        - dictionary indexed by charging and discharging rate (i.e. cycle group)
        - contains structured arrays of
            - cycle_number
            - capacity_vector: a vector where each element is a
              capacity associated with a given voltage
              [(voltage_grid[i], capacity_vector[i])
              is a voltage-capacity pair]
            - vq_curve_mask: a vector where each element is a weight
              corresponding to a voltage-capacity pair
              [this allows us to express the fact that sometimes a given
              voltage was not measured, so the capacity is meaningless.
              (mask of 0)]
        '''

        cyc_grp_dict = {}

        #TODO(sam): add the aux vars:
        # - the lower cutoff of discharge (for previous cycle)
        # - the rate of discharge (for previous cycle)
        # - cutoff rate of charge (for current cycle)
        # - cutoff rate of discharge (for previous cycle)

        for cyc_group in CycleGroup.objects.filter(
                barcode=barcode
        ).order_by('discharging_rate'):
            result = []
            for cyc in cyc_group.cycle_set.order_by(
                    'cycle_number'):
                if cyc.valid_cycle:
                    vq_curve, vq_mask = machine_learning_post_process_cycle(cyc, voltage_grid)
                    if vq_curve is None:
                        continue

                    result.append((
                        cyc.get_offset_cycle(),
                        vq_curve,
                        vq_mask,
                        cyc.chg_minimum_voltage,
                        cyc.chg_maximum_voltage,
                        cyc.dchg_minimum_voltage,
                        cyc.dchg_maximum_voltage,

                        cyc.get_temperature()
                    ))
            cyc_grp_dict[
                (cyc_group.charging_rate, cyc_group.discharging_rate)
            ] = numpy.array(
                result,
                dtype=[
                    ('cycle_number', 'f4'),
                    ('capacity_vector', 'f4', len(voltage_grid)),
                    ('vq_curve_mask', 'f4', len(voltage_grid)),
                    ('chg_minimum_voltage', 'f4'),
                    ('chg_maximum_voltage', 'f4'),
                    ('dchg_minimum_voltage', 'f4'),
                    ('dchg_maximum_voltage', 'f4'),

                    ('temperature', 'f4'),
                ])

        all_data[barcode] = cyc_grp_dict

    return {'voltage_grid':voltage_grid, 'all_data':all_data}


# === End: initial processing ==================================================
def compile_dataset(fit_args):
    my_barcodes = make_my_barcodes(fit_args)
    pick = initial_processing(my_barcodes, fit_args)
    if not os.path.exists(fit_args['path_to_dataset']):
        os.mkdir(fit_args['path_to_dataset'])
    with open(os.path.join(fit_args['path_to_dataset'], 'dataset_ver_{}.file'.format(fit_args['dataset_version'])), 'wb') as f:
        pickle.dump(pick, f, pickle.HIGHEST_PROTOCOL)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--path_to_dataset', required=True)
        parser.add_argument('--dataset_version', required=True)
        parser.add_argument('--voltage_grid_min_v', type=float, default=2.5)
        parser.add_argument('--voltage_grid_max_v', type=float, default=4.5)
        parser.add_argument('--voltage_grid_n_samples', type=int, default=32)
        parser.add_argument('--wanted_barcodes', type=int, nargs='+', default=[83220, 83083])

    def handle(self, *args, **options):
        compile_dataset(options)


