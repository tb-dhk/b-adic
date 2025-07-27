from __init__ import Badic 
from fractions import Fraction
import itertools

# ----- test cases for Badic -----

# case 1: int input
b1 = Badic(10, 123)
assert b1.main == [1, 2, 3]
assert b1.repeating == []
assert b1.point == []

# case 2: str input
b2 = Badic(16, "1A3")
assert b2.main == [1, 10, 3]
assert b2.repeating == []
assert b2.point == []

# case 3: list input (with repeating + post-decimal)
b3 = Badic(5, [1, 2, 3], [4], [0, 1])
assert b3.repeating == [1, 2, 3]
assert b3.main == [4]
assert b3.point == [0, 1]

# case 4: invalid digit in string
try:
    Badic(10, "1@3")
    assert False, "Expected Badic.BadicException for invalid digit"
except Badic.BadicException as e:
    assert "digits should be one of" in str(e)

# case 5: wrong type (dict instead of int/str/list)
try:
    Badic(10, {"a": 1})
    assert False, "Expected Badic.BadicException for wrong type"
except Badic.BadicException as e:
    assert "should be of types" in str(e)

# case 6: too few arguments (only base given)
try:
    Badic(10)
    assert False, "Expected Badic.BadicException for missing arguments"
except Badic.BadicException as e:
    assert "__init__ requires 2 to 4 arguments." in str(e)

# case 7: normalisation
b7 = Badic(10, [1, 2, 3, 4, 5], [1, 2, 3, 6])
assert b7.repeating == [4, 5, 1, 2, 3]
assert b7.main == [6]
assert b7.point == []

badics_16 = [
    # simple integer only
    Badic(16, 255),                         # 0xFF

    # simple string main
    Badic(16, "1A3"),                       # 0x1A3

    # string main + repeating
    Badic(16, "B", "C"),                    # ...CCCCCB in hex

    # string main + repeating + point
    Badic(16, "F", "A", "5"),               # ...AAAAAF.5 in hex

    # list main only
    Badic(16, [1, 2, 3]),                   # [1,2,3] base 16

    # list main + repeating
    Badic(16, [0, 14], [15]),               # ...FFFF0E

    # list main + point
    Badic(16, [10, 11, 12], [], [1, 2]),    # ABC.12

    # list main + repeating + point
    Badic(16, [2, 4], [15], [3]),           # ...FFFF24.3

    # large integer (forces convert_int_to_base recursion)
    Badic(16, 65535),                       # 0xFFFF

    # mixed case string (should still work)
    Badic(16, "DEADBEEF"),                  # DEADBEEF

    # string main + repeating, multi-digit repeating
    Badic(16, "1C", "AB"),                  # ...ABABAB1C

    # string main + repeating + multi-digit point
    Badic(16, "2", "F0", "1B"),              # ...F0F0F02.1B

    Badic(16, "F", "", "")
]

pairs = itertools.permutations(badics_16, 2)
for a, b in pairs:
    assert (a+b).to_num() == a.to_num() + b.to_num()
    assert (a-b).to_num() == a.to_num() - b.to_num()

print("all add/sub tests passed")

# create some Badic numbers
a = Badic.from_num(10, 15)    # 15 decimal
b = Badic.from_num(10, 256)   # 256 decimal

# left shift tests (multiply by base^shift)
assert float(a << 1) == 150      # 15 * 10^1 = 150
assert float(a << 2) == 1500     # 15 * 10^2 = 1500
assert float(b << 3) == 256000   # 256 * 10^3 = 256000

# right shift tests (integer division by base^shift)
assert float(a >> 1) == 1.5        # 15 // 10^1 = 1
assert float(a >> 2) == 0.15        # 15 // 10^2 = 0
assert float(b >> 4) == 0.0256        # 256 // 10^4 = 0

# shifting zero
zero = Badic.from_num(10, 0)
assert float(zero << 5) == 0
assert float(zero >> 3) == 0

# chaining shifts
c = Badic.from_num(10, 7)
assert float((c << 2) >> 1) == 70  # (7 * 10^2) // 10^1 = 70

print("all shift tests passed")

def almost_equal(a, b, tol=1e-12):
    return abs(a - b) < tol

# trivial integers
assert float(Badic.from_num(5, 0)) == 0.0
assert float(Badic.from_num(5, 7)) == 7.0
assert float(Badic.from_num(5, 100)) == 100.0

# negative integers
print("starting 5, -1")
assert float(Badic.from_num(5, -1)) == -1.0
assert float(Badic.from_num(5, -6)) == -6.0

# fractions that terminate exactly in base 5
assert almost_equal(float(Badic.from_num(5, 1, 5)), 1/5)      # 0.2
assert almost_equal(float(Badic.from_num(5, 3, 25)), 3/25)    # 0.12

# fractions that repeat (compare approximately)
assert almost_equal(float(Badic.from_num(5, 1, 3)), 1/3)
assert almost_equal(float(Badic.from_num(5, 2, 3)), 2/3)

# larger numerator / denominator mix
assert almost_equal(float(Badic.from_num(5, 7, 12)), 7/12)

# denominator with factor 5 (terminating) + factor not dividing 5 (mixed)
assert almost_equal(float(Badic.from_num(5, 7, 30)), 7/30)

print("all mult/div tests passed")

# abs() tests
# --------------
# plain integer
a = Badic.from_num(5, 25)     # 25₁₀ = 100₅, v₅(25) = 2, so |25|₅ = 5⁻²
assert abs(a) == Fraction(1, 25)

# unit (not divisible by 5)
b = Badic.from_num(5, 7)      # 7, v₅(7) = 0, so |7|₅ = 1
assert abs(b) == 1

# fraction with denominator containing 5
c = Badic.from_num(5, 3, 25)  # 3/25, v₅(3/25) = -2, so |3/25|₅ = 5² = 25
assert abs(c) == 25

# zero should have absolute value 0 by convention
z = Badic.from_num(5, 0)
assert abs(z) == 0


# mod tests (truncating digits)
# -----------------------------
x = Badic.from_num(5, 312)    # 312₁₀ = 2222₅
# truncate to 5¹ → keep 1 digit → result = 2 (mod 5)
assert (x % 1).to_num() == 0

# truncate to 5² → keep 2 digits → result = 12 (mod 25)
assert (x % 2).to_num() == 0

# truncate to 5³ → keep 3 digits → result = 62 (mod 125)
assert (x % 3).to_num() == 0

# test fraction truncation (like “floor” in p-adics)
y = Badic.from_num(5, 17, 5)  # 17/5
# modulo 5 should give the lowest digit
assert (y % 1).to_num() == Fraction(2, 5)   # 17/5 = ...22.2₅, mod 5 leaves 2

# zero modulo anything should be zero
assert (z % 5).to_num() == 0

print("all abs/mod tests passed")

func = lambda n, p: ((n ** 4 + 2 * n ** 3 + 3 * n ** 2 + 4 * n + 5) % p == 0 % p)
digits = 30
print(f"b-adic solutions for x^4 + 2x^3 + 3x^2 + 4x + 5 = 0, truncated to {digits} digits")
for i in range(2, 63):
    result = Badic.solve(func, i, digits)
    if len(result) > 1:
        print(f"{i}:", result)
