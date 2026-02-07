import struct


def _parse_color(value, palette):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        key = value.strip()
        if key in palette:
            key = palette[key]
        if key.startswith("#"):
            hexstr = key[1:]
            if len(hexstr) == 6:
                return int("FF" + hexstr, 16)
            if len(hexstr) == 8:
                return int(hexstr, 16)
        raise RuntimeError(f"Unsupported color: {value}")
    raise RuntimeError(f"Unsupported color type: {type(value)}")


def _float_bits(value):
    import struct
    return struct.unpack(">I", struct.pack(">f", float(value)))[0]

