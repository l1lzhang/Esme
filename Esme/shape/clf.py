import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import dionysus as d
import numpy as np

from Esme.dgms.format import load_dgm
from Esme.dgms.vector import dgms2vec
from Esme.graph.dataset.modelnet import modelnet2graphs
from Esme.ml.svm import classifier
from Esme.ml.eigenpro import eigenpro
from Esme.dgms.fake import permute_dgms
from sklearn.preprocessing import normalize
from Esme.dgms.arithmetic import add_dgm

from collections import Counter

parser = ArgumentParser("scoring", formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve')
parser.add_argument("--idx", default=4897, type=int, help='model index. Exclude models from 260 to 280') # (1515, 500) (3026,)
parser.add_argument("--clf", default='eigenpro', type=str, help='choose classifier')
parser.add_argument("--test_size", default=0.1, type=float, help='test size')
parser.add_argument("--n_iter", default=50, type=int, help='num of iters for eigenpro') # (1515, 500) (3026,)
parser.add_argument("--permute", action='store_true')
parser.add_argument("--norm", action='store_true')
parser.add_argument("--random", action='store_true')


DIRECT = '/home/cai.507/anaconda3/lib/python3.6/site-packages/save_dgms/' # mn10/fiedler'


if __name__ == '__main__':
    args = parser.parse_args()

    # check_partial_dgms(DIRECT, graph=graph, fil=fil, fil_d=fil_d, a = 200, b = 1700)
    # sys.exit()

    # load dgms and y
    print(dir)
    version = '10'

    from Esme.graph.dataset.modelnet import load_modelnet
    train_dataset, test_dataset = load_modelnet(version, point_flag=False)
    all_dataset = train_dataset + test_dataset

    dgms = []
    for i in range( args.idx):
        graph, fil = 'mn' + version, 'fiedler_w'
        dgm = d.Diagram([[np.random.random(), 1]])

        for fil_d in ['sub', 'sup', 'epd']:
            dir = os.path.join(DIRECT, graph, fil, fil_d, 'norm_True','')
            f = dir + str(i) + '.csv'
            try:
                tmp_dgm = load_dgm(dir, filename=f)
            except FileNotFoundError:
                print(f'{f} of size {all_dataset[i].pos.shape[0]}/{all_dataset[i].face.shape[1]} not found. Added a dummy one')
                tmp_dgm = d.Diagram([[0,0]])
            dgm = add_dgm(dgm, tmp_dgm)

        dgms.append(dgm)
    if args.permute:
        dgms = permute_dgms(dgms, permute_flag=True)

    # convert to vector
    x = dgms2vec(dgms, vectype='pvector')
    if args.random:
        x = np.random.random(x.shape)
    if args.norm:
        x = normalize(x, axis=0)

    _, y = modelnet2graphs(version=graph[-2:], print_flag=True, labels_only=True)
    print(f'total num is {len(y)}')
    y = np.array(y)[:args.idx]
    print(Counter(list(y)))

    # classifer
    if args.clf == 'rf':
        clf = classifier(x, y, method='svm', n_cv=1)
        clf.svm(n_splits=10)
    else:
        # eigenpro
        eigenpro(x, y, max_iter=args.n_iter, test_size=args.test_size)