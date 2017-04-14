#!/usr/bin/env python

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
    

