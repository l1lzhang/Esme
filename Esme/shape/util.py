import os
import pickle
from persUF import geodesic_diagrams_on_shape
import sys
import numpy as np
from Esme.dgms.format import diag2dgm
from Esme.helper.io_related import make_dir
from Esme.helper.time import timefunction

DGM_DIRECT = '/home/cai.507/Documents/DeepLearning/local-persistence-with-UF/dgms/'
SEG_DIRECT = '/home/cai.507/Documents/DeepLearning/meshdata/MeshsegBenchmark-1.0/data/seg/Benchmark/'

# off file format:
# https://en.wikipedia.org/wiki/OFF_(file_format)

def loady(model=1, seg=0):
    """
    :param model: model idx
    :param seg: use 0 (human segmentation) as default.
    :return:
    """
    # read ground truth from benchmark
    direct = os.path.join(SEG_DIRECT, str(model), str(model) + '_' + str(seg) + '.seg')
    print(direct)
    with open(direct, 'rb') as f:
        y = f.readlines()
    y = [int(i) for i in y]
    assert len(y) == face_num(str(model))
    return np.array(y)

def node_num(file='0', allflag=False, print_flag = False):
    if int(float(file)) in list(range(260, 281)): sys.exit()

    file = os.path.join(DGM_DIRECT, '..','tmp', '') + file
    with open(file + '.off') as f:
        first_line = f.readline()
        assert first_line == 'OFF\n'
        second_line = f.readline()

    if allflag: return second_line
    n =  int(second_line.split(' ')[0])
    if print_flag: print('file %s has %s nodes'%(file, n))
    return n

def face_num(file='0'):
    res = node_num(file, allflag=True)
    return int(res.split(' ')[1])

@timefunction
def face_idx(file = '0'):

    file_ = os.path.join(DGM_DIRECT, '..', 'tmp', '') + file
    with open(file_ + '.off') as f:
        res = f.readlines()

    n_node, n_face = node_num(file), face_num(file)
    assert len(res) == n_node + n_face + 2
    face_indices = res[n_node+2: ] # a list of face index ('3 1676 468 3987\n')
    assert len(face_indices) == n_face

    final_indices = []
    for indice in face_indices:
        tmp = indice.split('\n')[0].split(' ') # ['3', '1185', '1183', '1184']
        tmp = [int(i) for i in tmp]
        final_indices.append(tmp[1:])
    return final_indices

def off_pos(file='1'):
    # return the position of a off file
    file_ = os.path.join(DGM_DIRECT, '..', 'tmp', '') + file
    with open(file_ + '.off') as f:
        res = f.readlines()

    n_node, n_face = node_num(file), face_num(file)
    assert len(res) == n_node + n_face + 2
    pos = res[2: 2+n_node]
    pos_list = []
    for pt in pos:
        tmp = pt.split('\n')[0].split(' ')  # ['3', '1185', '1183', '1184']
        tmp = [float(i) for i in tmp]
        pos_list.append(tmp)
    res = np.array(pos_list)
    assert res.shape == (n_node, 3)
    return res

def off_face(file='1'):
    face_indices = face_idx(file)
    return np.array(face_indices)


def vdgms2fdgms(dgms):
    pass

def savedgm(res, f):
    direct = DGM_DIRECT
    direct = os.path.join(direct,  f)
    make_dir(direct)
    with open(os.path.join(direct,'m'+f +'.pkl'), 'wb') as fp:
        pickle.dump(res, fp)

@timefunction
def loaddgm(f, form = 'mathieu'):
    """
    :param f:
    :param form: either mathieu's form or dionysus's form
    :return:
    """
    assert form in ['methieu', 'dionysus']

    direct = DGM_DIRECT
    direct = os.path.join(direct,  f)
    with open(os.path.join(direct, 'm' + f + '.pkl'), 'rb') as fp:
        dgms = pickle.load(fp)

    if form == 'mathieu':
        return dgms # # a typical dgm is x the following form: x = ([(1834, 1), (2434, 2416)], [(1.5937974886466386, 0.0), (1.530983082142745, 0.49418551657459003)])
    else:
        dio_dgms = []  # a list of pd (array of shape (n,2))
        for dgm in dgms:
            idx_list, pd_list = dgm[0], dgm[1]
            assert len(idx_list) == len(pd_list)
            pd = np.array(pd_list)
            assert pd.shape[1] == 2
            dio_dgms.append(pd)
        dgms = [diag2dgm(diag) for diag in dio_dgms]
        return dgms


def check(f):
    res_ = loaddgm(f)
    file =  f + '.off'
    n = node_num(file=f)
    res = geodesic_diagrams_on_shape(file, range(n))
    assert res == res_

def modeidx(low=1000, upper=10000):
    res = []
    for f in range(1, 400):
        n = node_num(file=str(f))
        if low < n and n < upper: res.append(f)
    print('There are %s modes whose node is from %s to %s'%(len(res), low, upper))
    for i in res:
        print(i),
    return res

def exist_file(f):
    try:
        res = loaddgm(f)
        n = node_num(file=f)
        if len(res)==n:
            return True
        else:
            return False
    except IOError:
        return False

def prince_cat():
    # categories of princeton shape benchmark
    cats = ['human', 'cup']
    indices = [[range(0, 20), range(20, 40)]]

if __name__ == '__main__':
    off_pos('12')
    sys.exit()

    for i in range(1, 2):
        file = str(i)
        contents = face_idx(file)
        print(contents[-10:])
        n_node, n_face = node_num(file), face_num(file)
        assert len(contents) == n_node + n_face + 2
    # print('num of nodes', node_num(file))
    # print('num of faces', face_num(file))

    # print(node_num('1'))