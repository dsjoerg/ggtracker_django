def read_variable_int(bytes):
    # check continuation bits
    for byte in bytes[0:-1]:
        if (byte & 0x80 == 0):
            raise Error("non-final byte does not have continuation bit set")
        if (bytes[-1] & 0x80 != 0):
            raise Error("final byte has continuation bit set")

    shift = 0
    value = 0
    for byte in bytes:
        value = ((byte & 0x7F) << shift * 7) | value
        shift += 1

    #The least significant bit of the result is a sign flag
    if (value & 0x1 == 1):
        multiplier = -1
    else:
        multiplier = 1

    return multiplier * (value >> 1)
