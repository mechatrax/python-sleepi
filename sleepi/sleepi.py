import smbus


class FieldMapper(object):
    map = {}

    def __init__(self, fields):
        self.map = fields

    def read(self):
        assert False

    def write(self, data):
        assert False

    def get(self, name):
        bit = self.map[name]
        data = self.read()
        return (data >> bit) & 0x01

    def set(self, name, value):
        bit = self.map[name]
        data = self.read()
        mask = 0x1 << bit
        if value == 0:
            data &= ~mask
        else:
            data |= mask
        self.write(data)

    def __getattr__(self, name):
        if name in self.map:
            return self.get(name)
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name in self.map:
            self.set(name, value)
        else:
            return object.__setattr__(self, name, value)

    def __getitem__(self, key):
        if key in self.map:
            return self.get(key)
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if key in self.map:
            self.set(key, value)
        else:
            return object.__setitem__(self, key, value)


class Register(object):
    def __init__(self, bus, dev, addr, flags):
        self.bus = bus
        self.device = dev
        self.address = addr
        mapper = FieldMapper(flags)
        mapper.read = self.read
        mapper.write = self.write
        self.flags = mapper

    def read(self):
        assert False

    def write(self, data):
        assert False

    def __getattr__(self, name):
        if name == 'value':
            return self.read()
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name == 'value':
            return self.write(value)
        else:
            return object.__setattr__(self, name, value)


class RegisterMapper(object):
    map = {}

    def __init__(self, bus, dev, regs):
        self.bus = bus
        self.device = dev
        self.map = regs

    def get(self, name):
        reg = self.map[name]
        addr = reg['address']
        if 'flags' in reg:
            flags = reg['flags']
        else:
            flags = {}
        return reg['type'](self.bus, self.device, addr, flags)

    def __getattr__(self, name):
        return self.get(name)

    def __getitem__(self, key):
        return self.get(key)


class RegisterByte(Register):
    def read(self):
        return self.bus.read_byte_data(self.device, self.address)

    def write(self, data):
        self.bus.write_byte_data(self.device, self.address, data)


class RegisterWord(Register):
    def read(self):
        return self.bus.read_word_data(self.device, self.address)

    def write(self, data):
        self.bus.write_word_data(self.device, self.address, data)


class RegisterDWord(Register):
    def read(self):
        data = self.bus.read_i2c_block_data(self.device, self.address, 4)
        return int.from_bytes(bytes(data), 'little')

    def write(self, data):
        self.bus.write_i2c_block_data(self.device, self.address,
            list(data.to_bytes(4, 'little')))


class Sleepi(object):
    def __init__(self, busnum, devaddr):
        regmap = {
            'adc': { 'type': RegisterWord, 'address': 0x00 },
            'voltage': { 'type': RegisterWord, 'address': 0x02 },
            'push_switch_count': { 'type': RegisterByte, 'address': 0x04 },
            'restart': { 'type': RegisterWord, 'address': 0x05,
                'flags': { 'rse': 0x00 } },
            'timeout': { 'type': RegisterByte, 'address': 0x06 }
        }
        bus = smbus.SMBus(busnum)
        self.registers = RegisterMapper(bus, devaddr, regmap)


class Sleepi2(object):
    def __init__(self, busnum, devaddr):
        regmap = {
            'adc_value': { 'type': RegisterWord, 'address': 0x00 },
            'voltage': { 'type': RegisterWord, 'address': 0x02 },
            'push_switch_count': { 'type': RegisterByte, 'address': 0x04 },
            'watchdog_control': { 'type': RegisterByte, 'address': 0x05,
                'flags': { 'rste': 0x00, 'slpe': 0x01 } },
            'watchdog_timeout': { 'type': RegisterByte, 'address': 0x06 },
            'watchdog_wakeup_delay': { 'type': RegisterByte, 'address': 0x07 },
            'input_control': { 'type': RegisterByte, 'address': 0x08,
                'flags': { 'ritrg': 0x02, 'eitrg': 0x01, 'eipde': 0x00 } },
            'external_input_count': { 'type': RegisterByte, 'address': 0x09 },
            'output_control': { 'type': RegisterByte, 'address': 0x0A,
                'flags': { 'eoe': 0x00 } },
            'wakeup_status': { 'type': RegisterByte, 'address': 0x0B,
                'flags': { 'rif': 0x05, 'eif': 0x04, 'btnf': 0x03,
                    'almf': 0x02, 'wdto': 0x01, 'por': 0x00 } },
            'version': { 'type': RegisterByte, 'address': 0x0F }
        }
        bus = smbus.SMBus(busnum)
        self.registers = RegisterMapper(bus, devaddr, regmap)

class Sleepi3(object):
    def __init__(self, busnum, devaddr):
        regmap = {
            'voltage1': { 'type': RegisterWord, 'address': 0x00 },
            'voltage2': { 'type': RegisterWord, 'address': 0x02 },
            'restore_voltage': { 'type': RegisterWord, 'address': 0x04 },
            'adc_interval': { 'type': RegisterByte, 'address': 0x06 },
            'push_switch_count': { 'type': RegisterByte, 'address': 0x07 },
            'external_input_count': { 'type': RegisterByte, 'address': 0x08 },
            'watchdog_timeout': { 'type': RegisterByte, 'address': 0x09 },
            'sleep_timeout': { 'type': RegisterByte, 'address': 0x0A },
            'watchdog_control': { 'type': RegisterByte, 'address': 0x0B,
                'flags': { 'rste': 0x00, 'uvlo': 0x02 } },
            'input_control': { 'type': RegisterByte, 'address': 0x0C,
                'flags': { 'ritrg': 0x02, 'eitrg': 0x01, 'eipde': 0x00 } },
            'io_status': { 'type': RegisterByte, 'address': 0x0D,
                'flags': { 'eo': 0x00, 'ei': 0x01, 'sw': 0x02 } },
            'wakeup_status': { 'type': RegisterByte, 'address': 0x0E,
                'flags': { 'prf': 0x06, 'rif': 0x05, 'eif': 0x04,
                    'swf': 0x03, 'almf': 0x02, 'wdtf': 0x01, 'porf': 0x00 } },
            'version': { 'type': RegisterByte, 'address': 0x0F }
        }
        bus = smbus.SMBus(busnum)
        self.registers = RegisterMapper(bus, devaddr, regmap)

class Sleepi4(object):
    def __init__(self, busnum, devaddr):
        regmap = {
            'voltage1': { 'type': RegisterWord, 'address': 0x00 },
            'voltage2': { 'type': RegisterWord, 'address': 0x02 },
            'adc_interval': { 'type': RegisterByte, 'address': 0x06 },
            'push_switch_count': { 'type': RegisterByte, 'address': 0x07 },
            'watchdog_timeout': { 'type': RegisterByte, 'address': 0x09 },
            'sleep_timeout': { 'type': RegisterByte, 'address': 0x0A },
            'restore_voltage1': { 'type': RegisterWord, 'address': 0x10 },
            'restore_voltage2': { 'type': RegisterWord, 'address': 0x12 },
            'external_input_count1': { 'type': RegisterByte, 'address': 0x14 },
            'external_input_count2': { 'type': RegisterByte, 'address': 0x15 },
            'initial_watchdog_timeout': { 'type': RegisterByte, 'address': 0x16 },
            'input_status': { 'type': RegisterByte, 'address': 0x17,
                'flags': {
                    'ei2': 0x02,
                    'ei1': 0x01,
                    'sw': 0x00
                }
            },
            'wakeup_status': { 'type': RegisterWord, 'address': 0x18,
                'flags': {
                    'uvlo2': 0x0F,
                    'pr2f': 0x0E,
                    'ei2f': 0x0C,
                    'uvlo1': 0x07,
                    'pr1f': 0x06,
                    'rif': 0x05,
                    'ei1f': 0x04,
                    'swf': 0x03,
                    'almf': 0x02,
                    'wdtf': 0x01,
                    'porf': 0x00
                }
            },
            'input_control': { 'type': RegisterByte, 'address': 0x1A,
                'flags': {
                    'ei2trg': 0x04,
                    'ei2pde': 0x03,
                    'ei1trg': 0x02,
                    'ei1pde': 0x01,
                    'ritrg': 0x00
                }
            },
            'output_control': { 'type': RegisterByte, 'address': 0x1B,
                'flags': {
                    'eo2': 0x01,
                    'eo1': 0x00
                }
            },
            'wakeup_control': { 'type': RegisterByte, 'address': 0x1C,
                'flags': {
                    'uvlo2': 0x02,
                    'uvlo1': 0x01,
                    'rste': 0x00
                }
            },
            'watchdog_feed': { 'type': RegisterByte, 'address': 0x1D },
            'current': { 'type': RegisterWord, 'address': 0x1E },
            'power': { 'type': RegisterWord, 'address': 0x20 },
            'energy': { 'type': RegisterDWord, 'address': 0x22 },
            'raw_voltage1': { 'type': RegisterWord, 'address': 0x28 },
            'raw_voltage2': { 'type': RegisterWord, 'address': 0x2A },
            'raw_current': { 'type': RegisterWord, 'address': 0x2C },
            'version': { 'type': RegisterByte, 'address': 0x2F }
        }
        bus = smbus.SMBus(busnum)
        self.registers = RegisterMapper(bus, devaddr, regmap)


