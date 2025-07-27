import math
from fractions import Fraction

class Badic:
    DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def __init__(self, base, *digits):
        self.base = base
        repeating = []
        main = []
        point = []

        match len(digits):
            case 1:
                main = digits[0]
            case 2:
                repeating, main = digits
            case 3:
                repeating, main, point = digits
            case _:
                raise self.BadicException("__init__ requires 2 to 4 arguments.")

        self.BadicException.enforce_type("main", main, [int, str, list])
        if type(main) == list:
            self.BadicException.enforce_type_iter("main", main, int)
        elif type(main) == int:
            if not repeating:
                repeating = 0
            if not point:
                point = 0
        elif type(main) == str:
            if not repeating:
                repeating = "0"
            if not point:
                point = "0"

        neg = len(digits) == 1 and type(main) == int and main < 0 # special case for neg
        if neg:
            main = -main
        
        if len(digits) > 1:
            self.BadicException.enforce_type("repeating", repeating, type(main))
            if type(main) == list:
                self.BadicException.enforce_type_iter("repeating", repeating, int)

        if len(digits) > 2:
            self.BadicException.enforce_type("point", point, type(main))
            if type(main) == list:
                self.BadicException.enforce_type_iter("point", point, int)

        if type(main) == int:
            self.main = Badic.convert_int_to_base(base, main)
            self.repeating = Badic.convert_int_to_base(base, repeating)
            self.point = Badic.convert_int_to_base(base, point)
        elif type(main) == str:
            try:
                self.main = [Badic.DIGITS.index(i) for i in main]
                self.repeating = [Badic.DIGITS.index(i) for i in repeating]
                self.point = [Badic.DIGITS.index(i) for i in point]
            except:
                raise self.BadicException(f"digits should be one of the following: {Badic.DIGITS}")
        elif type(main) == list:
            self.main = main
            self.repeating = repeating
            self.point = point

        if Badic.is_empty(self.repeating):
            self.repeating = []
        if Badic.is_empty(self.point):
            self.point = []
        else:
            while self.point[-1] == 0:
                self.point = self.point[:-1]
        
        self.normalize()
        if neg:
            self.negate_in_place()

    @classmethod
    def is_empty(cls, iterable):
        return not bool(len([i for i in iterable if i]))

    @classmethod
    def convert_int_to_base(cls, base, num):
        if num < 0:
            return cls.convert_int_to_base(base, -num)
        elif num >= base:
            half = max(math.ceil(math.log(num, base)) // 2, 1) 
            left = cls.convert_int_to_base(base, num // (base ** half))
            right = cls.convert_int_to_base(base, num % (base ** half))
            while len(right) < half:
                right = [0] + right
            return left + right
        else:
            return [int(num)] 

    @classmethod
    def cycle_list(cls, ls, steps=1):
        steps = steps % len(ls)
        return ls[steps:] + ls[:steps]

    @classmethod
    def tosubscript(cls, num):
        if type(num) == int:
            num = str(num)

        for i in "0123456789":
            num = num.replace(i, "₀₁₂₃₄₅₆₇₈₉"[int(i)])

        return num

    @classmethod
    def list_to_int(cls, base, ls):
        return sum([ls[i] * (base ** (len(ls) - i - 1)) for i in range(len(ls))])

    @classmethod
    def invert_list(cls, base, ls):
        return [base - i - 1 for i in ls]

    @classmethod
    def list_addition(cls, base, list1, list2):
        length = max(len(list1), len(list2))
        result = cls.convert_int_to_base(base, cls.list_to_int(base, list1) + cls.list_to_int(base, list2))
        while len(result) < length:
            result = [0] + result
        return result

    @classmethod
    def smallest_repeating_unit(cls, seq):
        n = len(seq)
        for size in range(1, n + 1):
            if n % size != 0:
                continue
            unit = seq[:size]
            if unit * (n // size) == seq:
                return unit
        return seq  # fallback, though in theory seq itself is always a unit


    @classmethod
    def normalize_list(cls, base, ls):
        # prepend a zero for safety in case there's overflow
        ls = [0] + ls
        for i in range(len(ls)-1, 0, -1):  # iterate from least significant to most
            carry, ls[i] = divmod(ls[i], base)
            ls[i-1] += carry
            # handle negative values
            if ls[i] < 0:
                borrow = (-ls[i] + base - 1) // base
                ls[i] += borrow * base
                ls[i-1] -= borrow
        # strip off any unused leading zero
        if ls[0] == 0:
            ls = ls[1:]
        return ls

    @classmethod
    def common_expansion(cls, list1, list2):
        length = math.lcm(len(list1), len(list2))
        if 0 in [len(list1), len(list2)]:
            length = max(len(list1), len(list2))
            while len(list1) < length:
                list1.append(0)
            while len(list2) < length:
                list2.append(0)
            return list1, list2
        else:
            return list1 * int(length / len(list1)), list2 * int(length / len(list2))

    @classmethod
    def strip_common_factors(cls, a, b):
        if not a or not b:
            return a  # nothing to strip if b=0
        
        g = abs(b)
        result = a
        while True:
            common = math.gcd(result, g)
            if common == 1:
                break
            result //= common
        return result

    @classmethod
    def highest_power_dividing(cls, n, b):
        if b == 0:
            raise ValueError("b cannot be zero")
        if n == 0:
            return float('inf')  # 0 is divisible by every power of b

        k = 0
        while (b ** k) % n:
            k += 1
        return k

    @classmethod
    def from_num(cls, base, num, denom=1):
        if isinstance(num, (float, str, Fraction)):
            fraction = Fraction(Fraction(num), denom)
            return cls.from_num(base, fraction.numerator, fraction.denominator)

        without_common_factors = cls.strip_common_factors(denom, base)
        if denom == 1:
            if not num:
                return cls(base, 0)
            elif num > 0:
                return cls(base, num)
            elif num < 0:
                return -cls(base, -num)
        elif without_common_factors != denom or without_common_factors == 1:
            multiplier = denom // without_common_factors # common factors of denom and base 
            power = cls.highest_power_dividing(multiplier, base) # highest power for common factors
            gap = base ** power // multiplier # factors to multiply by after shift
            return cls.from_num(base, num * gap, without_common_factors) >> power 
        else:
            quotient = num // denom
            remainder = num % denom
            p = 1
            while (base ** p - 1) % denom:
                p += 1
            to_base = cls.convert_int_to_base(base, (base ** p - 1) // denom)
            while len(to_base) < p:
                to_base = [0] + to_base
            neg_inv_denom = cls(base, to_base, [])
            return (-neg_inv_denom) * remainder + Badic.from_num(base, quotient) 

    @classmethod
    def multiply_list_by_int(cls, base, ls, num):
        return cls.normalize_list(base, [i * num for i in ls])

    @classmethod
    def multiply_repeat_by_list(cls, base, repeat, ls):
        raw_result = cls.multiply_list_by_list(base, repeat * 3, ls)
        repeating_digits = raw_result[-len(repeat)-len(ls)+1:-len(ls)+1]
        main_digits = raw_result[-len(ls)+1:]
        return cls.smallest_repeating_unit(repeating_digits), main_digits

    @classmethod
    def multiply_repeat_by_int(cls, base, repeat, num):
        return cls.multiply_repeat_by_list(base, repeat, cls.convert_int_to_base(base, num))

    @classmethod
    def solve(cls, func, base, n, starting=[[]]):
        oglen = len(starting[0])
        if len(starting[0]) >= n + 1:
            starting = sorted(list(set(tuple(i[1:]) for i in starting)))
            return [Badic(base, list(entry)) for entry in starting]
        mod = base ** (len(starting[0]) + 1)
        new = []
        for entry in starting:
            for i in range(base):
                if func(Badic.list_to_int(base, [i] + entry), mod):
                    new.append([i] + entry)
        new = [s for s in new if len(s) >= oglen]
        if not new:
            return []
        return cls.solve(func, base, n, new) 
    
    def prime_base(self):
        if self.base < 2: 
            return False
        for x in range(2, int(self.base ** 2) + 1):
            if self.base % x == 0:
                return False
        return True

    def normalize(self):
        self.repeating = Badic.smallest_repeating_unit(self.repeating)
        if self.repeating:
            while self.main and self.repeating[0] == self.main[0]:
                self.repeating = Badic.cycle_list(self.repeating)
                self.main = self.main[1:]
        return self

    def __repr__(self):
        return str(self)

    def __str__(self):
        repeating_digits = ''.join([Badic.DIGITS[i % self.base] for i in self.repeating])
        main_digits = ''.join([Badic.DIGITS[i % self.base] for i in self.main])
        if not main_digits and not repeating_digits:
            main_digits = "0"
        point_digits = ''.join([Badic.DIGITS[i % self.base] for i in self.point])
        string = f"{main_digits}"
        if self.repeating:
            string = f"[{repeating_digits}]" + string
        if self.point:
            string += f".{point_digits}"
        return string + Badic.tosubscript(self.base)

    def __int__(self):
        return int(float(self))

    def __float__(self):
        return float(self.to_num())

    def to_num(self):
        main_values = Badic.list_to_int(self.base, self.main)
        point_values = sum([Fraction(self.point[i], self.base ** (i + 1)) for i in range(len(self.point))])
        if not self.repeating:
            return Fraction(main_values) + point_values
        else:
            # make it such that main extends repeating
            if self.main:
                extended_main = (self.repeating * math.ceil(len(self.main) / len(self.repeating)))[:len(self.main)]
            else:
                extended_main = []

            # find repeating + difference
            real_repeating = Badic.cycle_list(self.repeating, len(self.main))

            difference = Badic.list_to_int(self.base, self.main) - Badic.list_to_int(self.base, extended_main)

            num = Badic.list_to_int(self.base, real_repeating)
            denom = self.base ** len(real_repeating) - 1 

            return - Fraction(num, denom) + Fraction(difference) + point_values

    def __abs__(self):
        self.normalize()
        if self.point:
            return Fraction(self.base ** len(self.point))
        else:
            digits = self.repeating + self.main
            for i in range(len(digits)):
                if digits[-i-1]:
                    return Fraction(1, self.base ** i)
        return 0

    def __mod__(self, other):
        other_value = other
        if isinstance(other, Badic):
            other_value = other.to_num()
        return Badic.from_num(self.base, self.to_num() % other_value)

    def negate_in_place(self):
        # 1. invert all lists in place
        if self.repeating:
            self.repeating = Badic.invert_list(self.base, self.repeating)
        else:
            self.repeating = [self.base - 1]

        self.main = Badic.invert_list(self.base, self.main)
        self.point = Badic.invert_list(self.base, self.point)

        # 2. handle the +1 carry on point, main, or repeating as needed
        if self.point:
            self.point[-1] += 1
            self.point = Badic.normalize_list(self.base, self.point)
        elif self.main:
            self.main[-1] += 1
            self.main = Badic.normalize_list(self.base, self.main)
        else:
            self.main = [self.repeating[-1] + 1]
            self.main = Badic.normalize_list(self.base, self.main)
            self.repeating = Badic.cycle_list(self.repeating, -1)

    def __neg__(self):
        if self.repeating:
            repeating_inverse = Badic.invert_list(self.base, self.repeating)
        else:
            repeating_inverse = [self.base - 1]
        main_inverse = Badic.invert_list(self.base, self.main)
        point_inverse = Badic.invert_list(self.base, self.point)
        if point_inverse:
            point_inverse[-1] += 1
            point_inverse = Badic.normalize_list(self.base, point_inverse)
        elif main_inverse:
            main_inverse[-1] += 1
            main_inverse = Badic.normalize_list(self.base, main_inverse)
        else:
            main_inverse = [repeating_inverse[-1] + 1]
            main_inverse = Badic.normalize_list(self.base, main_inverse)
            repeating_inverse = Badic.cycle_list(repeating_inverse, -1)

        return Badic(self.base, repeating_inverse, main_inverse, point_inverse)

    def __add__(self, other):
        a, b = self.copy(), other.copy()

        Badic.BadicException.enforce_type("b", b, Badic)
        if a.base != b.base:
            raise Badic.BadicException("both bases must be the same")

        # uncycle repeating such that they both have the same number of main digits + 1 for safety
        required_main_digits = max(len(a.main), len(b.main)) + 1
        while len(a.main) < required_main_digits:
            if a.repeating:
                a.repeating = Badic.cycle_list(a.repeating, -1)
                a.main = [a.repeating[0]] + a.main
            else:
                a.main = [0] + a.main
        while len(b.main) < required_main_digits:
            if b.repeating:
                b.repeating = Badic.cycle_list(b.repeating, -1)
                b.main = [b.repeating[0]] + b.main
            else:
                b.main = [0] + b.main

        # add points to the end of each point
        required_point_digits = max(len(a.point), len(b.point))
        while len(a.point) < required_point_digits:
            a.point.append(0)
        while len(b.point) < required_point_digits:
            b.point.append(0)

        # add main, repeating and point
        new_main = Badic.list_addition(a.base, a.main, b.main)
        expanded_repeating = Badic.common_expansion(a.repeating, b.repeating)
        new_repeating = Badic.list_addition(a.base, *expanded_repeating)
        new_point = Badic.list_addition(a.base, a.point, b.point)

        # account for overflow
        if len(new_point) > required_point_digits and required_point_digits:
            new_main[-1] += 1
            new_point = new_point[1:]
            new_main = Badic.normalize_list(self.base, new_main)

        if not new_repeating:
            pass
        elif len(new_main) > required_main_digits:
            # main section carryover
            new_main[0] += new_repeating[-1]
            # repeating section carryover
            # [1, A, B] expands into [B+1, A, B+1, A, B+1, A, B+1]
            # the last one is only B+1 due to main section carryover
            # turning [1, A, B] into [A, B+1]
            if len(new_repeating) > len(expanded_repeating[0]):
                new_repeating[-1] += new_repeating[0]
                new_repeating = new_repeating[1:]
            # cycle to reflect changes (since the list should now end at A)
            if new_repeating:
                new_repeating = Badic.cycle_list(new_repeating, -1)
        elif len(new_repeating) > len(expanded_repeating[0]):
            # repeating section carryover
            # [1, A, B] expands into [B+1, A, B+1, A, B+1, A, B]
            # last one is just B due to no main section carryover
            # so we move B to the main section
            new_main = [new_repeating[-1]] + new_main
            # turning [1, A, B] into [A, B+1]
            new_repeating[-1] += new_repeating[0]
            new_repeating = new_repeating[1:]
            # cycle to reflect changes (since the list should now end at A)
            if new_repeating:
                new_repeating = Badic.cycle_list(new_repeating, -1)

        # create object and normalize
        new = Badic(a.base, new_repeating, new_main, new_point).normalize()
        return new

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return other + -self

    def __mul__(self, other):
        other_value = other
        if type(other) == int:
            if other < 0:
                return (self * -other)
            elif not other:
                return Badic(self.base, 0)
            elif other == 1:
                return self
            else:
                return self * (other // 2) + self * (other // 2) + self * (other % 2)
        if isinstance(other, Badic):
            other_value = other.to_num()
        return Badic.from_num(self.base, self.to_num() * other_value)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        other_value = other
        if isinstance(other, Badic):
            other_value = other.to_num()
        frac = Fraction(self.to_num(), other_value)
        return Badic.from_num(self.base, frac.numerator, frac.denominator)

    def __rtruediv__(self, other):
        other_value = other
        if isinstance(other, Badic):
            other_value = other.to_num()
        frac = Fraction(other_value, self.to_num())
        return Badic.from_num(self.base, frac.numerator, frac.denominator)

    def __lshift__(self, num):
        self = self.copy()
        for _ in range(num):
            if self.point:
                self.main.append(self.point[0])
                self.point = self.point[1:]
            else:
                self.main.append(0)
        return self

    def __rshift__(self, num):
        self = self.copy()
        for _ in range(num):
            if self.main:
                self.point = [self.main[-1]] + self.point
                self.main = self.main[:-1]
            elif self.repeating:
                self.point = [self.repeating[-1]] + self.point
                self.repeating = Badic.cycle_list(self.repeating, -1)
            else:
                self.point = [0] + self.point
        return self

    def __eq__(self, other):
        other_value = other
        if isinstance(other, Badic):
            other_value = other.to_num()
        return self.to_num() == other_value

    def __pow__(self, num, base=None):
        result = 0
        if num % 1 and num > 1:
            result = (self ** (num // 1)) * (self ** (num % 1))
        elif not num % 1:
            if num == 0:
                result = Badic(self.base, 1)
            elif num == 1:
                result = self
            else:
                result = (self ** (num // 2)) * (self ** (num // 2)) * (self ** (num % 2))
        if base:
            return result % base
        return result

    def copy(self):
        return Badic(
            self.base,
            self.repeating.copy(),
            self.main.copy(),
            self.point.copy()
        )

    class BadicException(Exception):
        def __init__(self, message):            
            super().__init__(message)

        @classmethod
        def enforce_type(cls, name, obj, tpe):
            if not isinstance(tpe, (list, tuple)):
                tpe = [tpe]
            if not isinstance(obj, tuple(tpe)):
                raise cls(f"argument {name} should be of types: {tpe}")

        @classmethod
        def enforce_type_iter(cls, name, obj, tpe):
            cls.enforce_type(name, obj, (list, tuple))
            if not isinstance(tpe, (list, tuple)):
                tpe = [tpe]
            if not all(isinstance(item, tuple(tpe)) for item in obj):
                raise cls(f"argument \"{name}\" should contain objects of types: {tpe}")
