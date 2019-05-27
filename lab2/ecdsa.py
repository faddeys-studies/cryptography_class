import random
import crypto_lib


class EllipticCurve:
    def __init__(self, a: int, b: int, p: int):
        self.a = a
        self.b = b
        self.p = p

    def __iter__(self):
        yield self.a
        yield self.b
        yield self.p

    def __eq__(self, other):
        if not isinstance(other, EllipticCurve):
            raise TypeError(other.__class__)
        return self.a == other.a and self.b == other.b and self.p == other.p

    def __hash__(self):
        return hash((self.a, self.b, self.p))

    def __repr__(self):
        return f"E_{self.p}({self.a}, {self.b})"

    @property
    def zero(self):
        return EllipticPoint(None, None, self)


class EllipticPoint:
    def __init__(self, x: int, y: int, curve: EllipticCurve):
        self.x = x
        self.y = y
        self.curve = curve
        self.is_null = x is None

    def __neg__(self) -> "EllipticPoint":
        if self.is_null:
            return self
        return EllipticPoint(self.x, (-self.y) % self.curve.p, self.curve)

    def __eq__(self, q) -> bool:
        return self.x == q.x and self.y == q.y

    def __hash__(self):
        return hash((self.x, self.y, self.curve))

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, q) -> "EllipticPoint":
        if not isinstance(q, EllipticPoint):
            raise TypeError(q.__class__)
        p = self
        if p.is_null:
            return q
        if q.is_null:
            return p
        c = self.curve
        if p == -q:
            return c.zero
        c_p = c.p
        if p == q:
            numer = (3 * p.x * p.x + c.a) % c_p
            denom = (2 * p.y) % c_p
            l = (numer * crypto_lib.inverse_in_group(denom, c_p)) % c_p
        else:
            numer = (q.y - p.y) % c_p
            denom = (q.x - p.x) % c_p
            l = (numer * crypto_lib.inverse_in_group(denom, c_p)) % c_p
        x = (l * l - p.x - q.x) % c_p
        y = (l * (p.x - x) - p.y) % c_p
        return EllipticPoint(x, y, c)

    def __mul__(self, k) -> "EllipticPoint":
        if not isinstance(k, int):
            raise TypeError(k.__class__)
        if k < 0:
            return -(self * (-k))
        p = self
        r = self.curve.zero
        while k > 0:
            if k % 2:
                r += p
            k >>= 1
            p += p
        return r

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __rmul__(self, other):
        return self * other

    def __repr__(self):
        if self.is_null:
            return "O"
        return repr(tuple(self))


def generate_curve_points(curve: EllipticCurve):
    result = []
    a, b, p = curve
    m = p // 4
    for x in range(p):
        y2 = (x * x * x + a * x + b) % p
        l = crypto_lib.fastpow(y2, (p - 1) // 2, p)
        if l not in (0, 1):
            continue
        y = crypto_lib.fastpow(y2, m + 1, p)
        result.append(EllipticPoint(x, y, curve))
        if y != 0:
            result.append(EllipticPoint(x, (-y) % p, curve))
    return result


def generate_primes(n):
    # решето Эратосфена, можно немного оптимизировать, сразу убрав из решетки четные
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, (n+1) // 2):
        for j in range(2*i, n+1, i):
            sieve[j] = False
    return [i for i, f in enumerate(sieve) if f]


def _test_generate_curve_points():
    curve = EllipticCurve(1, 2, 19)
    expected = {
        EllipticPoint(1, 2, curve),
        EllipticPoint(1, 17, curve),
        EllipticPoint(8, 3, curve),
        EllipticPoint(8, 16, curve),
        EllipticPoint(10, 9, curve),
        EllipticPoint(10, 10, curve),
        EllipticPoint(14, 9, curve),
        EllipticPoint(14, 10, curve),
        EllipticPoint(17, 7, curve),
        EllipticPoint(17, 12, curve),
        EllipticPoint(18, 0, curve),
    }
    actual = set(generate_curve_points(curve))
    assert expected == actual, (expected - actual, actual - expected)


def _test_ops():
    curve = EllipticCurve(1, 2, 19)
    p = EllipticPoint(1, 2, curve)
    q = EllipticPoint(10, 10, curve)
    assert p + q == EllipticPoint(17, 7, curve), p + q
    assert p + p == EllipticPoint(18, 0, curve), p + p
    assert 2 * p == EllipticPoint(18, 0, curve), 2 * p
    assert (q - q).is_null, q - q
    assert q + p - q == p, (p, q, q + p, q + p - q)
    r = p
    for _ in range(curve.p * curve.p):
        r += p
        if r.is_null:
            break
    assert r.is_null, r


def main():
    _test_generate_curve_points()
    _test_ops()
    assert generate_primes(17) == [2, 3, 5, 7, 11, 13, 17]

    curve = EllipticCurve(-5, -1, 23)
    assert (4 * curve.a ** 3 + 27 * curve.b ** 2) % curve.p != 0

    print("Generating keypair")
    points = generate_curve_points(curve)
    print(f"Generated points for {curve}: {points}")
    curve_order = len(points) + 1  # +1 is for the point at infinity
    print(f"n = {curve_order}")

    print("Generating P...")
    # Ищем такую точку, которая образует подгруппу простого порядка
    # причем желательно, чтобы порядок был по-больше.
    # Для всех точек кривой находим порядок циклической подгруппы, которую точка
    # порождает, после чего смотрим, является ли порядок простым.
    # И среди всех точек, порождающих подгруппу простого порядка, выбираем ту,
    # где порядок наибольший.
    # На практике так делать слишком медленно, на практике сначала вычисляют
    # порядок кривой (есть какой-то полиномиальный алгоритм для этого),
    # затем находят достаточно большой делитель и затем вычисляют базовую точку
    # по формуле (N/n)*P, N - порядок кривой, n - найденный делитель, P - любая точка.
    # Нетрудно доказать, что такая точка всегда генерирует подгруппу порядка n...
    p = None
    n = 0
    primes_up_to_n = set(generate_primes(curve_order))
    for pp in points:
        p_acc = curve.zero
        for i in range(1, curve_order+1):
            p_acc += pp
            if p_acc.is_null:
                if i > n:
                    if i in primes_up_to_n:
                        n = i
                        p = pp
                break
    print(f"Found P={p} of order = {n}")

    # Генерируем пару ключей:
    d = random.randrange(1, n)
    q = d * p
    public_key = curve.a, curve.b, p, n, q
    private_key = d
    print(f"public key (a, b, P, n, Q) = {public_key}")
    print(f"private key (d) = {private_key}")

    # Подпись:
    # Сообщение представлено в виде просто неотрицательного числа, по модулю
    # не превышающего n. На практике вычисляется какой-нибудь криптостойкий хеш и
    # обрезается до битовой длины не длинее n.
    t = random.randrange(n)
    print(f"Singing message t = {t}")
    signature = None
    while True:
        k = random.randrange(1, n)
        print(f"trying k = {k}")
        x1, y1 = k * p
        r = x1 % n
        if r == 0:
            continue
        l = crypto_lib.inverse_in_group(k, n)
        s = (l * (t + d * r)) % n
        if s == 0:
            continue
        signature = r, s
        break
    print(f"signature (r, s) = {signature}")

    # Проверка подписи:
    print(f"Validating signature")
    r, s = signature
    assert 1 <= s <= n - 1
    assert 1 <= r <= n - 1
    w = crypto_lib.inverse_in_group(s, n)
    u1 = (t * w) % n
    u2 = (r * w) % n
    x0, y0 = u1 * p + u2 * q
    v = x0 % n
    print(f"w = {w}; u1 = {u1}; u2 = {u2}; x0 = {x0}; v = {v}")
    valid = v == r
    print("OK" if valid else "Invalid!")


if __name__ == "__main__":
    main()
