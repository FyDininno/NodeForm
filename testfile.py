def identity_function(value):
    return value

def cap(comparison, true_value):
    return comparison if comparison<true_value else true_value

def threshold(comparison, true_value):
    return comparison if comparison>true_value else true_value