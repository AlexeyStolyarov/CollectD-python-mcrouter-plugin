#!/usr/bin/python


class Values:
    plugin = ''
    interval = ''
    plugin_instance = ''
    type = ''
    type_instance = ''
    values = ''

    def dispatch(self):
        print "[plugin_name/plugin_instance/type/type_instance]: %s/%s/%s/%s =  %s" % (
            self.plugin, self.plugin_instance, self.type, self.type_instance, self.values)


class Config:
    parent = None
    key = ''
    values = ()
    children = ()

    def __init__(self, parent=None, key='', values=(), children=()):
        self.parent = parent
        self.key = key
        self.values = values
        self.children = children


def debug(arg):
    print '[DEBUG] %s' % arg


def info(arg):
    print '[INFO] %s' % arg


def warning(arg):
    print '[WARNING] %s' % arg


def register_read(read_callback):
    read_callback()


def register_config(config_callback):
    config_callback(Config(key='HOST', values=('10.20.16.27',)))
    config_callback(Config(key='PORT', values=('11211',)))
    config_callback(Config(key='INSTANCE', values=('default_INSTANCE',)))
