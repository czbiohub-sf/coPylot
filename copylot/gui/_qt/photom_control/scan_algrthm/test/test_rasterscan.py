from widgets.scan_algrthm.scan_algorithm import ScanAlgorithm

def test_rasterscan():
    initial_coord = (0, 0)
    size = (100, 100)
    gap = 5
    rs = ScanAlgorithm(initial_coord, size, gap)
    coord = rs.generate_cornerline()


