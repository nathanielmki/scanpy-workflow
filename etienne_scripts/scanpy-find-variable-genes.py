#!/usr/bin/env python3

import logging

import scanpy.api as sc
from wrapper_utils import (
    ScanpyArgParser,
    read_input_object, write_output_object
)


def main(argv=None):
    argparser = ScanpyArgParser(argv, 'Logarithmize data and mark variable genes.')
    argparser.add_input_object()
    argparser.add_output_object()
    argparser.add_output_plot()
    argparser.add_argument('--flavor',
                           choices=['seurat', 'cell_ranger'],
                           default='seurat',
                           help='Choose the flavor for computing normalised dispersion. '
                                'Default: seurat')
    argparser.add_subset_parameters(params=['mean', 'disp'])
    argparser.add_argument('-b', '--n-bins',
                           type=int,
                           default=20,
                           help='Number of bins for binning the mean gene expression. '
                                'Normalisation is done with respect to each bin. Default: 20')
    argparser.add_argument('-n', '--n-top-genes',
                           type=int,
                           default=None,
                           help='Number of highly variable genes to keep, '
                                'ignoring --subset-parameters when set. Default: None')
    args = argparser.args

    logging.debug(args)

    adata = read_input_object(args.input_object_file, args.input_format)

    min_mean, max_mean, min_disp, max_disp = None, None, None, None
    for name, high, low in zip(args.parameter_names, args.high_thresholds, args.low_thresholds):
        if name == 'mean':
            min_mean = low
            max_mean = high
        elif name == 'disp':
            min_disp = low
            max_disp = high
        else:
            msg = 'Unsupported parameter name "{}", omitted'.format(name)
            logging.warning(msg)

    #Use highly_variable_genes instead of filter_genes_dispersion
    #This function expects logarithmized data, hence the log1p
    #As a consequence, it is not necessary anymore to logarithmize the data in the following process (scale_data).
    # --> scale_data.do_log should be set to false.
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata,
                                  flavor=args.flavor,
                                  min_mean=min_mean, max_mean=max_mean,
                                  min_disp=min_disp, max_disp=max_disp,
                                  n_bins=args.n_bins,
                                  n_top_genes=args.n_top_genes)

    write_output_object(adata, args.output_object_file, args.output_format)

    logging.info('Done')
    return 0


if __name__ == '__main__':
    main()