import h5py

# HDF5 파일 열기
with h5py.File('checkpoint\KRW-BTC.weights.h5') as f:
    # 파일 내 구조 출력
    def print_structure(name, obj):
        print(name)
    f.visititems(print_structure)