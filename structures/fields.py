from .descriptors import FieldDescriptor
from .markers import NoDefault

__all__ = [
    'Field',
    'Integer',
    'Float',
    'Decimal',
    'Boolean',
    'Bytes',
    'Binary',
    'String',
    'List',
    'Tuple',
    'Set',
    'FrozenSet',
    'Dict',
]


class Field(object):
    '''Basic class for attributes

       It may use for quick building simple type:

          >>> from structures import *
          >>> class S(Structure):
          ...     t = Field(int, '12')
          ...
          >>> s = S()
          >>> s.t
          12
          >>> s.t = '321'
          >>> s.t
          321
          >>> assert type(s.t) is int

       More complex type for reusable:

          >>> from structures import *
          >>> class T(Field):
          ...     func = int
          ...     def __init__(self, default=NoDefault):
          ...         super(T, self).__init__(self.func)
          ...         self.default = default
          ...
          >>> class S(Structure):
          ...     t1 = T
          ...     t2 = T(12)
          ...
          >>> s = S()
          >>> s.t2
          12
          >>> assert type(s.t2) is int
          >>> assert not hasattr(s, 't1')
          >>> s.t1 = '321'
          >>> s.t1
          321
          >>> assert type(s.t1) is int

    '''

    func = lambda x: x
    # The function is called when value is assigned for the attribute.
    # It must be accept one argument and return processed (e.g. casted) analog.
    # Also it is called for the default value in the creating (not instance!)
    # structure.

    default = NoDefault
    # Default value. It is processed by ``func`` in the creating structure
    # and by ``init_func`` in creating structure's instance.

    def __init__(self, func, default=NoDefault):
        self.func = func

        if default is not NoDefault:
            self.default = self.func(default)

    def contribute_to_structure(self, structure, name):
        setattr(structure, name, FieldDescriptor(name, self))


class SimpleField(Field):
    '''
          >>> from structures import *
          >>> class IntegerFromSimpleField(SimpleField):
          ...     func = int
          >>> class S(Structure):
          ...     i = IntegerFromSimpleField(10)
          ...
          >>> s = S()
          >>> s.i
          10
          >>> s.i = 5.2
          >>> s.i
          5
    '''
    func = lambda x: x

    def __init__(self, default=NoDefault):
        super(SimpleField, self).__init__(self.__class__.func, default)


class Integer(SimpleField):
    '''Integer type

          >>> from structures import *
          >>> class S(Structure):
          ...     i = Integer(10)
          ...
          >>> s = S()
          >>> s.i
          10
          >>> s.i = 5.2
          >>> s.i
          5
    '''
    func = int


class Float(SimpleField):
    '''Float type

          >>> from structures import *
          >>> class S(Structure):
          ...     f = Float(3.14)
          ...
          >>> s = S()
          >>> assert s.f == 3.14
          >>> assert type(s.f) is float
          >>> s.f = '9.82'
          >>> assert s.f == 9.82
          >>> assert type(s.f) is float
    '''
    func = float


class Decimal(SimpleField):
    '''Decimal type, contain a decimal.Decimal

          >>> import decimal
          >>> from structures import *
          >>> class S(Structure):
          ...     d = Decimal('8.62')
          ...
          >>> s = S()
          >>> assert s.d == decimal.Decimal('8.62')
          >>> assert type(s.d) is decimal.Decimal
          >>> s.d = '1.5'
          >>> assert s.d == decimal.Decimal('1.5')
          >>> assert type(s.d) is decimal.Decimal
    '''
    import decimal as __decimal
    func = __decimal.Decimal


class Boolean(SimpleField):
    '''Boolean type

          >>> from structures import *
          >>> class S(Structure):
          ...     b = Boolean(False)
          ...
          >>> s = S()
          >>> s.b
          False
          >>> s.b = 666
          >>> s.b
          True
          >>> s.b = 0
          >>> s.b
          False
    '''
    func = bool


class Bytes(SimpleField):
    '''Bytes type, this is a type introducing the sequence of bytes: str

          >>> from structures import *
          >>> class S(Structure):
          ...     b = Bytes(b'binary string')
          ...
          >>> s = S()
          >>> s.b
          b'binary string'
          >>>
          >>> try:
          ...     s.b = 'unicode string'
          ...     raise AssertionError('Must raise TypeError exception.')
          ...
          ... except TypeError:
          ...     pass
          ...
          >>> assert type(s.b) is bytes
          >>> s.b
          b'binary string'
    '''
    func = bytes


class Binary(SimpleField):
    '''Binary type is deprecated! Use Bytes!

          >>> from structures import *
          >>> class S(Structure):
          ...     b = Binary(b'binary string')
          ...
          >>> s = S()
          >>> s.b
          b'binary string'
          >>>
          >>> try:
          ...     s.b = 'unicode string'
          ...     raise AssertionError('Must raise TypeError exception.')
          ...
          ... except TypeError:
          ...     pass
          ...
          >>> assert type(s.b) is bytes
          >>> s.b
          b'binary string'
    '''
    @staticmethod
    def func(*args, **kwargs):
        import warnings
        warnings.warn('Binary type is deprecated! Use Bytes!', DeprecationWarning)
        return bytes(*args, **kwargs)


class String(Field):
    '''String type, this is a type introducing the symbolic string: unicode

        String(default, enc=UTF-8)
            - default: default value
            - enc: encoding name for binary data

          >>> from structures import *
          >>> class S(Structure):
          ...     s = String('test')
          ...
          >>> s = S()
          >>> s.s
          'test'
          >>> s.s = 777
          >>> s.s
          '777'
    '''

    def __init__(self, default=NoDefault, enc='UTF-8'):
        self.enc = enc
        super(String, self).__init__(lambda o, e=enc: self.__class__.func(o, e), default)

    @staticmethod
    def func(obj, enc='UTF-8'):
        '''Cast ``obj`` to the symbolic string (unicode) if it's possible

           Codepage ``enc`` is used for decoding str.'''

        if isinstance(obj, str):
            return obj
        else:
            try:
                return str(obj, enc)
            except TypeError:
                return str(obj)


class StandartContainer(Field):
    func = lambda x: x
    _default = NoDefault

    def __init__(self, default=NoDefault):
        super().__init__(self.func, default)

    @property
    def default(self):
        if self._default is not NoDefault:
            return self.func(self._default)
        else:
          return NoDefault

    @default.setter
    def default(self, value):
        self._default = value


class List(StandartContainer):
    '''List type

          >>> from structures import *
          >>> class S(Structure):
          ...     l = List(range(665, 668))
          ...
          >>> s = S()
          >>> s.l
          [665, 666, 667]
          >>> assert type(s.l) is list
          >>> s.l = range(667, 664, -1)
          >>> s.l
          [667, 666, 665]
          >>> assert type(s.l) is list
    '''
    func = list


class Tuple(StandartContainer):
    '''Tuple type

          >>> from structures import *
          >>> class S(Structure):
          ...     t = Tuple(range(665, 668))
          ...
          >>> s = S()
          >>> s.t
          (665, 666, 667)
          >>> assert type(s.t) is tuple
          >>> s.t = '999'
          >>> s.t
          ('9', '9', '9')
          >>> assert type(s.t) is tuple
    '''
    func = tuple


class Set(StandartContainer):
    '''Set type

          >>> from structures import *
          >>> class S(Structure):
          ...     s = Set(range(665, 668))
          ...
          >>> s = S()
          >>> assert s.s == set([665, 666, 667])
          >>> assert type(s.s) is set
          >>> s.s = '919293'
          >>> assert s.s == set(['1', '2', '3', '9'])
          >>> assert type(s.s) is set
    '''
    func = set


class FrozenSet(StandartContainer):
    '''FrozenSet type

          >>> from structures import *
          >>> class S(Structure):
          ...     fs = FrozenSet(range(665, 668))
          ...
          >>> s = S()
          >>> assert s.fs == frozenset([665, 666, 667])
          >>> assert type(s.fs) is frozenset
          >>> s.fs = '919293'
          >>> assert s.fs == frozenset(['1', '2', '3', '9'])
          >>> assert type(s.fs) is frozenset
    '''
    func = frozenset


class Dict(StandartContainer):
    '''Dict type

          >>> from structures import *
          >>> class S(Structure):
          ...     d = Dict({1: 'a', 2: 'b'})
          ...
          >>> s = S()
          >>> s.d = [('a', 1), ('b', 2)]
          >>> assert s.d == {'a': 1, 'b': 2}
          >>> assert type(s.d) is dict
          >>> s.d = {1: 'a', 2: 'b'}
          >>> assert s.d == {1: 'a', 2: 'b'}
          >>> assert type(s.d) is dict
    '''
    func = dict
