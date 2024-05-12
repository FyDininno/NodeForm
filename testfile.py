def identity_function(value):
    return value

def cap(comparison, true_value):
    return comparison if comparison<true_value else true_value

def thresh(comparison, true_value):
    return comparison if comparison>true_value else true_value

def barr(comparison, true_value):
    return 0 if comparison>true_value else true_value

def wall(comparison, true_value):
    return true_value if comparison>true_value else 0