"""
--- Support 338S (left) ---        --- Support 335S (right) ---
[16 rows, 4 columns]               [12 rows, 4 columns]

        0   1   2   4                  0   1   2   4
    0   .   .   .   .              0   .   .   .   .
    1   .   .   .   .              1   .   .   .   .
    2   .   .   .   .              2   .   .   .   .
    3   .   .   .   .              3   .   .   .   .
    4   .   .   .   .              4   .   .   .   .
    5   .   .   .   .              5   .   .   .   .
    6   .   .   .   .              6   .   .   .   .
    7   .   .   .   .              7   .   .   .   .
    8   .   .   .   .              8   .   .   .   .
    8   .   .   .   .              9   .   .   .   .
    10  .   .   .   .              10  .   .   .   .
    11  .   .   .   .              11  .   .   .   .
    12  .   .   .   .              12  .   .   .   .
    13  .   .   .   .
    14  .   .   .   .
    15  .   .   .   .
    16  .   .   .   .
    

Origin (top left):                 Origin (top left):
x=8.1                              x=100.6
y=40.2                             y=40.12

x_spacing = 18                     x_spacing = 18
y_spacing = 13.72                  y_spacing = 18.55

            x = x0 + y_index * x_spacing
            y = y0 + y_index * y_spacing

"""


def coordinates_lh(column_index, row_index, rack):
    """ Function to calculate the (x, y) coordinates for the needle.

    :param column_index: float
        Columns index in the 0...N range
    :param row_index: float
        Row index in the 0...N range
    :param rack: string
        descriptor for the rack '338S' or '335S'
    :return: list
        coordinates [x, y] corresponding to the input indices
    """
    if rack == '338S':
        x0 = 8.1
        y0 = 40.2
        x_spacing = 18
        y_spacing = 13.72
    else:
        x0 = 100.6
        y0 = 40.12
        x_spacing = 18
        y_spacing = 18.55
    x = x0 + column_index * x_spacing
    y = y0 + row_index * y_spacing
    return [x, y]
