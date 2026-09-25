def my_max_value(n: int ) -> int:
    return 2 ** n - 1

EPOCH_MS_DEFAULT = 1288834974657
NODE_ID_DEFAULT = 1


TIMESTAMP_BITS = 41 # число миллисекунд прощедщих с момента пользовательской эпохи
NODE_ID_BITS = 10 # номер узла
SEQUENCE_ID_BITS = 12 # порядковый номер 

TIMESTAMP_SHIFT = NODE_ID_BITS + SEQUENCE_ID_BITS

# так как номер и время(все три строчки) беззнаковые 
TIMESTAMP_MS_MAX = my_max_value(TIMESTAMP_BITS)
NODE_ID_MAX = my_max_value(NODE_ID_BITS)
SEQUENCE_ID_MAX = my_max_value(SEQUENCE_ID_BITS) 